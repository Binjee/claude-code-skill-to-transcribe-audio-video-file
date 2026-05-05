# Video & Audio Transcription in Claude Code

A step-by-step guide to setting up local video and audio transcription using the Video Input skill and whisper.cpp in Claude Code. (I have used this skill to convert instruction video to step by step guide document)

---

## Overview

This guide walks you through adding transcription capabilities to Claude Code using **whisper.cpp** (a lightweight, open-source speech-to-text engine) and the **Video Input skill** (a Claude Code skill that automates frame extraction, transcription, and content analysis).

Once set up, you can ask Claude Code to transcribe and analyze any local video or audio file — entirely offline, with no API costs.

### What You'll Be Able to Do

- Transcribe local video files (MP4, MOV, etc.) into timestamped text
- Transcribe audio files (MP3, WAV, M4A)
- Extract video frames and match them with spoken content
- Generate comprehensive markdown summaries of video content

### Architecture

```
Video/Audio File
       │
       ▼
   ┌────────┐
   │ ffmpeg  │──── Extracts audio (WAV) + video frames (PNG)
   └────────┘
       │
       ▼
 ┌────────────┐
 │ whisper.cpp │──── Transcribes audio to timestamped text (SRT)
 └────────────┘
       │
       ▼
 ┌─────────────────┐
 │ Video Input Skill│──── Matches frames ↔ transcript, generates summary
 └─────────────────┘
       │
       ▼
   analysis.md + transcription.srt + frames/
```

---

## Prerequisites

- **macOS** (Apple Silicon or Intel)
- **Terminal** access
- **Claude Code** installed (command-line tool by Anthropic)
- ~2 GB of free disk space (for models and temporary files)

---

## Step 1: Install Homebrew

Homebrew is the package manager for macOS. If you already have it, skip to Step 2.

