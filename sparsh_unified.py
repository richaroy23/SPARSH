import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

class GestureApp:
    def __init__(self):
        # Configuration
        self.SMOOTHING = 5
        self.CLICK_THRESHOLD = 50
        self.MODE_CHANGE_HOLD_TIME = 3.0  # Hold gesture for 3 seconds to initiate mode change
        self.CONFIRMATION_TIME = 2.0  # 2 seconds to confirm/cancel
        
        # Mouse control variables
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.click_cooldown = 0
        
        # Mode variables
        self.current_mode = "MOUSE"  # "MOUSE" or "GESTURE"
        self.mode_change_state = "NORMAL"  # "NORMAL", "WAITING_CONFIRMATION", "CONFIRMING"
        self.mode_change_start_time = 0
        self.confirmation_start_time = 0
        
        # Gesture control variables
        self.prev_finger_count = -1
        self.gesture_start_time = 0
        self.gesture_initialized = False
        
        # MediaPipe setup
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
    def count_fingers(self, landmarks):
        """Count extended fingers"""
        cnt = 0
        thresh = (landmarks.landmark[0].y*100 - landmarks.landmark[9].y*100)/2
        
        # Index finger
        if (landmarks.landmark[5].y*100 - landmarks.landmark[8].y*100) > thresh:
            cnt += 1
        # Middle finger
        if (landmarks.landmark[9].y*100 - landmarks.landmark[12].y*100) > thresh:
            cnt += 1
        # Ring finger
        if (landmarks.landmark[13].y*100 - landmarks.landmark[16].y*100) > thresh:
            cnt += 1
        # Pinky
        if (landmarks.landmark[17].y*100 - landmarks.landmark[20].y*100) > thresh:
            cnt += 1
        # Thumb
        if (landmarks.landmark[5].x*100 - landmarks.landmark[4].x*100) > 6:
            cnt += 1
            
        return cnt
    
    def detect_thumbs_gesture(self, landmarks):
        """Detect thumbs up or thumbs down"""
        thumb_tip = landmarks.landmark[4]
        thumb_mcp = landmarks.landmark[2]
        index_mcp = landmarks.landmark[5]
        middle_mcp = landmarks.landmark[9]
        
        # Check if only thumb is extended
        other_fingers_folded = (
            landmarks.landmark[8].y > landmarks.landmark[6].y and  # Index folded
            landmarks.landmark[12].y > landmarks.landmark[10].y and  # Middle folded
            landmarks.landmark[16].y > landmarks.landmark[14].y and  # Ring folded
            landmarks.landmark[20].y > landmarks.landmark[18].y     # Pinky folded
        )
        
        if other_fingers_folded:
            # Thumbs up: thumb tip is above thumb MCP
            if thumb_tip.y < thumb_mcp.y - 0.05:
                return "THUMBS_UP"
            # Thumbs down: thumb tip is below thumb MCP  
            elif thumb_tip.y > thumb_mcp.y + 0.05:
                return "THUMBS_DOWN"
        
        return None
    
    def detect_fist(self, landmarks):
        """Detect if hand is in a fist (mode change initiator)"""
        # Check if all fingers are folded
        all_folded = (
            landmarks.landmark[8].y > landmarks.landmark[6].y and  # Index folded
            landmarks.landmark[12].y > landmarks.landmark[10].y and  # Middle folded
            landmarks.landmark[16].y > landmarks.landmark[14].y and  # Ring folded
            landmarks.landmark[20].y > landmarks.landmark[18].y     # Pinky folded
        )
        return all_folded
    
    def handle_mouse_mode(self, hand_landmarks, frame):
        """Handle mouse control mode"""
        frame_height, frame_width = frame.shape[:2]
        
        # Get finger positions
        index_finger = hand_landmarks.landmark[8]
        thumb_tip = hand_landmarks.landmark[4]
        
        # Convert to pixel coordinates
        index_x = int(index_finger.x * frame_width)
        index_y = int(index_finger.y * frame_height)
        thumb_x = int(thumb_tip.x * frame_width)
        thumb_y = int(thumb_tip.y * frame_height)
        
        # Draw visual feedback
        cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), -1)
        cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 0), -1)
        cv2.line(frame, (index_x, index_y), (thumb_x, thumb_y), (255, 255, 255), 2)
        
        # Calculate distance for clicking
        distance = np.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
        cv2.putText(frame, f"Distance: {int(distance)}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Mouse movement
        mouse_x = np.interp(index_x, (0, frame_width), (0, self.screen_width))
        mouse_y = np.interp(index_y, (0, frame_height), (0, self.screen_height))
        
        self.clocX = self.plocX + (mouse_x - self.plocX) / self.SMOOTHING
        self.clocY = self.plocY + (mouse_y - self.plocY) / self.SMOOTHING
        
        pyautogui.moveTo(self.clocX, self.clocY)
        
        # Click detection
        if distance < self.CLICK_THRESHOLD and self.click_cooldown == 0:
            pyautogui.click()
            self.click_cooldown = 30
            cv2.putText(frame, "CLICK!", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            
        self.plocX, self.plocY = self.clocX, self.clocY
    
    def handle_gesture_mode(self, hand_landmarks, frame):
        """Handle gesture control mode"""
        current_time = time.time()
        cnt = self.count_fingers(hand_landmarks)
        
        # Display finger count
        cv2.putText(frame, f"Fingers: {cnt}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        if self.prev_finger_count != cnt:
            if not self.gesture_initialized:
                self.gesture_start_time = current_time
                self.gesture_initialized = True
            elif (current_time - self.gesture_start_time) > 0.2:
                if cnt == 1:
                    pyautogui.press("right")
                    cv2.putText(frame, "RIGHT", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif cnt == 2:
                    pyautogui.press("left") 
                    cv2.putText(frame, "LEFT", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif cnt == 3:
                    pyautogui.press("up")
                    cv2.putText(frame, "UP", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif cnt == 4:
                    pyautogui.press("down")
                    cv2.putText(frame, "DOWN", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif cnt == 5:
                    pyautogui.press("space")
                    cv2.putText(frame, "SPACE", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                self.prev_finger_count = cnt
                self.gesture_initialized = False
    
    def handle_mode_switching(self, hand_landmarks, frame):
        """Handle mode switching logic"""
        current_time = time.time()
        
        if self.mode_change_state == "NORMAL":
            # Check for fist to initiate mode change
            if self.detect_fist(hand_landmarks):
                if self.mode_change_start_time == 0:
                    self.mode_change_start_time = current_time
                elif (current_time - self.mode_change_start_time) >= self.MODE_CHANGE_HOLD_TIME:
                    self.mode_change_state = "WAITING_CONFIRMATION"
                    self.confirmation_start_time = current_time
                    self.mode_change_start_time = 0
                else:
                    # Show progress
                    progress = (current_time - self.mode_change_start_time) / self.MODE_CHANGE_HOLD_TIME
                    cv2.putText(frame, f"Hold fist to change mode: {progress:.1%}", (10, 160), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            else:
                self.mode_change_start_time = 0
                
        elif self.mode_change_state == "WAITING_CONFIRMATION":
            thumbs_gesture = self.detect_thumbs_gesture(hand_landmarks)
            remaining_time = self.CONFIRMATION_TIME - (current_time - self.confirmation_start_time)
            
            if remaining_time <= 0:
                # Timeout - cancel mode change
                self.mode_change_state = "NORMAL"
                self.confirmation_start_time = 0
            elif thumbs_gesture == "THUMBS_UP":
                # Confirm mode change
                self.current_mode = "GESTURE" if self.current_mode == "MOUSE" else "MOUSE"
                self.mode_change_state = "NORMAL"
                self.confirmation_start_time = 0
                print(f"Mode changed to: {self.current_mode}")
            elif thumbs_gesture == "THUMBS_DOWN":
                # Cancel mode change
                self.mode_change_state = "NORMAL"
                self.confirmation_start_time = 0
            else:
                # Show confirmation prompt
                new_mode = "GESTURE" if self.current_mode == "MOUSE" else "MOUSE"
                cv2.putText(frame, f"Change to {new_mode} mode?", (10, 160), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                cv2.putText(frame, f"Thumbs UP=Yes, DOWN=No ({remaining_time:.1f}s)", (10, 190), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    def run(self):
        """Main application loop"""
        print("=== SPARSH Gesture Control ===")
        print("Starting in MOUSE mode")
        print("Hold FIST for 3 seconds to change modes")
        print("THUMBS UP = Confirm, THUMBS DOWN = Cancel")
        print("Press 'q' to quit")
        
        while True:
            success, frame = self.cap.read()
            if not success:
                break
                
            frame = cv2.flip(frame, 1)
            frame_height, frame_width = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = self.hands.process(rgb_frame)
            
            # Display current mode
            mode_color = (0, 255, 0) if self.current_mode == "MOUSE" else (255, 0, 255)
            cv2.putText(frame, f"Mode: {self.current_mode}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Handle mode switching
                self.handle_mode_switching(hand_landmarks, frame)
                
                # Handle current mode functionality (only if not in mode change state)
                if self.mode_change_state == "NORMAL":
                    if self.current_mode == "MOUSE":
                        self.handle_mouse_mode(hand_landmarks, frame)
                    else:
                        self.handle_gesture_mode(hand_landmarks, frame)
            
            # Display instructions
            cv2.putText(frame, "Hold FIST for 3s to change modes", (10, frame_height - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, frame_height - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            cv2.imshow("SPARSH - Gesture Control", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = GestureApp()
    app.run()