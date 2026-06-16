# CNKI CSSCI Full-text Collection Skill

## Purpose

This skill collects Chinese academic journal articles from CNKI according to a professional search query. It is designed for building research corpora, especially for projects involving Chinese academic discourse, terminology translation, and CSSCI literature analysis.

## When to Use

Use this skill when the user needs to:

- collect CNKI journal articles;
- restrict results to CSSCI journals;
- save available HTML full texts as TXT files;
- build a corpus for literature review or discourse analysis;
- record failed or skipped articles for later manual checking.

## Input

The skill accepts the following inputs:

1. CNKI professional search query.
2. CNKI database code, usually `SCDB`.
3. Maximum number of result pages.
4. Output directory.
5. Delay settings.
6. Full-text loading timeout.

## Output

The skill produces:

1. TXT files of successfully collected full texts.
2. A CSV file named `failed_and_skipped_articles.csv`.
3. Console logs showing success, skipped, and failed counts.

## Main Tool

- `tools/cnki_fulltext_scraper.py`

## Human-in-the-loop Step

The user must manually log in to CNKI before automated collection starts.

## Ethical and Legal Notes

Use this skill only with legitimate access to CNKI. Do not use it to bypass paywalls, institutional restrictions, download limits, or copyright protections. The collected texts should be used only for permitted academic research purposes.