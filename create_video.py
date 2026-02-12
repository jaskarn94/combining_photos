import subprocess
import os
import sys
import glob
import json
import argparse

# Valid xfade transition types for FFmpeg
VALID_TRANSITIONS = [
    # Basic fades
    'fade', 'fadeblack', 'fadewhite', 'dissolve', 'fadegrays',
    # Wipes
    'wipeleft', 'wiperight', 'wipeup', 'wipedown',
    'wipetl', 'wipetr', 'wipebl', 'wipebr',
    # Slides
    'slideleft', 'slideright', 'slideup', 'slidedown',
    # Covers/Reveals
    'coverleft', 'coverright', 'coverup', 'coverdown',
    'revealleft', 'revealright', 'revealup', 'revealdown',
    # Geometric
    'circlecrop', 'rectcrop', 'radial',
    # Open/Close
    'circleopen', 'circleclose', 'vertopen', 'vertclose', 'horzopen', 'horzclose',
    # Slices
    'hlslice', 'hrslice', 'vuslice', 'vdslice',
    # Smooth
    'smoothleft', 'smoothright', 'smoothup', 'smoothdown',
    # Diagonal
    'diagtl', 'diagtr', 'diagbl', 'diagbr',
    # Special
    'pixelize', 'distance', 'hblur', 'squeezeh', 'squeezev', 'zoomin',
    # Wind
    'hlwind', 'hrwind', 'vuwind', 'vdwind',
    # Custom
    'custom'
]


def list_transitions():
    """
    Print all available transition types organized by category.
    """
    print("\n" + "=" * 70)
    print("Available Transition Types (44 total)")
    print("=" * 70)

    categories = {
        "Professional & Subtle": ['fade', 'fadeblack', 'fadewhite', 'dissolve', 'fadegrays'],
        "Wipes": ['wipeleft', 'wiperight', 'wipeup', 'wipedown', 'wipetl', 'wipetr', 'wipebl', 'wipebr'],
        "Slides": ['slideleft', 'slideright', 'slideup', 'slidedown'],
        "Covers": ['coverleft', 'coverright', 'coverup', 'coverdown'],
        "Reveals": ['revealleft', 'revealright', 'revealup', 'revealdown'],
        "Geometric": ['circlecrop', 'rectcrop', 'radial'],
        "Open/Close": ['circleopen', 'circleclose', 'vertopen', 'vertclose', 'horzopen', 'horzclose'],
        "Slices": ['hlslice', 'hrslice', 'vuslice', 'vdslice'],
        "Smooth": ['smoothleft', 'smoothright', 'smoothup', 'smoothdown'],
        "Diagonal": ['diagtl', 'diagtr', 'diagbl', 'diagbr'],
        "Special Effects": ['pixelize', 'distance', 'hblur', 'squeezeh', 'squeezev', 'zoomin'],
        "Wind": ['hlwind', 'hrwind', 'vuwind', 'vdwind'],
        "Custom": ['custom']
    }

    for category, transitions in categories.items():
        print(f"\n{category}:")
        for i in range(0, len(transitions), 4):
            row = transitions[i:i+4]
            print("  " + ", ".join(f"{t:15}" for t in row))

    print("\n" + "=" * 70)
    print(f"Use --transition <name> or -t <name> to specify a transition")
    print("Example: python3 create_video.py --transition circlecrop")
    print("=" * 70 + "\n")


