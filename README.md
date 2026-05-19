# convert-file2md 📄→📝

**Batch convert PDF, DOCX, PPTX, and XLSX files to Markdown using the mineru engine.**

A simple Python CLI tool that wraps [mineru](https://github.com/opendatalab/MinerU) to convert office documents and PDFs into clean Markdown with extracted images.

## Features

- 📄 **Multi-format** — PDF, DOCX, PPTX, XLSX
- 🖼️ **Image extraction** — Auto-extracts embedded images to `images/` subdirectory
- 🌐 **Multi-language** — Chinese, Japanese, Korean, Arabic, and more
- 📦 **Batch mode** — Process entire directories at once
- 🔍 **OCR support** — For scanned documents and image-based PDFs
- 🧹 **Auto-cleanup** — Removes intermediate files by default

## Installation

```bash
# Clone the repo
git clone https://github.com/thousandcents/convert-file2md.git
cd convert-file2md

# Install dependencies
pip install mineru

# Make it executable
chmod +x convert2md.py
```

## Usage

```bash
# Single file
python3 convert2md.py -i document.pdf -o ./output/

# Batch
python3 convert2md.py -i ./input/ -o ./output/

# Chinese document
python3 convert2md.py -i 中文文档.pdf -o ./output/ -l ch

# Scanned PDF (OCR mode)
python3 convert2md.py -i scanned.pdf -o ./output/ -m ocr
```

### All Options

```
-h, --help              Show help message
-i, --input PATH        Input file or directory (default: ./input/)
-o, --output PATH       Output directory (default: ./output/)
-b, --backend BACKEND   mineru backend: pipeline (default), vlm-http-client,
                        hybrid-http-client, vlm-auto-engine, hybrid-auto-engine
-m, --method METHOD     Parse method: auto (default), txt, ocr
-l, --lang LANG         Document language: en (default), ch, japan, korean, ...
    --keep-intermediates Keep temp files (default: clean up)
```

## Output

```
output/
└── DocumentName/
    ├── DocumentName.md
    └── images/
        ├── image1.png
        └── image2.jpg
```

## Requirements

- Python 3.7+
- [mineru CLI](https://github.com/opendatalab/MinerU) — install via `pip install mineru`

## About

This tool was originally created as a skill for [Hermes Agent](https://hermes-agent.nousresearch.com) to enable document-to-markdown conversion within AI agent workflows. It can be used standalone or integrated into any automation pipeline.

## License

MIT
