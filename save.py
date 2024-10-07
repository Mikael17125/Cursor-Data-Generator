import subprocess
import pyautogui
import os
import time
import cv2
import numpy as np
from pynput import keyboard
import random

# Function to get the last image number
def get_last_image_number(images_dir):
    image_files = [f for f in os.listdir(images_dir) if f.startswith("image_") and f.endswith(".jpg")]
    if not image_files:
        return -1
    image_numbers = [int(f.split('_')[1].split('.')[0]) for f in image_files]
    return max(image_numbers)

# Function to capture the screen and save image + annotation
def get_screen_with_cursor(image_path, annotation_path, class_id=0, box_size=30):
    # Use scrot to take a screenshot including the cursor
    subprocess.run(["scrot", "-p", image_path])
    
    # Load the screenshot using OpenCV
    img = cv2.imread(image_path)
    
    # Get the image dimensions
    img_height, img_width, _ = img.shape

    # Get the current mouse position using pyautogui
    mouse_x, mouse_y = pyautogui.position()

    # Create a bounding box around the cursor
    x1 = max(0, mouse_x - box_size // 2)
    y1 = max(0, mouse_y - box_size // 2)
    x2 = min(img_width, mouse_x + box_size // 2)
    y2 = min(img_height, mouse_y + box_size // 2)

    # Normalize coordinates for YOLO format (x_center, y_center, width, height)
    x_center = (x1 + x2) / 2 / img_width
    y_center = (y1 + y2) / 2 / img_height
    bbox_width = (x2 - x1) / img_width
    bbox_height = (y2 - y1) / img_height

    # Save annotation in YOLO format
    with open(annotation_path, 'w') as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")


# Function for random mouse movement and optional clicking (exploration mode)
def random_mouse_movement(images_dir, labels_dir, num_images, class_id=0, box_size=30, click=False):
    screen_width, screen_height = pyautogui.size()
    last_image_num = get_last_image_number(images_dir)
    image_count = last_image_num + 1

    while image_count < last_image_num + 1 + num_images:
        # Move the mouse to a random position on the screen
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        pyautogui.moveTo(x, y, duration=0.5)

        if click:
            # Simulate a random click with 50% probability
            if random.random() > 0.5:
                pyautogui.click()

        # Capture the screen and save annotation
        image_path = os.path.join(images_dir, f"image_{image_count}.jpg")
        annotation_path = os.path.join(labels_dir, f"image_{image_count}.txt")
        get_screen_with_cursor(image_path, annotation_path, class_id, box_size)
        print(f"Captured image_{image_count}.jpg")

        image_count += 1
        time.sleep(1)  # Delay between captures


# Function to select mode (exploration or manual)
def select_mode():
    print("Select mode: \n1. Exploration Mode (automatic mouse movement)\n2. Manual Save Mode (Ctrl + Space to save)")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        return "exploration"
    elif choice == "2":
        return "manual"
    else:
        print("Invalid choice, defaulting to Manual Save Mode.")
        return "manual"


# Function to generate dataset by capturing screenshots and annotations
def generate_dataset(output_dir, num_images=100, class_id=0, box_size=30, click=False):
    images_dir = os.path.join(output_dir, "images")
    labels_dir = os.path.join(output_dir, "labels")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    # Select exploration or manual save mode
    mode = select_mode()

    if mode == "exploration":
        # Exploration mode: Move the mouse randomly and capture the screen
        random_mouse_movement(images_dir, labels_dir, num_images, class_id, box_size, click)
    else:
        # Manual save mode: Capture the screen when Ctrl + Space is pressed
        manual_save(images_dir, labels_dir, num_images, class_id, box_size)


# Function for manual save mode with Ctrl + Space
def manual_save(images_dir, labels_dir, num_images, class_id=0, box_size=30):
    last_image_num = get_last_image_number(images_dir)
    image_count = last_image_num + 1  # Continue from the last image number
    print("Press Ctrl + Space to capture the screen.")

    # Define the key combination to trigger capture
    current_keys = set()

    def on_press(key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.space:
                current_keys.add(key)

            # Check if both Ctrl and Space are pressed
            if keyboard.Key.ctrl_l in current_keys and keyboard.Key.space in current_keys:
                nonlocal image_count
                if image_count < last_image_num + 1 + num_images:
                    image_path = os.path.join(images_dir, f"image_{image_count}.jpg")
                    annotation_path = os.path.join(labels_dir, f"image_{image_count}.txt")
                    
                    # Capture and annotate the screen
                    get_screen_with_cursor(image_path, annotation_path, class_id, box_size)
                    print(f"Captured image_{image_count}.jpg")
                    image_count += 1
                else:
                    print("Image limit reached.")
        except AttributeError:
            pass

    def on_release(key):
        # Remove key from the set when released
        if key in current_keys:
            current_keys.remove(key)
        if key == keyboard.Key.esc:
            # Stop the listener on 'Esc' key press
            return False

    # Start the listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# Example usage
output_directory = "mouse_dataset"
generate_dataset(output_directory, num_images=10000, box_size=40, click=True)