def parse_arguments():
    """
    Parse command-line arguments for video creation.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Create professional slideshow videos from images with transitions and music.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 create_video.py                              # Use default settings
  python3 create_video.py -t circlecrop                # Use circlecrop transition
  python3 create_video.py --transition wipeleft        # Use wipeleft transition
  python3 create_video.py -l                           # List all transitions
  python3 create_video.py -t smoothright -d 5.0        # 5 seconds per image
  python3 create_video.py -t fade -o my_video.mp4      # Custom output file
        """
    )

    parser.add_argument(
        '-t', '--transition',
        type=str,
        default='fade',
        metavar='TYPE',
        help='Transition type (default: fade). Use -l to list all available transitions.'
    )

    parser.add_argument(
        '-l', '--list-transitions',
        action='store_true',
        help='List all available transition types and exit'
    )

    parser.add_argument(
        '-i', '--images',
        type=str,
        default='images',
        metavar='DIR',
        help='Directory containing images (default: images)'
    )

    parser.add_argument(
        '-a', '--audio',
        type=str,
        default='background_music.mp3',
        metavar='FILE',
        help='Background music file (default: background_music.mp3)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output_multi.mp4',
        metavar='FILE',
        help='Output video file (default: output_multi.mp4)'
    )

    parser.add_argument(
        '-d', '--duration',
        type=float,
        default=3.5,
        metavar='SECS',
        help='Duration per image in seconds (default: 3.5)'
    )

    parser.add_argument(
        '--transition-duration',
        type=float,
        default=1.0,
        metavar='SECS',
        help='Transition duration in seconds (default: 1.0)'
    )

    parser.add_argument(
        '-r', '--resolution',
        type=str,
        default='1920x1080',
        metavar='WIDTHxHEIGHT',
        help='Output resolution (default: 1920x1080)'
    )

    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        metavar='N',
        help='Frame rate (default: 30)'
    )

    parser.add_argument(
        '--crf',
        type=int,
        default=18,
        metavar='N',
        help='Quality: 0-51, lower=better (default: 18)'
    )

    parser.add_argument(
        '--preset',
        type=str,
        default='slow',
        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
        help='Encoding preset (default: slow)'
    )

    return parser.parse_args()


# Define the paths
image_path = "images/Screenshot 2026-02-11 at 11.04.59 PM.png"
audio_path = "background_music.mp3"
output_path = "output_programmatic.mp4"

def get_image_files(directory='images'):
    """
    Scan directory for image files (.jpg, .jpeg, .png) and return sorted list.

    Args:
        directory: Path to directory containing images

    Returns:
        List of absolute paths to image files, sorted alphabetically

    Raises:
        ValueError: If directory doesn't exist or contains fewer than 2 images
    """
    if not os.path.exists(directory):
        raise ValueError(f"Images directory '{directory}' does not exist")

    if not os.path.isdir(directory):
        raise ValueError(f"'{directory}' is not a directory")

    # Get all image files (case-insensitive)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    image_files = []

    for ext in image_extensions:
        pattern = os.path.join(directory, ext)
        image_files.extend(glob.glob(pattern))

    # Remove duplicates and sort
    image_files = sorted(set(image_files))

    if len(image_files) < 2:
        raise ValueError(
            f"Found {len(image_files)} image(s) in '{directory}'. "
            "At least 2 images are required for transitions."
        )

    # Convert to absolute paths
    image_files = [os.path.abspath(f) for f in image_files]

    return image_files


def calculate_video_duration(num_images, duration_per_image, transition_duration):
    """
    Calculate total video duration accounting for overlapping transitions.

    Args:
        num_images: Number of images in the video
        duration_per_image: Display time for each image (seconds)
        transition_duration: Duration of crossfade transition (seconds)

    Returns:
        Total video duration in seconds

    Formula: (num_images × duration_per_image) - ((num_images - 1) × transition_duration)
    """
    if num_images < 1:
        raise ValueError("Number of images must be at least 1")

    if transition_duration >= duration_per_image:
        raise ValueError(
            f"Transition duration ({transition_duration}s) must be less than "
            f"duration per image ({duration_per_image}s)"
        )

    # Calculate with overlapping transitions
    total_duration = (num_images * duration_per_image) - ((num_images - 1) * transition_duration)

    return total_duration


