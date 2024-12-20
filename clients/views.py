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

    # Adresse et port du serveur
    HOST = "192.168.137.69"  # Remplacez par l'adresse de votre serveur
    PORT = 12345

    # Lancer le socket client dans un processus séparé
    client_process = multiprocessing.Process(target=stream_screen, args=(HOST, PORT))
    client_process.daemon = True  # Assurez-vous que ce processus se termine si le programme principal se termine
    client_process.start()

    return JsonResponse({"message": "Socket client démarré en arrière-plan !"})



# from django.http import JsonResponse
# import socket
# import platform
# import cv2
# import numpy as np
# import mss
# from pynput.mouse import Controller
# import threading

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

# def start_client_view(request):
#     """Vue Django pour démarrer automatiquement le socket client."""
#     # Adresse et port du serveur
#     HOST = "192.168.137.69"  # Remplacez par l'adresse de votre serveur, ici localhost
#     PORT = 12345

#     # Lancer le socket client dans un thread séparé
#     client_thread = threading.Thread(target=stream_screen, args=(HOST, PORT), daemon=True)
#     client_thread.start()

#     return JsonResponse({"message": "Socket client démarré automatiquement !"})
