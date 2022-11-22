# MA_IoT-Securaxis (voire demo)
Étape 1 : télécharger de l’image de mosquitto et la configurer en modifiant le fichier mosquitto.conf en se basant sur ce lien : https://mosquitto.org/man/mosquitto-conf-5.html
Étape 2 : modifier le fichier communicationtomqtt.py de l’application sonal puis on fait un build de l’application 
Etape 3 : Ecrire un docker-compose.yml contenant la configurons les deux modules et on vérifie si Sonal arrive à se connecter au broker.
Étape 4 : écrire le script du subscriber et le Dockerfile puis on fait un build de l’image.
Remarque : Pour installer la bibliothèque du blob storage dans le conteneur, nous avons besoin d’utiliser Rust.
Etape 5 : ajouter l’image du subscriber au docker-compose.yml  et on vérifie si le subscriber arrive à se connecter au broker.
Étape 6 : configuration de Azure iot Hub et l'installer sur notre device en suivant les instructions décrites dans ce lien :
https://learn.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-1.4&tabs=azure-portal%2Cubuntu
Étape 7 : traduire le docker-compose.yml en un deployment manifest en se basant sur ce lien :
https://docs.docker.com/engine/api/v1.32/#tag/Container/operation/ContainerCreate
Étape 8 : déployer les applications à partir du azure iot hub et vérifier si les conteneurs sont déployés sur le device en utilisant la commande « watch docker ps ».
Étape 9 : Nous testons l’application en ajoutant du bruit près du capteur. Nous vérifions les fichier log sur le portail de azure. 
Si un message est reçu par le subscriber, on doit vérifier si des fichier sont envoyer au blob Storage.
