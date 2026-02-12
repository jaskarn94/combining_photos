# Multi-Image Video Creator with Transitions

A Python utility for creating professional slideshow videos from multiple images with smooth transitions and background music using FFmpeg. Perfect for creating photo montages, presentations, or social media content.

## Features

- 🎬 **Automatic Image Discovery** - Automatically finds all images in a directory
- 🎨 **44+ Transition Effects** - Choose from fade, wipe, slide, zoom, and many more
- 🎵 **Background Music** - Add looping background music with automatic fade-out
- 📐 **Smart Aspect Ratio** - Maintains image aspect ratios with letterboxing
- ⚙️ **Highly Configurable** - Customize timing, quality, resolution, and more
- 🎥 **Professional Quality** - Outputs broadcast-quality 1080p video at 30fps

## Quick Start

### Prerequisites

**FFmpeg is required.** Check if installed:
```bash
which ffmpeg
```

If not installed:
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Basic Usage

1. **Add your images** to the `images/` directory (JPG, JPEG, or PNG)

2. **Add background music** as `background_music.mp3` (or update the path in the script)

3. **Run the script:**
   ```bash
   python3 create_video.py
   ```

4. **Output:** Your video will be saved as `output_multi.mp4`

That's it! The script uses sensible defaults to create a professional slideshow.

## Command-Line Usage

The script supports command-line arguments for easy customization without editing code.

### Quick Examples

```bash
# Use default settings (fade transition)
python3 create_video.py

# List all available transitions
python3 create_video.py -l

# Use a specific transition
python3 create_video.py -t circlecrop

# Customize multiple parameters
python3 create_video.py -t wipeleft -d 5.0 -o my_video.mp4

# Fast encoding for testing
python3 create_video.py -t smoothright --crf 23 --preset fast
```

### Available Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--transition` | `-t` | Transition type | `fade` |
| `--list-transitions` | `-l` | List all transitions and exit | - |
| `--images` | `-i` | Images directory | `images` |
| `--audio` | `-a` | Background music file | `background_music.mp3` |
| `--output` | `-o` | Output video file | `output_multi.mp4` |
| `--duration` | `-d` | Duration per image (seconds) | `3.5` |
| `--transition-duration` | - | Transition length (seconds) | `1.0` |
| `--resolution` | `-r` | Output resolution (WIDTHxHEIGHT) | `1920x1080` |
| `--fps` | - | Frame rate | `30` |
| `--crf` | - | Quality (0-51, lower=better) | `18` |
| `--preset` | - | Encoding speed | `slow` |
| `--help` | `-h` | Show help message | - |

### Command-Line Examples

**Professional portfolio with dissolve transitions:**
```bash
python3 create_video.py -t dissolve -d 5.0 -o portfolio.mp4
```

**Quick social media video:**
```bash
python3 create_video.py -t smoothright -d 2.0 -r 1080x1080 --crf 23 --preset fast
```

**4K presentation:**
```bash
python3 create_video.py -t fade -r 3840x2160 -d 6.0 --preset slower
```

**Custom paths:**
```bash
python3 create_video.py -i vacation_photos -a upbeat.mp3 -o vacation.mp4
```

**List all transitions before choosing:**
```bash
python3 create_video.py -l
# Then pick one:
python3 create_video.py -t circlecrop
```

## Example Output

For **9 images**, the script automatically creates:
- **Duration:** 23.5 seconds (3.5s per image with 1s transitions)
- **Resolution:** 1920×1080 (Full HD)
- **Frame Rate:** 30 fps
- **Transitions:** 8 smooth crossfades between images
- **File Size:** ~5-6 MB (high quality)

## Configuration Options

### Overview

