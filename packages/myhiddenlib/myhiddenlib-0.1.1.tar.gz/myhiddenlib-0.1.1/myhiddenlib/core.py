import base64

def get_api_timeout():
    return base64.b64decode("dGV4dDEyMzExaG8=").decode()