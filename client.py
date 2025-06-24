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

    def get_items(self):
        return self.send_command("get_items")

    def collide(self):
        return self.send_command(f"collide {self.idplayer}")

    def pickup_item(self, item_id):
        return self.send_command(f"pickup_item {self.idplayer} {item_id}")


class Player:
    def __init__(self, id='1', isremote=False):
        self.id = id
        self.isremote = isremote
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        # ATRIBUT
        self.speed = 5
        self.base_speed = 5
        self.health = 3
        self.max_health = 5
        # SPEED BOOST
        self.speed_boost_end_time = 0
        self.is_speed_boosted = False
        # HITBOX
        self.width = 24
        self.height = 24
        self.client = ClientInterface(self.id)
        face_data = self.client.get_players_face()
        if face_data and face_data['status'] == 'OK':
            original_image = pygame.image.load(io.BytesIO(base64.b64decode(face_data['face'])))
            self.image = pygame.transform.scale(original_image, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((0, 0, 0))

    def update_speed_boost(self):
        current_time = time.time()
        if self.is_speed_boosted and current_time >= self.speed_boost_end_time:
            self.speed = self.base_speed
            self.is_speed_boosted = False
            print("Speed boost ended!")

    def apply_health_boost(self):
        if self.health < self.max_health:
            self.health += 1
            print(f"Health increased! Current health: {self.health}")
        else:
            print("Health already at maximum!")

    def apply_speed_boost(self):
        self.speed = self.base_speed + 3  # Increase speed by 3
        self.is_speed_boosted = True
        self.speed_boost_end_time = time.time() + 5.0  # 5 seconds

    def check_item_collision(self, items):
        player_rect = self.get_hitbox()

        for item in items:
            item_rect = pygame.Rect(item['x'], item['y'], 16, 16)
            if player_rect.colliderect(item_rect):
                pickup_result = self.client.pickup_item(item['id'])
                if pickup_result and pickup_result.get('status') == 'OK':
                    item_type = pickup_result.get('item')
                    if item_type == 'health':
                        self.apply_health_boost()
                    elif item_type == 'speed':
                        self.apply_speed_boost()
                    return True
        return False

    def move(self, keys):
        self.update_speed_boost()

        if not self.isremote:
            if keys[pygame.K_UP] and self.y > 0:
                self.y -= self.speed
            if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
                self.y += self.speed
            if keys[pygame.K_LEFT] and self.x > 0:
                self.x -= self.speed
            if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
                self.x += self.speed
            self.client.set_location(self.x, self.y)
        else:
            pos = self.client.get_location()
            if pos and pos['status'] == 'OK':
                x, y = pos['location'].split(',')
                self.x, self.y = int(x), int(y)

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

        # speed boost indicator
        if self.is_speed_boosted:
            remaining_time = self.speed_boost_end_time - time.time()
            if remaining_time > 0:
                pygame.draw.rect(surface, (0, 0, 255), (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 2)

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

# Health
heart_image = pygame.Surface((20, 20))
heart_image.fill((255, 0, 0))

# Item images
item_health_image = pygame.Surface((16, 16))
item_health_image.fill((0, 255, 0))
item_speed_image = pygame.Surface((16, 16))
item_speed_image.fill((0, 0, 255))

# Items
items = []

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
    items_data = client.get_items()
    if items_data and items_data['status'] == 'OK':
        items = items_data['items']

    if items:
        player.check_item_collision(items)

    for item in items:
        if item['type'] == 'health':
            screen.blit(item_health_image, (item['x'], item['y']))
        elif item['type'] == 'speed':
            screen.blit(item_speed_image, (item['x'], item['y']))

    collision_result = client.collide()
    if collision_result and collision_result.get('hit'):
        player.health -= 1
        if player.health <= 0:
            print("Game Over!")

    for i in range(player.max_health):
        if i < player.health:
            screen.blit(heart_image, (10 + i * 25, 10))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (10 + i * 25, 10, 20, 20), 2)

    if player.is_speed_boosted:
        remaining_time = player.speed_boost_end_time - time.time()
        if remaining_time > 0:
            font_small = pygame.font.SysFont(None, 24)
            speed_text = font_small.render(f"Speed Boost: {remaining_time:.1f}s", True, (0, 0, 255))
            screen.blit(speed_text, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)
