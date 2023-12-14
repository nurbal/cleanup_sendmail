import argparse
import ldap
import os
import json
import pathlib

mydir = os.path.dirname(os.path.realpath(__file__))+'/'

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

    # scan moved files
    directory = pathlib.Path(args.movedfiles_dir).absolute()
    print(f"Scanning directory: {directory}...")
    subdirs = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    for subdir in subdirs:
        print(f"Scanning subdirectory: {directory/subdir}...")
        json_file = directory / subdir / 'map.json'
        if os.path.isfile(json_file):
            print(f"Reading file: {json_file}...")
            with open(json_file, "r") as f:
                map_data = json.load(f)
                # print(f"Found {len(map_data)} entries.")
                # for key in map_data:
                #     print(f"key: {key}")
                #     print(f"values: {map_data[key]}")
                
                                    

if __name__ == "__main__":
    main()
