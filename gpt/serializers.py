# Describes process of converting data to JSON format
from rest_framework import serializers
from .models import Conversation, Message

# class DrinkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Drink
#         fields = ('id', 'name', 'description')

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'