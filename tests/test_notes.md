# Test Notes

## Test 1: One-page collection

### Command

```bash
python3 tools/cnki_fulltext_scraper.py
```

### Test Setting

```text
max_pages = 1
```

### Expected Result

- Chrome opens successfully.
- The user can manually log in to CNKI.
- The script enters the professional search page.
- CSSCI restriction is selected.
- The result page is parsed.
- Available HTML full texts are saved as TXT files.
- Skipped or failed records are saved to CSV.

### Actual Result

```text
Status: Passed
Date:
Successful files:
Skipped articles:
Failed articles:
Output folder:
```

## Common Problems

### Browser does not open

Check Chrome and ChromeDriver compatibility.

### CNKI page structure changes

Update CSS selectors or XPath expressions.

### No HTML full text

Some articles may not provide HTML reading access.

### Text extraction is too short

The HTML full-text page may not have fully loaded.

### SSL certificate error

Run the Python certificate installation command on macOS, then retry.