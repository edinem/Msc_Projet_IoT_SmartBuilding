 # Gateway
 Ce répertoire contient les fichiers sources afin de pouvoir exécuter la gateway. Cette dernière est basée sur `flask`. La `gateway` est en charge de :
 * Intéroger le sensor et envoyer ses valeurs sur la plateforme `Microsoft Azure IoT Hub`
 * Exécuter les actions sur le serveur `knx` qui est en charge de la gestion des stores et des radiateurs.

 Afin de lancer, il suffit d'exécuter la commande suivante : 

 `python3 .\flask-main.py -H {adresse_ip_gateway} -l debug --knx-gateway {adresse_serveur_knx}`

Les paquets nécessaires à la bonne exécution du serveur se trouvent dans le fichier `requirements.txt`. Afin d'installer les paquets, il suffit de taper la commande ci-dessous : 

`pip3 install -r requirements.txt`