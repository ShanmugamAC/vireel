# backend/Dockerfile
#
# Multi-stage build for the Vireel backend.
#
# NOTE: the video pipeline shells out to external binaries (yt-dlp, ffmpeg),
# so this differs from the generic FastAPI Dockerfile in skills/DEPLOYMENT.md:
#   - ffmpeg is installed via apt-get in the final runtime stage (needed for
#     rendering/B-roll compositing).
#   - yt-dlp is a Python package already pinned in requirements.txt, so it is
#     installed as part of the pip install step and lands on PATH as a
#     console-script alongside uvicorn.

# ---- Stage 1: builder -------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Build-time OS deps needed to compile wheels (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install into /usr/local so it can be copied wholesale into the runtime
# stage below (keeps compilers/build headers out of the final image).
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: runtime ---------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime OS deps:
#   - ffmpeg: required by the render pipeline (trailer/summary compositing)
#   - libpq5: runtime Postgres client library for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Bring over installed Python packages + console scripts (uvicorn, yt-dlp)
# from the builder stage so PATH resolves them without recompiling.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./app ./app
COPY alembic.ini .
COPY ./alembic ./alembic

# Non-root user + media output directory (mounted as a volume in compose)
RUN useradd -m appuser \
    && mkdir -p /app/media \
    && chown -R appuser:appuser /app

USER appuser

# Confirm both external binaries resolve on PATH for the non-root user.
# Fails the build early if either is missing, rather than failing at
# render-time inside a running container.
RUN ffmpeg -version && yt-dlp --version

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
