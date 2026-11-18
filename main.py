#!/usr/bin/env python3
"""Copy the bundled news image to the output directory.

Entry for make.fun competition news-image-20261117:
"Sum up 17 November's world news in one image".

The image is shipped in this repository as entry.png (JPEG bytes in a
file named entry.png, which the competition rules allow: the format is
told apart by the file's first bytes, not its name). This program only
copies it to the output directory, deterministically, with no network
access and no dependencies beyond the Python standard library.

Output directory: the MAKEFUN_OUTPUT_DIR environment variable, or
/output when it is not set.
"""

import hashlib
import os
import sys

CHUNK_SIZE = 65536
JPEG_SOI = b"\xff\xd8"  # JPEG start-of-image marker
JPEG_EOI = b"\xff\xd9"  # JPEG end-of-image marker


def source_path():
    """Absolute path of the image shipped next to this program."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def sha256_of(path):
    """SHA-256 hex digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_image(path):
    """Check that a file is a whole JPEG image; return (size, sha256).

    Raises ValueError with a clear message when the file is missing,
    empty, or does not start and end with the JPEG markers.
    """
    if not os.path.isfile(path):
        raise ValueError("image file not found: %s" % path)
    size = os.path.getsize(path)
    if size == 0:
        raise ValueError("image file is empty: %s" % path)
    if size < 2:
        raise ValueError("image file too small to hold JPEG markers: %s"
                         % path)
    with open(path, "rb") as handle:
        head = handle.read(2)
        handle.seek(-2, os.SEEK_END)
        tail = handle.read(2)
    if head != JPEG_SOI:
        raise ValueError(
            "image does not start with the JPEG SOI marker: %s" % path
        )
    if tail != JPEG_EOI:
        raise ValueError(
            "image does not end with the JPEG EOI marker: %s" % path
        )
    return size, sha256_of(path)


def copy_file(source, destination):
    """Copy a file in fixed-size chunks."""
    with open(source, "rb") as src, open(destination, "wb") as dst:
        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            dst.write(chunk)


def main():
    source = source_path()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    destination = os.path.join(out_dir, "entry.png")

    try:
        src_size, src_sha256 = verify_image(source)
    except (OSError, ValueError) as exc:
        print("error: cannot use source image: %s" % exc, file=sys.stderr)
        return 1

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print("error: cannot create output dir %s: %s" % (out_dir, exc),
              file=sys.stderr)
        return 1

    try:
        copy_file(source, destination)
    except OSError as exc:
        print("error: copy failed: %s" % exc, file=sys.stderr)
        return 1

    try:
        dst_size, dst_sha256 = verify_image(destination)
    except (OSError, ValueError) as exc:
        print("error: output image failed verification: %s" % exc,
              file=sys.stderr)
        return 1

    if dst_size != src_size or dst_sha256 != src_sha256:
        print("error: output differs from source "
              "(size %d vs %d, sha256 %s vs %s)"
              % (dst_size, src_size, dst_sha256, src_sha256),
              file=sys.stderr)
        return 1

    print("wrote %s (%d bytes, sha256 %s)"
          % (destination, dst_size, dst_sha256))
    return 0


if __name__ == "__main__":
    sys.exit(main())
