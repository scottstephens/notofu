#!/usr/bin/env python3
"""
Notofu Proof Client CLI Application
"""

import argparse
import sys
import requests
import json
from notofu.verifier import send_request


def main() -> int:
    """Main entry point for the proof client CLI."""
    parser = argparse.ArgumentParser(
        description="notofu proof client",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "hostname",
        help="Hostname or IP address of the server"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Parse hostname and port
    if ":" in args.hostname:
        host, port = args.hostname.split(":", 1)
        port = int(port)
    else:
        host = args.hostname
        port = 22411
    
    try:
        # Make request to signkeys endpoint
        url = f"http://{host}:{port}/sign-keys"
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the JSON response
        signkeys_data = response.json()
        
        output = verifier.verify(signkeys_data)
        print(json.dumps(output))

        if output['status'] == 'success':
            return 0
        elif output['error_details']['type'] == 'SignatureDoesNotMatch':
            return 0
        else:
            return 1
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())