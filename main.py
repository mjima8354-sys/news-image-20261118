#!/usr/bin/env python3
"""
main.py - Copies entry.png to the MAKEFUN_OUTPUT_DIR
"""

import os
import shutil
import sys

def main():
    # Get output directory from environment variable or use default
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    
    # Ensure the source file exists
    if not os.path.exists('entry.png'):
        print("Error: entry.png not found. Please run gen_news.py first.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy the file
    destination = os.path.join(output_dir, 'entry.png')
    shutil.copy2('entry.png', destination)
    
    print(f"Copied entry.png to {destination}")

if __name__ == "__main__":
    main()