#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Explorer Launcher - Starts working version on Port 7862

© 2025 Carmen Wrede, Lino Casu
"""
import sys
import os

# UTF-8 fix
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("="*80)
print("SSZ EXPLORER - STARTING...")
print("="*80)
print()
print("Loading 50,000 star database...")
print("Starting on Port 7862...")
print()
print("Open in browser: http://localhost:7862")
print("="*80)
print()

# Import and modify gradio_app to use port 7862
import gradio_app

# Change the launch to use our port
if __name__ == "__main__":
    gradio_app.launch_app(share=False, port=7862)
