import os
import glob
from typing import List
from fastapi import FastAPI, HTTPException
from pathlib import Path
import sys

# Import signer functions from the notofu.signer package
import notofu.signer as signer

app = FastAPI(debug=True,title="Proof Server", description="SSH Host Key Proof Server")

@app.get("/sign-keys")
async def get_sign_keys():
    """
    GET /sign-keys endpoint that:
    1. Finds SSH host key files in /etc/ssh
    2. Loads them as strings
    3. Gets AWS credentials via IMDSv2
    4. Generates a signed proof request
    5. Returns the result
    """
    
    proof_request = signer.sign_keys()
    
    # Step 6: Return the result
    return proof_request

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)