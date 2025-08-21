#!/usr/bin/env python3

import json
import sys
import requests
from typing import Optional, Dict, Any
from botocore.awsrequest import AWSRequest
from botocore.signers import RequestSigner
from botocore.hooks import HierarchicalEmitter
from botocore.model import ServiceId
from botocore.credentials import Credentials

def get_credentials_via_imdsv2() -> Optional[Dict[str, Any]]:
    """Retrieve AWS instance credentials using direct IMDSv2 requests."""
    try:
        # Step 1: Get session token
        token_response = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=5
        )
        
        if token_response.status_code != 200:
            print(f"Failed to get IMDSv2 token: {token_response.status_code}")
            return None
            
        token = token_response.text
        
        # Step 2: Get EC2 instance credentials directly
        creds_response = requests.get(
            "http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=5
        )
        
        if creds_response.status_code != 200:
            print(f"Failed to get credentials: {creds_response.status_code}")
            return None
            
        credentials = json.loads(creds_response.text)
        return {
            "method": "IMDSv2",
            "endpoint": "identity-credentials/ec2/security-credentials/ec2-instance",
            "credentials": credentials
        }
        
    except requests.RequestException as e:
        print(f"Network error accessing IMDS: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse credentials JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def call_get_caller_identity(credentials, region) -> Optional[Dict[str, Any]]:
    """Generate an AWS API request for STS get-caller-identity, sign it, and send it."""
    # Create the STS get-caller-identity request
    endpoint = f'https://sts.{region}.amazonaws.com/'
    service = 'sts'
    action="GetCallerIdentity"
    # Create AWSRequest
    request = AWSRequest(
        method='POST',
        url=endpoint,
        data=f'Action={action}&Version=2011-06-15',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': f'{service}.{region}.amazonaws.com'
        }
    )
    
    # Create RequestSigner
    emitter = HierarchicalEmitter()

    signer = RequestSigner(
        service_id=ServiceId('STS'),
        region_name=region,
        signing_name='sts',
        signature_version='v4',
        credentials=credentials,
        event_emitter=emitter
    )
    
    # Sign the request
    signer.sign(operation_name=action,request=request)
    
    # Prepare the request
    prepared_request = request.prepare()
    
    # Send the signed request
    response = requests.request(
        method=prepared_request.method,
        url=prepared_request.url,
        headers=dict(prepared_request.headers),
        data=prepared_request.body,
        timeout=30
    )
    
    return {
        'status': response.status_code,
        'content': response.content.decode('utf-8')
    }

def main():
    print("AWS Instance Credentials Retrieval PoC")
    print("=" * 40)
    
    # Try IMDSv2 first
    print("\n1. Attempting to retrieve credentials via IMDSv2...")
    imds_creds = get_credentials_via_imdsv2()
    print(json.dumps(imds_creds,indent=2))
    creds = Credentials(
        access_key=imds_creds['credentials']['AccessKeyId'], 
        secret_key=imds_creds['credentials']['SecretAccessKey'],
        token=imds_creds['credentials']['Token'],
        method=imds_creds['method']
    )
    response = call_get_caller_identity(creds,'us-east-2')
    
    print(json.dumps(response))
        
    # Try boto3
    # print("\n2. Attempting to retrieve credentials via boto3...")
    # boto3_creds = get_credentials_via_boto3()
    
    # if boto3_creds:
    #     print("✓ Successfully retrieved credentials via boto3")
    #     print(f"  Access Key: {boto3_creds['credentials']['AccessKeyId'][:10]}...")
    #     expiration = boto3_creds['credentials'].get('Expiration')
    #     if expiration:
    #         print(f"  Expiration: {expiration}")
    # else:
    #     print("✗ Failed to retrieve credentials via boto3")
    
    # # Summary
    # print("\n" + "=" * 40)
    # if imds_creds or boto3_creds:
    #     print("Status: ✓ At least one method succeeded")
    #     return 0
    # else:
    #     print("Status: ✗ Both methods failed")
    #     print("This may be normal if not running on an EC2 instance with an IAM role")
    #     return 1

if __name__ == "__main__":
    sys.exit(main())
