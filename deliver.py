#!/usr/bin/env python3
"""
Kindle News Delivery Script
Fetches newspapers via Calibre recipes and delivers them to your Kindle Scribe.
"""

import argparse
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from pathlib import Path
import smtplib
import subprocess
import sys

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

NEWSPAPERS = {
    'toi': {
        'name': 'The Times of India',
        'recipe': 'recipes/times_of_india.recipe',
        'slug': 'Times_of_India'
    },
    'irishtimes': {
        'name': 'The Irish Times',
        'recipe': 'recipes/irish_times.recipe',
        'slug': 'Irish_Times'
    },
    'independent': {
        'name': 'Irish Independent',
        'recipe': 'recipes/irish_independent.recipe',
        'slug': 'Irish_Independent'
    }
}


def build_epub(recipe_path: Path, output_epub: Path) -> bool:
    """Builds an EPUB file using Calibre's ebook-convert."""
    output_epub.parent.mkdir(parents=True, exist_ok=True)
    
    if not recipe_path.exists():
        print(f"[-] Error: Recipe not found at {recipe_path}")
        return False

    print(f"\n[+] Compiling {recipe_path.name} -> {output_epub.name}...")
    cmd = [
        "ebook-convert",
        str(recipe_path),
        str(output_epub),
        "--output-profile", "kindle",
        "--dont-compress"
    ]

    try:
        process = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(f"[✓] Successfully generated {output_epub} ({output_epub.stat().st_size // 1024} KB)")
        return True
    except FileNotFoundError:
        print("[-] Error: 'ebook-convert' not found.")
        print("    Calibre is required to compile recipes.")
        print("    - On Mac: brew install --cask calibre")
        print("    - On GitHub Actions: Ubuntu runner installs Calibre automatically.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[-] Error compiling {recipe_path.name}:")
        print(e.stderr or e.stdout)
        return False


def send_to_kindle(
    epub_path: Path,
    paper_name: str,
    kindle_email: str,
    smtp_user: str,
    smtp_pass: str,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> bool:
    """Sends an EPUB to Amazon Send-to-Kindle via SMTP."""
    if not epub_path.exists():
        print(f"[-] File not found: {epub_path}")
        return False

    print(f"\n[+] Sending '{paper_name}' to Kindle: {kindle_email}...")
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = kindle_email
    msg['Subject'] = f"{paper_name} - {datetime.now().strftime('%d %b %Y')}"

    body = f"Daily delivery of {paper_name} for Kindle Scribe.\nDelivered on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    msg.attach(MIMEText(body, 'plain'))

    with open(epub_path, 'rb') as attachment:
        part = MIMEBase('application', 'epub+zip')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{epub_path.name}"'
        )
        msg.attach(part)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
            
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[✓] Successfully emailed {epub_path.name} to {kindle_email}!")
        return True
    except Exception as e:
        print(f"[-] Failed to send email to Kindle: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Deliver newspapers to Kindle Scribe")
    parser.add_argument(
        '--paper',
        choices=['all', 'toi', 'irishtimes', 'independent'],
        default='all',
        help="Which paper to fetch (default: all)"
    )
    parser.add_argument('--kindle-email', default=os.getenv('KINDLE_EMAIL'))
    parser.add_argument('--smtp-user', default=os.getenv('SMTP_USER'))
    parser.add_argument('--smtp-pass', default=os.getenv('SMTP_PASS'))
    parser.add_argument('--smtp-host', default=os.getenv('SMTP_HOST', 'smtp.gmail.com'))
    parser.add_argument('--smtp-port', type=int, default=int(os.getenv('SMTP_PORT', 587)))
    parser.add_argument('--output-dir', default='./output')
    parser.add_argument('--no-send', action='store_true', help="Compile EPUB only, do not send email")

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    today_str = datetime.now().strftime('%Y-%m-%d')
    targets = NEWSPAPERS.keys() if args.paper == 'all' else [args.paper]

    if not args.no_send:
        if not args.kindle_email:
            print("[-] Error: Kindle email is missing.")
            print("    Provide --kindle-email or set KINDLE_EMAIL environment variable.")
            sys.exit(1)
        if not args.smtp_user or not args.smtp_pass:
            print("[-] Error: SMTP credentials missing.")
            print("    Set SMTP_USER and SMTP_PASS environment variables (or use --no-send to test compilation only).")
            sys.exit(1)

    success_count = 0
    total = len(targets)

    for key in targets:
        info = NEWSPAPERS[key]
        recipe_path = project_root / info['recipe']
        epub_filename = f"{info['slug']}_{today_str}.epub"
        epub_path = output_dir / epub_filename

        build_ok = build_epub(recipe_path, epub_path)
        if not build_ok:
            continue

        if not args.no_send:
            send_ok = send_to_kindle(
                epub_path=epub_path,
                paper_name=info['name'],
                kindle_email=args.kindle_email,
                smtp_user=args.smtp_user,
                smtp_pass=args.smtp_pass,
                smtp_host=args.smtp_host,
                smtp_port=args.smtp_port
            )
            if send_ok:
                success_count += 1
        else:
            success_count += 1

    print(f"\n[+] Finished: {success_count}/{total} newspapers processed successfully.")


if __name__ == '__main__':
    main()
