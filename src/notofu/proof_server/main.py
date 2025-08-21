import os
import glob
from typing import List
from fastapi import FastAPI, HTTPException
from pathlib import Path
import sys

# Import signer functions from the notofu.signer package
from notofu.signer import get_credentials_via_imdsv2, get_imdsv2_token, get_proof_req, get_region

app = FastAPI(debug=True,title="Proof Server", description="SSH Host Key Proof Server")


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


@app.get("/signkeys")
async def get_signkeys():
    """
    GET /signkeys endpoint that:
    1. Finds SSH host key files in /etc/ssh
    2. Loads them as strings
    3. Gets AWS credentials via IMDSv2
    4. Generates a signed proof request
    5. Returns the result
    """
    # Step 1 & 2: Find and load SSH host keys
    host_keys = find_ssh_host_keys()
    
    # Step 4: Get credentials via IMDSv2
    token = get_imdsv2_token()
    credentials = get_credentials_via_imdsv2(token)

    # Step 5: Get proof request with credentials and host keys
    # Extract region from credentials if available, default to us-east-1
    region = get_region(token)  # Default region

    proof_request = get_proof_req(credentials, region, host_keys)
    
    # Step 6: Return the result
    return proof_request

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)