#!/usr/bin/env python3
"""Publish the excuse line from entry.txt to the output the gate expects.

Reads entry.txt as raw bytes, validates it against the gate rules in the
kit's RULES.txt (UTF-8 text, 1 to 140 characters, not only whitespace, a
single line, at most 20 words, no trailing whitespace or control
characters), then writes those exact bytes to /output/entry.txt, falling
back to ./output-entry.txt in the working directory when /output is not
writable. The published bytes are re-read and compared; any mismatch
refuses to finish. Deterministic: no network, no randomness, no time
dependence. Python standard library only.
"""

import os
import sys

SOURCE = "entry.txt"
PRIMARY_OUTPUT = "/output/entry.txt"
FALLBACK_OUTPUT = "output-entry.txt"
MAX_WORDS = 20
MAX_CHARS = 140


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    try:
        with open(SOURCE, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        fail("cannot read %s: %s" % (SOURCE, exc))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail("entry.txt is not valid UTF-8: %s" % exc)

    if not (1 <= len(text) <= MAX_CHARS):
        fail("entry must be 1 to %d characters, got %d"
             % (MAX_CHARS, len(text)))
    if not text.strip():
        fail("entry must not be only whitespace")
    if "\n" in text or "\r" in text:
        fail("entry must be a single line")
    if text != text.rstrip():
        fail("entry must not end with trailing whitespace")
    if any(ord(ch) < 0x20 for ch in text):
        fail("entry must not contain control characters")

    words = text.split()
    if len(words) > MAX_WORDS:
        fail("entry must be at most %d words, got %d"
             % (MAX_WORDS, len(words)))

    output = PRIMARY_OUTPUT
    try:
        os.makedirs(os.path.dirname(PRIMARY_OUTPUT), exist_ok=True)
        with open(PRIMARY_OUTPUT, "wb") as handle:
            handle.write(raw)
    except OSError:
        output = FALLBACK_OUTPUT
        try:
            with open(FALLBACK_OUTPUT, "wb") as handle:
                handle.write(raw)
        except OSError as exc:
            fail("cannot write %s or %s: %s"
                 % (PRIMARY_OUTPUT, FALLBACK_OUTPUT, exc))

    try:
        with open(output, "rb") as handle:
            published = handle.read()
    except OSError as exc:
        fail("cannot re-read published output %s: %s" % (output, exc))
    if published != raw:
        fail("published bytes do not match entry.txt")

    print("published %d characters (%d words) to %s"
          % (len(text), len(words), output))


if __name__ == "__main__":
    main()
