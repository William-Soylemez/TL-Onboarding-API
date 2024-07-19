from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import os

@api_view(['GET'])
def test(request, format=None):
    return Response({'message': 'Hello, world!'})

@api_view(['POST'])
def prompt(request, format=None):
    
    if request.method == 'POST':
        # Reauthenticate if needed
        authorization_token = reauthenticate()
        if not authorization_token:
            print('\033[91mError: No token found\033[0m')
            return Response({'message': 'Error!'}, status=400)

        # Get the prompt from the request
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'message': 'Prompt not found!'}, status=400)

        # Set up the request
        url = 'https://tl-onboarding-project-dxm7krgnwa-uc.a.run.app/prompt'
        headers = {
            'Authorization': 'Bearer ' + authorization_token,
        }
        body = {'model': 'gpt-4o', 'messages': [{ 'role': 'user', 'content': prompt }]}
        
        # Make and check request
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            print('\033[91mError: Call to wrapper API failed\033[0m')
            return Response({'message': 'Error!'}, status=400)
        
        # Return the message
        message = response.json()['message']['content']
        return Response({'message': message})

    return Response({'message': 'Invalid request!'}, status=400)

# Used to get a new JTW token if needed
def reauthenticate():
    # Get the token from the cache
    token = cache.get('token')
    if token:
        print("Returning cached token")
        return token
    
    print("No cached token found")
    # Get a new token
    url = 'https://tl-onboarding-project-dxm7krgnwa-uc.a.run.app/login'
    body = {
        'username': os.environ.get('AUTH_USERNAME'),
        'password': os.environ.get('AUTH_PASSWORD')
    }
    print(body)
    response = requests.post(url, json=body)
    if response.status_code != 200:
        print('\033[91mError: Call to wrapper API failed\033[0m')
        return None
    
    # Cache the token and return it
    token = response.json()['token']
    cache.set('token', token, 60 * 60)
    print("Got new token")
    return token