import json
import urllib.parse
import logging
import threading
import sys
import time
from datetime import datetime
from logic import PlayerServerInterface

game_logic = PlayerServerInterface()

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'
        self.types['.json'] = 'application/json'

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        """Generate HTTP response"""
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: gameserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''
        for i in resp:
            response_headers = "{}{}".format(response_headers, i)

        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')

            requests = data.split("\r\n")
            if not requests:
                return self.response(400, 'Bad Request', '', {})

            baris = requests[0]
            all_headers = [n for n in requests[1:] if n != '']

            j = baris.split(" ")
            if len(j) < 2:
                return self.response(400, 'Bad Request', '', {})

            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                return self.http_post(object_address, all_headers, data)
            else:
                return self.response(405, 'Method Not Allowed', '', {})

        except Exception as e:
            logging.error(f"Error processing request: {e}")
            return self.response(500, 'Internal Server Error', str(e), {})

    def http_get(self, object_address, headers):
        try:
            parsed_url = urllib.parse.urlparse(object_address)
            path = parsed_url.path
            query_params = urllib.parse.parse_qs(parsed_url.query)

            params = []
            for key, value_list in query_params.items():
                if value_list:
                    params.append(value_list[0])

            if path == '/get_all_players':
                result = game_logic.get_all_players(params)
            elif path == '/get_players_face':
                result = game_logic.get_players_face(params)
            elif path == '/get_location':
                result = game_logic.get_location(params)
            elif path == '/is_ready':
                result = game_logic.is_ready(params)
            elif path == '/get_projectiles':
                result = game_logic.get_projectiles(params)
            elif path == '/get_items':
                result = game_logic.get_items(params)
            elif path == '/collide':
                result = game_logic.collide(params)
            elif path == '/':
                # Default homepage
                return self.response(200, 'OK', 'Game Server API v1.0 - Use POST for game commands',
                                   {'Content-Type': 'text/plain'})
            else:
                result = {"status": "ERROR", "message": "Endpoint not found"}

            json_response = json.dumps(result)
            return self.response(200, 'OK', json_response, {'Content-Type': 'application/json'})

        except Exception as e:
            logging.error(f"Error in GET request: {e}")
            error_response = json.dumps({"status": "ERROR", "message": str(e)})
            return self.response(500, 'Internal Server Error', error_response,
                               {'Content-Type': 'application/json'})

    def http_post(self, object_address, headers, full_data):
        try:
            parsed_url = urllib.parse.urlparse(object_address)
            path = parsed_url.path

            post_data = {}
            if '\r\n\r\n' in full_data:
                body_part = full_data.split('\r\n\r\n', 1)[1]
                if body_part.strip():
                    try:
                        post_data = json.loads(body_part)
                    except json.JSONDecodeError:
                        parsed_data = urllib.parse.parse_qs(body_part)
                        post_data = {key: value[0] if value else '' for key, value in parsed_data.items()}

            if path == '/join_game':
                params = [post_data.get('player_id', '')]
                result = game_logic.join_game(params)
            elif path == '/leave_game':
                params = [post_data.get('player_id', '')]
                result = game_logic.leave_game(params)
            elif path == '/set_ready':
                params = [post_data.get('player_id', '')]
                result = game_logic.set_ready(params)
            elif path == '/set_location':
                params = [post_data.get('player_id', ''), post_data.get('x', '0'), post_data.get('y', '0')]
                result = game_logic.set_location(params)
            elif path == '/pickup_item':
                params = [post_data.get('player_id', ''), post_data.get('item_id', '0')]
                result = game_logic.pickup_item(params)
            else:
                result = {"status": "ERROR", "message": "Endpoint not found"}

            json_response = json.dumps(result)
            return self.response(200, 'OK', json_response, {'Content-Type': 'application/json'})

        except Exception as e:
            logging.error(f"Error in POST request: {e}")
            error_response = json.dumps({"status": "ERROR", "message": str(e)})
            return self.response(500, 'Internal Server Error', error_response,
                               {'Content-Type': 'application/json'})


if __name__ == "__main__":
    httpserver = HttpServer()
