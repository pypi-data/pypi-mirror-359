"""Command-line interface for svg2png-clipboard"""

import os
import sys
import tempfile
from pathlib import Path

import click

from .core import (
    check_dependencies,
    get_clipboard_text,
    is_valid_svg,
    svg_to_png,
    copy_png_to_clipboard,
    show_notification,
    DependencyError,
    SVGConversionError,
)


@click.command()
@click.option(
    '-s', '--size',
    default=180,
    type=int,
    help='Output PNG size in pixels (width and height)'
)
@click.option(
    '-o', '--output',
    type=click.Path(dir_okay=False),
    help='Save PNG to file instead of clipboard'
)
@click.option(
    '-i', '--input',
    type=click.Path(exists=True, dir_okay=False),
    help='Read SVG from file instead of clipboard'
)
@click.option(
    '--no-notification',
    is_flag=True,
    help='Disable macOS notifications'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Show detailed output'
)
@click.version_option()
def main(size, output, input, no_notification, verbose):
    """Convert SVG from clipboard to PNG and copy back to clipboard.
    
    This tool reads SVG content from the macOS clipboard (or a file),
    converts it to PNG format, and copies the result back to the clipboard
    (or saves it to a file).
    
    Examples:
        svg2png-clipboard                    # Default: 180x180 from/to clipboard
        svg2png-clipboard -s 512            # 512x512 PNG
        svg2png-clipboard -o output.png     # Save to file
        svg2png-clipboard -i input.svg      # Read from file
    """
    try:
        # Check dependencies first
        if verbose:
            click.echo("Checking dependencies...")
        check_dependencies()
        
        # Get SVG content
        if input:
            if verbose:
                click.echo(f"Reading SVG from {input}...")
            svg_content = Path(input).read_text(encoding='utf-8')
        else:
            if verbose:
                click.echo("Reading SVG from clipboard...")
            svg_content = get_clipboard_text()
        
        # Validate SVG
        if not is_valid_svg(svg_content):
            click.echo("❌ Error: Invalid SVG content", err=True)
            if verbose and svg_content:
                click.echo(f"First 100 chars: {svg_content[:100]}...", err=True)
            sys.exit(1)
        
        # Convert to PNG
        if verbose:
            click.echo(f"Converting SVG to {size}x{size} PNG...")
        
        png_path = svg_to_png(svg_content, size=size, output_path=output)
        
        try:
            if output:
                click.echo(f"✅ PNG saved to: {output}")
            else:
                # Copy to clipboard
                if verbose:
                    click.echo("Copying PNG to clipboard...")
                copy_png_to_clipboard(png_path)
                click.echo(f"✅ PNG ({size}×{size}) copied to clipboard")
                
                # Show notification
                if not no_notification:
                    show_notification(
                        "SVG to PNG",
                        f"{size}×{size} PNG copied to clipboard"
                    )
        finally:
            # Clean up temp file if we created one
            if not output and os.path.exists(png_path):
                try:
                    os.unlink(png_path)
                except:
                    pass
    
    except DependencyError as e:
        click.echo(f"❌ Dependency Error:\n{e}", err=True)
        click.echo("\nPlease install missing dependencies and try again.", err=True)
        sys.exit(1)
    
    except SVGConversionError as e:
        click.echo(f"❌ Conversion Error: {e}", err=True)
        sys.exit(1)
    
    except KeyboardInterrupt:
        click.echo("\n⚠️  Cancelled by user", err=True)
        sys.exit(130)
    
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()