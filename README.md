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
python3 run_skill.py
## Usage

Run the skill:

```bash
python3 run_skill.py
```

After the browser opens, manually log in to CNKI. Then return to the terminal and press Enter.

## Recommended Usage

Run one page with safer delay settings:

```bash
python3 run_skill.py --max-pages 1 --delay-min 6 --delay-max 10
```

Specify an output directory:

```bash
python3 run_skill.py --max-pages 1 --output-dir outputs/test_run
```

Use a custom CNKI professional search query:

```bash
python3 run_skill.py \
  --query "SU%='马克思主义' AND FT='术语' AND YE<2018" \
  --max-pages 1
```
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