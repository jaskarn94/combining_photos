# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python utility for creating videos from static images and audio files using ffmpeg. The script combines a single image with background music to generate a video file.

## System Requirements

- **ffmpeg**: Required for video generation. The script calls ffmpeg via subprocess.
  - Check if installed: `which ffmpeg`
  - Install on macOS: `brew install ffmpeg`

## Running the Script

```bash
python create_video.py
```

The script is currently configured to:
- Read from: `images/Screenshot 2026-02-11 at 11.04.59 PM.png`
- Use audio: `background_music.mp3`
- Output to: `output_programmatic.mp4`
- Duration: 10 seconds

## Architecture

**Single-file architecture**: All logic is in `create_video.py`

The script uses subprocess to execute ffmpeg with the following key parameters:
- `-loop 1`: Loops the input image
- `-t 10`: Sets video duration to 10 seconds
- `-c:v libx264`: Uses H.264 video codec
- `-pix_fmt yuv420p`: Ensures broad compatibility
- `-vf scale=trunc(iw/2)*2:trunc(ih/2)*2`: Forces even dimensions (required by H.264)
- `-c:a aac -b:a 192k`: Audio codec and bitrate

## Modifying Behavior

To change input/output paths or video parameters:
- Edit the constants at the top of `create_video.py` (image_path, audio_path, output_path)
- Modify the ffmpeg command array in the `create_video()` function to adjust video settings

## Generated Artifacts

The following files/directories are gitignored:
- `*.mp4` - Generated video files
- `images/` - Source images directory
- `background_music.mp3` - Audio source
- `waveform.png` - Audio visualization artifacts
