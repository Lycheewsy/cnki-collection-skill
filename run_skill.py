#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entry point for CNKI CSSCI Full-text Collection Skill.

This file provides a clean skill-level interface.
The actual scraping logic is implemented in:
tools/cnki_fulltext_scraper.py
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the CNKI CSSCI Full-text Collection Skill"
    )

    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="CNKI professional search query"
    )

    parser.add_argument(
        "--db-code",
        type=str,
        default="SCDB",
        help="CNKI database code"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Maximum number of result pages to process"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for collected full texts"
    )

    parser.add_argument(
        "--delay-min",
        type=float,
        default=6.0,
        help="Minimum delay between article requests"
    )

    parser.add_argument(
        "--delay-max",
        type=float,
        default=10.0,
        help="Maximum delay between article requests"
    )

    parser.add_argument(
        "--fulltext-timeout",
        type=int,
        default=30,
        help="Timeout for loading HTML full text"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    project_root = Path(__file__).resolve().parent
    tool_path = project_root / "tools" / "cnki_fulltext_scraper.py"

    if args.output_dir is None:
        output_dir = project_root / "outputs" / "cnki_fulltext_output"
    else:
        output_dir = Path(args.output_dir)

    command = [
        sys.executable,
        str(tool_path),
        "--db-code",
        args.db_code,
        "--max-pages",
        str(args.max_pages),
        "--output-dir",
        str(output_dir),
        "--delay-min",
        str(args.delay_min),
        "--delay-max",
        str(args.delay_max),
        "--fulltext-timeout",
        str(args.fulltext_timeout),
    ]

    if args.query:
        command.extend(["--query", args.query])

    print("=" * 60)
    print("Running CNKI CSSCI Full-text Collection Skill")
    print("=" * 60)
    print(f"Tool path: {tool_path}")
    print(f"Output directory: {output_dir}")
    print(f"Max pages: {args.max_pages}")
    print(f"Delay: {args.delay_min}–{args.delay_max} seconds")
    print("=" * 60)

    subprocess.run(command, check=False)


if __name__ == "__main__":
    main()