Open Terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Enter your Mac password when prompted (characters won't appear as you type — this is normal).

After installation, add Homebrew to your PATH.

**For Apple Silicon Macs (M1/M2/M3/M4):**

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**For Intel Macs:**

```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

To check which Mac you have: Apple menu → About This Mac → look for "Chip."

**Verify installation:**

```bash
brew --version
```

---

## Step 2: Install ffmpeg

ffmpeg is a multimedia toolkit used to extract audio and video frames from files.

```bash
brew install ffmpeg
```

**Verify installation:**

```bash
ffmpeg -version
ffprobe -version
```

Both commands should return version information.

---

## Step 3: Install whisper.cpp

whisper.cpp is a C++ implementation of OpenAI's Whisper speech recognition model. It runs entirely on your machine — no internet or API key required.

```bash
brew install whisper-cpp
```

**Verify installation:**

```bash
which whisper-cli || which whisper-cpp || which whisper
```

This should return a file path confirming the tool is installed.

---

## Step 4: Download a Whisper Model

whisper.cpp needs a pre-trained model file to perform transcription. Models vary in size and accuracy.

**Create the model directory:**

```bash
mkdir -p ~/.cache/whisper
```

**Download the medium English model (recommended):**

```bash
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin" \
  -o ~/.cache/whisper/ggml-medium.bin
```

**Optional — download the base model for faster (but less accurate) transcription:**

```bash
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" \
  -o ~/.cache/whisper/ggml-base.bin
```

### Model Comparison

| Model  | Size    | Speed       | Accuracy   | Best For                        |
|--------|---------|-------------|------------|---------------------------------|
| base   | ~148 MB | Fast        | Good       | Quick tests, clear audio        |
| medium | ~1.5 GB | Moderate    | Very Good  | General use (recommended)       |
| large  | ~3.1 GB | Slow        | Excellent  | Noisy audio, multiple languages |

You can keep multiple models installed simultaneously — they don't conflict.

**Verify the model file exists:**

```bash
ls -lh ~/.cache/whisper/
```

---

## Step 5: Install the Video Input Skill

The Video Input skill teaches Claude Code how to process video files by orchestrating ffmpeg and whisper.cpp.

**Create the skill directory:**

```bash
mkdir -p ~/.claude/skills/video-input
```

**Download the skill files:**

```bash
cd ~/.claude/skills/video-input

# Download SKILL.md (instructions for Claude Code)
curl -L "https://gist.github.com/msadig/b109ff286929b79c14a8480e9b848651/raw/SKILL.md" \
  -o SKILL.md

# Download the analysis script
curl -L "https://gist.github.com/msadig/b109ff286929b79c14a8480e9b848651/raw/analyze-video.sh" \
  -o analyze-video.sh

# Download the README
curl -L "https://gist.github.com/msadig/b109ff286929b79c14a8480e9b848651/raw/README.md" \
  -o README.md

# Make the script executable
chmod +x analyze-video.sh
```

**Verify the directory structure:**

```bash
ls -la ~/.claude/skills/video-input/
```

You should see:

```
├── SKILL.md
├── analyze-video.sh
└── README.md
```

---

## Step 6: Verify the Full Setup

Run through this checklist to confirm everything is ready:

```bash
# 1. ffmpeg installed?
ffmpeg -version

# 2. whisper installed?
which whisper-cli || which whisper-cpp || which whisper

# 3. Model file exists?
ls ~/.cache/whisper/ggml-medium.bin

# 4. Skill files in place?
ls ~/.claude/skills/video-input/SKILL.md

# 5. Script is executable?
ls -la ~/.claude/skills/video-input/analyze-video.sh
```

All five checks should pass before proceeding.

---

## Step 7: Test with a Video File

### Option A: Run the Script Directly

Navigate to your working directory and run:

```bash
cd ~/Documents

# Using the medium model at 1 frame per second
~/.claude/skills/video-input/analyze-video.sh /path/to/your/video.mp4 1 medium
```

**Script arguments:**

```
./analyze-video.sh <video-path> [fps] [whisper-model]
```

- `video-path` — full path to your video or audio file (required)
- `fps` — frames extracted per second, default: 1 (optional)
- `whisper-model` — model name: base, medium, or large, default: base (optional)

### Option B: Use Claude Code (Recommended)

Open Claude Code in your terminal:

```bash
claude
```

Then ask naturally:

```
Analyze this video: /path/to/your/video.mp4
```

Or be more specific:

```
Transcribe this file: /path/to/meeting-recording.mov
```

```
Extract the main points from this tutorial: /path/to/tutorial.mp4
```

Claude Code will automatically detect the Video Input skill and run the full pipeline.

---

## Step 8: Review the Output

After processing, the script creates a timestamped folder:

```
.video-input/analysis_{timestamp}/
├── video_file.mp4                  # Copy of original video
├── audio.wav                       # Extracted audio (16kHz mono)
├── transcription.srt               # Full timestamped transcript
├── frame_transcription_map.txt     # Frame-to-transcript correlation
├── frames/                         # Extracted video frames
│   ├── frame_0001.png
│   ├── frame_0002.png
│   └── ...
├── metadata.txt                    # Video duration, resolution, format
├── analysis.md                     # Comprehensive summary
└── .completed                      # Completion marker
```

**View the analysis summary:**

```bash
cat .video-input/analysis_*/analysis.md
```

**View the full transcript:**

```bash
cat .video-input/analysis_*/transcription.srt
```

**View frame-to-transcript mapping:**

```bash
cat .video-input/analysis_*/frame_transcription_map.txt
```

---

## Supported File Formats

| Type  | Formats                        |
|-------|--------------------------------|
| Video | MP4, MOV, AVI, MKV, WebM      |
| Audio | MP3, WAV, M4A, FLAC, OGG, AAC |

Note: Audio files will skip the frame extraction step and go straight to transcription.

---

## Tips for Best Results

1. **Start small** — test with a 1–2 minute video first to verify the pipeline works.
2. **Audio quality matters** — clearer audio produces better transcripts. Background noise reduces accuracy.
3. **Adjust FPS to content type:**
   - 1 fps for lectures, presentations, and talking-head videos
   - 2+ fps for screen recordings or fast-moving visual content
4. **Use the medium model** for most work. Fall back to base for quick drafts.
5. **Clean up old analyses** periodically — frame extraction uses significant disk space:
   ```bash
   rm -rf .video-input/analysis_*/
   ```
6. **Apple Silicon acceleration** — if you're on an M-series Mac, whisper.cpp automatically uses Metal GPU acceleration for faster processing.

---

## Troubleshooting

### "command not found: brew"
Homebrew isn't installed or not in your PATH. Re-run Step 1 and make sure you complete the PATH setup for your Mac type.

### "whisper not found"
Try all three possible command names:
```bash
which whisper-cli
which whisper-cpp
which whisper
```
If none work, reinstall: `brew install whisper-cpp`

### "Whisper model not found"
Verify the model file is in the expected location:
```bash
ls ~/.cache/whisper/
```
If empty, re-download the model from Step 4.

### Transcription is inaccurate
- Try a larger model (medium or large instead of base)
- Check that the source audio is clear
- Ensure audio is extracted at 16kHz mono (the script handles this automatically)

### Script hangs or is very slow
- Long videos take time — a 60-minute video can take 10–20 minutes to process depending on your hardware
- Use the base model for faster processing during testing
- Check available disk space: `df -h`

### "No audio stream found in video"
The video file has no audio track. The script will still extract frames but will skip transcription.

---

## Uninstalling

If you ever need to remove the setup:

```bash
# Remove the skill
rm -rf ~/.claude/skills/video-input

# Remove whisper models
rm -rf ~/.cache/whisper

# Uninstall whisper.cpp
brew uninstall whisper-cpp

# Uninstall ffmpeg (only if no other tools depend on it)
brew uninstall ffmpeg
```

---

## References

- [whisper.cpp GitHub Repository](https://github.com/ggml-org/whisper.cpp)
- [Video Input Skill (GitHub Gist)](https://gist.github.com/msadig/b109ff286929b79c14a8480e9b848651)
- [Claude Code Documentation](https://docs.claude.com)
- [Anthropic Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)

---

*Last updated: April 2026*
