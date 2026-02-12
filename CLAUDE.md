# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python utility for creating professional slideshow videos from multiple images with smooth crossfade transitions and background music using ffmpeg. The script automatically discovers images in a directory, combines them with transitions, and adds looping background music to create polished video output.

## System Requirements

- **ffmpeg**: Required for video generation. The script calls ffmpeg via subprocess.
  - Check if installed: `which ffmpeg`
  - Install on macOS: `brew install ffmpeg`

## Running the Script

```bash
python3 create_video.py
```

The script automatically:
- **Auto-discovers** all images (JPG, JPEG, PNG) in the `images/` directory
- **Calculates duration** based on number of images (3.5s per image with 1s transitions)
- **Adds background music** from `background_music.mp3` (loops if needed)
- **Outputs** to `output_multi.mp4`

**Example output for 9 images:**
- Duration: 23.5 seconds
- Resolution: 1920×1080 (Full HD)
- Frame rate: 30 fps
- 8 smooth crossfade transitions

## Architecture

**Single-file architecture**: All logic is in `create_video.py`

### Main Functions

1. **`create_multi_image_video()`** - Primary function (default)
   - Auto-discovers images from directory
   - Calculates video duration: `(num_images × 3.5s) - ((num_images - 1) × 1.0s)`
   - Builds complex FFmpeg filter graph for transitions
   - Supports customizable parameters (duration, transitions, quality)

2. **`create_video()`** - Legacy single-image function (preserved for backward compatibility)

### Helper Functions

- **`get_image_files(directory)`** - Scans for JPG/JPEG/PNG files (case-insensitive)
- **`calculate_video_duration()`** - Computes duration with overlapping transitions
- **`get_audio_duration()`** - Uses ffprobe to extract audio length
- **`build_filter_complex()`** - Generates FFmpeg filter graph with:
  - Uniform scaling and padding (1920×1080 with letterboxing)
  - xfade crossfade transitions
  - 30 fps frame rate normalization

### FFmpeg Command Structure

The script constructs complex FFmpeg commands with:
- **Multiple image inputs**: Each image looped to full video duration
- **Audio looping**: `-stream_loop -1` for infinite audio loop
- **Filter complex**: Scale → Pad → FPS → xfade transitions
- **Video codec**: H.264 with CRF 18 (visually lossless quality)
- **Audio codec**: AAC at 192k bitrate
- **Audio fade-out**: 2-second fade at end of video
- **Web optimization**: `-movflags +faststart` for streaming
- **Duration trimming**: `-t <duration>` to exact length

### Transition Mechanics

- **Offset calculation**: `(i + 1) × (duration_per_image - transition_duration)`
- **xfade filter**: Handles smooth crossfading between consecutive images
- Each transition overlaps by 1 second, creating seamless flow

## Modifying Behavior

### Default Configuration

The script uses these defaults (configurable via function parameters):

```python
create_multi_image_video(
    image_directory='images',
    audio_path='background_music.mp3',
    output_path='output_multi.mp4',
    duration_per_image=3.5,        # Display time per image
    transition_duration=1.0,        # Crossfade duration
    resolution=(1920, 1080),        # Full HD
    fps=30,                         # Frame rate
    crf=18,                         # Quality (lower = better)
    preset='slow'                   # Encoding speed (slower = better quality)
)
```

### Customization Options

**To change paths**: Edit the hardcoded values in the `if __name__ == "__main__"` block

**To adjust timing**:
- `duration_per_image`: How long each image displays (default: 3.5s)
- `transition_duration`: How long the crossfade lasts (default: 1.0s)
- Must satisfy: `transition_duration < duration_per_image`

**To modify quality**:
- `crf`: 0-51, where 18 = visually lossless, 23 = default, 28 = acceptable
- `preset`: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow

**To change resolution**:
- `resolution=(width, height)`: Any standard resolution (e.g., (1280, 720) for 720p)
- Images are automatically letterboxed to maintain aspect ratio

## Generated Artifacts

The following files/directories are gitignored:
- `*.mp4` - Generated video files (e.g., `output_multi.mp4`)
- `images/` - Source images directory (keep images private)
- `waveform.png` - Audio visualization artifacts
- `__pycache__/` - Python bytecode cache
- `.DS_Store` - macOS system files

**Note**: `background_music.mp3` is committed to the repository for portability.

## Error Handling

The script provides clear error messages for common issues:
- **No images found**: "Found 0 image(s) in 'directory'. At least 2 images are required for transitions."
- **Directory doesn't exist**: "Images directory 'directory' does not exist"
- **Missing audio file**: Continues with warning (FFmpeg will fail gracefully)
- **Invalid parameters**: Validates `transition_duration < duration_per_image`

## Output Quality

Default settings produce:
- **High-quality video**: CRF 18 (visually lossless)
- **Smooth transitions**: 30 fps ensures fluid crossfades
- **Professional look**: Letterboxing maintains aspect ratios
- **Web-optimized**: Fast-start enabled for streaming
- **Small file size**: ~5-6 MB for 23.5s video at 1080p
