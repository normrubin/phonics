#!/usr/bin/env python3
"""
RunPod Setup Script for Phonics Book Generator

Python implementation of setup logic for RunPod environments.
Handles token validation, trigger word configuration, and environment setup.
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Import validation utilities from config module
from config import (
    validate_hf_token,
    validate_trigger_word,
    read_env_token,
    write_env_token,
    get_config,
)


def check_runpod_environment():
    """Detect if running on RunPod and print template info"""
    runpod_vars = {
        k: v for k, v in os.environ.items() if k.startswith("RUNPOD_")}

    if runpod_vars:
        print("Detected RunPod environment.")
        print("Available RUNPOD_* variables:")
        for key in sorted(runpod_vars.keys()):
            print(f"  {key} {os.environ.get(key)}")
    else:
        print(
            "Not running on RunPod (no RUNPOD_* environment variables found).")
        exit(1)


def print_versions():
    """Print Python and PyTorch versions"""
    print("\nPython version:")
    result = subprocess.run(
        [sys.executable, "--version"], capture_output=True, text=True
    )
    print(result.stdout.strip())

    print("\nPyTorch version:")
    import torch  # pyright: ignore[reportMissingImports]

    print(f"torch {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
    else:
        print("CUDA version: N/A")


def _parse_version_tuple(ver_str: str):
    """Extract numeric prefix of a version string and return tuple of ints."""
    m = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?", ver_str)
    if not m:
        return (0, 0, 0)
    parts = [p for p in m.groups(default="0")]
    try:
        return tuple(int(p) for p in parts)  # type: ignore[return-value]
    except Exception:
        return (0, 0, 0)


def check_python_version(min_version: str = "3.12.3") -> None:
    """Ensure current Python is >= min_version, else exit with error."""
    req = _parse_version_tuple(min_version)
    cur = (
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    if cur < req:
        print("✗ Python version too low.")
        print(f"  Required: >= {min_version}")
        print(
            f"  Found:    {sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )
        sys.exit(1)
    else:
        print(
            f"✓ Python version OK: {sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )


def check_torch_version(min_version: str = "2.8.0") -> None:
    """Ensure installed torch is >= min_version, else exit with error."""
    try:
        import torch  # pyright: ignore[reportMissingImports]
    except Exception:
        print("PyTorch not installed. Please install requirements and retry.")
        sys.exit(1)

    cur = _parse_version_tuple(str(torch.__version__))
    req = _parse_version_tuple(min_version)
    if cur < req:
        print("✗ PyTorch version too low.")
        print(f"  Required: >= {min_version}")
        print(f"  Found:    {torch.__version__}")
        sys.exit(1)
    else:
        print(f"✓ PyTorch version OK: {torch.__version__}")


def prompt_for_token():
    """
    Interactively prompt for Hugging Face token and validate

    Returns:
        str: Valid token, or empty string if failed/cancelled
    """
    print("\n" + "=" * 60)
    print("Enter your Hugging Face access token (starts with hf_).")
    print("Get one at: https://huggingface.co/settings/tokens")
    print("=" * 60)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            token = input("\nHF Token: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nToken input cancelled.")
            return ""

        if not token or not token.startswith("hf_"):
            print("Invalid format. Token must start with hf_.")
            continue

        print("Validating token...")
        if validate_hf_token(token):
            print("✓ Token validated successfully.")
            return token
        else:
            print(
                f"✗ Token validation failed "
                f"(attempt {attempt}/{max_attempts}). "
                "Check token and try again."
            )

    print(f"\nGiving up after {max_attempts} attempts.")
    return ""


def setup_env_file(env_file: str = "ENV"):
    """
    Set up ENV file with Hugging Face token

    Args:
        env_file: Path to ENV file

    Returns:
        bool: True if token is valid and saved, False otherwise
    """
    env_path = Path(env_file)

    # Check existing token
    if env_path.exists():
        existing_token = read_env_token(env_file)
        if existing_token:
            print(f"\nExisting token found in {env_file}")
            if validate_hf_token(existing_token):
                print("✓ Existing token is valid.")
                return True
            else:
                print("✗ Existing token is invalid.")

    # Prompt for new token
    token = prompt_for_token()
    if not token:
        # Create placeholder if no valid token
        print(f"\n⚠️  Creating placeholder {env_file} file.")
        print("You'll need to manually add your token later.")
        placeholder = """# Hugging Face Token
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN=your_huggingface_token_here
"""
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(placeholder)
        return False

    # Write valid token
    if write_env_token(token, env_file):
        print(f"✓ Token saved to {env_file}")
        return True
    else:
        return False


def prompt_for_trigger_word():
    """
    Interactively prompt for trigger word

    Returns:
        str: Valid trigger word, or empty string if failed/cancelled
    """
    print("\n" + "=" * 60)
    print("Enter a unique identifier for your child.")
    print("Format: childname_trigger (e.g., 'alicegirl' or 'bobbytrigger')")
    print("Use letters, numbers, and underscores only.")
    print("This will be added to all image captions during training.")
    print("=" * 60)

    while True:
        try:
            trigger = input("\nTrigger word: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nTrigger word input cancelled.")
            return ""

        if not trigger:
            print("Trigger word cannot be empty. Please enter a value.")
            continue

        if not validate_trigger_word(trigger):
            print(
                "Invalid format. Use only letters, numbers, and underscores.")
            continue

        return trigger


def setup_trigger_word(config_file: str = "config.json"):
    """
    Set up trigger word in config.json

    Args:
        config_file: Path to config.json

    Returns:
        str: The trigger word (existing or newly set),
             or empty string if failed
    """
    try:
        config = get_config(config_file)
        existing_trigger = config.trigger_word

        if existing_trigger and existing_trigger != "your_trigger_word_here":
            print(f"\nTrigger word already configured: {existing_trigger}")
            try:
                response = input(
                    "Do you want to change it? (y/n): ").strip().lower()
                if response not in ("y", "yes"):
                    return existing_trigger
            except (EOFError, KeyboardInterrupt):
                print("\nKeeping existing trigger word.")
                return existing_trigger

        # Prompt for new trigger word
        trigger = prompt_for_trigger_word()
        if not trigger:
            print(
                "No trigger word set. You'll need to configure it manually.")
            return ""

        if config.update_trigger_word(trigger):
            return trigger
        else:
            return ""

    except FileNotFoundError:
        print(f"\n⚠️  {config_file} not found. It will be created later.")
        return ""


def clone_ai_toolkit(target_dir: str = "/workspace/ai-toolkit"):
    """
    Clone ai-toolkit repository if not present

    Args:
        target_dir: Directory where ai-toolkit should be cloned

    Returns:
        bool: True if ai-toolkit is available, False otherwise
    """
    toolkit_path = Path(target_dir)
    if toolkit_path.exists():
        print(f"ai-toolkit already exists at {target_dir}")
        return True

    print(f"Cloning ai-toolkit to {target_dir} (quiet)...")
    parent = toolkit_path.parent
    parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "https://github.com/ostris/ai-toolkit.git",
                str(toolkit_path),
            ],
            check=True,
            cwd=str(parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("✓ ai-toolkit cloned")

        # Update submodules quietly
        subprocess.run(
            [
                "git",
                "submodule",
                "update",
                "--init",
                "--recursive",
                "--quiet",
            ],
            check=True,
            cwd=str(toolkit_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("✓ Submodules initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to clone ai-toolkit: {e}")
        return False


def install_requirements():
    """Install Python requirements"""
    print("\nInstalling Python requirements...")

    # Combine ai-toolkit and project requirements
    toolkit_req = Path("/workspace/ai-toolkit/requirements.txt")
    project_req = Path("requirements.txt")

    requirements = []
    if project_req.exists():
        with open(project_req, "r", encoding="utf-8") as f:
            requirements.extend(f.readlines())
    if toolkit_req.exists():
        with open(toolkit_req, "r", encoding="utf-8") as f:
            requirements.extend(f.readlines())

    if not requirements:
        print("⚠️  No requirements files found")
        return False

    # Write combined requirements to temp file
    temp_req = Path("/tmp/combined_requirements.txt")
    with open(temp_req, "w", encoding="utf-8") as f:
        f.writelines(requirements)

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(temp_req),
        "-q",  # quiet output
        "--no-input",
        "--progress-bar",
        "off",
        "--disable-pip-version-check",
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("✗ Failed to install requirements")
        if e.stdout:
            print(e.stdout)
        return False
    finally:
        try:
            temp_req.unlink(missing_ok=True)
        except Exception:
            pass


def generate_flux_config():
    """Generate FLUX training configuration"""
    print("\nGenerating FLUX training configuration...")
    try:
        subprocess.run(
            [
                sys.executable,
                "finetune_flux_train.py",
                "--generate-config-only",
            ],
            check=True,
        )
        print("✓ Training configuration generated")
        return True
    except subprocess.CalledProcessError:
        print(
            "Could not generate config. " +
            "It will be created when you run training.")
        return False


def test_gpu():
    """Test GPU availability"""
    print("\nTesting GPU availability...")
    try:
        import torch  # type: ignore

        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("GPU: None")
    except ImportError:
        print("⚠️  PyTorch not installed, cannot test GPU")


def print_next_steps(token_valid: bool, trigger_set: bool):
    """
    Print next steps based on setup status

    Args:
        token_valid: Whether HF token is valid
        trigger_set: Whether trigger word is configured
    """
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")

    step = 1
    if not token_valid:
        print(
            f"{step}. Edit ENV and add your HuggingFace token "
            "(HF_TOKEN=hf_...)"
        )
        step += 1
    if not trigger_set:
        print(
            f"{step}. Edit config.json and set trigger_word "
            "(your unique identifier)"
        )
        step += 1

    print(f"{step}. Upload your training images to ./photos/")
    step += 1
    print(f"{step}. Label images: python3 label_images.py")
    step += 1
    print(f"{step}. Fine-tune model: python3 finetune_flux_train.py")
    step += 1
    print(f"{step}. Generate images: python3 flux_infer.py prompts.txt")

    print(f"\nProject directory: {Path.cwd()}")
    print("AI Toolkit directory: /workspace/ai-toolkit")
    print()


def main():
    """Main setup routine"""
    print("=" * 60)
    print("Phonics Book Generator - RunPod Setup")
    print("=" * 60)

    # Version checks (Python first, torch later after install)
    check_python_version("3.12.3")

    # Detect environment
    check_runpod_environment()

    # Print versions
    print_versions()

    # Create project directory if needed
    project_dir = Path.cwd()
    print(f"\nProject directory: {project_dir}")

    # Set up ENV file with token
    token_valid = setup_env_file()

    # Clone ai-toolkit
    clone_ai_toolkit()

    # Create directories
    print("\nCreating directory structure...")
    try:
        config = get_config()
        config.ensure_directories()
    except FileNotFoundError:
        print("⚠️  config.json not found, creating basic directories...")
        Path("photos").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)

    # Set up trigger word
    trigger_word = setup_trigger_word()

    # Install requirements
    install_requirements()

    # Torch version check after install
    check_torch_version("2.8.0")

    # Make scripts executable (if on Unix-like system)
    for script in ["quick_start.sh", "runpod_setup.sh"]:
        script_path = Path(script)
        if script_path.exists() and os.name != "nt":
            script_path.chmod(0o755)
            print(f"✓ Made {script} executable")

    # Create example prompts file
    prompts_file = Path("prompts.txt")
    if not prompts_file.exists():
        example = Path("prompts.txt.example")
        if example.exists():
            prompts_file.write_text(example.read_text())
            print("✓ Created prompts.txt from example")

    # Generate FLUX config
    generate_flux_config()

    # Test GPU
    test_gpu()

    # Print next steps
    print_next_steps(token_valid, bool(trigger_word))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
