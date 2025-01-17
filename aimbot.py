import cv2
import numpy as np
import pyautogui
import random
import keyboard
import time
import win32gui
import win32con


# Load the pre-trained model for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to capture the entire screen
def capture_screen():
    screen = pyautogui.screenshot()
    frame = np.array(screen)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

# Function to detect faces in an image
def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

# Function to draw rectangles around detected faces and move mouse to a random position within the face
def draw_faces_and_move_mouse(frame, faces):
    for (x, y, w, h) in faces:
        # Calculate a random position within the face
        random_x = x + random.randint(0, w)
        random_y = y + random.randint(0, h)
        # Move the mouse to the random position within the face
        pyautogui.moveTo(random_x, random_y)

# Global variables to control the program and mouse following
mouse_following = False
program_running = True
status_text = "Mouse Following: Disabled"
overlay_window = None
overlay = None # create overlay as global variable.

#Function to create a transparent window to display text
def create_overlay_window():
    global overlay_window, overlay
    if overlay_window is not None:
        return

    screen_width, screen_height = pyautogui.size()
    overlay_width = 300
    overlay_height = 50
    
    overlay_window = cv2.namedWindow("Overlay Status", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Overlay Status", overlay_width, overlay_height)
    cv2.moveWindow("Overlay Status", 0, 0)
    hwnd = win32gui.FindWindow(None, "Overlay Status")
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32con.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY) # Set transparent color key (0, 0, 0)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE) # set window to topMost.
     
    overlay = np.zeros((overlay_height, overlay_width, 4), dtype=np.uint8) # create an overlay of 50x300 with alpha
    overlay[:,:,3] = 0 # set alpha to 0


def display_status_on_screen(text):
    global overlay_window, overlay

    #create the window only once
    create_overlay_window()
    screen_width, screen_height = pyautogui.size()

    overlay[:] = (0, 0, 0, 0)  # clear previous text

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    color = (255, 255, 255, 255)  # White color with alpha
    thickness = 2
    org = (10, 30)  # Position of text (top-left corner)

    cv2.putText(overlay, text, org, font, font_scale, color, thickness, cv2.LINE_AA)

    cv2.imshow("Overlay Status", overlay)

def toggle_mouse_following():
    global mouse_following, status_text
    mouse_following = not mouse_following
    status_text = f"Mouse Following: {'Enabled' if mouse_following else 'Disabled'}"
    print(status_text)


def stop_program():
    global program_running
    program_running = False
    if overlay_window is not None:
        cv2.destroyWindow("Overlay Status") # destroy the overlay window.
    print("Program stopped.")

# Set up keyboard shortcuts
keyboard.add_hotkey('ctrl+shift+0', toggle_mouse_following)
keyboard.add_hotkey('ctrl+shift+9', stop_program)

while program_running:
    # Capture the screen
    frame = capture_screen()

    # Detect faces
    faces = detect_faces(frame)

    # If mouse following is enabled, draw faces and move the mouse
    if mouse_following:
        draw_faces_and_move_mouse(frame, faces)

    #display status
    display_status_on_screen(status_text)
    cv2.waitKey(1)