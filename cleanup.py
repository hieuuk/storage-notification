import os
import time


def expand_path(path: str) -> str:
    """Expand ~ and environment variables in a path, cross-platform."""
    return os.path.normpath(os.path.expandvars(os.path.expanduser(path)))


def cleanup_folder(path: str, max_age_days: int, patterns: list[str],
                   max_file_size: int = 0) -> tuple[int, int]:
    """Delete files matching patterns that are older than max_age_days OR larger than max_file_size.

    Args:
        path: Folder to clean.
        max_age_days: Delete files older than this (0 to disable age check).
        patterns: Glob patterns to match filenames (empty = match all).
        max_file_size: Delete files larger than this in bytes (0 to disable size check).

    Returns (files_deleted, bytes_freed).
    """
    path = expand_path(path)
    if not os.path.isdir(path):
        return 0, 0

    cutoff = time.time() - (max_age_days * 86400) if max_age_days > 0 else 0
    files_deleted = 0
    bytes_freed = 0

    for dirpath, _dirnames, filenames in os.walk(path):
        for fname in filenames:
            if not _matches_any_pattern(fname, patterns):
                continue

            fpath = os.path.join(dirpath, fname)
            try:
                stat = os.stat(fpath)
                too_old = max_age_days > 0 and stat.st_mtime < cutoff
                too_big = max_file_size > 0 and stat.st_size >= max_file_size
                if too_old or too_big:
                    size = stat.st_size
                    os.remove(fpath)
                    files_deleted += 1
                    bytes_freed += size
            except OSError:
                pass

    # Remove empty directories left behind (bottom-up)
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        if dirpath == path:
            continue
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
        except OSError:
            pass

    return files_deleted, bytes_freed


def _matches_any_pattern(filename: str, patterns: list[str]) -> bool:
    """Check if filename matches any of the glob-style patterns."""
    if not patterns:
        return True
    import fnmatch
    return any(fnmatch.fnmatch(filename, p) for p in patterns)
