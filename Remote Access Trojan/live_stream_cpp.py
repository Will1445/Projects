import socket
import cv2
import numpy as np
import threading
import pyautogui
import queue
from pynput import keyboard, mouse
import struct
import time

# Target machine IP and ports (separate ports mouse controls and livestream)
Host_IP = "192.168.1.195"  
Host_Port_stream = 5001
Host_Port_mouse = 5003
 
running = True
frame_queue = queue.Queue(maxsize=2)
mouse_enabled = False
window_rect = (0, 0, 0, 0)


# Invert mouse controlled state when required key ('f2') is pressed
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

# Livestream feed from host  
def receive_stream():
    global running, width, height, window_size
    
    # Setup connection 
    print("Connecting to screen stream...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Get connection and display received window size 
        client.connect((Host_IP, Host_Port_stream))
        dims = client.recv(8)
        width, height = struct.unpack("!II", dims)
        window_size = width * height * 4
        print(f"Screen resolution: {width}x{height}")
        
        while running:
            # Receive data continuously from host 
            data = bytearray()
            while len(data) < window_size and running:
                packet = client.recv(min(4096, window_size - len(data)))
                if not packet: break
                data.extend(packet)
             
            # Convert data to display as image 
            if len(data) == window_size:
                frame = np.frombuffer(data, dtype=np.uint8)
                frame = frame.reshape((height, width, 4)) 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                if frame_queue.full():
                    frame_queue.get_nowait()
                frame_queue.put(frame)
    except Exception as e:
        print(f"Streaming error: {str(e)}")
    finally:
        client.close()

# Mouse control (mirroring)
def mirror_mouse():
    
    # Setup connection 
    print("Connecting to mouse control...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Get current mouse state
        client.connect((Host_IP, Host_Port_mouse))
        last_sent = time.time()
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

        mouse_logger = MouseListener()
        mouse_logger.start()

        while running:
            current_time = time.time() 
            current_x, current_y = pyautogui.position()
            
            try:
                window_rect = cv2.getWindowImageRect("Remote Screen")
            except:
                window_rect = (0, 0, 0, 0)
            
            in_window = (window_rect[0] <= current_x <= window_rect[0] + window_rect[2] and 
                         window_rect[1] <= current_y <= window_rect[1] + window_rect[3])
            
            # When enabled, get mouse positions 
            if mouse_enabled and in_window and window_rect[2] > 0:
                norm_x = (current_x - window_rect[0]) / window_rect[2] 
                norm_y = (current_y - window_rect[1]) / window_rect[3]
                norm_x = max(0.0, min(1.0, norm_x))
                norm_y = max(0.0, min(1.0, norm_y))
                
                # Control data rate
                if current_time - last_sent >= 0.033:
                    client.sendall(f"move {norm_x:.3f} {norm_y:.3f}\n".encode())
                    last_sent = current_time
                    prev_coords = (norm_x, norm_y)
                
                # When enabled, get mouse state (left/right click)
                if mouse_logger.left_state != last_left_state: 
                    action = 'down' if mouse_logger.left_state else 'up'
                    client.sendall(f"click 1 {action}\n".encode())
                    last_left_state = mouse_logger.left_state
                
                if mouse_logger.right_state != last_right_state:
                    action = 'down' if mouse_logger.right_state else 'up'
                    client.sendall(f"click 2 {action}\n".encode())
                    last_right_state = mouse_logger.right_state
            
            time.sleep(0.001) 
             
    except Exception as e:
        print(f"Mouse error: {str(e)}")
    finally:
        client.close()
        

# Main connection and data control
def main():
    global running 
    
    # Receive data from host for screen and mouse mirroring 
    threading.Thread(target=receive_stream, daemon=True).start()
    threading.Thread(target=mirror_mouse, daemon=True).start()

    # Setup window
    try: 
        cv2.namedWindow("Remote Screen", cv2.WINDOW_NORMAL)
        while running:
            if not frame_queue.empty():
                frame = frame_queue.get()
                cv2.imshow("Remote Screen", frame)
                cv2.resizeWindow("Remote Screen", width, height)
            
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
    
 