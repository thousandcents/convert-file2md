#!/usr/bin/env python3
"""
convert2md - Convert PDF, DOCX, PPTX, and XLSX files to Markdown.

Uses the mineru CLI as the conversion engine.
Automatically finds mineru in PATH or common installation locations.

Usage:
    # Single file
    python3 convert2md.py -i document.pdf -o ./output/

    # Batch directory
    python3 convert2md.py -i ./input/ -o ./output/

    # Chinese document
    python3 convert2md.py -i document.pdf -o ./output/ -l ch

    # OCR for scanned documents
    python3 convert2md.py -i scanned.pdf -o ./output/ -m ocr
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}

# Common locations to search for mineru
MINERU_CANDIDATE_PATHS = [
    "mineru",  # in PATH
    str(Path.home() / ".local" / "bin" / "mineru"),
    str(Path.home() / ".hermes" / "hermes-agent" / "venv" / "bin" / "mineru"),
    "/usr/local/bin/mineru",
    "/usr/bin/mineru",
]


def find_mineru() -> Path:
    """Find the mineru executable by checking common locations."""
    for candidate in MINERU_CANDIDATE_PATHS:
        found = shutil.which(candidate)
        if found:
            return Path(found)
    raise FileNotFoundError(
        "mineru not found. Install it via: pip install mineru"
    )


def setup_logging(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("convert2md")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def extract_markdown_and_images(
    mineru_output_dir: Path,
    file_stem: str,
    output_subdir: Path,
    logger: logging.Logger,
) -> Optional[Path]:
    """Extract .md files from mineru output and organize them properly."""
    md_files = list(mineru_output_dir.rglob("*.md"))
    md_files = [f for f in md_files if f.stem.startswith(file_stem)]

    if not md_files:
        logger.error(f"No markdown files found in {mineru_output_dir}")
        return None

    main_md_file = output_subdir / f"{file_stem}.md"
    images_dir = output_subdir / "images"

    for md_file in md_files:
        md_content = md_file.read_text(encoding="utf-8")
        md_images_dir = md_file.parent / "images"
        if md_images_dir.exists():
            images_dir.mkdir(parents=True, exist_ok=True)
            for img in md_images_dir.iterdir():
                if img.is_file():
                    dest_img = images_dir / img.name
                    if not dest_img.exists():
                        shutil.copy2(img, dest_img)

        if md_file.name == f"{file_stem}.md":
            main_md_file.write_text(md_content, encoding="utf-8")
            logger.debug(f"Main md file written to {main_md_file}")

    if not main_md_file.exists():
        primary_md = md_files[0]
        shutil.copy2(primary_md, main_md_file)
        main_md_file.write_text(primary_md.read_text(encoding="utf-8"), encoding="utf-8")

    logger.info(f"Markdown saved to {main_md_file}")
    return main_md_file


def process_file(
    input_file: Path,
    output_dir: Path,
    mineru_path: Path,
    backend: str,
    method: str,
    lang: str,
    keep_intermediates: bool,
    logger: logging.Logger,
) -> bool:
    """Process a single file through mineru and extract markdown."""
    file_stem = input_file.stem
    logger.info(f"Processing: {input_file.name}")

    temp_mineru_output = output_dir / f"__mineru_temp_{file_stem}"
    temp_mineru_output.mkdir(parents=True, exist_ok=True)

    try:
        cmd = [
            str(mineru_path),
            "-p", str(input_file.resolve()),
            "-o", str(temp_mineru_output),
            "-b", backend,
            "-m", method,
            "-l", lang,
        ]
        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600,
        )

        if result.returncode != 0:
            logger.error(f"mineru failed for {input_file.name}: {result.stderr}")
            return False

        mineru_result_dir = temp_mineru_output / file_stem
        if not mineru_result_dir.exists():
            logger.error(f"mineru output directory not found: {mineru_result_dir}")
            return False

        output_subdir = output_dir / file_stem
        output_subdir.mkdir(parents=True, exist_ok=True)

        md_file = extract_markdown_and_images(
            mineru_result_dir, file_stem, output_subdir, logger,
        )
        if md_file is None:
            return False

        logger.info(f"Successfully converted: {input_file.name} -> {md_file}")

        if not keep_intermediates:
            shutil.rmtree(temp_mineru_output)
            logger.debug(f"Cleaned up temp directory: {temp_mineru_output}")

        return True

    except subprocess.TimeoutExpired:
        logger.error(f"mineru timed out for {input_file.name}")
        return False
    except Exception as e:
        logger.error(f"Error processing {input_file.name}: {e}")
        return False
    finally:
        if keep_intermediates and temp_mineru_output.exists():
            logger.debug(f"Kept temp directory: {temp_mineru_output}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert PDF, DOCX, PPTX, and XLSX files to Markdown using mineru.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input", "-i", type=Path, default=Path("./input/"),
        help="Input file or directory (default: ./input/)",
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=Path("./output/"),
        help="Output directory (default: ./output/)",
    )
    parser.add_argument(
        "--backend", "-b",
        default="pipeline",
        choices=["pipeline", "vlm-http-client", "hybrid-http-client",
                 "vlm-auto-engine", "hybrid-auto-engine"],
        help="mineru backend (default: pipeline)",
    )
    parser.add_argument(
        "--method", "-m",
        default="auto",
        choices=["auto", "txt", "ocr"],
        help="Parse method (default: auto)",
    )
    parser.add_argument(
        "--lang", "-l",
        default="en",
        choices=["ch", "ch_server", "ch_lite", "en", "korean", "japan",
                 "chinese_cht", "ta", "te", "ka", "th", "el", "latin",
                 "arabic", "east_slavic", "cyrillic", "devanagari"],
        help="Language (default: en)",
    )
    parser.add_argument(
        "--keep-intermediates",
        action="store_true",
        help="Keep intermediate files (default: clean up)",
    )

    args = parser.parse_args()
    log_file = Path("convert2md.log")
    logger = setup_logging(log_file)

    logger.info("=" * 60)
    logger.info("convert2md.py - File to Markdown converter")
    logger.info("=" * 60)
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Backend: {args.backend}")
    logger.info(f"Method: {args.method}")
    logger.info(f"Language: {args.lang}")

    try:
        mineru_path = find_mineru()
        logger.info(f"mineru path: {mineru_path}")
    except FileNotFoundError as e:
        logger.error(e)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)

    if args.input.is_file():
        files_to_process = [args.input]
    elif args.input.is_dir():
        files_to_process = []
        for ext in SUPPORTED_EXTENSIONS:
            files_to_process.extend(args.input.glob(f"*{ext}"))
        files_to_process = sorted(set(files_to_process))
    else:
        logger.error(f"Input path does not exist: {args.input}")
        return 1

    if not files_to_process:
        logger.warning("No supported files found to process")
        return 0

    logger.info(f"Found {len(files_to_process)} file(s) to process")
    success_count = 0
    fail_count = 0

    for i, file_path in enumerate(files_to_process, 1):
        logger.info(f"[{i}/{len(files_to_process)}] Processing {file_path.name}")
        if process_file(
            file_path, args.output, mineru_path,
            args.backend, args.method, args.lang,
            args.keep_intermediates, logger,
        ):
            success_count += 1
        else:
            fail_count += 1

    logger.info("=" * 60)
    logger.info(f"Completed: {success_count} succeeded, {fail_count} failed")
    logger.info("=" * 60)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
