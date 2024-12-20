from django.shortcuts import render
from django.http import JsonResponse
import socket
import platform
import cv2
import numpy as np
import mss
from pynput.mouse import Controller
import threading
import multiprocessing
import os
import signal

def discover_server_ip(broadcast_port=54321):
    """Fonction pour découvrir l'adresse IP du serveur via broadcast."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as discovery_socket:
            discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            discovery_socket.bind(("", broadcast_port))  # Écouter sur toutes les interfaces
            print("En attente de l'adresse IP du serveur...")
            message, server_address = discovery_socket.recvfrom(1024)  # Attente du message du serveur
            print(f"Adresse IP du serveur détectée : {server_address[0]}")
            return server_address[0]
    except Exception as e:
        print(f"Erreur lors de la découverte du serveur : {e}")
        return None

def stream_screen(host, port):
    """Fonction pour démarrer le socket client."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            print("Connecté au serveur, envoi des informations...")

            # Récupérer les informations du client
            pc_name = platform.node()  # Nom du PC
            os_name = platform.system() + " " + platform.release()  # Système d'exploitation

            # Envoyer le nom du PC
            client_socket.sendall(len(pc_name.encode('utf-8')).to_bytes(4, 'big'))
            client_socket.sendall(pc_name.encode('utf-8'))

            # Envoyer le système d'exploitation
            client_socket.sendall(len(os_name.encode('utf-8')).to_bytes(4, 'big'))
            client_socket.sendall(os_name.encode('utf-8'))

            print("Informations envoyées, streaming en cours...")

            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Capture le premier écran
                mouse_controller = Controller()  # Contrôleur de la souris

                while True:
                    # Capture l'écran
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)

                    # Récupérer la position actuelle de la souris
                    mouse_position = mouse_controller.position

                    # Compression JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])

                    # Envoi des données : la taille de la frame + la position de la souris
                    data = buffer.tobytes()
                    client_socket.sendall(len(data).to_bytes(4, 'big'))
                    client_socket.sendall(data)

                    # Envoi des coordonnées de la souris
                    mouse_position_data = f"{mouse_position[0]},{mouse_position[1]}".encode('utf-8')
                    client_socket.sendall(len(mouse_position_data).to_bytes(4, 'big'))
                    client_socket.sendall(mouse_position_data)

    except Exception as e:
        print(f"Erreur : {e}")
        # Assurez-vous que le processus se termine correctement
        os.kill(os.getpid(), signal.SIGTERM)


def start_client_view(request):
    """Vue Django pour démarrer automatiquement le socket client en arrière-plan."""
    # Découvrir dynamiquement l'adresse IP du serveur
    HOST = discover_server_ip()
    if not HOST:
        return render(request, 'error.html', {"error_message": "Impossible de découvrir l'adresse IP du serveur."})

    PORT = 12345  # Port fixe du serveur

    # Lancer le socket client dans un processus séparé
    client_process = multiprocessing.Process(target=stream_screen, args=(HOST, PORT))
    client_process.daemon = True  # Assurez-vous que ce processus se termine si le programme principal se termine
    client_process.start()

    # Renvoyer une réponse HTML
    return render(request, 'client_started.html')

# def start_client_view(request):
#     """Vue Django pour démarrer automatiquement le socket client en arrière-plan."""
#     # Découvrir dynamiquement l'adresse IP du serveur
#     HOST = discover_server_ip()
#     if not HOST:
#         return JsonResponse({"error": "Impossible de découvrir l'adresse IP du serveur."})

#     PORT = 12345  # Port fixe du serveur

#     # Lancer le socket client dans un processus séparé
#     client_process = multiprocessing.Process(target=stream_screen, args=(HOST, PORT))
#     client_process.daemon = True  # Assurez-vous que ce processus se termine si le programme principal se termine
#     client_process.start()

#     return JsonResponse({"message": "Socket client démarré en arrière-plan !"})



# from django.http import JsonResponse
# import socket
# import platform
# import cv2
# import numpy as np
# import mss
# from pynput.mouse import Controller
# import threading
# import multiprocessing
# import os
# import signal

# def stream_screen(host, port):
#     """Fonction pour démarrer le socket client."""
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#             client_socket.connect((host, port))
#             print("Connecté au serveur, envoi des informations...")

#             # Récupérer les informations du client
#             pc_name = platform.node()  # Nom du PC
#             os_name = platform.system() + " " + platform.release()  # Système d'exploitation

#             # Envoyer le nom du PC
#             client_socket.sendall(len(pc_name.encode('utf-8')).to_bytes(4, 'big'))
#             client_socket.sendall(pc_name.encode('utf-8'))

#             # Envoyer le système d'exploitation
#             client_socket.sendall(len(os_name.encode('utf-8')).to_bytes(4, 'big'))
#             client_socket.sendall(os_name.encode('utf-8'))

#             print("Informations envoyées, streaming en cours...")

#             with mss.mss() as sct:
#                 monitor = sct.monitors[1]  # Capture le premier écran
#                 mouse_controller = Controller()  # Contrôleur de la souris

#                 while True:
#                     # Capture l'écran
#                     screenshot = sct.grab(monitor)
#                     frame = np.array(screenshot)

#                     # Récupérer la position actuelle de la souris
#                     mouse_position = mouse_controller.position

#                     # Compression JPEG
#                     _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])

#                     # Envoi des données : la taille de la frame + la position de la souris
#                     data = buffer.tobytes()
#                     client_socket.sendall(len(data).to_bytes(4, 'big'))
#                     client_socket.sendall(data)

#                     # Envoi des coordonnées de la souris
#                     mouse_position_data = f"{mouse_position[0]},{mouse_position[1]}".encode('utf-8')
#                     client_socket.sendall(len(mouse_position_data).to_bytes(4, 'big'))
#                     client_socket.sendall(mouse_position_data)

#     except Exception as e:
#         print(f"Erreur : {e}")
#         # Assurez-vous que le processus se termine correctement
#         os.kill(os.getpid(), signal.SIGTERM)

# def start_client_view(request):
#     """Vue Django pour démarrer automatiquement le socket client en arrière-plan."""

#     # Adresse et port du serveur
#     HOST = "192.168.0.102"  # Remplacez par l'adresse de votre serveur
#     PORT = 12345

#     # Lancer le socket client dans un processus séparé
#     client_process = multiprocessing.Process(target=stream_screen, args=(HOST, PORT))
#     client_process.daemon = True  # Assurez-vous que ce processus se termine si le programme principal se termine
#     client_process.start()

#     return JsonResponse({"message": "Socket client démarré en arrière-plan !"})