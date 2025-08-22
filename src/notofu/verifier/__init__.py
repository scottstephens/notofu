import requests
import xmltodict

def send_request(request, timeout=30):

    # Send the signed request
    response = requests.request(
        method=request['method'],
        url=request['url'],
        headers=request['headers'],
        data=request['data'],
        timeout=timeout
    )
    
    return {
        'status_code': response.status_code,
        'content': response.content.decode('utf-8')
    }

def verify(signkeys_data):
    
    # Extract public keys from headers
    public_keys = []
    headers = signkeys_data.get("headers", {})
    for key, value in headers.items():
        if key.startswith("X-SSH-HOST-KEY-"):
            public_keys.append(value)
    
    # Use notofu.verifier.send_request to make the AWS STS request
    result = send_request(signkeys_data)
    
    # Parse the response based on status code
    if result['status_code'] == 200:
        # Success case - parse XML response to extract instance ID
        instance_id = None
        try:
            parsed = xmltodict.parse(result['content'])
            caller_identity = parsed.get('GetCallerIdentityResponse', {}).get('GetCallerIdentityResult', {})
            user_id = caller_identity.get('UserId', '')
            # UserId format: account:role:instance-id, extract the last part
            if ':' in user_id:
                instance_id = user_id.split(':')[-1]
        except Exception:
            pass
        
        output = {
            "status": "success",
            "public_keys": public_keys,
            "instance_id": instance_id
        }
        print(json.dumps(output))
        return 0
    else:
        # Failure case - parse XML error
        error_details = {
            "status_code": result['status_code']
        }
        
        try:
            # Parse XML error response using xmltodict
            parsed = xmltodict.parse(result['content'])
            
            # Navigate to error information
            error_response = parsed.get('ErrorResponse', {})
            error = error_response.get('Error', {})
            
            error_details["type"] = error.get('Type')
            error_details["code"] = error.get('Code')
            error_details["message"] = error.get('Message')
            
        except Exception:
            error_details["message"] = "Failed to parse error response"
        
        output = {
            "status": "failure",
            "instance_id": None,
            "public_keys": None,
            "error_details": error_details
        }