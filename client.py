import socket
import json
import threading
import pygame
import time
import os
import dotenv

class GameClient:
    def __init__(self, server_ip="localhost", server_port=5555):
        self.server_ip = server_ip
        self.server_port = server_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.player_id = None
        self.game_state = {}
        self.running = True

    def connect(self):
        try:
            self.sock.connect((self.server_ip, self.server_port))
            self.connected = True
            print(f"[CLIENT] Connected to {self.server_ip}:{self.server_port}")
            threading.Thread(target=self.listen_server).start()
        except Exception as e:
            print(f"[CLIENT] Error: {e}")

    def listen_server(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("[CLIENT] Lost connection to server.")
                    self.running = False
                    break
                msg = json.loads(data.decode("utf-8"))
                self.handle_server_message(msg)
            except Exception as e:
                print(f"[CLIENT] Error: {e}")
                self.running = False
                break
        self.sock.close()

    def handle_server_message(self, msg):
        if msg.get("type") == "WELCOME":
            self.player_id = msg.get("client_id")
            print(f"[CLIENT] You are player {self.player_id}")
        elif msg.get("type") == "STATE":
            self.game_state = msg.get("players", {})
        else:
            print(f"[CLIENT] Unknown message: {msg}")

    def send_move(self, dx, dy):
        if not self.connected:
            return
        move_msg = {"type": "MOVE", "dx": dx, "dy": dy}
        self.send_data(move_msg)

    def send_data(self, data_dict):
        try:
            msg_str = json.dumps(data_dict)
            self.sock.sendall(msg_str.encode("utf-8"))
        except:
            print("[CLIENT] Error sending data.")

    def close(self):
        self.running = False
        self.sock.close()
        print("[CLIENT] Connection closed.")

    def game_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption("Game Client")
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    pygame.quit()
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.send_move(-1, 0)
            if keys[pygame.K_RIGHT]:
                self.send_move(1, 0)
            if keys[pygame.K_UP]:
                self.send_move(0, -1)
            if keys[pygame.K_DOWN]:
                self.send_move(0, 1)

            # Render local game state
            screen.fill((255, 255, 255))
            for player_id, player_data in self.game_state.items():
                x, y = player_data["x"], player_data["y"]
                color = (255, 0, 0) if player_id == self.player_id else (0, 0, 255)
                pygame.draw.rect(screen, color, (x, y, 20, 20))
            pygame.display.flip()
            clock.tick(30)

import time

if __name__ == "__main__":
    
    dotenv.load_dotenv()
    server_ip = os.getenv("SERVER_IP")
    
    client = GameClient(server_ip, 5555)  # Oder IP des Servers
    client.connect()

    # Dummy-Test: Spieler läuft 3 Sekunden lang nach rechts
    start_time = time.time()
    while time.time() - start_time < 3:
        client.send_move(dx=1, dy=0)
        time.sleep(0.1)

    client.close()