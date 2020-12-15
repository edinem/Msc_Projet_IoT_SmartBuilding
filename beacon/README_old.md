# Labo 3 - Beacons

Ce laboratoire a été implémenté et effectué par Daniel Oliveira Paiva et Edin Mujkanovic. 

### Marche à suivre

Pour pouvoir utiliser l'application Android, il faut dans un premier temps :

1. Lancer le serveur Zwave
2. (Optionnel) Lancer le serveur Actuasim
3. Lancer la passerelle développée en spécifiant l'IP du serveur Zwave et du serveur Knx
4. Lancer l'application Android

Il faut s'assurer que le matériel Zwave aie une la bonne location avant d'utiliser l'application. En effet, les changements sont effectuées uniquement sur les matériels se trouvant dans la bonne location.

### À changer si nécessaire

L'adresse IP de la passerelle est codé en dur dans l'application. Il faudra la changer par l'adresse IP actuelle de votre passerelle.

Il faut également changer la correspondance minor-chambre des iBeacons dans la passerelle et dans le backend.py si un changement de beacon est effectué.

