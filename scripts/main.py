#!/usr/bin/env python3

import json
import sys

from notofu.signer import get_credentials_via_imdsv2, get_region, get_imdsv2_token




def main():
    # print("AWS Instance Credentials Retrieval PoC")
    # print("=" * 40)
    
    # Try IMDSv2 first
    # print("\n1. Attempting to retrieve credentials via IMDSv2...")
    token = get_imdsv2_token()
    imds_region = get_region(token)
    print(f"region: {imds_region}")

    # imds_creds = get_credentials_via_imdsv2(token)
    # print(json.dumps(imds_creds,indent=2))
    # creds = Credentials(
    #     access_key=imds_creds['credentials']['AccessKeyId'], 
    #     secret_key=imds_creds['credentials']['SecretAccessKey'],
    #     token=imds_creds['credentials']['Token'],
    #     method=imds_creds['method']
    # )
    # host_keys = [
    #     "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDDXLx1QDm+4rKdPy1bv6LQYskyTyTu6Tortxxq7+yXq root@nixos",
    #     "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCeZNdAkVAyf+AyKIW36WHUylEom/f8qSC8mAe4aZPLH0BDIiCXwVK35W9WXvgDmDwCvQQfMDbfQkdBQ9qkrr945YO0T6H9lasb03pF7EFyBu0L4qNwrwhMnaWk/0MtUDaVArXjWTwFAo+BtCAMOYdALcNeibbeLYCcaSVVy1ffHkRbCFbJeNnKPgScmDvPrj0fbBiUuHQ9vpO6Ott4XMGPJiRZlHoZ2sSgviHQTRwpZqhS9t8y1QWdx/YLNfox9TefVOTezdM8SJSj8DEs9sgHul9TDipqZaelob+MvBoKCrtjKxM9gao/jG4UUI3ZFvXZioqlCY3wymh75No01f44Rko4SEqh+Zhx0V772x1amAuZ9auahU8CofIq+GCDbxlZCWNh7eNrie4OQ5xfSqv/X1fyJ3nZthNzyXwDZHv7jTuXtj+mQJQZtEqI8jld4vNAkMPmON2jTM4pR6kxaXTbYw3GmbNiUCumTZhkQK1VZ2mXAySwqSNHRf3muIxP/pxzkKMvQNOeTDZzEu07o09Dz/y/nuyLzcXxOU9NvZo1Dtula6vcsDEMFNEPGaPDXRi1y5oRPGdcPIsIxWGYWulyY7PM07jMHDsTZLVM/4vIJfCqdr+xdigM3wy/M+DEp3j+XftYw+xf22DlgH5+ba9ALKuMHe7D0bIYLK4gVT/ETQ== root@nixos"
    # ]
    # req = get_proof_req(creds, 'us-east-2', host_keys)
    # req_json = json.dumps(req,indent=2)
    # req_dict = json.loads(req_json)
    # req_obj = rebuild_request(req_dict)
    # response = send_request(req_obj)
    
    # print("request:")
    # print(req_json)
    # print()

    # print(f"staus: {response['status']}")
    # print(f"content")
    # print(response['content'])

if __name__ == "__main__":
    sys.exit(main())
