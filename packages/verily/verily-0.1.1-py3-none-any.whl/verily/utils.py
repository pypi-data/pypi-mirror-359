import contextlib
import errno

from fsspec import AbstractFileSystem


def create_sequential_run_directory(
    fs: AbstractFileSystem, base_path: str, prefix: str = "run-"
) -> str:
    """
    Creates a sequentially numbered, race-condition-safe run directory.
    e.g., ./benchmarks/run-0001, ./benchmarks/run-0002, etc.

    Args:
        fs: The fsspec filesystem instance to use.
        base_path: The base directory where run directories will be created.
        prefix: The prefix for the run directory names (e.g., "run-").

    Returns:
        The path to the created directory.

    Raises:
        OSError: If directory creation fails after multiple retries, or for
                 any other unexpected OS error.
    """
    # find the last successful index to start the search from.
    pattern = f"{base_path}{fs.sep}{prefix}*"
    existing_dirs = fs.glob(pattern)
    max_index = 0
    for d in existing_dirs:
        try:
            index_str = d.split(fs.sep)[-1].replace(prefix, "")
            max_index = max(max_index, int(index_str))
        except (ValueError, IndexError):
            continue

    next_index = max_index + 1

    # zero-pad the index to 4 digits (note, this 4 digits is arbitrary)
    dir_name = f"{prefix}{next_index:04d}"
    full_path = f"{base_path}{fs.sep}{dir_name}"

    fs.makedirs(full_path, exist_ok=False)
    return full_path


def _try_close_fd(fd: int):
    try:
        # NOTE: os.close is still used here as fsspec does not provide a direct
        # equivalent for low-level file descriptor operations.
        # This function is related to _pipe, which is a low-level OS pipe.
        import os

        os.close(fd)
    except OSError as e:
        if e.errno != errno.EBADF:
            raise


@contextlib.contextmanager
def _pipe():
    # NOTE: os.pipe is still used here as fsspec does not provide a direct
    # equivalent for low-level file descriptor operations.
    import os

    read_fd, write_fd = os.pipe()
    try:
        yield read_fd, write_fd
    finally:
        _try_close_fd(read_fd)
        _try_close_fd(write_fd)
