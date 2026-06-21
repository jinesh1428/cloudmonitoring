import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/nirajpawar981/cloud-monitor-key.json"

from google.cloud import pubsub_v1

PROJECT_ID = "southern-ivy-498911-g8"
SUBSCRIPTION_ID = "cloud-monitor-sub"

subscriber = pubsub_v1.SubscriberClient()

subscription_path = subscriber.subscription_path(
    PROJECT_ID,
    SUBSCRIPTION_ID
)

response = subscriber.pull(
    request={
        "subscription": subscription_path,
        "max_messages": 10,
    }
)

for msg in response.received_messages:
    print(msg.message.data.decode())

    subscriber.acknowledge(
        request={
            "subscription": subscription_path,
            "ack_ids": [msg.ack_id]
        }
    )
