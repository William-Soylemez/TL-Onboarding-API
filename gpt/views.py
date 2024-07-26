from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import os
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

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

        # Add the message to the database
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({'message': 'Conversation ID not found!'}, status=400)

        add_message_success = add_message(conversation_id, True, prompt)
        if not add_message_success:
            return Response({'message': 'Error adding message!'}, status=400)
        
        # Build the complete prompt from the conversation
        messages = Message.objects.filter(conversation_id=conversation_id)
        prompt = 'The following is a conversation between the user and the bot:\n'
        for message in messages:
            if message.is_user_entry:
                prompt += 'User: ' + message.contents + '\n'
            else:
                prompt += 'Bot: ' + message.contents + '\n\n'
        prompt += 'Now respond to the user as if you are a large and aggressive ogre. The user is a small and timid human.'

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
        
        # Get the message
        message = response.json()['message']['content']

        # Add the message to the database
        add_message_success = add_message(conversation_id, False, message)

        # Return the message
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
    response = requests.post(url, json=body)
    if response.status_code != 200:
        print('\033[91mError: Call to wrapper API failed\033[0m')
        return None
    
    # Cache the token and return it
    token = response.json()['token']
    cache.set('token', token, 60 * 60)
    print("Got new token")
    return token


################# MESSAGES #################

@api_view(['GET'])
def get_messages(request, format=None):
    conversation_id = request.query_params.get('conversation_id')
    if not conversation_id:
        return Response({'message': 'Conversation ID not given!'}, status=400)

    # Get the messages
    messages = Message.objects.filter(conversation_id=conversation_id)
    
    # Serialize the messages
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

# @api_view(['POST']) Actually just gets called from the prompt function
def add_message(conversation_id, is_user_entry, contents, format=None):
    # Get the conversation
    conversation = Conversation.objects.filter(conversation_id=conversation_id).first()
    if not conversation:
        return False

    # Create the message
    message = Message(conversation_id=conversation, is_user_entry=is_user_entry, contents=contents)
    message.save()
    return True


################# CONVERSATIONS #################

@api_view(['GET'])
def get_conversations(request, format=None):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'message': 'User ID not given!'}, status=400)

    # Get the conversation
    conversations = Conversation.objects.filter(user_id=user_id)
    
    # Serialize the conversation
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_conversation(request, format=None):
    if request.method == 'POST':
        # Get the user ID from the request
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        if not user_id or not name:
            return Response({'message': 'Missing information!'}, status=400)
        
        # Create the conversation
        conversation = Conversation(user_id=user_id, name=name)
        conversation.save()
        conversation_data = ConversationSerializer(conversation).data
        return Response({'message': 'Conversation added!', 'conversation': conversation_data})

    return Response({'message': 'Invalid request!'}, status=400)

@api_view(['DELETE'])
def delete_conversation(request, format=None):
    
    conversation_id = request.query_params.get('conversation_id')
    if not conversation_id:
        return Response({'message': 'Conversation ID not given!'}, status=400)

    conversation = Conversation.objects.filter(conversation_id=conversation_id).first()
    if not conversation:
        return Response({'message': 'Conversation not found!'}, status=400)
    conversation.delete()
    return Response({'message': 'Conversation deleted!'})