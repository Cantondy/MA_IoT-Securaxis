# IoT - Projet Securaxis : Documentation 

###### Dylan Canton & Salim Grayaa

###### 24.11.2022

---



## Architecture

Le schéma ci-dessous montre l'architecture utilisée pour l'implémentation de ce projet.

<img src="media/schemaMosquitto.PNG" alt="schémaMosquitto" style="zoom:80%;" />

---



L'utilisation de l'écosystème Azure et de ses éléments joue un rôle central. Cependant seulement certains éléments ont été utilisé dans ce projet :

**Azure IoT Hub**

L'*Azure IoT Hub* permet de gérer les messages des différents modules à l'aide du *Azure Iot Edge Runtime* installé sur le Device (Raspberry Pi). 

Il joue également un rôle au niveau de la gestion des images de containers, il récupère les images de conteneurs sur le *Container Registry* pour ensuite les transmettre au *Azure IoT Edge Runtime* sous la forme d'un manifest. Cela permet de mettre à jour les images des conteneurs des 3 modules présents sur le Device.

**Azure Container Registry**

Le *container registry* permet de stocker des images docker afin de les utiliser ensuite au niveau du Edge pour construire les 3 modules nécessaires au projet. Ces images sont récupérées depuis le *container registry* par *Azure IoT Hub*, qui va ensuite les transmettre au *Azure IoT Edge Runtime*, ce dernier va alors les utiliser pour construire les modules SONAL, MQTT Broker et Subscriber. 

L'utilisation d'un registre de container au sein même d'Azure, contrairement à l'utilisation d'un *DockerHub* par exemple, permet de rester dans l'écosystème et de tirer profit des facilités d'échange entre l'*Azure Container Registry* et l'*Azure IoT Hub*. 

**Storage blob**

Le *Blob Storage* est l'*object storage* d'Azure, il est utilisé par le module du Subscriber qui va y stocker les données récoltées par l'application SONAL, à savoir donc des fichiers audios et vidéos. 

**Azure IoT Edge Runtime**

Le *IoT Edge Runtime* est installé sur le Device pour lui permettre de communiquer avec l'*Azure IoT Hub*. 

---



Initialement, il était prévu d'utiliser le Broker MQTT d'Azure (*Azure IoT Hub MQTT*) présent dans le *Edge Hub* avec le module SONAL et le module du Subscriber. 

<img src="media/schemaAzure.PNG" alt="schemaAzure" style="zoom:80%;" />

Cependant, alors que le *Edge Hub* parvient à se connecter correctement au module SONAL, il n'arrivent pas à se connecter au module du Subscriber ce qui rend impossible ensuite l'envoie des données au *Storage Blob*. Après plusieurs recherches, il s'est avéré que le Broker d'Azure ne peut se connecter qu'à un module à la fois et que son intégration ainsi que sa maintenance ont été abandonnées par Azure au profit d'autres brokers comme *Mosquitto*. Le choix a donc été fait d'utiliser à la place le Broker MQTT *Mosquitto* qui s'avère pleinement fonctionnel dans la solution actuelle. 



## Application

**Module Subscriber**

Le module du Subscriber permet de récupérer les données provenant de SONAL qui sont transmissent par le MQTT Broker. Il s'occupe ensuite de les envoyer au *Storage Blob* d'Azure pour stockage. Nous allons décrire ici le contenu du fichier `app.py` qui effectue le travail du Subscriber.

Il convient tout d'abord d'importer un client MQTT (`paho.mqtt.client`) afin que le Subscriber puisse se connecter au Brokee MQTT. Afin d'envoyer les informations au *Blob Storage*, il faut également importer le package `azure.storage.blob`. 

```python
import paho.mqtt.client as mqtt
import os
import json
from azure.storage.blob import BlobServiceClient
from decimal import Decimal
```



La fonction `on_connect` permet ensuite, lorsque la connexion est établie avec le Broker MQTT, d'effectuer le Subscribe afin de recevoir les messages de la part du Broker.

```python
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
AZURE_STORAGE_CONNECTION_STRING=os.environ["AZURE_STORAGE_CONNECTION_STRING"]
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(os.environ["topic"])
```



La fonction `on_message` permet, lors de la réception d'un message, de récupérer les fichiers et de les envoyer au *Blob Storage* d'Azure : 

1. On récupère tout d'abord le chemin des dossiers contenant les fichiers Vidéo et Audio (ces fichiers proviennent de l'application SONAL). On récupère également les timestamps et noms des fichiers issus de la détection.
2. La connexion au *Blob Storage* est effectuée en utilisant la variable `AZURE_STORAGE_CONNECTION_STRING` correspondant au point de terminaison du *Blob* sur Azure.
3. On stock ensuite dans une liste le chemin des fichiers audios et vidéos ainsi que leur noms selon le format suivant et :
   * Fichiers audio : `audio_TIMESTAMP.wav` 
   * Fichiers vidéos : `video_TIMESTAMP.mp4`
4. Il est alors temps d'envoyer les fichiers au *Blob Storage*, la liste comportant le chemin des fichiers audios est alors parcourue. On récupère d'abord le nom de fichier dans une variable `FILENAME` nécessaire à l'envoie vers le *Blob Storage*, puis on indique au client *Blob* le container *Blob* configuré sur le cloud d'Azure dans lequel on va stocker les fichiers. Pour finir, les fichier sont uploadés sur le *Blob Storage* avec l'appel à la fonction `upload_blob`.
5. L'envoie des fichiers vidéos sur le *Blob Storage* s'effectue de la même manière que l'envoie des fichiers audios (décris au point 4.)

![subscruber-1](media/subscruber-1.PNG)



L'exécution du fichier s'effectue alors de la manière suivante :

* Création du client MQTT
* Appel à la fonction `on_connect` pour effectuer le Subscribe lorsque le client sera connecté à un Broker MQTT (fonction de callback).
* Appel à la fonction `on_message` pour la réception et l'envoie des données au *Blob Storage*.
* Connexion au broker
* La fonction `loop_forever()` permet de faire tourner le programme indéfiniment. 

```python
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(os.environ["broker"], 1883, 60)
client.loop_forever()
```



**Module SONAL**





**Module Mosquitto (MQTT Broker)**





**Fichier Manifest**
