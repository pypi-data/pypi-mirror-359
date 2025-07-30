"""
Command-line interface for ffenc.
"""

import sys
import getpass
from pathlib import Path
import click
from .crypto import encrypt, decrypt


@click.group()
@click.version_option()
def main():
    """FFenc - File encryption and decryption tool."""
    pass


@main.command(name='e')
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--password', '-p', help='Password for encryption (will prompt if not provided)')
def encrypt_file(input_file: Path, output_file: Path, password: str):
    """Encrypt a file with a password."""
    try:
        # Get password if not provided
        if not password:
            password = getpass.getpass("Enter encryption password: ")
            if not password:
                click.echo("Error: Password cannot be empty", err=True)
                sys.exit(1)
        
        # Read input file
        if input_file.is_file():
            content = input_file.read_bytes()
        else:
            click.echo(f"Error: {input_file} is not a file", err=True)
            sys.exit(1)
        
        # Encrypt and save
        encrypt(password, content, str(output_file))
        click.echo(f"File encrypted successfully: {output_file}")
        
    except Exception as e:
        click.echo(f"Error during encryption: {e}", err=True)
        sys.exit(1)


@main.command(name='d')
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path), required=False)
@click.option('--password', '-p', help='Password for decryption (will prompt if not provided)')
@click.option('--stdout', is_flag=True, help='Output to stdout instead of file')
def decrypt_file(input_file: Path, output_file: Path, password: str, stdout: bool):
    """Decrypt a file with a password."""
    try:
        # Get password if not provided
        if not password:
            password = getpass.getpass("Enter decryption password: ")
            if not password:
                click.echo("Error: Password cannot be empty", err=True)
                sys.exit(1)
        
        # Decrypt content
        decrypted_content = decrypt(password, str(input_file))
        
        # Output handling
        if stdout:
            # Output to stdout
            sys.stdout.buffer.write(decrypted_content)
        elif output_file:
            # Output to file
            output_file.write_bytes(decrypted_content)
            click.echo(f"File decrypted successfully: {output_file}")
        else:
            # Try to output to stdout, but warn if it might be binary
            try:
                text_content = decrypted_content.decode('utf-8')
                click.echo(text_content)
            except UnicodeDecodeError:
                click.echo("Warning: Decrypted content appears to be binary. Use --stdout to output binary data or specify an output file.", err=True)
                sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error during decryption: {e}", err=True)
        sys.exit(1)


@main.command(name='et')
@click.argument('content', required=False)
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--password', '-p', help='Password for encryption (will prompt if not provided)')
@click.option('--file', '-f', type=click.Path(exists=True, path_type=Path), help='Read content from file instead of argument')
def encrypt_text(content: str, output_file: Path, password: str, file: Path):
    """Encrypt text content with a password."""
    try:
        # Get password if not provided
        if not password:
            password = getpass.getpass("Enter encryption password: ")
            if not password:
                click.echo("Error: Password cannot be empty", err=True)
                sys.exit(1)
        
        # Get content
        if file:
            content = file.read_text()
        elif not content:
            # Read from stdin
            click.echo("Enter content to encrypt (Ctrl+D to finish):")
            content = sys.stdin.read()
        
        if not content:
            click.echo("Error: No content provided", err=True)
            sys.exit(1)
        
        # Encrypt and save
        encrypt(password, content, str(output_file))
        click.echo(f"Content encrypted successfully: {output_file}")
        
    except Exception as e:
        click.echo(f"Error during encryption: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    # Register aliases for commands
    main.add_command(encrypt_file, name='e')
    main.add_command(decrypt_file, name='d')
    main.add_command(encrypt_text, name='et')
    main() 