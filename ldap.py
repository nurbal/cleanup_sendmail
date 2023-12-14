# get a user email from its username, using the Mila LDAP
# usage: python ldap.py <username> (debug purpose only)


import argparse
import os
import ssl
import json
from ldap3 import ALL_ATTRIBUTES, SUBTREE, Connection, Server, Tls


def query_ldap_users(local_private_key_file = "secrets/ldap/Google_2026_01_26_66827.key", 
                     local_certificate_file = "secrets/ldap/Google_2026_01_26_66827.crt", 
                     ldap_service_uri = "ldaps://ldap.google.com"):
    """
    returns a dic of the user information from the ldap
    user['posixUid'] = {'email': '...', 'display_name': '...'}
    """

    assert os.path.exists(
        local_private_key_file
    ), f"Missing local_private_key_file {local_private_key_file}."
    assert os.path.exists(
        local_certificate_file
    ), f"Missing local_certificate_file {local_certificate_file}."

    # Prepare TLS Settings
    tls_conf = Tls(
        local_private_key_file=local_private_key_file,
        local_certificate_file=local_certificate_file,
        validate=ssl.CERT_REQUIRED,
        version=ssl.PROTOCOL_TLSv1_2,
    )
    # Connect to LDAP
    server = Server(ldap_service_uri, use_ssl=True, tls=tls_conf)
    conn = Connection(server)
    conn.open()
    # Extract all the data
    conn.search(
        "dc=mila,dc=quebec",
        "(objectClass=inetOrgPerson)",
        search_scope=SUBTREE,
        attributes=ALL_ATTRIBUTES,
    )

    print(f"Found {len(conn.entries)} entries.")
    print(f"First entry: {conn.entries[0]}")
    
    users = {}
    for entry in conn.entries:
        user = {}
        user["email"] = str(entry["mail"])
        user["display_name"] = str(entry["displayName"])
        user['posixUid'] = str(entry["posixUid"])
        user['googleUid'] = str(entry["googleUid"])
        users[user['posixUid']] = user

        if user['googleUid'] != user['posixUid']:
            print(f"Warning: googleUid != posixUid for user {user['posixUid']} ({user['display_name']})")
            print(f"googleUid: {user['googleUid']}")
            print(f"posixUid:  {user['posixUid']}")
            print(f"email: {user['email']}")


    print(f"Found {len(users)} users.")
    return users
 


if __name__ == "__main__":
    # use directly only for test purpose

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username to query")
    parser.add_argument(
        "--ldap_service_uri",
        default="ldaps://ldap.google.com",
        help="URI of the LDAP service",
    )
    parser.add_argument(
        "--local_private_key_file",
        default="secrets/ldap/Google_2026_01_26_66827.key",
        help="local private key file for the LDAP service",
    )
    parser.add_argument(
        "--local_certificate_file",
        default="secrets/ldap/Google_2026_01_26_66827.crt",
        help="local certificate file for the LDAP service",
    )
    args = parser.parse_args()


    use_cache = True
    cache_file = f"ldap_users.json"

    # Query LDAP
    if use_cache and os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            ldap_data = json.load(f)
    else:
        ldap_data = query_ldap_users(
            args.local_private_key_file,
            args.local_certificate_file,
            args.ldap_service_uri
        )
        with open(cache_file, "w") as f:
            json.dump(ldap_data, f) 

    # print paramters
    print(f"username: {args.username}")
    print(f"ldap_service_uri: {args.ldap_service_uri}")
    print(f"local_private_key_file: {args.local_private_key_file}")
    print(f"local_certificate_file: {args.local_certificate_file}")

    user = ldap_data[args.username]

    # print user information
    print(f"email: {user['email']}")
    print(f"display_name: {user['display_name']}")
    print(f"posixUid: {user['posixUid']}")
    print(f"googleUid: {user['googleUid']}")

 