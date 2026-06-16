# CNKI Collection Skill

This project provides a reusable skill for collecting CNKI CSSCI journal articles through professional search.

## Project Structure

```text
cnki_collection_skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── tools/
│   └── cnki_fulltext_scraper.py
├── examples/
├── outputs/
└── tests/
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run:

```bash
python tools/cnki_fulltext_scraper.py
```

After the browser opens, manually log in to CNKI. Then return to the terminal and press Enter.

## Output

Collected full texts will be saved in:

```text
cnki_fulltext_output/
```

Failed or skipped articles will be recorded in:

```text
failed_and_skipped_articles.csv
```

## Notes

This skill is intended for academic research and corpus construction. Use it only with authorized access.