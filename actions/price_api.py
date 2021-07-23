import base64
import requests

API_KEY = 'nqzum2aq44amvq8g8b8wbqx4'
SECRET_KEY = '2FgCD9uN8b'
TOKEN_ENDPOINT = 'https://api.manheim.com/oauth2/token.oauth2'

 

def get_encoded_header():
    authorization_string = API_KEY + ":" + SECRET_KEY
    authorization_string_bytes = authorization_string.encode("ascii")
    # print("authorization_string_bytes-> created")

    authorization_header_encoded = base64.b64encode(authorization_string_bytes)
    # print("authorization_header_encoded:" + authorization_header_encoded.decode('ascii'))
    return authorization_header_encoded.decode('ascii')

def get_access_token(authorization_header_encoded):
    r = requests.post(TOKEN_ENDPOINT,
                      headers={'Authorization': 'Basic ' + authorization_header_encoded,
                               'content-type': 'application/x-www-form-urlencoded'},
                      data={'grant_type': 'client_credentials'})
    return r.json()

def has_token_expires(token):
    r = requests.get('https://api.manheim.com/oauth2/token/status',
                     headers={'Authorization': f'{token["token_type"]} {token["access_token"]}'})
    if r.status_code == 200:return False
    else:return True
def get_data(token,vin):
    r = requests.get(f'https://api.manheim.com/valuations/vin/{vin}?include=retail,historical,forecast',
                      headers={'Authorization': f'{token["token_type"]} {token["access_token"]}'})
    data = r.json()['items'][0]['adjustedPricing']['wholesale']

    if data['average']==0 and data['above']==0 and data['below']==0:
        return None
    else:
        text=f'{data["average"]} USD  ~  {data["above"]} USD' 
        return text



vin='JT4RN55R5G0222654'
vin='JHMGE8H43AS002030'

def FETCH_PRICE(value):
    print('--> Calling FETCH_PRICE API')
    token = {'token_type': 'Bearer', 'access_token': 'tdvmtdz436rb6tm7evaajvpw'}
    if has_token_expires(token): 
        print("Token expired. Generating new one")
        header = get_encoded_header()
        token = get_access_token(header)
    if len(str(value))==17: 
        price = get_data(token,value)
        print("** PRICE FETCHED --> ", price)
        return price


if __name__ == '__main__':
    FETCH_PRICE(vin)