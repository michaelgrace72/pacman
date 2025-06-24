import pygame
import sys
import random
from collections import deque

# ========================
# LABIRIN 3x LIPAT MANUAL
# 0 = jalan, 1 = dinding
# Ukuran: 33 baris × 45 kolom
# ========================
labyrinth = [
    # Baris atas (dinding pembatas)
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    
    # Area utama dengan jalur yang terhubung
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
    
    # Area tengah dengan ruang terbuka untuk pergerakan hantu
    [1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    
    # Area bawah dengan pola serupa
    [1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    
    # Area bawah dengan jalur terbuka
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    
    # Baris bawah (dinding pembatas)
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

CELL_SIZE = 18
ROWS = len(labyrinth)
COLS = len(labyrinth[0])
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
BLUE = (0, 200, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ghost Chase Logic - Improved")
clock = pygame.time.Clock()

# Load images
ghost_img = pygame.image.load("./images/cyan.png")
ghost_img = pygame.transform.scale(ghost_img, (CELL_SIZE - 4, CELL_SIZE - 4))

# Game objects
ghost = {'x': 1, 'y': 1, 'dx': 1, 'dy': 0, 'last_direction': (1, 0)}
player = {'x': 43, 'y': 31}  # Player di pojok kanan bawah
projectiles = []

def is_empty(x, y):
    return 0 <= y < ROWS and 0 <= x < COLS and labyrinth[y][x] == 0

def get_distance(x1, y1, x2, y2):
    """Menghitung jarak Manhattan"""
    return abs(x1 - x2) + abs(y1 - y2)

def find_path_to_player(ghost_x, ghost_y, player_x, player_y):
    """
    Menggunakan BFS untuk mencari jalur terpendek ke player
    Mengembalikan arah langkah pertama yang harus diambil
    """
    if ghost_x == player_x and ghost_y == player_y:
        return None
    
    queue = deque([(ghost_x, ghost_y, [])])
    visited = set()
    visited.add((ghost_x, ghost_y))
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # down, right, up, left
    
    while queue:
        x, y, path = queue.popleft()
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            if (nx, ny) not in visited and is_empty(nx, ny):
                new_path = path + [(dx, dy)]
                
                if nx == player_x and ny == player_y:
                    # Mencapai player, kembalikan arah langkah pertama
                    return new_path[0] if new_path else None
                
                queue.append((nx, ny, new_path))
                visited.add((nx, ny))
    
    return None  # Tidak ada jalur

def get_smart_direction(ghost_x, ghost_y, player_x, player_y, last_direction):
    """
    Mendapatkan arah bergerak yang cerdas untuk mengejar player
    """
    # Coba cari jalur optimal dengan BFS
    optimal_direction = find_path_to_player(ghost_x, ghost_y, player_x, player_y)
    
    if optimal_direction:
        return optimal_direction
    
    # Jika tidak ada jalur langsung, gunakan strategi heuristik
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # down, right, up, left
    valid_directions = []
    
    for dx, dy in directions:
        nx, ny = ghost_x + dx, ghost_y + dy
        if is_empty(nx, ny):
            distance = get_distance(nx, ny, player_x, player_y)
            valid_directions.append((dx, dy, distance))
    
    if not valid_directions:
        return None
    
    # Prioritaskan arah yang mendekatkan ke player
    valid_directions.sort(key=lambda x: x[2])
    
    # Hindari berbalik arah kecuali terpaksa
    best_direction = valid_directions[0]
    reverse_direction = (-last_direction[0], -last_direction[1])
    
    for direction in valid_directions:
        if (direction[0], direction[1]) != reverse_direction:
            return (direction[0], direction[1])
    
    # Jika harus berbalik arah
    return (best_direction[0], best_direction[1])

def move_ghost():
    """Menggerakkan hantu dengan AI yang lebih cerdas"""
    # Dapatkan arah optimal
    new_direction = get_smart_direction(
        ghost['x'], ghost['y'], 
        player['x'], player['y'], 
        ghost['last_direction']
    )
    
    if new_direction:
        ghost['dx'], ghost['dy'] = new_direction
        ghost['last_direction'] = new_direction
        
        nx, ny = ghost['x'] + ghost['dx'], ghost['y'] + ghost['dy']
        if is_empty(nx, ny):
            ghost['x'], ghost['y'] = nx, ny
    else:
        # Jika benar-benar stuck, coba arah acak
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = ghost['x'] + dx, ghost['y'] + dy
            if is_empty(nx, ny):
                ghost['dx'], ghost['dy'] = dx, dy
                ghost['last_direction'] = (dx, dy)
                ghost['x'], ghost['y'] = nx, ny
                break

def ghost_shoot():
    """Hantu menembak ke arah player"""
    # Tembak ke arah player (tidak selalu ke arah pergerakan)
    dx = 0 if player['x'] == ghost['x'] else (1 if player['x'] > ghost['x'] else -1)
    dy = 0 if player['y'] == ghost['y'] else (1 if player['y'] > ghost['y'] else -1)
    
    # Jika player tidak sejajar, gunakan arah pergerakan hantu
    if dx == 0 and dy == 0:
        dx, dy = ghost['dx'], ghost['dy']
    elif dx != 0 and dy != 0:
        # Pilih arah yang lebih dominan
        if abs(player['x'] - ghost['x']) > abs(player['y'] - ghost['y']):
            dy = 0
        else:
            dx = 0
    
    projectiles.append({
        'x': ghost['x'],
        'y': ghost['y'],
        'dx': dx,
        'dy': dy,
        'speed': 0.5  # Kecepatan projectile diperlambat
    })

def update_projectiles():
    """Update projectiles dengan kecepatan yang diperlambat"""
    global projectiles
    updated = []
    
    for p in projectiles:
        # Update posisi dengan kecepatan yang diperlambat
        p['x'] += p['dx'] * p['speed']
        p['y'] += p['dy'] * p['speed']
        
        # Cek apakah masih dalam bounds dan tidak menabrak dinding
        grid_x, grid_y = int(p['x']), int(p['y'])
        
        if is_empty(grid_x, grid_y):
            # Cek apakah mengenai player
            if grid_x == player['x'] and grid_y == player['y']:
                print("Player hit by projectile!")
                # Bisa tambahkan efek hit di sini
            else:
                updated.append(p)
        # Jika menabrak dinding atau keluar bounds, projectile dihapus
    
    projectiles = updated

def move_player():
    """Menggerakkan player dengan keyboard"""
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        if is_empty(player['x'], player['y'] - 1):
            player['y'] -= 1
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        if is_empty(player['x'], player['y'] + 1):
            player['y'] += 1
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        if is_empty(player['x'] - 1, player['y']):
            player['x'] -= 1
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        if is_empty(player['x'] + 1, player['y']):
            player['x'] += 1

def draw_labyrinth():
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if labyrinth[y][x] == 1:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_ghost():
    gx, gy = ghost['x'], ghost['y']
    screen.blit(ghost_img, (gx * CELL_SIZE + 2, gy * CELL_SIZE + 2))

def draw_player():
    px, py = player['x'], player['y']
    rect = pygame.Rect(px * CELL_SIZE + 4, py * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8)
    pygame.draw.rect(screen, YELLOW, rect)

def draw_projectiles():
    for p in projectiles:
        rect = pygame.Rect(int(p['x'] * CELL_SIZE + CELL_SIZE//3), 
                          int(p['y'] * CELL_SIZE + CELL_SIZE//3), 6, 6)
        pygame.draw.rect(screen, RED, rect)

# def draw_debug_info():
#     """Menampilkan informasi debug"""
#     font = pygame.font.Font(None, 24)
    
#     # Jarak antara ghost dan player
#     distance = get_distance(ghost['x'], ghost['y'], player['x'], player['y'])
#     distance_text = font.render(f"Distance: {distance}", True, BLACK)
#     screen.blit(distance_text, (10, 10))
    
#     # Posisi ghost dan player
#     ghost_pos_text = font.render(f"Ghost: ({ghost['x']}, {ghost['y']})", True, BLACK)
#     screen.blit(ghost_pos_text, (10, 35))
    
#     player_pos_text = font.render(f"Player: ({player['x']}, {player['y']})", True, BLACK)
#     screen.blit(player_pos_text, (10, 60))
    
#     # Arah pergerakan ghost
#     direction_text = font.render(f"Ghost direction: ({ghost['dx']}, {ghost['dy']})", True, BLACK)
#     screen.blit(direction_text, (10, 85))

def main():
    move_timer = pygame.time.get_ticks()
    shoot_timer = pygame.time.get_ticks()
    player_move_timer = pygame.time.get_ticks()

    GHOST_MOVE_DELAY = 300  # Hantu bergerak setiap 300ms
    SHOOT_DELAY = 2500      # Hantu menembak setiap 2.5 detik
    PLAYER_MOVE_DELAY = 150 # Player bergerak setiap 150ms
    
    while True:
        screen.fill(WHITE)
        draw_labyrinth()
        draw_ghost()
        draw_player()
        draw_projectiles()
        # draw_debug_info()
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        now = pygame.time.get_ticks()
        
        # Update ghost movement
        if now - move_timer >= GHOST_MOVE_DELAY:
            move_ghost()
            move_timer = now
            
        # Update ghost shooting
        if now - shoot_timer >= SHOOT_DELAY:
            ghost_shoot()
            shoot_timer = now
        
        # Update player movement
        if now - player_move_timer >= PLAYER_MOVE_DELAY:
            move_player()
            player_move_timer = now

        # Update projectiles
        update_projectiles()

if __name__ == "__main__":
    main()