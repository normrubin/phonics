#!/usr/bin/env python3
"""
DEPRECATED ENTRY POINT
======================

This script has been superseded by:

    - finetune_flux_train.py (training + config generation)
    - flux_infer.py (inference / image generation)

It remains only to avoid breaking older documentation or automation.
Please migrate any calls to:

    python finetune_flux_train.py            # for training
    python flux_infer.py prompts.txt         # for inference

If you need to regenerate the training config only:

    python finetune_flux_train.py --generate-config-only

All logic here now proxies to finetune_flux_train.py for backward
compatibility when training flags are used, otherwise it prints this
notice and exits.
"""

import sys
import subprocess


def main():  # noqa: D401
    """Proxy or warn about deprecation."""
    if len(sys.argv) > 1:
        # Forward arguments to new training script for backward compatibility
        cmd = [sys.executable, "finetune_flux_train.py", *sys.argv[1:]]
        print("[DEPRECATED] Redirecting to finetune_flux_train.py ...")
        try:
            raise SystemExit(subprocess.call(cmd))
        except KeyboardInterrupt:  # noqa: PIE786
            print("Interrupted.")
            raise SystemExit(1)

    print(
        """
finetune_flux.py is deprecated.

Use:
  python finetune_flux_train.py            # training
  python finetune_flux_train.py --generate-config-only
  python flux_infer.py prompts.txt         # inference
""".strip()
    )
    raise SystemExit(0)


if __name__ == "__main__":
    main()
