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
            data_received=""
            while True:
                data = sock.recv(16)
                if data:
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    break
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

    def create_session(self, session_id):
        return self.send_command(f"create_session {session_id}")

    def join_session(self, session_id):
        return self.send_command(f"join_session {session_id} {self.idplayer}")

    def set_ready_in_session(self, session_id):
        return self.send_command(f"set_ready_in_session {session_id} {self.idplayer}")

    def is_ready_in_session(self, session_id):
        return self.send_command(f"is_ready_in_session {session_id}")

    def get_sessions(self):
        return self.send_command("get_sessions")

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

def player_name_input_ui():
    font = pygame.font.SysFont(None, 36)
    input_box = pygame.Rect(180, 200, 280, 48)
    input_active = True
    input_text = ''
    error_message = ''
    while True:
        screen.fill((220, 240, 255))
        prompt = font.render("Enter your player name:", True, (0,0,0))
        screen.blit(prompt, (180, 150))
        pygame.draw.rect(screen, (255,255,255), input_box, 0)
        pygame.draw.rect(screen, (0,0,0), input_box, 2)
        input_surf = font.render(input_text or 'Type here...', True, (100,100,100) if not input_text else (0,0,0))
        screen.blit(input_surf, (input_box.x+10, input_box.y+8))
        if error_message:
            err_surf = font.render(error_message, True, (255,0,0))
            screen.blit(err_surf, (180, 260))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        return input_text.strip()
                    else:
                        error_message = 'Name cannot be empty.'
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 16 and event.unicode.isprintable():
                        input_text += event.unicode
        clock.tick(30)

# --- SESSION SELECTION UI ---
def session_selection_ui(client):
    font = pygame.font.SysFont(None, 32)
    input_box = pygame.Rect(180, 340, 280, 48)
    input_text = ''
    error_message = ''
    selected_idx = 0
    creating_new = False
    sessions = []
    last_fetch = 0
    session_id = None
    while True:
        now = pygame.time.get_ticks()
        if now - last_fetch > 1000:
            resp = client.get_sessions()
            if resp and resp.get('status') == 'OK':
                sessions = list(resp.get('sessions', {}).keys())
            last_fetch = now
        screen.fill((220, 240, 255))
        title = font.render("Select a session or create new:", True, (0,0,0))
        screen.blit(title, (120, 40))
        session_rects = []
        # List sessions
        for i, s in enumerate(sessions):
            color = (0,0,0) if i != selected_idx else (0,100,255)
            txt = font.render(f"{s}", True, color)
            rect = txt.get_rect(topleft=(200, 100 + i*40))
            screen.blit(txt, rect.topleft)
            session_rects.append(rect)
        # Option to create new
        new_color = (0,100,255) if creating_new else (0,0,0)
        new_txt = font.render("+ Create New Session", True, new_color)
        new_rect = new_txt.get_rect(topleft=(200, 120 + len(sessions)*40))
        screen.blit(new_txt, new_rect.topleft)
        # Input box for new session
        if creating_new:
            pygame.draw.rect(screen, (255,255,255), input_box, 0)
            pygame.draw.rect(screen, (0,0,0), input_box, 2)
            input_surf = font.render(input_text or 'Session name...', True, (100,100,100) if not input_text else (0,0,0))
            screen.blit(input_surf, (input_box.x+10, input_box.y+8))
        if error_message:
            err_surf = font.render(error_message, True, (255,0,0))
            screen.blit(err_surf, (180, 400))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if creating_new:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip():
                            session_id = input_text.strip()
                            resp = client.create_session(session_id)
                            if resp and resp.get('status') == 'OK':
                                return session_id
                            else:
                                error_message = 'Session exists or error.'
                        else:
                            error_message = 'Session name required.'
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        creating_new = False
                        input_text = ''
                    else:
                        if len(input_text) < 16 and event.unicode.isprintable():
                            input_text += event.unicode
                else:
                    if event.key == pygame.K_UP:
                        selected_idx = max(0, selected_idx-1)
                    elif event.key == pygame.K_DOWN:
                        if selected_idx < len(sessions):
                            selected_idx += 1
                    elif event.key == pygame.K_RETURN:
                        if selected_idx == len(sessions):
                            creating_new = True
                            input_text = ''
                        else:
                            session_id = sessions[selected_idx]
                            resp = client.join_session(session_id)
                            if resp and resp.get('status') == 'OK':
                                return session_id
                            else:
                                error_message = 'Failed to join session.'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Check session clicks
                for i, rect in enumerate(session_rects):
                    if rect.collidepoint(mx, my):
                        selected_idx = i
                        session_id = sessions[selected_idx]
                        resp = client.join_session(session_id)
                        if resp and resp.get('status') == 'OK':
                            return session_id
                        else:
                            error_message = 'Failed to join session.'
                        break
                # Check create new session click
                if new_rect.collidepoint(mx, my):
                    creating_new = True
                    input_text = ''
        clock.tick(30)

# --- SESSION WAITING ROOM ---
def session_waiting_room_ui(client, session_id, player_id):
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 28)
    waiting = True
    ready_sent = False
    while waiting:
        screen.fill((220, 220, 220))
        title = font.render(f"Session: {session_id}", True, (0,0,0))
        screen.blit(title, (180, 40))
        prompt = small_font.render("Press R to Ready. Waiting for all players...", True, (0,0,0))
        screen.blit(prompt, (100, 80))
        # List players in session
        resp = client.get_sessions()
        players = []
        ready_map = {}
        if resp and resp.get('status') == 'OK':
            session_info = resp.get('session_info', {})
            if session_info and session_id in session_info:
                players = session_info[session_id].get('players', [])
                ready_map = session_info[session_id].get('ready', {})
        for i, p in enumerate(players):
            ready = ready_map.get(p, False)
            color = (0,180,0) if ready else (180,0,0)
            txt = small_font.render(f"{p} {'[READY]' if ready else '[NOT READY]'}", True, color)
            screen.blit(txt, (180, 130 + i*30))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and not ready_sent:
                client.set_ready_in_session(session_id)
                ready_sent = True
        ready_state = client.is_ready_in_session(session_id)
        if ready_state and ready_state.get('ready'):
            waiting = False
        clock.tick(10)

# --- MAIN FLOW ---
player_id = player_name_input_ui()
client = ClientInterface(player_id)
session_id = session_selection_ui(client)
session_waiting_room_ui(client, session_id, player_id)

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