def get_audio_duration(audio_path):
    """
    Get duration of audio file using ffprobe.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds as float

    Raises:
        FileNotFoundError: If audio file doesn't exist
        subprocess.CalledProcessError: If ffprobe fails
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file '{audio_path}' does not exist")

    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        return duration
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            f"Failed to get audio duration: {e.stderr}"
        )
    except ValueError as e:
        raise ValueError(f"Could not parse audio duration: {e}")


def build_filter_complex(num_images, duration_per_image, transition_duration, transition_type='fade', resolution=(1920, 1080), fps=30):
    """
    Build FFmpeg filter_complex string for multi-image video with crossfade transitions.

    Args:
        num_images: Number of images
        duration_per_image: Display time per image (seconds)
        transition_duration: Crossfade duration (seconds)
        transition_type: xfade transition type (e.g., 'fade', 'wipeleft', 'circlecrop')
        resolution: Output resolution as (width, height)
        fps: Frame rate

    Returns:
        Tuple of (filter_complex_string, final_output_stream_name)
    """
    width, height = resolution

    filters = []

    # Part 1: Scale and pad each image to uniform resolution
    for i in range(num_images):
        filter_chain = (
            f"[{i}:v]"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,"
            f"fps={fps}"
            f"[v{i}]"
        )
        filters.append(filter_chain)

    # Part 2: Chain xfade transitions between consecutive images
    if num_images == 1:
        # Single image, no transitions needed
        final_stream = "[v0]"
    else:
        # Calculate offsets and chain transitions
        # Offset for transition i = (i+1) * (duration_per_image - transition_duration)
        # This accounts for the overlapping nature of transitions
        for i in range(num_images - 1):
            # Calculate offset for this transition
            offset = (i + 1) * (duration_per_image - transition_duration)

            if i == 0:
                # First transition
                input_a = "[v0]"
                input_b = "[v1]"
                output = "[vx0]" if num_images > 2 else "[vout]"
            elif i == num_images - 2:
                # Last transition
                input_a = f"[vx{i-1}]"
                input_b = f"[v{i+1}]"
                output = "[vout]"
            else:
                # Middle transitions
                input_a = f"[vx{i-1}]"
                input_b = f"[v{i+1}]"
                output = f"[vx{i}]"

            xfade_filter = (
                f"{input_a}{input_b}"
                f"xfade=transition={transition_type}:duration={transition_duration}:offset={offset}"
                f"{output}"
            )
            filters.append(xfade_filter)

        final_stream = "[vout]"

    filter_complex = ";".join(filters)

    return filter_complex, final_stream


def create_multi_image_video(
    image_directory='images',
    audio_path='background_music.mp3',
    output_path='output_multi.mp4',
    duration_per_image=3.5,
    transition_duration=1.0,
    transition_type='fade',
    resolution=(1920, 1080),
    fps=30,
    crf=18,
    preset='slow'
):
    """
    Create a video from multiple images with crossfade transitions and background music.

    Args:
        image_directory: Directory containing image files
        audio_path: Path to background music file
        output_path: Path for output video file
        duration_per_image: Display time per image in seconds
        transition_duration: Crossfade transition duration in seconds
        transition_type: xfade transition type (default: 'fade')
        resolution: Output resolution as (width, height)
        fps: Frame rate
        crf: Constant Rate Factor (0-51, lower = better quality, 18 = visually lossless)
        preset: Encoding preset (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)

    Raises:
        Various exceptions for validation failures or FFmpeg errors
    """
    print(f"Creating multi-image video...")
    print(f"  Image directory: {image_directory}")
    print(f"  Audio file: {audio_path}")
    print(f"  Output: {output_path}")

    # Validate transition type
    if transition_type not in VALID_TRANSITIONS:
        print(f"\nWarning: '{transition_type}' is not a recognized transition type. Using 'fade' instead.")
        print(f"Valid transitions: {', '.join(VALID_TRANSITIONS[:10])}... (and {len(VALID_TRANSITIONS)-10} more)")
        transition_type = 'fade'

    # Step 1: Discover images
    print("\n[1/6] Discovering images...")
    image_files = get_image_files(image_directory)
    print(f"  Found {len(image_files)} images:")
    for i, img in enumerate(image_files, 1):
        print(f"    {i}. {os.path.basename(img)}")

    # Step 2: Calculate video duration
    print("\n[2/6] Calculating video duration...")
    video_duration = calculate_video_duration(len(image_files), duration_per_image, transition_duration)
    print(f"  Video duration: {video_duration:.2f} seconds")
    print(f"  ({len(image_files)} images × {duration_per_image}s - {len(image_files)-1} transitions × {transition_duration}s)")

    # Step 3: Check audio duration
    print("\n[3/6] Checking audio duration...")
    try:
        audio_duration = get_audio_duration(audio_path)
        print(f"  Audio duration: {audio_duration:.2f} seconds")
        if audio_duration < video_duration:
            print(f"  Audio will loop to match video duration")
        else:
            print(f"  Audio will be trimmed to match video duration")
    except Exception as e:
        print(f"  Warning: Could not get audio duration: {e}")
        print(f"  Continuing anyway...")

    # Step 4: Build filter complex
    print("\n[4/6] Building filter graph...")
    filter_complex, final_stream = build_filter_complex(
        len(image_files),
        duration_per_image,
        transition_duration,
        transition_type,
        resolution,
        fps
    )
    print(f"  Filter graph created ({len(image_files)} inputs, {len(image_files)-1} transitions)")

    # Step 5: Construct FFmpeg command
    print("\n[5/6] Constructing FFmpeg command...")
    command = ['ffmpeg', '-y']

    # Add image inputs (each with loop and full video duration)
    # All images need to be the full video duration for xfade to work correctly
    for image_file in image_files:
        command.extend([
            '-loop', '1',
            '-t', str(video_duration),
            '-i', image_file
        ])

    # Add audio input (with infinite loop)
    command.extend([
        '-stream_loop', '-1',
        '-i', audio_path
    ])

    # Add filter complex
    command.extend([
        '-filter_complex', filter_complex
    ])

    # Calculate audio fade-out start time (2 seconds before end)
    fade_start = max(0, video_duration - 2.0)

    # Map video output
    command.extend([
        '-map', final_stream
    ])

    # Add audio filter (fade out at the end)
    command.extend([
        '-af', f'afade=t=out:st={fade_start}:d=2'
    ])

    # Map audio (from the last input, which is the audio file)
    audio_input_index = len(image_files)
    command.extend([
        '-map', f'{audio_input_index}:a'
    ])

    # Video encoding options
    command.extend([
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', preset,
        '-pix_fmt', 'yuv420p'
    ])

    # Audio encoding options
    command.extend([
        '-c:a', 'aac',
        '-b:a', '192k'
    ])

    # Additional options
    command.extend([
        '-movflags', '+faststart',  # Optimize for web streaming
        '-t', str(video_duration)  # Trim output to exact video duration
    ])

    # Output file
    command.append(output_path)

    # Step 6: Execute FFmpeg command
    print("\n[6/6] Encoding video...")
    print(f"  This may take a while depending on number of images and preset...")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("\n✓ Video created successfully!")
        print(f"  Output saved to: {os.path.abspath(output_path)}")
        print(f"  Duration: {video_duration:.2f} seconds")
        print(f"  Resolution: {resolution[0]}×{resolution[1]}")
        print(f"  Frame rate: {fps} fps")

        # Get output file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # Convert to MB
            print(f"  File size: {file_size:.2f} MB")

    except subprocess.CalledProcessError as e:
        print("\n✗ Error creating video!")
        print(f"  FFmpeg error: {e.stderr}")
        raise


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
    # Parse command-line arguments
    args = parse_arguments()

    # Handle --list-transitions flag
    if args.list_transitions:
        list_transitions()
        sys.exit(0)

    # Parse resolution string (e.g., "1920x1080" -> (1920, 1080))
    try:
        width, height = map(int, args.resolution.lower().split('x'))
        resolution = (width, height)
    except ValueError:
        print(f"✗ Error: Invalid resolution format '{args.resolution}'. Use format: WIDTHxHEIGHT (e.g., 1920x1080)")
        sys.exit(1)

    print("=" * 60)
    print("Multi-Image Video Creator with Transitions")
    print("=" * 60)

    try:
        create_multi_image_video(
            image_directory=args.images,
            audio_path=args.audio,
            output_path=args.output,
            duration_per_image=args.duration,
            transition_duration=args.transition_duration,
            transition_type=args.transition,
            resolution=resolution,
            fps=args.fps,
            crf=args.crf,
            preset=args.preset
        )
        print("\n" + "=" * 60)
        print("Done!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
