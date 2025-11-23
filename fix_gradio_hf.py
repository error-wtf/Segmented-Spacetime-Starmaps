#!/usr/bin/env python3
"""
Fix Gradio HuggingFace Hub Import Error
Patches the oauth.py to avoid HfFolder import
"""
import sys
from pathlib import Path

# Find gradio oauth.py
import gradio
gradio_dir = Path(gradio.__file__).parent
gradio_path = gradio_dir / "oauth.py"

if not gradio_path.exists():
    print(f"Gradio oauth.py not found at {gradio_path}")
    sys.exit(1)

print(f"Patching {gradio_path}...")

# Read the file
content = gradio_path.read_text(encoding='utf-8')

# Replace the problematic import
old_import = "from huggingface_hub import HfFolder, whoami"
new_import = """# from huggingface_hub import HfFolder, whoami
# PATCHED: HuggingFace deployment disabled
class HfFolder:
    @staticmethod
    def get_token():
        return None

def whoami(token=None):
    return None"""

if old_import in content:
    content = content.replace(old_import, new_import)
    gradio_path.write_text(content, encoding='utf-8')
    print("[OK] Successfully patched!")
else:
    print("[WARN] Import already patched or not found")
