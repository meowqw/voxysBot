import requests
# API_DOMAIN = 'http://voxys.meatqwtest.ga'
API_DOMAIN = 'http://80.87.194.13:2110'

def post_client(client):
    response = requests.post(API_DOMAIN + '/api/client', client)
    if response.status_code in [200, 201]:
        return response.json()['data']['id']
    else:
        return None
    
def post_meeting(data):
    
    response = requests.post(API_DOMAIN + '/api/meeting', data)
    if response.status_code in [200, 201]:
        return True
    else:
        return False
    
def get_information():
    
    response = requests.get(API_DOMAIN + '/api/information')
    if response.status_code == 200:
        return response.json()['data']
    else:
        return False
    
