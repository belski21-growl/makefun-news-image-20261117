#!/usr/bin/env python3
"""Ship the round-2 front page (entry.png) to the output directory.

make.fun competition news-image-20261117, round 2:
"Sum up 17 November's world news in one image".

The repository holds the finished image as entry.png. Although the
name says .png, the bytes are JPEG, which the competition rules allow:
the format is told apart by the file's first bytes, not its name.
This program's only job is to place an exact copy at
$MAKEFUN_OUTPUT_DIR/entry.png (default /output). It uses the Python
standard library only, performs no network access, and is fully
deterministic: two runs produce byte-identical output.

Safety: the source is authenticated before anything is written, and
the copy is authenticated again afterwards. Either check failing
aborts with a non-zero exit status and a message on stderr.
"""

import hashlib
import os
import sys

READ_SIZE = 1 << 16
JPEG_START = b"\xff\xd8"
JPEG_END = b"\xff\xd9"


class Fingerprint:
    """Size plus SHA-256 of one file, computed in a single stream."""

    def __init__(self, size, sha256):
        self.size = size
        self.sha256 = sha256

    def __eq__(self, other):
        return (isinstance(other, Fingerprint)
                and self.size == other.size
                and self.sha256 == other.sha256)

    def __repr__(self):
        return "Fingerprint(size=%d, sha256=%s)" % (self.size, self.sha256)


class ImageFile:
    """A JPEG file on disk, with whole-image authentication."""

    def __init__(self, path):
        self.path = path

    def fingerprint(self):
        """Return the file's Fingerprint, or raise ValueError.

        The file must exist, hold at least the two JPEG markers, and
        start with the SOI marker and end with the EOI marker. The
        digest covers every byte, so a truncated or altered file can
        never fingerprint the same as the shipped original.
        """
        try:
            handle = open(self.path, "rb")
        except OSError as exc:
            raise ValueError("cannot open %s: %s" % (self.path, exc))
        with handle:
            head = handle.read(len(JPEG_START))
            handle.seek(-len(JPEG_END), os.SEEK_END)
            tail = handle.read(len(JPEG_END))
            if head != JPEG_START:
                raise ValueError("%s is not a JPEG (bad SOI marker)"
                                 % self.path)
            if tail != JPEG_END:
                raise ValueError("%s is not a whole JPEG (bad EOI marker)"
                                 % self.path)
            handle.seek(0)
            digest = hashlib.sha256()
            total = 0
            while True:
                chunk = handle.read(READ_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                digest.update(chunk)
        if total < len(JPEG_START) + len(JPEG_END):
            raise ValueError("%s is too small to be a JPEG" % self.path)
        return Fingerprint(total, digest.hexdigest())

    def stream_into(self, destination):
        """Copy the file to destination, hashing as bytes flow through.

        Returns the Fingerprint of the bytes written, so the caller
        can compare it against the source fingerprint without a
        second read of either file.
        """
        digest = hashlib.sha256()
        total = 0
        with open(self.path, "rb") as reader, \
                open(destination, "wb") as writer:
            while True:
                chunk = reader.read(READ_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                digest.update(chunk)
                writer.write(chunk)
        return Fingerprint(total, digest.hexdigest())


def fail(message):
    """Print an error and return the failure exit status."""
    print("error: %s" % message, file=sys.stderr)
    return 1


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    source = ImageFile(os.path.join(here, "entry.png"))
    try:
        wanted = source.fingerprint()
    except (OSError, ValueError) as exc:
        return fail("source image rejected: %s" % exc)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        return fail("cannot create output dir %s: %s" % (out_dir, exc))

    destination = os.path.join(out_dir, "entry.png")
    try:
        written = source.stream_into(destination)
    except OSError as exc:
        return fail("copy to %s failed: %s" % (destination, exc))

    if written != wanted:
        return fail("output mismatch: wrote %r, expected %r"
                    % (written, wanted))

    # Independent re-read of the delivered file: the strongest check,
    # since it reads back what actually landed on disk.
    try:
        delivered = ImageFile(destination).fingerprint()
    except (OSError, ValueError) as exc:
        return fail("delivered image rejected: %s" % exc)
    if delivered != wanted:
        return fail("delivered file differs from source: %r vs %r"
                    % (delivered, wanted))

    print("wrote %s (%d bytes, sha256 %s)"
          % (destination, delivered.size, delivered.sha256))
    return 0


if __name__ == "__main__":
    sys.exit(main())
