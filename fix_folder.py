import os
import shutil
import glob

# Path to your dataset
BASE_DIR = "output/fancy_run"
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def reorganize():
    # 1. Create the 'images' subfolder
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"Created folder: {IMAGES_DIR}")

    # 2. Find all PNG images in the root folder
    # (Note: Isaac Sim BasicWriter outputs .png)
    png_files = glob.glob(os.path.join(BASE_DIR, "rgb_*.png"))

    if not png_files:
        print("No PNG files found to move! (Did you already run this?)")
        return

    print(f"Moving {len(png_files)} images...")

    # 3. Move them
    for png in png_files:
        filename = os.path.basename(png)
        dst = os.path.join(IMAGES_DIR, filename)
        shutil.move(png, dst)

    print("Success! Files reorganized.")
    print(f"Images are now in: {IMAGES_DIR}")
    print(f"Labels remain in: {os.path.join(BASE_DIR, 'labels')}")


if __name__ == "__main__":
    reorganize()