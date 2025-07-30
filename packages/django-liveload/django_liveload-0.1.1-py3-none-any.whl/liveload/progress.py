import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ProgressTracker:
    def __init__(self, task_id):
        self.task_id = task_id
        self.group_name = f"progress_{task_id}"
        self.channel_layer = get_channel_layer()

    def update(self, message=None, percent=None):
        if message is None and percent is None:
            raise ValueError("At least one of 'message' or 'percent' must be provided.")

        data = {}
        if message is not None:
            print(f"Status: {message}")
            data["status"] = message
        if percent is not None:
            print(f"Progress: {percent}%")
            data["percent"] = percent

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "send_update",
                "data": json.dumps(data)
            }
        )
