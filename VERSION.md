# Version History

## v0.1.0 — Skill V1 Prototype

### Status

Basic functional prototype completed.

### Completed Features

* Built a reusable skill project structure.
* Added `SKILL.md` to define the purpose, usage scenarios, inputs, outputs, and ethical notes of the skill.
* Added `README.md` for human-readable project instructions.
* Added `requirements.txt` for dependency management.
* Added `run_skill.py` as the skill-level entry point.
* Placed the core CNKI collection script in `tools/cnki_fulltext_scraper.py`.
* Added example input and output documents under `examples/`.
* Added test notes under `tests/`.
* Supported manual CNKI login before automated collection.
* Supported CNKI professional search query execution.
* Supported CSSCI journal restriction.
* Supported available HTML full-text extraction.
* Supported TXT output for successfully collected full texts.
* Supported CSV recording for skipped or failed articles.

### Known Limitations

* Continuous collection may cause Chrome to slow down or freeze after processing multiple articles.
* CNKI page structure changes may break some CSS selectors or XPath expressions.
* Some articles do not provide HTML full-text access and will be skipped.
* The current version still requires manual login.
* The extraction success rate may vary depending on CNKI access permissions, browser stability, and article page structure.

### Recommended Use

This version is recommended for small-batch testing and corpus collection with conservative settings, for example:

```bash
python3 run_skill.py --max-pages 1 --delay-min 6 --delay-max 10
```

### Next Planned Improvements

* Improve browser stability during long-running collection.
* Add batch-size control to process a limited number of articles per run.
* Add more robust recovery after failed detail-page or HTML-reader loading.
* Add structured metadata export.
* Add a literature screening skill for classifying collected articles.
* Prepare integration with a future academic corpus-building agent.
