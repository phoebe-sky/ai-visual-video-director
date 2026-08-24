# Runtime Setup

The Skill uses an isolated runtime outside the installed Skill folder.

## Required
- Python 3.9+
- FFmpeg + ffprobe
- faster-whisper
- Pillow

## Check
```bash
python scripts/setup_runtime.py --check
```

## Install or repair
Only after the user confirms local dependency/model downloads:

```bash
python scripts/setup_runtime.py --install --confirm-local-downloads --model small
```

The setup script creates an isolated virtual environment and downloads the local Whisper model. It must not modify the user's global Python environment.

When system FFmpeg is absent, the setup can use the bundled static-ffmpeg Python package to obtain local executables.
