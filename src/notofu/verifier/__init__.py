import requests

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
        'status': response.status_code,
        'content': response.content.decode('utf-8')
    }