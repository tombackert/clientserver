import socket
import json
import threading
import pygame
import time
import os
import dotenv
import sys

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
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Client Loop Example")

        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    elif event.key == pygame.K_LEFT:
                        client.send_move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        client.send_move(1, 0)
                    elif event.key == pygame.K_UP:
                        client.send_move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        client.send_move(0, 1)


            screen.fill((200, 200, 200))

            for pid, data in client.game_state.items():
                x, y = data["x"], data["y"]
                color = (255, 0, 0) if pid == client.player_id else (0, 0, 255)
                pygame.draw.rect(screen, color, (x, y, 20, 20))

            pygame.display.flip()

        
        pygame.quit()

    def start(self):
        threading.Thread(target=self.listen_server).start()
        self.game_loop()
    

if __name__ == "__main__":
    
    dotenv.load_dotenv()
    server_ip = os.getenv("SERVER_IP")
    
    client = GameClient(server_ip, 5555)
    client.connect()
    client.start()
    client.close()