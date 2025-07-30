"""Core functionality for SVG to PNG conversion"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    import pyperclipimg as pci
except ImportError:
    print("Error: pyperclipimg is not installed. This should have been installed automatically.")
    print("Try: pip install pyperclipimg")
    sys.exit(1)


class DependencyError(Exception):
    """Raised when a required system dependency is missing"""
    pass


class SVGConversionError(Exception):
    """Raised when SVG conversion fails"""
    pass


def check_dependencies():
    """Check if all system dependencies are available"""
    errors = []
    
    # Check OS
    if platform.system() != "Darwin":
        errors.append("This tool only works on macOS (requires pbpaste and osascript)")
    
    # Check rsvg-convert
    if not shutil.which("rsvg-convert"):
        errors.append(
            "rsvg-convert is not installed. Install it with: brew install librsvg"
        )
    
    # Check pbpaste
    if not shutil.which("pbpaste"):
        errors.append("pbpaste is not found (macOS system tool)")
    
    # Check osascript
    if not shutil.which("osascript"):
        errors.append("osascript is not found (macOS system tool)")
    
    if errors:
        raise DependencyError("\n".join(errors))


def get_clipboard_text():
    """Get text content from macOS clipboard"""
    try:
        result = subprocess.run(
            ["pbpaste"], 
            text=True, 
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise SVGConversionError(f"Failed to read clipboard: {e}")


def is_valid_svg(text):
    """Check if the text is valid SVG"""
    if not text or not text.strip():
        return False
    
    try:
        root = ET.fromstring(text)
        # Check if root tag is svg (with or without namespace)
        return root.tag.endswith("svg") or root.tag == "svg"
    except ET.ParseError:
        return False


def svg_to_png(svg_content, size=180, output_path=None):
    """Convert SVG content to PNG file
    
    Args:
        svg_content: SVG content as string
        size: Output size in pixels (width and height)
        output_path: Optional output path. If None, a temp file is created
        
    Returns:
        Path to the created PNG file
    """
    # Create temp SVG file
    with tempfile.NamedTemporaryFile(
        mode='w', 
        suffix='.svg', 
        delete=False, 
        encoding='utf-8'
    ) as svg_file:
        svg_file.write(svg_content)
        svg_path = svg_file.name
    
    # Create output path if not provided
    if output_path is None:
        png_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        png_file.close()
        output_path = png_file.name
    
    try:
        # Convert SVG to PNG
        cmd = [
            "rsvg-convert",
            "-w", str(size),
            "-h", str(size),
            "-o", output_path,
            svg_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stderr:
            print(f"Warning from rsvg-convert: {result.stderr}")
        
        return output_path
        
    except subprocess.CalledProcessError as e:
        raise SVGConversionError(
            f"Failed to convert SVG to PNG: {e}\n"
            f"stderr: {e.stderr}"
        )
    finally:
        # Clean up temp SVG file
        try:
            os.unlink(svg_path)
        except:
            pass


def copy_png_to_clipboard(png_path):
    """Copy PNG file to clipboard"""
    try:
        pci.copy(png_path)
    except Exception as e:
        raise SVGConversionError(f"Failed to copy PNG to clipboard: {e}")


def show_notification(title, message):
    """Show macOS notification"""
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        # Notifications might fail in some environments, don't crash
        pass