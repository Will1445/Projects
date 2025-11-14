import mediapipe as mp
import cv2
import pyautogui  
import time    

# Setup
prev_finger_x = None
movement_threshold = 0.02

cooldown = 0.5
scroll_time = 0

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
capture = cv2.VideoCapture(0)

# Finger position detection 
def is_thumb_open(hand_label, landmarks):
    """
    Determines thumb position for left and right hand cases
    """
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    if hand_label == "Right":
        return thumb_tip.x < thumb_ip.x
    else:
        return thumb_tip.x > thumb_ip.x

def is_finger_open(tip, pip):
    """
    Determines finger position for left and right hand cases
    """
    return tip.y < pip.y

# MacOS scroll commands
def scroll_left():
    pyautogui.hotkey('ctrl', 'left')

def scroll_right():
    pyautogui.hotkey('ctrl', 'right')


while True:
    ret, frame = capture.read()
    if not ret: 
        break 

    # Flip the frame and convert BGR to RGB
    frame = cv2.flip(frame, 1) 
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
  
    if results.multi_hand_landmarks:
        for idx, hand_points in enumerate(results.multi_hand_landmarks):

            mp_draw.draw_landmarks(frame, hand_points, mp_hands.HAND_CONNECTIONS) 


            hand_label = results.multi_handedness[idx].classification[0].label
            landmarks = hand_points.landmark

            # Log the state of each finger
            thumb_open = is_thumb_open(hand_label, landmarks)
            
            index_open = is_finger_open(landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP], landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]) 
            
            middle_open = is_finger_open(landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP], landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]) 
            
            ring_open = is_finger_open(landmarks[mp_hands.HandLandmark.RING_FINGER_TIP], landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]) 
            
            pinky_open = is_finger_open(landmarks[mp_hands.HandLandmark.PINKY_TIP], landmarks[mp_hands.HandLandmark.PINKY_PIP]) 


            # Add an open finger count for debug
            finger_count = sum([thumb_open, index_open, middle_open, ring_open, pinky_open]) 
            print(f"Fingers: {finger_count}")
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 50 + idx * 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) 

            # Motion tracking
            if (hand_label == "Right" and index_open and middle_open and not thumb_open and not ring_open and not pinky_open):
                current_finger_x = (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].x + landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x) / 2
    
                if prev_finger_x is not None:
                    dx = current_finger_x - prev_finger_x
                    
                    if abs(dx) > movement_threshold:
                        current_time = time.time()

                        # Scrolling command for MacOS
                        if current_time - scroll_time > cooldown:
                            if dx > 0:
                                movement = "Hand moved right"
                                scroll_right()  
                                
                            else: 
                                movement = "Hand moved left"
                                scroll_left()
                                
                            scroll_time = current_time
                            cv2.putText(frame, movement, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            
                prev_finger_x = current_finger_x
                
            else:
                prev_finger_x = None

    cv2.imshow("Finger motion to scroll", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()

