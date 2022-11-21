import paho.mqtt.client as mqtt
import os
import json
from azure.storage.blob import BlobServiceClient
from decimal import Decimal


CONTAINER_NAME = os.environ["CONTAINER_NAME"]
AZURE_STORAGE_CONNECTION_STRING=os.environ["AZURE_STORAGE_CONNECTION_STRING"]
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(os.environ["topic"])


def on_message(client, userdata, msg):
    print("Received {data} from {topic} topic".format(data=msg.payload.decode(),topic=msg.topic))
    audio_location = os.environ["audio_location"] # Folder with Audio Files
    video_location = os.environ["video_location"] # Folder with Video files
    message_json = json.loads(msg.payload, parse_float=Decimal) # Detection results from VehicleDetection


    timestamps = [entry["t"] for entry in message_json["vd"]]# Timestamp of the detection, and filename

    sensor_name = os.environ["SENSOR_NAME"]

    print(message_json)
    
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    # Filepath formatting
    audio_filenames = [(timestamp, os.path.join("/audio/", "audio_" + str(int(float(timestamp)*1000)) + ".wav")) for timestamp in timestamps]
    print("Audio location: ", audio_filenames)
    video_filenames = [(timestamp, os.path.join("/video/", "video_" + str(int(float(timestamp)*1000)) + ".mp4")) for timestamp in timestamps]
    print("Video location: ", video_filenames)
    for audio_filename in audio_filenames:
        if os.path.isfile(audio_filename[1]):
            print("Audio file exists, uploading to Azure")

            #out = audio_bucket.put_file(audio_filename[1], '{}/{}.wav'.format(sensor_name, str(int(float(audio_filename[0])*1000))))

            FILENAME = '{}/{}.wav'.format(sensor_name, str(int(float(audio_filename[0])*1000)))
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=FILENAME)
            blob_client.upload_blob(audio_filename[1])

            os.remove(audio_filename[1])
            print("Audio file pushed and deleted.")
        else:
            print("Audio file does not exist...")
    for video_filename in video_filenames:
        if os.path.isfile(video_filename[1]):
            print("Video file exists, uploading to Azure")

            #out = video_bucket.put_file(video_filename[1], '{}/{}.mp4'.format(sensor_name, str(int(float(video_filename[0])*1000))))

            FILENAME = '{}/{}.mp4'.format(sensor_name, str(int(float(video_filename[0])*1000)))
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=FILENAME)
            blob_client.upload_blob(video_filename[1])

            os.remove(video_filename[1])
            print("Video file pushed and deleted.")
        else:
            print("Video file does not exist...")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(os.environ["broker"], 1883, 60)

client.loop_forever()
