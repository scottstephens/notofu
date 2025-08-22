import json
import sys
import requests
from typing import Optional, Dict, Any
from botocore.awsrequest import AWSRequest, AWSPreparedRequest
from botocore.signers import RequestSigner
from botocore.hooks import HierarchicalEmitter
from botocore.model import ServiceId
from botocore.credentials import Credentials

def get_proof_req(imds_creds, region, host_keys=[]):
    """Generate an AWS API request for STS get-caller-identity, sign it, and send it."""

    # Create the STS get-caller-identity request
    endpoint = f'https://sts.{region}.amazonaws.com/'
    service = 'sts'
    action="GetCallerIdentity"
    
    host_key_headers = {
        f'X-SSH-HOST-KEY-{i}': x
        for (i,x) in enumerate(host_keys)
    }

    # Create AWSRequest
    request = AWSRequest(
        method='POST',
        url=endpoint,
        data=f'Action={action}&Version=2011-06-15',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': f'{service}.{region}.amazonaws.com'    
        } | host_key_headers
    )
    
    # Create RequestSigner
    emitter = HierarchicalEmitter()

    credentials = Credentials(
        access_key=imds_creds['credentials']['AccessKeyId'], 
        secret_key=imds_creds['credentials']['SecretAccessKey'],
        token=imds_creds['credentials']['Token'],
        method=imds_creds['method']
    )

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

    return {
        'method': prepared_request.method,
        'url': prepared_request.url,
        'headers': dict(prepared_request.headers),
        'data': prepared_request.body
    }

def get_imdsv2_token():
    token_response = requests.put(
        "http://169.254.169.254/latest/api/token",
        headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        timeout=5
    )
        
    if token_response.status_code != 200:
        raise Exception(f"Failed to get IMDSv2 token: {token_response.status_code}")
        
    token = token_response.text
    return token

def get_region(token):
    response = requests.get(
        "http://169.254.169.254/latest/meta-data/placement/region",
        headers={"X-aws-ec2-metadata-token": token},
        timeout=5
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get credentials: {response.status_code}")
    else:
        return response.content.decode('utf-8')

def get_credentials_via_imdsv2(token) -> Optional[Dict[str, Any]]:
    """Retrieve AWS instance credentials using direct IMDSv2 requests."""

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

def rebuild_request(prepared_request_dict):
    return AWSPreparedRequest(
        method=prepared_request_dict['method'],
        url=prepared_request_dict['url'],
        headers=prepared_request_dict['headers'],
        body=prepared_request_dict['data'],
        stream_output=None
    )

def find_ssh_host_keys() -> List[str]:
    """Find SSH host key files in /etc/ssh that contain 'host' and end with '.pub'"""
    ssh_dir = Path("/etc/ssh")
    host_keys = []
    
    if not ssh_dir.exists():
        return host_keys
    
    # Look for files that have "host" in the name and end in .pub
    pattern = str(ssh_dir / "*host*.pub")
    key_files = glob.glob(pattern)
    
    for key_file in key_files:
        try:
            with open(key_file, 'r') as f:
                content = f.read().strip()
                if content:
                    host_keys.append(content)
        except (IOError, OSError) as e:
            # Skip files that can't be read
            continue
    
    return host_keys

def sign_keys():
    # Step 1 & 2: Find and load SSH host keys
    host_keys = find_ssh_host_keys()
    
    # Step 4: Get credentials via IMDSv2
    token = get_imdsv2_token()
    credentials = get_credentials_via_imdsv2(token)

    # Step 5: Get proof request with credentials and host keys
    # Extract region from credentials if available, default to us-east-1
    region = get_region(token)  # Default region

    proof_request = get_proof_req(credentials, region, host_keys)