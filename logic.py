import base64
import random
import shelve
import time
import threading

class PlayerServerInterface:
    def __init__(self):
        self.players = {}
        self.players_face=dict()
        self.ready_status = dict()
        self.active_players = set()
        self.projectiles = []
        self.projectile_last_spawn = time.time()
        self.items = []
        self.item_last_spawn = 0
        self.player_hit_cooldown = {}
        self.player_data = {
            '1': {'image': 'images/UFO-1.png'},
            '2': {'image': 'images/UFO-2.png'},
            '3': {'image': 'images/UFO-3.png'}
        }
        self.projectile_lock = threading.Lock()
        self.item_lock = threading.Lock()

    # PLAYER
    def get_all_players(self, params=[]):
        return dict(status='OK', players=list(self.active_players))

    def get_players_face(self, params=[]):
        pnum = params[0]
        try:
            if pnum in self.active_players and pnum in self.players_face:
                return dict(status='OK', face=self.players_face[pnum])
            return dict(status='ERROR')
        except Exception:
            return dict(status='ERROR')

    def set_location(self, params=[]):
        pnum, x, y = params[0], params[1], params[2]
        try:
            if pnum in self.active_players:
                self.players[pnum] = f"{x},{y}"
                return dict(status='OK', player=pnum)
            return dict(status='ERROR', message='Player not active')
        except Exception:
            return dict(status='ERROR')

    def get_location(self, params=[]):
        pnum = params[0]
        try:
            if pnum in self.active_players:
                return dict(status='OK', location=self.players[pnum])
            return dict(status='ERROR')
        except Exception:
            return dict(status='ERROR')

    # NOTES: ini testing aja
    def join_game(self, params=[]):
        pnum = params[0]
        if pnum in self.active_players:
            return dict(status='ERROR', message='Player already in use')
        if pnum not in self.player_data:
            return dict(status='ERROR', message='Invalid player number')
        if len(self.active_players) >= 3:
            return dict(status='ERROR', message='Game is full')

        self.active_players.add(pnum)
        self.players[pnum] = "100,100"
        self.players_face[pnum] = self.player_data[pnum]['image']
        return dict(status='OK', player=pnum)

    def leave_game(self, params=[]):
        pnum = params[0]
        if pnum in self.active_players:
            self.active_players.remove(pnum)
            if pnum in self.ready_status:
                del self.ready_status[pnum]
            if pnum in self.players_face:
                del self.players_face[pnum]
            if pnum in self.players:
                del self.players[pnum]
            return dict(status='OK')
        return dict(status='ERROR', message='Player not in game')

    def set_ready(self, params=[]):
        pnum = params[0]
        if pnum in self.active_players:
            self.ready_status[pnum] = True
            return dict(status='OK')
        return dict(status='ERROR')

    def is_ready(self, params=[]):
        if not self.active_players:
            return dict(status='OK', ready=False, player_count=0)
        ready_count = sum(1 for p in self.active_players if self.ready_status.get(p, False))
        return dict(status='OK', ready=(ready_count == len(self.active_players)), player_count=len(self.active_players))

    # PROJECTILE
    def spawn_projectile(self):
        with self.projectile_lock:
            now = time.time()
            if now - self.projectile_last_spawn >= 3 and len(self.projectiles) < 7:
                spawn = random.randint(1, 5)

                new_projectiles = []
                for _ in range(spawn):
                    edge = random.choice(['top', 'bottom', 'left', 'right'])
                    if edge == 'top':
                        x, y = random.randint(0, 640), 0
                        dx = random.randint(-2, 2)
                        dy = 5
                    elif edge == 'bottom':
                        x, y = random.randint(0, 640), 480
                        dx = random.randint(-2, 2)
                        dy = -5
                    elif edge == 'left':
                        x, y = 0, random.randint(0, 480)
                        dx = 5
                        dy = random.randint(-2, 2)
                    else:
                        x, y = 640, random.randint(0, 480)
                        dx = -5
                        dy = random.randint(-2, 2)

                    new_projectiles.append({"x": x, "y": y, "dx": dx, "dy": dy})

                self.projectiles.extend(new_projectiles)
                self.projectile_last_spawn = now

    def update_projectiles(self):
        self.spawn_projectile()
        for p in self.projectiles:
            p['x'] += p['dx']
            p['y'] += p['dy']
        self.projectiles = [p for p in self.projectiles if -100 <= p['x'] <= 740 and -100 <= p['y'] <= 580]

    def get_projectiles(self, params=[]):
        self.update_projectiles()
        return dict(status='OK', data=self.projectiles.copy())

    # COLLIDE
    def collide(self, params=[]):
        pnum = params[0]
        if pnum not in self.active_players:
            return dict(status='ERROR', message='Player not active')

        current_time = time.time()
        if pnum in self.player_hit_cooldown:
            if current_time - self.player_hit_cooldown[pnum] < 0.5:
                return dict(status='OK', hit=False)

        player_location = self.players[pnum].split(',')
        player_x, player_y = int(player_location[0]), int(player_location[1])

        player_width, player_height = 52, 52

        for i, projectile in enumerate(self.projectiles):
            proj_x, proj_y = projectile['x'], projectile['y']
            proj_width, proj_height = 10, 10

            if (player_x < proj_x + proj_width and
                player_x + player_width > proj_x and
                player_y < proj_y + proj_height and
                player_y + player_height > proj_y):

                self.player_hit_cooldown[pnum] = current_time
                removed_projectile = self.projectiles.pop(i)
                return dict(status='OK', hit=True, projectile=removed_projectile)

        return dict(status='OK', hit=False)

    # ITEMS
    def spawn_item(self):
        now = time.time()
        w, h = 640, 480

        with self.item_lock:
            if now - self.item_last_spawn > 10 and len(self.items) < 5:
                x = random.randint(0, w - 32)
                y = random.randint(0, h - 32)
                item_type = random.choice(['health', 'speed'])

                item = {
                    'id': len(self.items),
                    'type': item_type,
                    'x': x,
                    'y': y,
                    'spawned_at': now
                }
                self.items.append(item)
                self.item_last_spawn = now
                return dict(status='OK', item=item)
            return dict(status='ERROR', message='Item spawn cooldown not met')

    def get_items(self, params=[]):
        self.spawn_item()
        return dict(status='OK', items=self.items.copy())

    def pickup_item(self, params=[]):
        pnum = params[0]
        item_id = int(params[1])

        if pnum not in self.active_players:
            return dict(status='ERROR', message='Player not active')

        for i, item in enumerate(self.items):
            if item['id'] == item_id:
                removed_item = self.items.pop(i)
                return dict(status='OK', item=removed_item['type'], player=pnum)

        return dict(status='ERROR', message='Item not found')

if __name__ == '__main__':
    p = PlayerServerInterface()
