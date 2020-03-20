import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
DEFAULT_OAUTH_URL = 'https://allegro.pl/auth/oauth'
DEFAULT_REDIRECT_URI = 'http://localhost:8000'
DEFAULT_CLIENT_ID = "1c9ecb33f4374284bf16ef6f48e8891a"
DEFAULT_CLIENT_SECRET = "7HM1XgQYhiopMIZ9XGVbhjXfZmdxSuXCrQzgBE7IdSYplEx9PDQf2Q71l9L8m0aM"

def get_access_code(client_id=DEFAULT_CLIENT_ID, client_secret=DEFAULT_CLIENT_SECRET, redirect_uri=DEFAULT_REDIRECT_URI, oauth_url=DEFAULT_OAUTH_URL):

    auth_url = '{}/authorize' \
               '?response_type=code' \
               '&client_id={}' \
               '&client_secret={}' \
               '&redirect_uri={}'.format(oauth_url,client_id,client_secret,redirect_uri)
    print(auth_url)
    parsed_redirect_uri = requests.utils.urlparse(redirect_uri)

    print(parsed_redirect_uri)

    server_address = parsed_redirect_uri.hostname, parsed_redirect_uri.port

    class AllegroAuthHandler(BaseHTTPRequestHandler):
        def __init__(self, request,address, server):
            super().__init__(request,address,server)

        def do_GET(self):
            self.send_response(200,"ok")
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.server.path = self.path
            self.server.access_code = self.path.rsplit("?code=", 1)[-1]


    print("server_address: ", server_address)

    webbrowser.open(auth_url)
    httpd = HTTPServer(server_address, AllegroAuthHandler)
    print('Waiting for response with access_code from Allegro.pl (user authorization in progress)...')

    httpd.handle_request()

    httpd.server_close()

    _access_code = httpd.access_code

    print("Got an authorize code: ", _access_code)

    return _access_code


def sign_in(client_id, client_secret, access_code, redirect_uri='http://localhost:8000', oauth_url=DEFAULT_OAUTH_URL):
    token_url = oauth_url + "/token"

    access_token_data = {'grant_type': "authorization_code",
                         "code": access_code,
                         'redirect_uri': redirect_uri}

    response = requests.post(url=token_url,
                             auth=requests.auth.HTTPBasicAuth(client_id,client_secret),
                             data = access_token_data)
    print(response.json())
    return response.json()

# TO DO:
# Delete default client id and client secret in get_access_code()

access_code = get_access_code()
sign_in(DEFAULT_CLIENT_ID, DEFAULT_CLIENT_SECRET,access_code)

def searchOffer(token, )