You can configure the video creation in two ways:
1. **Command-line arguments** (recommended) - See [Command-Line Usage](#command-line-usage) above
2. **Python function calls** - For programmatic use or scripting

### All Available Parameters

When using the script programmatically, call `create_multi_image_video()` in your Python code:

```python
create_multi_image_video(
    image_directory='images',           # Directory containing images
    audio_path='background_music.mp3',  # Background music file
    output_path='output_multi.mp4',     # Output video filename
    duration_per_image=3.5,             # Seconds each image displays
    transition_duration=1.0,            # Transition length in seconds
    transition_type='fade',             # Transition effect (see below)
    resolution=(1920, 1080),            # Output resolution (width, height)
    fps=30,                             # Frame rate
    crf=18,                             # Quality (lower = better, 0-51)
    preset='slow'                       # Encoding speed vs quality
)
```

### Parameter Details

#### `image_directory` (string)
Path to directory containing images. Supports JPG, JPEG, and PNG files.
- **Default:** `'images'`
- **Example:** `'my_photos'` or `'/path/to/photos'`

#### `audio_path` (string)
Path to background music file. Audio will loop if video is longer than the audio file.
- **Default:** `'background_music.mp3'`
- **Formats:** MP3, WAV, AAC, or any FFmpeg-supported audio format

#### `output_path` (string)
Output video filename.
- **Default:** `'output_multi.mp4'`
- **Example:** `'vacation_slideshow.mp4'`

#### `duration_per_image` (float)
How long each image displays in seconds.
- **Default:** `3.5` seconds
- **Range:** Must be greater than `transition_duration`
- **Examples:**
  - `2.0` - Fast-paced slideshow
  - `5.0` - Relaxed viewing pace
  - `7.0` - Slow, contemplative pace

#### `transition_duration` (float)
Length of transition effect between images in seconds.
- **Default:** `1.0` second
- **Range:** Must be less than `duration_per_image`
- **Examples:**
  - `0.5` - Quick, snappy transitions
  - `1.5` - Longer, more dramatic transitions
  - `2.0` - Very slow, artistic transitions

**Duration Calculation:**
```
Total Duration = (num_images × duration_per_image) - ((num_images - 1) × transition_duration)
```

#### `transition_type` (string)
Visual transition effect between images. Choose from 44+ options!
- **Default:** `'fade'`
- **See:** [Transition Types Guide](#transition-types) below

#### `resolution` (tuple)
Output video resolution as `(width, height)`.
- **Default:** `(1920, 1080)` - Full HD
- **Common Options:**
  - `(1280, 720)` - 720p HD
  - `(3840, 2160)` - 4K Ultra HD
  - `(1080, 1920)` - Vertical (Instagram Stories, TikTok)
  - `(1080, 1080)` - Square (Instagram Feed)

Images are automatically letterboxed to maintain aspect ratio.

#### `fps` (integer)
Frame rate (frames per second).
- **Default:** `30`
- **Options:**
  - `24` - Cinematic film look
  - `30` - Standard video (recommended)
  - `60` - Smooth, high-motion

#### `crf` (integer)
Constant Rate Factor - controls video quality.
- **Default:** `18` (visually lossless)
- **Range:** 0-51 (lower = better quality, larger file)
- **Guide:**
  - `0-17` - Visually lossless (very large files)
  - `18-23` - High quality (recommended, 18 is excellent)
  - `24-28` - Good quality (smaller files)
  - `29-51` - Lower quality (not recommended)

#### `preset` (string)
Encoding speed vs compression efficiency.
- **Default:** `'slow'` (best quality-to-size ratio)
- **Options:** `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`
- **Trade-off:**
  - Slower presets = longer encoding time but better quality/smaller files
  - Faster presets = quick encoding but larger files
- **Recommendation:** Use `slow` or `slower` for final output

## Transition Types

The `transition_type` parameter supports 44+ visual effects:

### Professional & Subtle
Best for business presentations, portfolios, or elegant slideshows.
```python
transition_type='fade'          # Smooth fade (default)
transition_type='dissolve'      # Cross-dissolve
transition_type='fadeblack'     # Fade through black
transition_type='fadewhite'     # Fade through white
transition_type='fadegrays'     # Fade through gray scale
```

### Dynamic & Energetic
Great for travel videos, action shots, or modern content.
```python
transition_type='wipeleft'      # Wipe from left to right
transition_type='wiperight'     # Wipe from right to left
transition_type='wipeup'        # Wipe from bottom to top
transition_type='wipedown'      # Wipe from top to bottom
transition_type='slideleft'     # Slide left
transition_type='slideright'    # Slide right
transition_type='slideup'       # Slide up
transition_type='slidedown'     # Slide down
```

### Geometric & Creative
Perfect for artistic projects, music videos, or creative content.
```python
transition_type='circlecrop'    # Circular crop transition
transition_type='circleopen'    # Circle opens to reveal
transition_type='circleclose'   # Circle closes
transition_type='rectcrop'      # Rectangular crop
transition_type='radial'        # Radial wipe
```

### Modern & Smooth
Excellent for contemporary videos, vlogs, or social media.
```python
transition_type='smoothleft'    # Smooth slide left
transition_type='smoothright'   # Smooth slide right
transition_type='smoothup'      # Smooth slide up
transition_type='smoothdown'    # Smooth slide down
```

### Special Effects
Fun for creative projects, experimental videos, or standout content.
```python
transition_type='pixelize'      # Pixelization effect
transition_type='zoomin'        # Zoom in effect
transition_type='distance'      # Distance transformation
transition_type='hblur'         # Horizontal blur
transition_type='squeezeh'      # Horizontal squeeze
transition_type='squeezev'      # Vertical squeeze
```

### Complete List
All 44 available transitions:
```
fade, fadeblack, fadewhite, dissolve, fadegrays,
wipeleft, wiperight, wipeup, wipedown, wipetl, wipetr, wipebl, wipebr,
slideleft, slideright, slideup, slidedown,
coverleft, coverright, coverup, coverdown,
revealleft, revealright, revealup, revealdown,
circlecrop, rectcrop, radial,
circleopen, circleclose, vertopen, vertclose, horzopen, horzclose,
hlslice, hrslice, vuslice, vdslice,
smoothleft, smoothright, smoothup, smoothdown,
diagtl, diagtr, diagbl, diagbr,
pixelize, distance, hblur, squeezeh, squeezev, zoomin,
hlwind, hrwind, vuwind, vdwind,
custom
```

**Invalid transitions** automatically fallback to `fade` with a warning.

## Usage Examples

### Example 1: Quick Social Media Video
```python
create_multi_image_video(
    image_directory='vacation_photos',
    audio_path='upbeat_music.mp3',
    output_path='instagram_post.mp4',
    duration_per_image=2.0,      # Fast pace
    transition_duration=0.5,      # Quick transitions
    transition_type='smoothright',
    resolution=(1080, 1080),      # Square format
    crf=23,                       # Smaller file size
    preset='medium'               # Faster encoding
)
```

### Example 2: Professional Portfolio
```python
create_multi_image_video(
    image_directory='portfolio',
    audio_path='classical.mp3',
    output_path='portfolio_2024.mp4',
    duration_per_image=5.0,       # Slow, elegant pace
    transition_duration=1.5,       # Smooth transitions
    transition_type='dissolve',
    resolution=(1920, 1080),       # Full HD
    crf=18,                        # High quality
    preset='slow'                  # Best quality
)
```

### Example 3: Creative Photo Montage
```python
create_multi_image_video(
    image_directory='art_photos',
    audio_path='ambient.mp3',
    output_path='art_montage.mp4',
    duration_per_image=4.0,
    transition_duration=2.0,       # Long, artistic transitions
    transition_type='circlecrop',
    resolution=(1920, 1080),
    crf=18,
    preset='slow'
)
```

### Example 4: 4K Presentation
```python
create_multi_image_video(
    image_directory='conference_slides',
    audio_path='presentation_music.mp3',
    output_path='conference_video_4k.mp4',
    duration_per_image=6.0,        # Time to read slides
    transition_duration=0.8,
    transition_type='fade',
    resolution=(3840, 2160),       # 4K resolution
    fps=24,                        # Cinematic frame rate
    crf=18,
    preset='slower'                # Best compression for 4K
)
```

## Project Structure

```
combining_photos/
├── create_video.py           # Main script
├── background_music.mp3      # Your background music
├── images/                   # Put your images here (JPG, JPEG, PNG)
│   ├── photo1.jpg
│   ├── photo2.png
│   └── ...
├── output_multi.mp4          # Generated video (created by script)
├── README.md                 # This file
└── CLAUDE.md                 # Development documentation
```

**Note:** The `images/` directory and `*.mp4` files are gitignored for privacy.

## How It Works

The script follows these steps:

1. **Image Discovery** - Scans the specified directory for image files
2. **Duration Calculation** - Calculates total video duration based on number of images and timing parameters
3. **Audio Handling** - Verifies audio file and prepares it for looping
4. **Filter Graph Creation** - Builds FFmpeg filter chain with:
   - Image scaling and padding (letterboxing)
   - Frame rate normalization
   - Transition effects between images
5. **Video Encoding** - Constructs and executes FFmpeg command with:
   - H.264 video codec (high compatibility)
   - AAC audio codec
   - Audio fade-out at the end
   - Web optimization for streaming
6. **Output** - Saves the final video file

## Troubleshooting

### "ffmpeg: command not found"
FFmpeg is not installed. See [Prerequisites](#prerequisites) section.

### "Found 0 image(s) in 'images'"
No images found in the directory. Check:
- Images are in the correct directory
- Files have valid extensions: `.jpg`, `.jpeg`, `.png` (case-insensitive)
- You're running the script from the correct location

### "At least 2 images are required for transitions"
You need at least 2 images to create transitions. Add more images to the directory.

### "Could not get audio duration"
Audio file is missing or invalid. Check:
- `background_music.mp3` exists in the project directory
- File is a valid audio format
- Path in script matches actual filename

### Video is too short/long
Adjust `duration_per_image` and `transition_duration` parameters. Remember:
```
Total = (images × duration_per_image) - ((images - 1) × transition_duration)
```

### Large file size
Reduce file size by:
- Increasing `crf` value (try 23 or 28)
- Using faster `preset` (try 'medium' or 'fast')
- Reducing `resolution` (try 1280×720)
- Lowering `fps` (try 24)

### Slow encoding
Speed up encoding by:
- Using faster `preset` ('medium', 'fast', or 'faster')
- Lowering `resolution`
- Reducing number of images

### Images look stretched/distorted
This shouldn't happen - images are automatically letterboxed. If it does:
- Check source image quality
- Verify `resolution` parameter is set correctly
- Images might have unusual aspect ratios

## Advanced Usage

### Using as a Python Module

You can import and use the function in your own scripts:

```python
from create_video import create_multi_image_video

# Use in your code
create_multi_image_video(
    image_directory='my_images',
    audio_path='my_music.mp3',
    output_path='my_output.mp4',
    transition_type='wipeleft'
)
```

### Batch Processing Multiple Folders

```python
import os
from create_video import create_multi_image_video

folders = ['vacation1', 'vacation2', 'vacation3']

for folder in folders:
    create_multi_image_video(
        image_directory=folder,
        audio_path='music.mp3',
        output_path=f'{folder}_video.mp4',
        transition_type='fade'
    )
```

### Dynamic Transition Selection

```python
import random
from create_video import create_multi_image_video, VALID_TRANSITIONS

# Choose a random professional transition
professional = ['fade', 'dissolve', 'fadewhite', 'fadeblack']
transition = random.choice(professional)

create_multi_image_video(
    image_directory='images',
    audio_path='music.mp3',
    output_path='output.mp4',
    transition_type=transition
)
```

## Tips & Best Practices

### Image Quality
- Use high-resolution images (at least 1920×1080 for Full HD output)
- Consistent aspect ratios look more professional
- Consider cropping or editing images before adding them

### Music Selection
- Match music tempo to `duration_per_image` and `transition_duration`
- Upbeat music works well with faster transitions
- Ambient/classical music suits slower, elegant transitions
- Audio automatically fades out at the end (2 seconds)

### Transition Selection
- **Consistency:** Use the same transition throughout for professional look
- **Purpose:** Match transition to content mood
- **Subtlety:** Simpler transitions ('fade', 'dissolve') work for most cases
- **Creativity:** Experiment with special effects for artistic projects

### Performance
- First run may be slow while FFmpeg processes
- Use `preset='medium'` for testing, `'slow'` or `'slower'` for final output
- Large resolutions (4K) take significantly longer to encode
- Consider using `crf=23` instead of `18` for faster encoding with minimal quality loss

### File Management
- Organize images by renaming them (e.g., `01_photo.jpg`, `02_photo.jpg`)
- Images are processed in alphabetical order
- Remove unwanted images from the directory before running
- Keep a backup of original images

## Requirements

- **Python 3.6+** (uses f-strings)
- **FFmpeg** (with libx264 and libfdk-aac or standard AAC support)
- **Standard library only** - no additional Python packages needed!

## License

This project is provided as-is for educational and personal use.

## Contributing

Found a bug or have a feature request? Please open an issue on the project repository.

## Support

For questions or help:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Configuration Options](#configuration-options)
3. Try the [Usage Examples](#usage-examples)

## Credits

Built with:
- **FFmpeg** - The leading multimedia framework
- **Python** - For easy scripting and automation
- **xfade filter** - For smooth video transitions

---

**Enjoy creating beautiful video slideshows!** 🎬✨
