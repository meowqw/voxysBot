import requests
API_DOMAIN = 'http://voxys.meatqwtest.ga'

def post_client(client):
    response = requests.post(API_DOMAIN + '/api/client', client)
    
    if response.status_code == 201:
        return response.json()['data']['id']
    else:
        return None
    
def post_meeting(data):
    
    response = requests.post(API_DOMAIN + '/api/meeting', data)
    
    if (response.status_code == 201):
        return True
    else:
        return False