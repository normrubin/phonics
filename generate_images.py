#!/usr/bin/env python3
"""Deprecated: use flux_infer.py instead.

This script remains for compatibility and forwards to flux_infer.main().
"""

from flux_infer import main as flux_main  # type: ignore


if __name__ == "__main__":
    flux_main()
