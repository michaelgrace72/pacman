import socket
import json
import logging

class ClientHTTPInterface:
    def __init__(self, idplayer='1', host='localhost', port=55555):
        self.idplayer = idplayer
        self.host = host
        self.port = port

    def _send_http_request(self, method, path, data=None, params=None):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))

            url = path
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                url += f"?{param_str}"

            if method == 'GET':
                request = f"GET {url} HTTP/1.0\r\n\r\n"
            else:
                body = ""
                if data:
                    body = json.dumps(data)
                request = f"POST {url} HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n{body}"

            sock.sendall(request.encode())

            response = b""
            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response += chunk
                if b'\r\n\r\n' in response:
                    break

            sock.close()
            response_str = response.decode()

            if '\r\n\r\n' in response_str:
                _, body = response_str.split('\r\n\r\n', 1)
                if body.strip():
                    try:
                        return json.loads(body)
                    except json.JSONDecodeError:
                        return {"status": "ERROR", "message": "Invalid JSON response"}
            else:
                return {"status": "ERROR", "message": "Invalid HTTP response"}

        except Exception as e:
            logging.error(f"Request failed: {e}")
            return {"status": "ERROR", "message": str(e)}

    def _get_request(self, endpoint, params=None):
        return self._send_http_request('GET', endpoint, params=params)

    def _post_request(self, endpoint, data=None):
        return self._send_http_request('POST', endpoint, data=data)

    def join_game(self):
        data = {"player_id": self.idplayer}
        return self._post_request("/join_game", data)

    def leave_game(self):
        data = {"player_id": self.idplayer}
        return self._post_request("/leave_game", data)

    def set_ready(self):
        data = {"player_id": self.idplayer}
        return self._post_request("/set_ready", data)

    def is_ready(self):
        return self._get_request("/is_ready")

    def get_other_players(self):
        return self._get_request("/get_all_players")

    def get_players_face(self):
        params = {"player_id": self.idplayer}
        return self._get_request("/get_players_face", params)

    def get_location(self):
        params = {"player_id": self.idplayer}
        return self._get_request("/get_location", params)

    def set_location(self, x, y):
        data = {"player_id": self.idplayer, "x": str(x), "y": str(y)}
        return self._post_request("/set_location", data)

    def get_projectiles(self):
        return self._get_request("/get_projectiles")

    def get_items(self):
        return self._get_request("/get_items")

    def collide(self):
        params = {"player_id": self.idplayer}
        return self._get_request("/collide", params)

    def pickup_item(self, item_id):
        data = {"player_id": self.idplayer, "item_id": str(item_id)}
        return self._post_request("/pickup_item", data)

    def close(self):
        pass

class ClientInterface(ClientHTTPInterface):
    def __init__(self, idplayer='1'):
        super().__init__(idplayer, 'localhost', 55555)

    def send_command(self, command_str=""):
        parts = command_str.strip().split()
        if not parts:
            return {"status": "ERROR", "message": "Empty command"}

        command = parts[0].lower()

        try:
            if command == "join_game":
                return self.join_game()
            elif command == "leave_game":
                return self.leave_game()
            elif command == "set_ready":
                return self.set_ready()
            elif command == "is_ready":
                return self.is_ready()
            elif command == "get_all_players":
                return self.get_other_players()
            elif command == "get_players_face":
                return self.get_players_face()
            elif command == "get_location":
                return self.get_location()
            elif command == "set_location" and len(parts) >= 4:
                return self.set_location(parts[2], parts[3])
            elif command == "get_projectiles":
                return self.get_projectiles()
            elif command == "get_items":
                return self.get_items()
            elif command == "collide":
                return self.collide()
            elif command == "pickup_item" and len(parts) >= 3:
                return self.pickup_item(parts[2])
            else:
                return {"status": "ERROR", "message": f"Unknown command: {command}"}
        except Exception as e:
            logging.error(f"Error processing command '{command_str}': {e}")
            return {"status": "ERROR", "message": str(e)}
