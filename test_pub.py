import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/nirajpawar981/cloud-monitor-key.json"

from google.cloud import pubsub_v1

PROJECT_ID = "southern-ivy-498911-g8"
TOPIC_ID = "cloud-monitor-alerts"

publisher = pubsub_v1.PublisherClient()

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

future = publisher.publish(
    topic_path,
    b"PARTH TEST MESSAGE"
)

print("Message ID:", future.result())
