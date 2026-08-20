import cv2
import os
import glob
import numpy as np

# --- CONFIGURATION ---
DATA_DIR = "/path_to/issac-data-synth/output/fancy_run"  # Make sure this matches your new output folder


def visualize_dataset():
    # 1. Find the images and labels
    img_files = sorted(glob.glob(os.path.join(DATA_DIR, "rgb_*.png")))
    # print(img_files[0])
    label_files = sorted(glob.glob(os.path.join(DATA_DIR, "labels", "rgb_*.txt")))


    if not img_files:
        print("No images found. Check your DATA_DIR.")
        return

    print(f"Found {len(img_files)} images. Showing the first 5...")

    # 2. Loop through a few images
    for i in range(min(5, len(img_files))):
        img_path = img_files[i]
        label_path = label_files[i]

        # Load Image
        img = cv2.imread(img_path)
        height, width, _ = img.shape

        # Load Labels
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                # YOLO Format: class_id x_center y_center w h
                parts = list(map(float, line.strip().split()))
                cls_id = int(parts[0])
                xc, yc, w, h = parts[1], parts[2], parts[3], parts[4]

                # Convert back to Pixel Coordinates for drawing
                x_min = int((xc - w / 2) * width)
                y_min = int((yc - h / 2) * height)
                x_max = int((xc + w / 2) * width)
                y_max = int((yc + h / 2) * height)

                # Draw the box (Green)
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(img, "Target", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Show the image
        # Note: If you are on a remote server without a screen, we save the file instead.
        out_name = "debug_vis_" + os.path.basename(img_path)
        cv2.imwrite(out_name, img)
        print(f"Saved visualization to: {out_name}")


if __name__ == "__main__":
    visualize_dataset()