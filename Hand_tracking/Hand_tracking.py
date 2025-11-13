import cv2
import mediapipe as mp
import pyautogui  
import time    

# Initialize MediaPipe Hands and drawing utilities.
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# Global variable to store the previous average x-coordinate of the index and middle finger tips.
prev_finger_x = None
# Threshold for detecting a significant lateral movement (normalized coordinate range: 0-1).
finger_movement_threshold = 0.02

# Cooldown parameters: only one scroll command per gesture (0.5 seconds).
SCROLL_COOLDOWN = 0.5
last_scroll_time = 0

def is_thumb_open(hand_label, landmarks):
    """
    Determines if the thumb is extended.
    For a flipped (mirror) view:
      - For the Right hand, the thumb is considered open if the thumb tip is to the left of its IP joint.
      - For the Left hand, the thumb is open if the thumb tip is to the right of its IP joint.
    """
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    if hand_label == "Right":
        return thumb_tip.x < thumb_ip.x
    else:
        return thumb_tip.x > thumb_ip.x

def is_finger_open(tip, pip):
    """
    For non-thumb fingers: if the tip's y-coordinate is less than the PIP joint's y-coordinate,
    the finger is considered extended.
    """
    return tip.y < pip.y

def scroll_left():
    # Simulate Ctrl+Left Arrow (e.g., for switching desktops or scrolling left)
    pyautogui.hotkey('ctrl', 'left')

def scroll_right():
    # Simulate Ctrl+Right Arrow (e.g., for switching desktops or scrolling right)
    pyautogui.hotkey('ctrl', 'right')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally (mirror view) and convert BGR to RGB.
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Draw the hand landmarks.
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the hand label ("Left" or "Right") for the current hand.
            hand_label = results.multi_handedness[idx].classification[0].label
            landmarks = hand_landmarks.landmark

            # Determine the open/closed status of each finger.
            thumb_open = is_thumb_open(hand_label, landmarks)
            index_open = is_finger_open(landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                                        landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP])
            middle_open = is_finger_open(landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                                         landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP])
            ring_open = is_finger_open(landmarks[mp_hands.HandLandmark.RING_FINGER_TIP],
                                       landmarks[mp_hands.HandLandmark.RING_FINGER_PIP])
            pinky_open = is_finger_open(landmarks[mp_hands.HandLandmark.PINKY_TIP],
                                        landmarks[mp_hands.HandLandmark.PINKY_PIP])


            # Optionally, display the overall finger count.
            finger_count = sum([thumb_open, index_open, middle_open, ring_open, pinky_open])
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 50 + idx * 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Motion tracking: Only for the right hand when exactly the index and middle are extended.
            if (hand_label == "Right" and index_open and middle_open 
                and not thumb_open and not ring_open and not pinky_open):
                # Calculate the average x-coordinate of the index and middle finger tips.
                finger_to_track = (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].x +
                                   landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x) / 2


                # If we have a previous position, compare to detect lateral movement.
                if prev_finger_x is not None:
                    dx = finger_to_track - prev_finger_x
                    if abs(dx) > finger_movement_threshold:
                        current_time = time.time()
                        # Only trigger if the cooldown has passed.
                        if current_time - last_scroll_time > SCROLL_COOLDOWN:
                            if dx > 0:
                                message = "Finger moved right"
                                scroll_right()  # Simulate scrolling right
                            else:
                                message = "Finger moved left"
                                scroll_left()   # Simulate scrolling left
                            last_scroll_time = current_time
                            cv2.putText(frame, message, (10, 150),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                prev_finger_x = finger_to_track
            else:
                # Reset tracking if the condition isn't met.
                prev_finger_x = None

    cv2.imshow("Finger Motion to Scroll", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
