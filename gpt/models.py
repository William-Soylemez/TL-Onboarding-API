from django.db import models

# class Drink(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.CharField(max_length=1000)

#     def __str__(self):
#         return self.name

class Conversation(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    name = models.CharField(max_length=100)

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    is_user_entry = models.BooleanField()
    contents = models.TextField()
    