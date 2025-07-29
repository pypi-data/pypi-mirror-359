import pandas as pd
from pathlib import Path
import os
from tqdm import tqdm
import argparse
from importlib import resources

# --- Configuration ---
# The base directory where the 'frames' structure is located.
FRAMES_DIR = Path('frames')
# -------------------

def create_labels_from_parquet(frames_dir: Path):
    """
    Reads a Parquet file and creates a corresponding .txt label file for EVERY image
    in the frames directory structure.
    """
    print("--- Merging Labels into Frames Directory ---")

    # 1. Load annotations into a DataFrame
    try:
        # Use importlib.resources to find the Parquet file within the package
        with resources.path('clubhead_db.data', 'annotations.parquet') as annotations_path:
            print(f"Loading annotations from '{annotations_path}'...")
            df = pd.read_parquet(annotations_path)
    except FileNotFoundError:
        raise FileNotFoundError("Could not find 'annotations.parquet' within the package data. The package may be installed incorrectly.")

    # Create a lookup dictionary for much faster access
    # The key is the relative image path, the value is a list of YOLO strings
    print("Creating annotation lookup table for faster processing...")
    annotation_lookup = {}

    # Filter for rows that actually have annotations
    annotated_df = df.dropna(subset=['x_center'])

    for _, row in tqdm(annotated_df.iterrows(), total=len(annotated_df), desc="Processing annotations"):
        relative_path = row['image_path']
        class_id = int(row['class_id'])
        x_c, y_c, w, h = row['x_center'], row['y_center'], row['width'], row['height']
        yolo_line = f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}"

        if relative_path not in annotation_lookup:
            annotation_lookup[relative_path] = []
        annotation_lookup[relative_path].append(yolo_line)

    # 2. Iterate through all discovered image files
    print(f"Scanning all images in '{frames_dir}' to create label files...")
    all_image_paths = list(frames_dir.rglob('*.jpg'))
    if not all_image_paths:
        raise FileNotFoundError(f"No .jpg images found in '{frames_dir}'. Please run the download and processing script first.")

    print(f"Writing .txt label files for {len(all_image_paths)} images...")
    for img_path in tqdm(all_image_paths, desc="Creating label files"):

        # Construct the corresponding label path
        # e.g., 'frames/swing_001/images/frame_0001.jpg' -> 'frames/swing_001/labels/frame_0001.txt'
        label_dir = img_path.parent.parent / 'labels'
        label_path = label_dir / img_path.with_suffix('.txt').name

        # Create the 'labels' subdirectory if it doesn't exist
        os.makedirs(label_dir, exist_ok=True)

        # Create the relative path key to search in our lookup table
        relative_path_key = '/'.join(img_path.parts[-4:])

        # Get the annotation content from the lookup
        yolo_content_list = annotation_lookup.get(relative_path_key)

        # Write the file (either with content or empty)
        with open(label_path, 'w', encoding='utf-8') as f:
            if yolo_content_list:
                f.write("\n".join(yolo_content_list))

    print("\nStatus: Label creation complete.")
    print(f"The '{frames_dir}' directory now contains 'labels' subfolders with .txt files for every image.")

def main():
    parser = argparse.ArgumentParser(description="Create YOLO .txt label files in the 'frames' directory structure.")
    parser.add_argument('--frames_dir', type=Path, default=FRAMES_DIR, help="Path to the base directory containing swing frames.")
    
    args = parser.parse_args()

    try:
        create_labels_from_parquet(args.frames_dir)
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
