import argparse
import ldap
import gmail
import os
import json
import pathlib
from string import Template
import pwd

mydir = os.path.dirname(os.path.realpath(__file__))+'/'

def send_warning_mail(D_user,map_data,template_message):
    print(f"Sending warning mail to {D_user['email']}...")

    restore_commands = ""
    for key in map_data:
        restore_commands += f"mv {key} {map_data[key]}\n"

    message = Template(template_message)
    message = message.substitute(
        display_name=D_user['display_name'],
        email=D_user['email'],
        restore_commands=restore_commands
    )
    # print(f"message:\n{message}")

    # send mail
    creds = gmail.getCrendentials()
    gmail.sendMessage(creds, D_user['email'], 'Scratch files deleted', message)




def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("movedfiles_dir", help="directory where moved files are stored")
    parser.add_argument(
        "--ldap_service_uri",
        default="ldaps://ldap.google.com",
        help="URI of the LDAP service",
    )
    parser.add_argument(
        "--local_private_key_file",
        default=mydir+"secrets/ldap/Google_2026_01_26_66827.key",
        help="local private key file for the LDAP service",
    )
    parser.add_argument(
        "--local_certificate_file",
        default=mydir+"secrets/ldap/Google_2026_01_26_66827.crt",
        help="local certificate file for the LDAP service",
    )
    args = parser.parse_args()

    # print parameters
    # print(f"ldap_service_uri: {args.ldap_service_uri}")
    # print(f"local_private_key_file: {args.local_private_key_file}")
    # print(f"local_certificate_file: {args.local_certificate_file}")


    # Query LDAP
    use_cache = True
    cache_file = mydir+"ldap_users.json"
    # print(f"cache_file: {cache_file}")

    if use_cache and os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            ldap_data = json.load(f)
    else:
        ldap_data = ldap.query_ldap_users(
            args.local_private_key_file,
            args.local_certificate_file,
            args.ldap_service_uri
        )
        with open(cache_file, "w") as f:
            json.dump(ldap_data, f) 

    # debug...
    ldap_data['brunocarrez'] = ldap_data['bruno.carrez']

    # load template message
    template_file = mydir+"message_template.txt"
    with open(template_file, "r") as f:
        template_message = f.read()
    # print(f"template_message:\n{template_message}")

    # scan moved files
    directory = pathlib.Path(args.movedfiles_dir).absolute()
    print(f"Scanning directory: {directory}...")
    subdirs = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    for subdir in subdirs:
        print(f"Scanning subdirectory: {directory/subdir}...")
        # subdir is the uid of the user
        uid = int(subdir)
        # translate uid to posixid
        posixId = pwd.getpwuid(uid).pw_name
        print(f"posixId: {posixId}")
        # translate posixid to user infos
        D_user = None
        if posixId not in ldap_data:
            print(f"posixId {posixId} not found in ldap_data")
            continue    
        else:
            D_user = ldap_data[posixId]
            # print(f"user: {D_user}")


        json_file = directory / subdir / 'map.json'
        if os.path.isfile(json_file):
            print(f"Reading file: {json_file}...")
            with open(json_file, "r") as f:
                map_data = json.load(f)
                # print(f"Found {len(map_data)} entries.")
                # for key in map_data:
                #     print(f"key: {key}")
                #     print(f"values: {map_data[key]}")

                # send mail to user...
                send_warning_mail(D_user,map_data,template_message)


                                    

if __name__ == "__main__":
    main()
