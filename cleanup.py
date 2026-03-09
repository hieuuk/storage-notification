import os
import time


def expand_path(path: str) -> str:
    """Expand ~ and environment variables in a path, cross-platform."""
    return os.path.normpath(os.path.expandvars(os.path.expanduser(path)))


def cleanup_folder(path: str, max_age_days: int, patterns: list[str]) -> tuple[int, int]:
    """Delete files matching patterns older than max_age_days.

    Returns (files_deleted, bytes_freed).
    """
    path = expand_path(path)
    if not os.path.isdir(path):
        return 0, 0

    cutoff = time.time() - (max_age_days * 86400)
    files_deleted = 0
    bytes_freed = 0

    for dirpath, _dirnames, filenames in os.walk(path):
        for fname in filenames:
            if not _matches_any_pattern(fname, patterns):
                continue

            fpath = os.path.join(dirpath, fname)
            try:
                stat = os.stat(fpath)
                if stat.st_mtime < cutoff:
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
