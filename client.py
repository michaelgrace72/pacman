import pygame
import sys
import io
import socket
import logging
import json
import base64
import time

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Progjar Multiplayer Game")
clock = pygame.time.Clock()
FPS = 60

class ClientInterface:
    def __init__(self, idplayer='1'):
        self.idplayer = idplayer
        self.server_address = ('127.0.0.1', 55555)

    def send_command(self,command_str=""):
        global server_address
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        logging.warning(f"connecting to {self.server_address}")
        try:
            logging.warning(f"sending message ")
            sock.sendall(command_str.encode())
            # Look for the response, waiting until socket is done (no more data)
            data_received="" #empty string
            while True:
                #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
                data = sock.recv(16)
                if data:
                    #data is not empty, concat with previous content
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    # no more data, stop the process by break
                    break
            # at this point, data_received (string) will contain all data coming from the socket
            # to be able to use the data_received as a dict, need to load it using json.loads()
            hasil = json.loads(data_received)
            logging.warning("data received from server:")
            return hasil
        except:
            logging.warning("error during data receiving")
            return False

    def join_game(self):
        return self.send_command(f"join_game {self.idplayer}")

    def set_ready(self):
        return self.send_command(f"set_ready {self.idplayer}")

    def is_ready(self):
        return self.send_command("is_ready")

    def get_other_players(self):
        return self.send_command("get_all_players")

    def get_players_face(self):
        return self.send_command(f"get_players_face {self.idplayer}")

    def get_location(self):
        return self.send_command(f"get_location {self.idplayer}")

    def set_location(self, x, y):
        return self.send_command(f"set_location {self.idplayer} {x} {y}")

    def get_projectiles(self):
        return self.send_command("get_projectiles")

class Player:
    def __init__(self, id='1', isremote=False):
        self.id = id
        self.isremote = isremote
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.client = ClientInterface(self.id)
        face_data = self.client.get_players_face()
        if face_data and face_data['status'] == 'OK':
            self.image = pygame.image.load(io.BytesIO(base64.b64decode(face_data['face'])))
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((0, 0, 0))

    def move(self, keys):
        if not self.isremote:
            if keys[pygame.K_UP]:
                self.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.y += self.speed
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
            self.client.set_location(self.x, self.y)
        else:
            pos = self.client.get_location()
            if pos and pos['status'] == 'OK':
                x, y = pos['location'].split(',')
                self.x, self.y = int(x), int(y)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# NOTES: ini testing aja
player_id = input("Enter player ID (1/2/3): ")
client = ClientInterface(player_id)
response = client.join_game()
if not response or response['status'] != 'OK':
    print("ID already taken")
    sys.exit()

# Lobby
waiting = True
font = pygame.font.SysFont(None, 36)
while waiting:
    screen.fill((220, 220, 220))
    text = font.render(f"Player {player_id} joined. Press R to Ready.", True, (0, 0, 0))
    screen.blit(text, (100, HEIGHT // 2 - 20))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            client.set_ready()

    ready_state = client.is_ready()
    if ready_state and ready_state['ready']:
        waiting = False

# Game
player = Player(player_id)
other_players = {}
players_list = client.get_other_players()
if players_list and players_list['status'] == 'OK':
    for pid in players_list['players']:
        if pid != player_id:
            other_players[pid] = Player(pid, isremote=True)

projectile_image = pygame.Surface((10, 10))
projectile_image.fill((255, 0, 0))
projectiles = []

while True:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    player.move(keys)
    player.draw(screen)

    for pid, op in other_players.items():
        op.move(keys)
        op.draw(screen)

    if pygame.time.get_ticks() % 1 == 0:
        projectile_data = client.get_projectiles()
        if projectile_data and projectile_data['status'] == 'OK':
            projectiles = projectile_data['data']

    for p in projectiles:
        screen.blit(projectile_image, (p['x'], p['y']))

    pygame.display.flip()
    clock.tick(FPS)
