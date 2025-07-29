import os
import subprocess
import pandas as pd
from importlib import resources

# --- Configuration ---
VIDEOS_DIR = 'videos'
FRAMES_DIR = 'frames'

def setup_directories():
    """Create the necessary directories if they don't exist."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print("Directories `videos` and `frames` are ready.")

def download_clip(video_url_or_id, source, start_time, end_time, output_path):
    """
    Constructs the correct URL and command based on the 'source' column and downloads the clip.
    """
    command = []
    
    if source == 'reddit':
        if 'packaged-media.redd.it' in video_url_or_id:
            print(f"WARNING: The URL '{video_url_or_id}' appears to be a direct Reddit media link.")
            print("Please use the full Reddit comment page URL (e.g., https://www.reddit.com/r/GolfSwing/comments/...) for better reliability.")
        
        video_url = video_url_or_id
        print(f"Downloading clip from Reddit URL: {video_url}...")
        command = [
            'yt-dlp', '-q', '--no-warnings',
            '-o', output_path,
            video_url
        ]
    
    elif source == 'yt_shorts':
        video_url = f'https://www.youtube.com/shorts/{video_url_or_id}'
        print(f"Downloading clip from {video_url} from {start_time} to {end_time}...")
        command = [
            'yt-dlp', '-q', '--no-warnings', '-f', 'bestvideo[ext=mp4]',
            '--download-sections', f'*{start_time}-{end_time}',
            '-o', output_path, '--force-keyframes-at-cuts',
            video_url
        ]
    elif source == 'yt':
        video_url = f'https://www.youtube.com/watch?v={video_url_or_id}'
        print(f"Downloading clip from {video_url} from {start_time} to {end_time}...")
        command = [
            'yt-dlp', '-q', '--no-warnings', '-f', 'bestvideo[ext=mp4]',
            '--download-sections', f'*{start_time}-{end_time}',
            '-o', output_path, '--force-keyframes-at-cuts',
            video_url
        ]
    else:
        print(f"ERROR: Unknown source '{source}' for ID {video_url_or_id}. Skipping.")
        return False

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully downloaded clip to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to download video. yt-dlp stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("ERROR: `yt-dlp` command not found. Please ensure it is installed.")
        return False

def extract_frames(video_path, output_dir, target_fps):
    """
    Extracts frames from a video clip using ffmpeg.
    """
    images_output_dir = os.path.join(output_dir, 'images')
    print(f"Extracting frames from {video_path} at {target_fps} FPS...")
    os.makedirs(images_output_dir, exist_ok=True)
    
    output_pattern = os.path.join(images_output_dir, 'frame_%04d.jpg')
    command = ['ffmpeg', '-i', video_path, '-r', str(target_fps), '-q:v', '2', '-y', output_pattern]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        frame_count = len(os.listdir(images_output_dir))
        print(f"Successfully extracted {frame_count} frames to {images_output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to extract frames from {video_path}. ffmpeg output: {e.stdout}")
        return False
    except FileNotFoundError:
        print("ERROR: `ffmpeg` command not found. Please ensure it is installed.")
        return False

def main():
    """Main function to orchestrate the download and processing pipeline."""
    print("--- Starting ClubheadDB Data Pipeline ---")
    setup_directories()

    try:
        # Use importlib.resources to find the file within the package
        with resources.path('clubhead_db.data', 'metadata.csv') as metadata_path:
            metadata = pd.read_csv(metadata_path, delimiter=';')
        print(f"Successfully loaded metadata for {len(metadata)} video(s).")
    except FileNotFoundError:
        print("ERROR: Could not find 'metadata.csv' within the package data. The package may be installed incorrectly.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return

    required_cols = ['youtube_id', 'source']
    if not all(col in metadata.columns for col in required_cols):
        print(f"ERROR: 'metadata.csv' must contain 'youtube_id' and 'source' columns.")
        return

    for index, row in metadata.iterrows():
        if pd.isna(row['video_id']) or pd.isna(row['source']):
            continue

        youtube__id = ''
        if pd.notna(row['youtube_id']):
            youtube_id = str(row['youtube_id']).strip()
        elif row['source'] in ['yt', 'yt_shorts', 'reddit']:
            print(f"WARNING: Skipping row for video_id {row['video_id']} due to missing 'youtube_id' for source '{row['source']}'.")
            continue

        video_id = str(row['video_id']).strip()
        source = str(row['source']).strip()
        start_time = str(row['start_time']).strip() if pd.notna(row['start_time']) else ''
        end_time = str(row['end_time']).strip() if pd.notna(row['end_time']) else ''
        
        # Check for NaN in target_fps before processing
        if pd.isna(row['target_fps']):
            print(f"WARNING: Skipping row for video_id {row['video_id']} due to missing 'target_fps'.")
            continue
        target_fps = row['target_fps']
        
        print(f"\n--- Processing video: {video_id} ---")
        
        video_clip_path = os.path.join(VIDEOS_DIR, f'{video_id}.mp4')
        base_frame_output_dir = os.path.join(FRAMES_DIR, video_id)
        images_dir = os.path.join(base_frame_output_dir, 'images')

        if os.path.exists(images_dir) and len(os.listdir(images_dir)) > 0:
            print(f"Frames for {video_id} already exist. Skipping.")
            continue
            
        if download_clip(youtube_id, source, start_time, end_time, video_clip_path):
            if not extract_frames(video_clip_path, base_frame_output_dir, target_fps):
                continue
        else:
            continue
    
    print("\n--- Data Acquisition Pipeline Finished ---")

if __name__ == '__main__':
    main()
