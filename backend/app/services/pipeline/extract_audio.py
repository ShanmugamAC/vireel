"""Stage: extract a mono 16kHz audio track from the downloaded video via ffmpeg.

`ffmpeg` is always invoked with an explicit argument list (never `shell=True`,
never a string-interpolated command) so a malicious/odd `video_path` cannot
result in shell injection.
"""

import subprocess
from pathlib import Path


def extract_audio(video_path: Path) -> Path:
    """Extract mono 16kHz PCM audio from `video_path` into a sibling .wav file.

    Returns the Path to the generated audio file. Raises
    `subprocess.CalledProcessError` if ffmpeg fails.
    """
    audio_path = video_path.with_name("audio.wav")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-acodec",
        "pcm_s16le",
        str(audio_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return audio_path
