"""Source URL validation — the sole gate between user input and subprocesses.

Every downstream stage (yt-dlp, ffmpeg) ultimately consumes the value returned
by `validate_source_url`. Keep this strict: only http(s) URLs on an allowed
video-platform host are let through.

SECURITY: `source_url` is fetched server-side by yt-dlp (`download.py`), which
can invoke a generic page-scraping extractor for any host that doesn't match a
known site. Without a host allowlist, an authenticated user could point this
at an internal service or a cloud metadata endpoint (e.g.
`http://169.254.169.254/...`) and read back fragments of the response via
`Project.error_message`, i.e. SSRF. Restricting to a small set of known video
platforms (the only thing this product actually needs to support) closes that
off entirely, rather than trying to IP-filter around DNS rebinding.
"""

from urllib.parse import urlparse

from app.exceptions import ValidationError

_ALLOWED_SCHEMES = {"http", "https"}

# Known video-hosting platforms this product supports. Add new platforms here
# deliberately — do not widen this to a denylist/IP-range check instead, since
# yt-dlp's generic extractor makes any other host an SSRF vector.
_ALLOWED_HOST_SUFFIXES = (
    "youtube.com",
    "youtu.be",
    "vimeo.com",
    "dailymotion.com",
)


def _host_is_allowed(hostname: str) -> bool:
    hostname = hostname.lower().rstrip(".")
    return any(hostname == suffix or hostname.endswith(f".{suffix}") for suffix in _ALLOWED_HOST_SUFFIXES)


def validate_source_url(url: str) -> str:
    """Validate that `url` is a well-formed http(s) URL on an allowed video
    platform host, returning it unchanged.

    Raises `ValidationError` for anything else (empty string, other schemes
    such as `file://`, `javascript:`, malformed URLs, missing host, a host
    outside the supported platform allowlist, etc).
    """
    if not url or not isinstance(url, str):
        raise ValidationError("source_url must be a non-empty string")

    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise ValidationError(f"source_url could not be parsed: {exc}") from exc

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValidationError("source_url must use http or https")
    if not parsed.hostname:
        raise ValidationError("source_url must include a host")
    if not _host_is_allowed(parsed.hostname):
        raise ValidationError(
            "source_url must be a link from a supported platform "
            f"({', '.join(_ALLOWED_HOST_SUFFIXES)})"
        )

    return url
