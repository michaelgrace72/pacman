import pygame
import sys
import io
import socket
import logging
import json
import base64
import time
import math

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Progjar Multiplayer Game")
clock = pygame.time.Clock()
FPS = 60

# Load background image
try:
    background_image = pygame.image.load('images/background.png')
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except pygame.error:
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill((255, 255, 255))

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

    def leave_game(self):
        return self.send_command(f"leave_game {self.idplayer}")

class Player:
    def __init__(self, id='1', isremote=False):
        self.id = id
        self.isremote = isremote
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        # ATRIBUT
        self.speed = 7
        self.base_speed = 7
        self.health = 4
        self.max_health = 4
        # SPEED BOOST
        self.speed_boost_end_time = 0
        self.is_speed_boosted = False
        # HITBOX
        self.width = 52
        self.height = 52
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

    def apply_health_boost(self):
        if self.health < self.max_health:
            self.health += 1

    def apply_speed_boost(self):
        self.speed = self.base_speed + 3
        self.is_speed_boosted = True
        self.speed_boost_end_time = time.time() + 5.0

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
            # Efek gradien pulsing
            if remaining_time > 0:
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2

                base_radius = 40
                pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
                outer_radius = int(base_radius + pulse)
                inner_radius = int(base_radius - 8 + pulse)

                for i in range(inner_radius, outer_radius, 2):
                    # Hitung alpha berdasarkan jarak dari inner radius
                    distance_ratio = (i - inner_radius) / (outer_radius - inner_radius)
                    alpha = int(200 * (1 - distance_ratio))

                    color = (255, 255 - int(distance_ratio * 100), 0, alpha)

                    ring_surf = pygame.Surface((i*2 + 4, i*2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, color, (i + 2, i + 2), i, 1)
                    surface.blit(ring_surf, (center_x - i - 2, center_y - i - 2))

def select_id_screen():
    isSelect = True
    font_large = pygame.font.SysFont(None, 48)
    font_medium = pygame.font.SysFont(None, 36)
    selected_id = None

    # ID buttons
    button_1 = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 60, 80, 40)
    button_2 = pygame.Rect(WIDTH//2 - 30, HEIGHT//2 - 60, 80, 40)
    button_3 = pygame.Rect(WIDTH//2 + 90, HEIGHT//2 - 60, 80, 40)

    while isSelect:
        screen.fill((50, 50, 50))

        # Title
        title_text = font_large.render("Select Player ID", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
        screen.blit(title_text, title_rect)

        mouse_pos = pygame.mouse.get_pos()

        for i, (button, player_id) in enumerate([(button_1, "1"), (button_2, "2"), (button_3, "3")]):
            if button.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (100, 100, 100), button)
                pygame.draw.rect(screen, (255, 255, 255), button, 3)
            else:
                pygame.draw.rect(screen, (80, 80, 80), button)
                pygame.draw.rect(screen, (200, 200, 200), button, 2)

            button_text = font_medium.render(player_id, True, (255, 255, 255))
            text_rect = button_text.get_rect(center=button.center)
            screen.blit(button_text, text_rect)

        instruction_text = font_medium.render("Click to select player ID", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        screen.blit(instruction_text, instruction_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint(mouse_pos):
                        selected_id = "1"
                        isSelect = False
                    elif button_2.collidepoint(mouse_pos):
                        selected_id = "2"
                        isSelect = False
                    elif button_3.collidepoint(mouse_pos):
                        selected_id = "3"
                        isSelect = False

        # Quit button
        quit_button = pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)
        if quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (200, 0, 0), quit_button)
            pygame.draw.rect(screen, (255, 255, 255), quit_button, 3)

        else:
            pygame.draw.rect(screen, (150, 0, 0), quit_button)
            pygame.draw.rect(screen, (255, 255, 255), quit_button, 2)

        quit_text = font_medium.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        screen.blit(quit_text, quit_text_rect)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

    return selected_id

def game_over_screen():
    # Window untuk game over
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    game_over_font = pygame.font.SysFont(None, 72)
    game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(game_over_text, text_rect)

    button_font = pygame.font.SysFont(None, 36)
    info_text = button_font.render(f"Player {player_id} has been eliminated!", True, (255, 255, 255))
    info_rect = info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(info_text, info_rect)

    button_width, button_height = 200, 60
    button_x = WIDTH // 2 - button_width // 2
    button_y = HEIGHT // 2 + 50

    # Quit
    pygame.draw.rect(screen, (100, 100, 100), (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 3)

    quit_text = button_font.render("QUIT GAME", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
    screen.blit(quit_text, quit_rect)

    return pygame.Rect(button_x, button_y, button_width, button_height)

def handle_game_over_click(mouse_pos, quit_button_rect):
    if quit_button_rect.collidepoint(mouse_pos):
        pygame.quit()
        sys.exit()

# NOTES: ini testing aja
isSelectID = True

while isSelectID:
    player_id = select_id_screen()
    client = ClientInterface(player_id)
    response = client.join_game()
    if not response or response['status'] == 'OK':
        isSelectID = False
    else:
        font = pygame.font.SysFont(None, 36)
        error_text = font.render(f'{player_id} Already Selected!', True, (255, 0, 0))
        screen.fill((50, 50, 50))
        screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 2 - error_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(1000)

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

projectile_image = pygame.Surface((10, 10), pygame.SRCALPHA)
pygame.draw.circle(projectile_image, (255, 0, 0), (5, 5), 5)
projectiles = []
game_over = False

# Health
heart_full_image = pygame.image.load('images/heart_full.png')
heart_blank_image = pygame.image.load('images/heart_blank.png')

# Item images
item_health_image = pygame.transform.scale(pygame.image.load('images/potion_red.png'), (24, 24))
item_speed_image = pygame.transform.scale(pygame.image.load('images/energy.png'), (24, 24))

# Items
items = []

while True:
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            mouse_pos = pygame.mouse.get_pos()

            button_width, button_height = 200, 60
            button_x = WIDTH // 2 - button_width // 2
            button_y = HEIGHT // 2 + 50
            quit_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            handle_game_over_click(mouse_pos, quit_button_rect)

    if not game_over:
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

        if pygame.time.get_ticks() % 30 == 0:
            players_list = client.get_other_players()
            if players_list and players_list['status'] == 'OK':
                active_player_ids = set(players_list['players'])
                # Remove player kalah
                players_to_remove = [pid for pid in other_players.keys() if pid not in active_player_ids]
                for pid in players_to_remove:
                    del other_players[pid]
                # Player baru join
                for pid in active_player_ids:
                    if pid != player_id and pid not in other_players:
                        other_players[pid] = Player(pid, isremote=True)

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
                game_over = True

        for i in range(player.max_health):
            if i < player.health:
                screen.blit(heart_full_image, (10 + i * 25, 10))
            else:
                screen.blit(heart_blank_image, (10 + i * 25, 10))

        # if player.is_speed_boosted:
        #     remaining_time = player.speed_boost_end_time - time.time()
        #     if remaining_time > 0:
        #         font_small = pygame.font.SysFont(None, 24)
        #         speed_text = font_small.render(f"Speed Boost: {remaining_time:.1f}s", True, (0, 0, 255))
        #         screen.blit(speed_text, (10, HEIGHT - 30))

    if game_over:
        client.leave_game()
        quit_button_rect = game_over_screen()

    pygame.display.flip()
    clock.tick(FPS)
