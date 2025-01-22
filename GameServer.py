import socket
import threading
import json
import time

class GameServer:
    def __init__(self, host="0.0.0.0", port=5555, tick_rate=30):
        self.host = host
        self.port = port
        self.tick_rate = tick_rate
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"[SERVER] Running on {self.host}:{self.port}")
        self.clients = {}
        self.next_client_id = 0
        self.game_state = {}
        self.running = True

    def start(self):
        threading.Thread(target=self.accept_clients).start()
        self.game_loop()

    def accept_clients(self):
        while self.running:
            conn, addr = self.server_socket.accept()
            client_id = self.next_client_id
            self.next_client_id += 1
            self.clients[client_id] = conn
            self.game_state[client_id] = {"x": 100, "y": 100}
            print(f"[SERVER] Player {client_id} connected.")
            threading.Thread(target=self.client_handler, args=(client_id,)).start()

    def client_handler(self, client_id):
        conn = self.clients[client_id]
        welcome_msg = {"type": "WELCOME", "client_id": client_id}
        conn.sendall((json.dumps(welcome_msg) + "\n").encode("utf-8"))
        while self.running:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode("utf-8"))
                self.handle_client_message(client_id, msg)
            except Exception as e:
                print(f"[SERVER] Error with player {client_id}: {e}")
                break
        print(f"[SERVER] Player {client_id} disconnected.")
        del self.clients[client_id]
        del self.game_state[client_id]
        conn.close()

    def handle_client_message(self, client_id, msg):
        if msg.get("type") == "MOVE":
            dx, dy = msg.get("dx", 0), msg.get("dy", 0)
            self.game_state[client_id]["x"] += dx
            self.game_state[client_id]["y"] += dy

    def game_loop(self):
        while self.running:
            time.sleep(1 / self.tick_rate)
            self.broadcast_game_state()

    def broadcast_game_state(self):
        state_msg = {"type": "STATE", "players": self.game_state}
        msg_str = json.dumps(state_msg) + "\n"
        for conn in self.clients.values():
            conn.sendall(msg_str.encode("utf-8"))

    def shutdown(self):
        self.running = False
        self.server_socket.close()
        print("[SERVER] Shutdown complete.")

if __name__ == "__main__":
    server = GameServer(host="0.0.0.0", port=5555, tick_rate=30)
    server.start()