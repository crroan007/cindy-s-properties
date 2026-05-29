# Cindy's Properties — STR Portfolio Dashboard

A single-pane investment dashboard for the Wong family's short-term rental
portfolio (Atlanta area, 2016–2020). Built from 57 monthly Airbnb P&L
workbooks consolidated into one local SQLite database.

**Live dashboard:** <https://crroan007.github.io/cindy-s-properties/>

## What's in this repo

```
.
├── index.html                  ← the dashboard (open directly, or via Pages)
├── lauren_way_rental.db        ← single SQLite consolidating all 57 workbooks
├── xlsx/                       ← every source workbook as a real .xlsx
├── etl.py                      ← parses xlsx/*.xlsx → lauren_way_rental.db
├── gen_html.py                 ← renders index.html from the DB
└── dump_xlsx.py                ← diagnostic dumper for inspecting structure
```

## The data

5 properties tracked across 53 monthly P&Ls + 3 annual summary workbooks:

| Property                       | First reported |
|--------------------------------|----------------|
| 260 East Taylors Crossing      | 2016-09        |
| 4645 Valais Ct                 | 2016-09        |
| 5525 Taylor Road               | 2016-09        |
| 1120 Lauren Way                | 2017-09        |
| 115 Peachtree Memorial Drive   | 2017-11        |

Each monthly workbook has one tab per property + a Totals tab. Each tab is a
small ledger of `line_item / debit / credit` rows with a `Total / Net` summary.

## Database schema (`lauren_way_rental.db`)

| Table             | Rows  | Purpose                                                 |
|-------------------|-------|---------------------------------------------------------|
| `files`           |   57  | One row per source workbook (period, kind, tab list)    |
| `raw_cells`       | 7,938 | Lossless capture: every non-empty cell of every tab     |
| `ledger_entries`  | 1,400 | Structured line items per property × month              |
| `monthly_totals`  |   293 | Per-property + grand-total debits / credits / net       |

## Regenerating

```bash
# rebuild the DB from xlsx/
python etl.py

# rebuild index.html from the DB
python gen_html.py
```

Requires Python 3.10+ and `openpyxl`.

## Source files

The dashboard's "Source" links resolve to the original Google Sheets in the
owner's Drive (auth-gated) and to the local `.xlsx` mirrors in `xlsx/`.

## Notes / data-quality flags

- April–December 2020 for **1120 Lauren Way** show identical hard-coded totals
  (`352.37 / 0 / 1597.63`) in the source spreadsheets — those are stale template
  values, not parser bugs. Verified against `raw_cells`.
- Two duplicate workbooks (January 2017 and May 2019) are kept and disambiguated
  via the `b` suffix (`2017-01b`, `2019-05b`).
