import cv2
import matplotlib.pyplot as plt
import imageio
import os

# Function to plot the image with bounding box and save it in a new folder
def get_image_with_bbox(image_path, annotation_path, output_dir):
    # Check if the image file exists
    if not os.path.exists(image_path):
        print(f"Warning: Image file {image_path} does not exist.")
        return None
    
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    
    # Handle case where image couldn't be loaded
    if image is None:
        print(f"Warning: Couldn't read the image {image_path}. Check the file path or file integrity.")
        return None
    
    img_height, img_width, _ = image.shape

    # Check if annotation file exists
    if not os.path.exists(annotation_path):
        print(f"Warning: Annotation file {annotation_path} does not exist.")
        return image  # Return the image without bounding box if annotation is missing

    # Read the annotation file (YOLO format)
    with open(annotation_path, 'r') as f:
        line = f.readline().strip()
        class_id, x_center, y_center, bbox_width, bbox_height = map(float, line.split())

    # Convert YOLO format back to pixel values
    x_center *= img_width
    y_center *= img_height
    bbox_width *= img_width
    bbox_height *= img_height

    # Calculate top-left and bottom-right coordinates of the bounding box
    x1 = int(x_center - bbox_width / 2)
    y1 = int(y_center - bbox_height / 2)
    x2 = int(x_center + bbox_width / 2)
    y2 = int(y_center + bbox_height / 2)

    # Draw the bounding box on the image
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Blue rectangle with thickness 2

    # Convert the image from BGR to RGB for matplotlib
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Save the image with bounding box to the new output directory
    os.makedirs(output_dir, exist_ok=True)
    output_image_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(output_image_path, image)
    
    return image_rgb

# Function to create a GIF from multiple images
def create_gif(image_dir, annotation_dir, output_dir, gif_path):
    images = []
    
    # Get the list of images from the directory
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
    
    for image_file in image_files:
        # Derive paths for the image and corresponding annotation
        img_path = os.path.join(image_dir, image_file)
        ann_file = image_file.replace('.jpg', '.txt')
        ann_path = os.path.join(annotation_dir, ann_file)

        # Process the image and bounding box
        image = get_image_with_bbox(img_path, ann_path, output_dir)
        if image is not None:
            images.append(image)

    # Only save if there are valid images
    if images:
        # Save the gif
        imageio.mimsave(gif_path, images, fps=2)  # fps=2 for 2 frames per second
        print(f"GIF saved at {gif_path}")
    else:
        print("No valid images to create a GIF.")

# Example usage
image_dir = "cursor_data_sample/images/"
annotation_dir = "cursor_data_sample/labels/"
output_dir = "cursor_data_sample/bbox_images/"  # New directory to save images with bounding boxes
gif_path = "mouse_bbox_animation.gif"

create_gif(image_dir, annotation_dir, output_dir, gif_path)
