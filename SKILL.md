---
name: convert-file2md
description: Convert PDF, DOCX, PPTX, XLSX files to Markdown using mineru CLI
---

# convert-file2md — File to Markdown Converter

## Overview

Batch convert PDF, DOCX, PPTX, and XLSX files to Markdown format using the [mineru](https://github.com/opendatalab/MinerU) CLI engine.

## Requirements

- Python 3.7+
- [mineru CLI](https://github.com/opendatalab/MinerU) (`pip install mineru`)
- `curl` (for image download)

The script automatically locates `mineru` in your PATH or common installation directories.

## Quick Start

```bash
# Single file conversion
python3 convert2md.py -i document.pdf -o ./output/

# Batch conversion (all supported files in a directory)
python3 convert2md.py -i ./input/ -o ./output/

# Chinese document
python3 convert2md.py -i document.pdf -o ./output/ -l ch

# Scanned document (OCR mode)
python3 convert2md.py -i scanned.pdf -o ./output/ -m ocr
```

## CLI Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--input` | `-i` | Input file or directory | `./input/` |
| `--output` | `-o` | Output directory | `./output/` |
| `--backend` | `-b` | mineru backend engine | `pipeline` |
| `--method` | `-m` | Parse method | `auto` |
| `--lang` | `-l` | Document language | `en` |
| `--keep-intermediates` | — | Keep intermediate files | `false` |

### Backend Options

| Value | Description |
|-------|-------------|
| `pipeline` | (Default) Local Pipeline engine |
| `vlm-http-client` | VLM HTTP client mode |
| `hybrid-http-client` | Hybrid HTTP client mode |
| `vlm-auto-engine` | VLM auto engine |
| `hybrid-auto-engine` | Hybrid auto engine |

### Parse Methods

| Value | Description |
|-------|-------------|
| `auto` | (Default) Auto-detect |
| `txt` | Plain text mode (fast) |
| `ocr` | OCR mode for scanned documents |

### Language Options

| Value | Use Case |
|-------|----------|
| `en` | (Default) English |
| `ch` | Chinese |
| `ch_server` | Chinese (server model) |
| `ch_lite` | Chinese (lightweight model) |
| `japan` | Japanese |
| `korean` | Korean |
| `chinese_cht` | Traditional Chinese |
| `latin` | Latin scripts |
| `arabic` | Arabic |
| `cyrillic` | Cyrillic |
| `devanagari` | Devanagari |

## Output Structure

```
output_dir/
└── <filename>/
    ├── <filename>.md
    └── images/
        ├── image1.png
        └── image2.jpg
```

## Supported Formats

Only `.pdf`, `.docx`, `.pptx`, `.xlsx` are supported. Legacy `.doc` files require conversion first.

## Troubleshooting

1. **mineru not found**: Install via `pip install mineru` or ensure it's in PATH.
   ```bash
   pip install mineru
   which mineru
   ```

2. **Poor Chinese recognition**: Use `-l ch` instead of the default `-l en`.
   Traditional Chinese: `-l chinese_cht`.

3. **Conversion timeout**: Single file timeout is 600 seconds (10 minutes). For large files, try `-m txt` to skip OCR.

4. **Unsupported formats**: Only `.pdf`, `.docx`, `.pptx`, `.xlsx` are supported.
