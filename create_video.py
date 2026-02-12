import subprocess
import os

# Define the paths
image_path = "images/Screenshot 2026-02-11 at 11.04.59 PM.png"
audio_path = "background_music.mp3"
output_path = "output_programmatic.mp4"

def create_video():
    print(f"Creating video from {image_path} and {audio_path}...")
    
    # ffmpeg command to create a 10s video from an image and audio
    # -loop 1: loop the input image
    # -i: input files
    # -t 10: duration 10 seconds
    # -c:v libx264: video codec
    # -pix_fmt yuv420p: pixel format for compatibility
    # -vf scale: ensure even dimensions
    # -c:a aac: audio codec
    # -b:a 192k: audio bitrate
    # -shortest: finish when the shortest stream ends (though we use -t 10)
    
    command = [
        'ffmpeg',
        '-y', # Overwrite output file
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-t', '10',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_path
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Video created successfully!")
        print(f"Output saved to: {os.path.abspath(output_path)}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        print(f"ffmpeg output: {e.stderr}")

if __name__ == "__main__":
    create_video()
