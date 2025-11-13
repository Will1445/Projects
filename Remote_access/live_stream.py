import socket
import struct
import pickle
import cv2
import threading
import pyautogui
import queue
from pynput import keyboard, mouse  
import time

HOST = "192.168.1.195"  # Ubuntu IP
PORT_STREAM = 5001
PORT_KEYLOG = 5002
PORT_MOUSE = 5003

running = True
frame_queue = queue.Queue(maxsize=2)
mouse_enabled = False
window_rect = (0, 0, 0, 0)
last_click_time = 0
click_debounce = 0.1


def on_press(key):
    global mouse_enabled
    try:
        if key == keyboard.Key.f2:
            mouse_enabled = not mouse_enabled
            print(f"Mouse mirroring {'ENABLED' if mouse_enabled else 'DISABLED'}")
    except AttributeError:
        pass

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

def receive_stream():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT_STREAM))
    
    try:
        while running:
            size_data = b""
            while len(size_data) < 4:
                chunk = client.recv(4 - len(size_data))
                if not chunk: break
                size_data += chunk
            
            if len(size_data) != 4: break
            
            data_size = struct.unpack("!I", size_data)[0]
            data = b""
            while len(data) < data_size:
                packet = client.recv(min(4096, data_size - len(data)))
                if not packet: break
                data += packet
            
            if len(data) == data_size:
                try:
                    buffer = pickle.loads(data)
                    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                    if frame is not None:
                        if frame_queue.full():
                            frame_queue.get_nowait()
                        frame_queue.put(frame)
                except Exception as e:
                    print(f"Frame error: {e}")
    finally:
        client.close()

def receive_keys():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT_KEYLOG))
    
    try:
        while running:
            data = client.recv(1024)
            if data:
                print("Keys:", data.decode().strip())
    except Exception as e:
        print(f"Key error: {e}")
    finally:
        client.close()

# Mirror_mouse function
def mirror_mouse():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT_MOUSE))
    
    last_sent = time.time()
    move_interval = 1/30  # 30 updates/sec
    prev_coords = (0.0, 0.0)
    last_left_state = False
    last_right_state = False

    class MouseListener(mouse.Listener):
        def __init__(self):
            super().__init__(on_click=self.on_click)
            self.left_state = False
            self.right_state = False
            
        def on_click(self, x, y, button, pressed):
            if button == mouse.Button.left:
                self.left_state = pressed
            elif button == mouse.Button.right:
                self.right_state = pressed
            return True

    mouse_listener = MouseListener()
    mouse_listener.start()

    try:
        while running:
            current_time = time.time()
            current_x, current_y = pyautogui.position()
            screen_w, screen_h = pyautogui.size()
            
            try:
                window_rect = cv2.getWindowImageRect("Remote Screen")
            except:
                window_rect = (0, 0, 0, 0)
            
            in_window = (window_rect[0] <= current_x <= window_rect[0] + window_rect[2] and
                         window_rect[1] <= current_y <= window_rect[1] + window_rect[3])
            
            if mouse_enabled and in_window:
                # Movement handling 
                if current_time - last_sent >= move_interval:
                    norm_x = current_x / screen_w
                    norm_y = current_y / screen_h
                    if abs(norm_x - prev_coords[0]) > 0.01 or abs(norm_y - prev_coords[1]) > 0.01:
                        client.sendall(f"move {norm_x:.3f} {norm_y:.3f}\n".encode())
                        prev_coords = (norm_x, norm_y)
                        last_sent = current_time
                
                # Click handling
                if mouse_listener.left_state != last_left_state:
                    action = 'down' if mouse_listener.left_state else 'up'
                    client.sendall(f"click 1 {action}\n".encode())
                    last_left_state = mouse_listener.left_state
                
                if mouse_listener.right_state != last_right_state:
                    action = 'down' if mouse_listener.right_state else 'up'
                    client.sendall(f"click 3 {action}\n".encode())
                    last_right_state = mouse_listener.right_state
            
            threading.Event().wait(0.001)

    except Exception as e:
        print(f"Mouse error: {e}")
    finally:
        mouse_listener.stop()
        client.close()
        
        
def main():
    global running
    
    # Start threads
    threading.Thread(target=receive_stream).start()
    threading.Thread(target=receive_keys).start()
    threading.Thread(target=mirror_mouse).start()

    try:
        cv2.namedWindow("Remote Screen", cv2.WINDOW_NORMAL)
        while running:
            if not frame_queue.empty():
                frame = frame_queue.get()
                cv2.imshow("Remote Screen", frame)
                try:
                    window_rect = cv2.getWindowImageRect("Remote Screen")
                except:
                    pass
            
            status = "ACTIVE" if mouse_enabled else "INACTIVE"
            cv2.setWindowTitle("Remote Screen", f"Remote Screen - [{status}]")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        running = False
        cv2.destroyAllWindows()
        keyboard_listener.stop()

if __name__ == "__main__":
    main()