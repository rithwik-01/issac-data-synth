import json
import glob
import os
import numpy as np

# --- CONFIGURATION ---
DATA_DIR = "/path_to/issac-data-synth/output/fancy_run"
IMG_WIDTH = 1024
IMG_HEIGHT = 1024
TARGET_LABEL = "industrial_box"


def find_target_id(json_path):
    """Parses the specific JSON structure: { '11': {'class': 'industrial_box'} }"""
    with open(json_path, 'r') as f:
        data = json.load(f)

    print(f"Scanning mapping file: {os.path.basename(json_path)}")

    # Iterate through keys (which are the IDs in string format)
    for id_str, attributes in data.items():
        # Check if the value is a dictionary and has the class name we want
        if isinstance(attributes, dict) and attributes.get('class') == TARGET_LABEL:
            return int(id_str)

    return None


def convert_to_yolo(x_min, y_min, x_max, y_max, width, height):
    x_center = ((x_min + x_max) / 2) / width
    y_center = ((y_min + y_max) / 2) / height
    w = (x_max - x_min) / width
    h = (y_max - y_min) / height
    return x_center, y_center, w, h


def main():
    # 1. Locate the Mapping JSON
    json_files = glob.glob(os.path.join(DATA_DIR, "*labels*.json"))
    if not json_files:
        print("Error: No labels JSON file found.")
        return

    # 2. Find the ID
    target_id = find_target_id(json_files[0])

    if target_id is None:
        print(f"ERROR: Could not find '{TARGET_LABEL}' in the file.")
        return

    print(f"Found Target ID for '{TARGET_LABEL}': {target_id}")
    print("Starting conversion with filter...")

    # 3. Convert .npy files using the filter
    npy_files = glob.glob(os.path.join(DATA_DIR, "bounding_box_2d_tight_*.npy"))

    count = 0
    skipped_count = 0

    for npy_file in npy_files:
        try:
            data = np.load(npy_file)
        except:
            continue

        base_name = os.path.basename(npy_file)
        txt_name = base_name.replace("bounding_box_2d_tight_", "rgb_").replace(".npy", ".txt")
        out_path = os.path.join(DATA_DIR, "labels", txt_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        has_target = False
        with open(out_path, 'w') as out_f:
            for row in data:
                # --- FILTER: Only write if ID matches 11 ---
                if row['semanticId'] == target_id:
                    xc, yc, w, h = convert_to_yolo(
                        row['x_min'], row['y_min'], row['x_max'], row['y_max'],
                        IMG_WIDTH, IMG_HEIGHT
                    )
                    out_f.write(f"0 {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
                    has_target = True

        if has_target:
            count += 1
        else:
            # If an image has NO box (e.g. only pallets), we still keep the empty file
            # because YOLO needs to know "there is nothing here"
            skipped_count += 1

    print(f"Success! Converted {count + skipped_count} files.")
    print(f"   - Images with Target: {count}")
    print(f"   - Images with ONLY background/distractors: {skipped_count}")


if __name__ == "__main__":
    main()