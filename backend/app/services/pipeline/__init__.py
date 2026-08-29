"""Video pipeline stages: validate -> download -> extract_audio -> transcribe ->
analyze -> script -> render, orchestrated by `runner.run_pipeline`.

Each stage is a small, individually-testable function so a later test phase
can mock the external calls (yt-dlp, OpenAI, ffmpeg) in isolation.
"""
