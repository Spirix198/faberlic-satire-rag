#!/usr/bin/env python3
"""
JWT Secret Key Generator

Generates secure JWT_SECRET_KEY for the Faberlic Satire RAG application.
Usage:
    python jwt_generator.py
    python jwt_generator.py --length 64
"""

import secrets
import argparse
from datetime import datetime


def generate_jwt_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure JWT secret key.
    
    Args:
        length: Length of the secret key in bytes (default: 32)
        
    Returns:
        URL-safe base64 encoded secret key
    """
    return secrets.token_urlsafe(length)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a secure JWT_SECRET_KEY for Faberlic Satire RAG"
    )
    parser.add_argument(
        "--length",
        type=int,
        default=32,
        help="Length of the secret key in bytes (default: 32)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of keys to generate (default: 1)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("JWT SECRET KEY GENERATOR - Faberlic Satire RAG")
    print("="*70)
    print(f"\nGenerated at: {datetime.now().isoformat()}")
    print(f"Key length: {args.length} bytes")
    print(f"Number of keys: {args.count}\n")
    
    for i in range(args.count):
        secret = generate_jwt_secret(args.length)
        print(f"Key #{i+1}:")
        print(f"{secret}\n")
    
    print("="*70)
    print("\n🔐 SECURITY RECOMMENDATIONS:")
    print("  1. Copy one of the generated keys above")
    print("  2. Paste it in your .env file as JWT_SECRET_KEY")
    print("  3. Use different keys for different environments (dev/staging/prod)")
    print("  4. Never commit .env files to Git")
    print("  5. Rotate keys periodically (every 90 days recommended)\n")
    print("  📤 Use in .env file:")
    print(f"     JWT_SECRET_KEY={generate_jwt_secret(args.length)}\n")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
