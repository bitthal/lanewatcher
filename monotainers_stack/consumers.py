# # monotainers_stack/consumers.py

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import LaneData

# # class DataUpdateConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         await self.accept()

# #     async def disconnect(self, close_code):
# #         pass

# #     async def receive(self, text_data):
# #         data = json.loads(text_data)
# #         # Update the LaneData model with the received data
# #         # Send the updated data to the WebSocket
# #         await self.send(text_data=data)

# class DataUpdateConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.channel_layer.group_add('data_update', self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard('data_update', self.channel_name)

#     async def send_data_update(self, event):
#         data = []
#         for position in range(1, 9):
#             try:
#                 lane_data = LaneData.objects.get(lane=1, position=position)
#                 lane1_upper = lane_data.upper if lane_data.upper else 'NA'
#                 lane1_lower = lane_data.lower if lane_data.lower else 'NA'
#             except LaneData.DoesNotExist:
#                 lane1_upper = 'NA'
#                 lane1_lower = 'NA'

#             try:
#                 lane_data = LaneData.objects.get(lane=2, position=position)
#                 lane2_upper = lane_data.upper if lane_data.upper else 'NA'
#                 lane2_lower = lane_data.lower if lane_data.lower else 'NA'
#             except LaneData.DoesNotExist:
#                 lane2_upper = 'NA'
#                 lane2_lower = 'NA'

#             data.append({
#                 'position': position,
#                 'lane1_upper': lane1_upper,
#                 'lane1_lower': lane1_lower,
#                 'lane2_upper': lane2_upper,
#                 'lane2_lower': lane2_lower,
#             })

#         await self.send(json.dumps(data))


# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import LaneData

# class DataUpdateConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.channel_layer.group_add('data_update', self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard('data_update', self.channel_name)

#     async def send_data_update(self, event):
#         data = await self.get_lane_data()
#         await self.send(json.dumps(data))

#     @database_sync_to_async
#     def get_lane_data(self):
#         data = []
#         for position in range(1, 9):
#             try:
#                 lane_data = LaneData.objects.get(lane=1, position=position)
#                 lane1_upper = lane_data.upper if lane_data.upper else 'NA'
#                 lane1_lower = lane_data.lower if lane_data.lower else 'NA'
#             except LaneData.DoesNotExist:
#                 lane1_upper = 'NA'
#                 lane1_lower = 'NA'

#             try:
#                 lane_data = LaneData.objects.get(lane=2, position=position)
#                 lane2_upper = lane_data.upper if lane_data.upper else 'NA'
#                 lane2_lower = lane_data.lower if lane_data.lower else 'NA'
#             except LaneData.DoesNotExist:
#                 lane2_upper = 'NA'
#                 lane2_lower = 'NA'

#             data.append({
#                 'position': position,
#                 'lane1_upper': lane1_upper,
#                 'lane1_lower': lane1_lower,
#                 'lane2_upper': lane2_upper,
#                 'lane2_lower': lane2_lower,
#             })

#         return data



# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

# class DataUpdateConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         await self.send(text_data=json.dumps({'message': message}))


# In myapp/consumers.py (replace `myapp` with the name of your app)
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DataUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

