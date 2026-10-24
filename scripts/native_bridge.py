#!/usr/bin/env python3
"""Entry point for the experimental Android 12-14 ARM64 profile."""
from android11_arm64 import ROOT, main

if __name__ == '__main__':
    raise SystemExit(main(ROOT / 'config/libndk-android12-14-arm64.json'))
