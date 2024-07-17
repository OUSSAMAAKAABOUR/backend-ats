from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from authentication.models import Message, User, Clients
import json
from datetime import datetime
# Global variable to store connected clients
connected_clients = {}
incalls = []

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_id = self.scope['url_route']['kwargs']['sender_id']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        
        await self.add_client_channel(self.sender_id, self.channel_name)

        await self.accept()
        print(f"Connected: sender_id={self.sender_id}")

    async def disconnect(self, close_code):
        await self.remove_client_channel(self.channel_name)
        print(f"Disconnected: sender_id={self.sender_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        print(f"Received message: {data}")

        handlers = {
            'chat_message': self.handle_chat_message,
            'offer': self.handle_offer,
            'answer': self.handle_answer,
            'ice_candidate': self.handle_ice_candidate,
            'call_ended': self.handle_call_ended,
            'handele_check_if_busy':self.handele_check_if_busy,
            'file_message': self.handle_file_message,  # Add this line

        }

        if message_type in handlers:
            await handlers[message_type](data)
        else:
            print(f"Unknown message type: {message_type}")

    async def handele_check_if_busy(self,data):
        receiver_id=data['receiver_id']
        sender_id=data['sender_id']
        
        receiver_in_call = await self.get_in_call_status(int(receiver_id))
        sender_in_call = await self.get_in_call_status(int(sender_id))
        if receiver_in_call==True or sender_in_call==True :
            call = True
        else:
            call = False
        sender_channel_name = await self.get_channel_name(sender_id)
        if sender_channel_name:
            await self.channel_layer.send(
                sender_channel_name,
                {
                    "type": "webrtc.busy",
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "incalls":incalls,
                    "call":call
                }
            )
        print("Sending busy message.....",call,incalls,receiver_id,sender_id)
        


    async def handle_file_message(self, data):
        file_name = data['fileName']
        file_type = data['fileType']
        file_data = data['fileData']
        receiver_id = data['receiver_id']
        timestamp = datetime.now().isoformat()

        await self.save_file_message(file_name, file_type, file_data, timestamp)

        receiver_channel_name = await self.get_channel_name(receiver_id)
        if receiver_channel_name:
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type": "file.message",
                    "fileName": file_name,
                    "fileType": file_type,
                    "fileData": file_data,
                    "sender_id": self.sender_id,
                    "receiver_id": receiver_id,
                    "timestamp": timestamp
                }
            )
    async def handle_chat_message(self, data):
        message = data['message']
        receiver_id= data['receiver_id'] 
        timestamp = datetime.now().isoformat()  # Get current timestamp in ISO format
        print(f"Handling chat message: {message}")
        await self.save_message(message, timestamp)

        receiver_channel_name = await self.get_channel_name(receiver_id)
        if receiver_channel_name:
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "sender_id": self.sender_id,
                    "receiver_id": receiver_id,
                    "timestamp": timestamp  # Include timestamp in the message
                }
            )


    async def handle_offer(self, data):
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        global connected_clients
        receiver_channel_name = await self.get_channel_name(receiver_id)
        connected_clients[receiver_id] = sender_id
        if receiver_channel_name:
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type": "webrtc.offer",
                    "offer": data['offer'],
                    "callType": data.get('callType'),
                    "sender_id": self.sender_id,
                }
            )
        print(f'Offer handled: sender_id={self.sender_id}, receiver_id={receiver_id}')

    async def handle_answer(self, data):
        
        global incalls
        sender_id = int(data['sender_id'])
        receiver_id = int(data['receiver_id'])
        await self.update_in_call_status(sender_id, True)
        await self.update_in_call_status(receiver_id, True)
        
        print(f"Updated incalls: {incalls}")
        
        # Rest of your handle_answer function...
        global connected_clients
        sender_id = connected_clients.get(self.sender_id)
        if sender_id:
            receiver_channel_name = await self.get_channel_name(sender_id)
            if receiver_channel_name:
                await self.channel_layer.send(
                    receiver_channel_name,
                    {
                        "type": "webrtc.answer",
                        "answer": data['answer'],
                        "sender_id": self.sender_id,
                    }
                )
            


            print(f'Answer handled: sender_id={self.sender_id}, receiver_id={sender_id}')
        else:
            print(f'No sender found for receiver_id={self.sender_id}')

    async def handle_ice_candidate(self, data):
        print(f"Handling ICE candidate: {data}")
        global connected_clients
        receiver_channel_name = await self.get_channel_name(self.receiver_id)
        connected_clients[self.receiver_id] = data['sender_id']
        if receiver_channel_name:
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type": "webrtc.ice_candidate",
                    "candidate": data['candidate'],
                    "sender_id": self.sender_id,
                }
            )
            

    async def handle_call_ended(self, data):
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        print(f"Handling call ended: sender_id={sender_id}, receiver_id={receiver_id}")
        global connected_clients, incalls
        receiver_id = connected_clients.get(self.sender_id)
        if receiver_id:
            receiver_channel_name = await self.get_channel_name(receiver_id)
            if receiver_channel_name:
                await self.channel_layer.send(
                    receiver_channel_name,
                    {
                        "type": "webrtc.call_ended",
                        "sender_id": self.sender_id,
                    }
                )
                
            # del connected_clients[self.sender_id]  # Remove the connection
            # del connected_clients[receiver_id]  # Remove the connection

            await self.update_in_call_status(int(sender_id), False)
            await self.update_in_call_status(int(receiver_id), False)
            await self.update_in_call_status(int(self.sender_id), False)
            await self.update_in_call_status(int(self.receiver_id), False)
        else:
            print(f"No active call found for sender_id={self.sender_id}")

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        receiver_id = event['receiver_id']
        timestamp = event['timestamp']
        print(f"Sending chat message: {message}, sender_id: {sender_id}")
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'timestamp': timestamp
        }))

    async def webrtc_offer(self, event):
        print(f"Sending WebRTC offer: {event}")
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer'],
            'callType': event.get('callType'),
            'sender_id': event['sender_id'],
        }))

    async def webrtc_answer(self, event):
        print(f"Sending WebRTC answer: {event}")
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'sender_id': event['sender_id'],
        }))

    async def webrtc_ice_candidate(self, event):
        print(f"Sending WebRTC ICE candidate: {event}")
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'sender_id': event['sender_id'],
        }))

    async def webrtc_call_ended(self, event):
        print(f"Sending WebRTC call ended: {event}")
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'sender_id': event['sender_id'],
        }))
    async def webrtc_busy(self, event):
        print(f"Sending WebRTC busy: {event}")
        await self.send(text_data=json.dumps({
            'type': 'busy',
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'incalls':event['incalls'],
            'call':event['call']
        }))
        print("Sending busy message.....",event['call'],event['incalls'])

    async def file_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'file_message',
            'fileName': event['fileName'],
            'fileType': event['fileType'],
            'fileData': event['fileData'],
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'timestamp': event['timestamp']
        }))
    @sync_to_async
    def save_file_message(self, file_name, file_type, file_data, timestamp):
        try:
            sender = User.objects.get(id=self.sender_id)
            recipient = User.objects.get(id=self.receiver_id)
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                content=f"File: {file_name}",
                file_name=file_name,
                file_type=file_type,
                file_data=file_data,
                timestamp=datetime.fromisoformat(timestamp)
            )
        except User.DoesNotExist as e:
            print(f"Error saving file message: {e}")

    @sync_to_async
    def get_channel_name(self, user_id):
        try:
            client = Clients.objects.filter(user_id=user_id).first()
            return client.channel_name if client else None
        except Clients.DoesNotExist:
            return None

    @sync_to_async
    def add_client_channel(self, user_id, channel_name):
        try:
            client, created = Clients.objects.update_or_create(
                user_id=user_id,
                defaults={'channel_name': channel_name}
            )
            if not created:
                print(f"Updated channel for user {user_id}")
            else:
                print(f"Created new channel for user {user_id}")
        except Exception as e:
            print(f"Error updating/creating client channel: {e}")

    @sync_to_async
    def remove_client_channel(self, user_id):
        try:
            Clients.objects.filter(user_id=user_id).delete()
            print(f"Removed channel for user {user_id}")
        except Exception as e:
            print(f"Error removing client channel: {e}")
    @sync_to_async
    def update_in_call_status(self, user_id, status):
        try:
            user = User.objects.get(id=user_id)
            user.in_call = status
            user.save()
        except User.DoesNotExist:
            print(f"User with id {user_id} not found")

    @sync_to_async
    def get_in_call_status(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user.in_call
        except User.DoesNotExist:
            print(f"User with id {user_id} not found")
            return False
    @sync_to_async
    def save_message(self, message, timestamp):
        try:
            sender = User.objects.get(id=self.sender_id)
            recipient = User.objects.get(id=self.receiver_id)
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                content=message,
                timestamp=datetime.fromisoformat(timestamp)
            )
        except User.DoesNotExist as e:
            print(f"Error saving message: {e}")
