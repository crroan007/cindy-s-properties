"""
Generate edwin.html — a dedicated, no-filter view of 1120 Lauren Way (Acworth, GA)
in the simple Rent / Expense / Profit form requested by Edwin Wong.
"""
import sqlite3, os, json

ROOT = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(ROOT, "lauren_way_rental.db")
OUT  = os.path.join(ROOT, "edwin.html")

FILE_IDS = {  # imported from gen_html.py mapping (subset for Lauren Way periods)
    "2017-09":"1c34zYlAktHI5v__rj6ehdiSUr6dd6Gv9EYiFqJpLnJw",
    "2017-10":"19sG6iGh0P1c23N-Hb4ceRnX3awgHbYNOed5idMvJbls",
    "2017-11":"1Kx9OFW2NJfa4KdXkRxHmZZx8YKAoclyhl6T1hGr_M9g",
    "2017-12":"1mHqkH1vuaicEqPDiRK9X1NiktgoEzrbLzpoBtIGh7ck",
    "2018-01":"15o9NWTbHf6meo-V6qQ8-JTALNY-GBiwXJjh8JNXsqd0",
    "2018-02":"1B984xEsXf75Uh2S0TXknk1usci_ItntfxXuwudebneQ",
    "2018-03":"13RPzrykK0VHuq3Ob7nsdf07cBFM1PPV2DIuWS4OnyNU",
    "2018-04":"10hY5Mzax-XefrukbRTR7Tb2lmhsxWS-AVszYqfIh3w4",
    "2018-05":"1D_4RuY0kUAq1ZPMWNLdhnvQV1udjdou54kg_3Q1Kfps",
    "2018-06":"1LtnowLCEEJh8VBpRpToRXiz8Wimvkh82QrxtZPNCNLE",
    "2018-07":"1Xfj1CnxzsxMOmj-DZ8S6BZ2ywpvGrO7MJolRbF1ZSYg",
    "2018-08":"1e-dRZQEu2Zdn6QslESjmaCnb95X7eMeN5lAE9qHb2ho",
    "2018-09":"1jff4yikbbZVaDTzncnerFMkuG8pXHjKADuLq7d1SK3Q",
    "2018-10":"1ovT-vTvG97Mc6dlO3KQy5NTttaZNIybBQgskAA3tkJ0",
    "2018-11":"1uqiEmuMazaSx83T0iWwITP9xJwbFYfMwQfI0W4K7aEM",
    "2018-12":"1y_EgIql3HO_un5sG-iE9UOhOiRHTu8zbf_d0cDEF86s",
    "2019-01":"1-XmjCevVp7vC-35YY2cPyiMBgHUQU0NG6mJ_kcg8v14",
    "2019-02":"18oIDcZdyI-ooI-O2FjV3huVl8TWO4dTw1mNkuuBRMM8",
    "2019-03":"1DMTPqA4ee0txts67ZZuOoNN5CMqWuqWptyvxQwHTzTw",
    "2019-04":"1bYleTWVfgkRgd1ySLVzeEc-ha3UjDzAKbzWPotmmWO4",
    "2019-05":"1pGR41xhSWS070nyWaBQgxxi4ElFWtW5SM0_S1UP3MOg",
    "2019-06":"1pL2OqZ3PYBRhaqIE4n-hei9tVsbtJdMuDSmqqTl5s-w",
    "2019-07":"1hHd7lwg79sLqRoDfUhZjlAoe_3M2DvwyG1WAONzMsew",
    "2019-08":"10YTplEW98U7--TT-b_gYi9IcxsjEnesefghATcFN-uw",
    "2019-09":"1HkXni4P2mBNqJeFelq6eay2zhn7vZpKsdXHay9A16yU",
    "2019-10":"1GhEg9ahKmb1rjX55IblpxD6NoiXB_2y_050_PVYgLew",
    "2019-11":"14osA8eHobwlCbDBIxSGeUBqycjsvLQGk5Od7Y6ysdYs",
    "2019-12":"1yKHrODCjYomiXSJRJSBe8vwP31evOmMqXcx2E1Kt164",
    "2020-01":"1K1d0Hm_n0cLQbAMhgAWOPz5o8uKEbSmb4wZnn4po5To",
    "2020-02":"1UQMmrnqSFX2-BFvt2P5KLaZpjDL5WOZYgqJ7AAcBYBI",
    "2020-03":"1SrFoZcOTjbLRHtd9ftV-CfWOFr1q0_019aFAiBS-KvQ",
    "2020-04":"1ZTL_wGKcQYTiRn_RL71OIeL5fT7KyhhFtyUu_4PgnnY",
    "2020-05":"1uOPpMif1Ltd0TK7_7afBfEas77wwOar9-o32Xv_IPvM",
    "2020-06":"1kcqhXXGChqDrlHggQkShvTevlOMvDEwrYj6s0sly2VA",
    "2020-07":"16QFMlkS4qcWXJrhlK86dWhkJyJRe5P1OhAdMo9joRmY",
    "2020-08":"1MsfEtvHHjr7g_WcW1zTqxm8o2qYP-RakLQ2d4THeqXM",
    "2020-09":"1a6mt4pJnXCGkNvV2cqDnJcuwyOrHntv_Vhl_nTEb1gk",
    "2020-10":"17_8Fq50mNHkxp3sYHHyuxxUQ8GGC3DITdeSMQxsk3cU",
    "2020-11":"12qi3FoUeuKUBqpocythE6cuazCPDVcBHWycYP2sFA3A",
    "2020-12":"1vIgUddd05I393Or2zlTG7xBAmzQcR9wFnDBIw8NGYCo",
}

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# Months whose source spreadsheets contain Cindy's stale-template numbers
# (identical Total/Net values copy-pasted across months). Verified against raw_cells.
STALE = {
    ("2020-04","2020-05","2020-06","2020-07","2020-08","2020-09","2020-10","2020-11","2020-12"): "Stale template — source spreadsheet has identical hardcoded totals ($352.37 / $0 / -$352.37) across all these months. Treat as unreliable.",
    ("2018-03","2018-04","2018-05"): "Identical template — source has the same rent and expense across these three months. Likely copy-paste.",
}

def stale_note(period):
    for ks, msg in STALE.items():
        if period in ks: return msg
    return None


def fetch():
    con = sqlite3.connect(DB)
    c = con.cursor()
    rows = list(c.execute("""
        SELECT year, month,
               COALESCE(SUM(CASE WHEN line_item LIKE '%rent%' OR line_item LIKE '%rental%' THEN credit END),0) AS rent,
               COALESCE(SUM(CASE WHEN NOT (line_item LIKE '%rent%' OR line_item LIKE '%rental%') THEN debit END),0) AS expense,
               GROUP_CONCAT(DISTINCT source_file) AS sources
        FROM ledger_entries
        WHERE property = '1120 Lauren Way'
        GROUP BY year, month
        ORDER BY year, month
    """))
    # filter out the 2016 stray row (one $31 water entry before tracking really started)
    rows = [r for r in rows if not (r[0]==2016)]
    con.close()
    return rows


def fmt(v): return '${:,.2f}'.format(v) if v else '$0.00'
def cls(p):
    if p > 0: return 'pos'
    if p < 0: return 'neg'
    return 'dim'


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>1120 Lauren Way (Acworth) — Rent / Expense / Profit</title>
<style>
  :root {
    --bg:#0a0d13; --panel:#12161f; --panel2:#1a2030; --border:#262e42;
    --text:#e6e9ef; --muted:#7c8499; --dim:#5b6378; --accent:#5aa9ff;
    --pos:#4ade80; --neg:#f87171; --warn:#fbbf24;
  }
  * { box-sizing:border-box; }
  body { margin:0; font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); }
  header { padding:22px 26px; background:linear-gradient(180deg,var(--panel),var(--bg)); border-bottom:1px solid var(--border); }
  header h1 { margin:0 0 6px; font-size:22px; font-weight:700; letter-spacing:-0.01em; }
  header .sub { color:var(--muted); font-size:13px; }
  header .links { margin-top:10px; font-size:12px; }
  header .links a { color:var(--accent); text-decoration:none; margin-right:14px; }
  header .links a:hover { text-decoration:underline; }
  main { padding:22px 26px; max-width:1100px; margin:0 auto; display:flex; flex-direction:column; gap:18px; }
  section { background:var(--panel); border:1px solid var(--border); border-radius:9px; padding:14px 16px; }
  section h2 { margin:0 0 12px; font-size:13px; font-weight:600; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); }

  .kpis { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; }
  .kpi { background:var(--panel2); border:1px solid var(--border); border-radius:7px; padding:12px 14px; }
  .kpi .label { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px; }
  .kpi .value { font-size:24px; font-weight:700; font-variant-numeric:tabular-nums; }
  .kpi .value.pos { color:var(--pos); }
  .kpi .value.neg { color:var(--neg); }
  .kpi .delta { color:var(--muted); font-size:11px; margin-top:4px; }

  table { width:100%; border-collapse:collapse; font-size:13.5px; }
  th, td { padding:7px 10px; border-bottom:1px solid var(--border); text-align:right; vertical-align:middle; font-variant-numeric:tabular-nums; }
  th:first-child, td:first-child { text-align:left; }
  th { color:var(--muted); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.04em; background:var(--panel); position:sticky; top:0; }
  tr:hover td { background:var(--panel2); }
  tr.year-sub td { background:var(--panel2); font-weight:600; border-top:1px solid var(--border); }
  tr.grand td { background:#162033; font-weight:700; font-size:14.5px; border-top:2px solid var(--accent); }
  .pos { color:var(--pos); }
  .neg { color:var(--neg); }
  .dim { color:var(--dim); }
  .warn-pill { display:inline-block; background:rgba(251,191,36,0.18); color:var(--warn); padding:1px 7px; border-radius:99px; font-size:10.5px; margin-left:6px; cursor:help; }
  a.src { color:var(--accent); text-decoration:none; font-size:11px; padding:1px 7px; border:1px solid var(--border); border-radius:4px; margin-right:3px; }
  a.src:hover { background:var(--panel2); }

  .notes { color:var(--muted); font-size:12px; line-height:1.6; }
  .notes b { color:var(--text); }
  footer { padding:18px 26px; color:var(--dim); font-size:11px; border-top:1px solid var(--border); text-align:center; }
</style>
</head>
<body>

<header>
  <h1>1120 Lauren Way · Acworth, GA</h1>
  <div class="sub">Monthly Rent / Expense / Profit — from Cindy's Airbnb P&amp;L workbooks, Sept&nbsp;2017 – Dec&nbsp;2020</div>
  <div class="links">
    <a href="index.html">← Full portfolio dashboard</a>
    <a href="https://github.com/crroan007/cindy-s-properties" target="_blank">Source repo ↗</a>
  </div>
</header>

<main>

  <section>
    <h2>Lifetime totals</h2>
    <div class="kpis">__KPIS__</div>
  </section>

  <section>
    <h2>Monthly breakdown</h2>
    <table>
      <thead>
        <tr><th>Period</th><th>Rent</th><th>Expense</th><th>Profit</th><th>Source workbook</th></tr>
      </thead>
      <tbody>__ROWS__</tbody>
    </table>
  </section>

</main>

<footer>
  Generated from <code>lauren_way_rental.db</code> via <code>gen_edwin.py</code>. Single-file, offline-capable. Every "Drive" link opens the original source spreadsheet.
</footer>

</body>
</html>
"""


def build():
    rows = fetch()
    # totals
    grand_r = sum(r[2] for r in rows)
    grand_e = sum(r[3] for r in rows)
    grand_p = grand_r - grand_e
    by_year = {}
    for y, m, r, e, src in rows:
        by_year.setdefault(y, [0,0]); by_year[y][0]+=r; by_year[y][1]+=e

    # KPI cards
    months_reported = len(rows)
    months_with_rent = sum(1 for r in rows if r[2] > 0)
    avg_mo_rent = grand_r / months_reported if months_reported else 0
    avg_mo_profit = grand_p / months_reported if months_reported else 0
    kpis_html = ''.join([
        f'<div class="kpi"><div class="label">Total Rent collected</div><div class="value">${grand_r:,.0f}</div><div class="delta">over {months_reported} months</div></div>',
        f'<div class="kpi"><div class="label">Total Expense</div><div class="value">${grand_e:,.0f}</div><div class="delta">all categories combined</div></div>',
        f'<div class="kpi"><div class="label">Net Profit</div><div class="value {cls(grand_p)}">${grand_p:,.0f}</div><div class="delta">Rent − Expense</div></div>',
        f'<div class="kpi"><div class="label">Avg monthly Rent</div><div class="value">${avg_mo_rent:,.0f}</div><div class="delta">{months_with_rent}/{months_reported} months produced rent</div></div>',
        f'<div class="kpi"><div class="label">Avg monthly Profit</div><div class="value {cls(avg_mo_profit)}">${avg_mo_profit:,.0f}</div><div class="delta">across full period</div></div>',
    ])

    # Rows
    rows_html = []
    current_year = None
    for y, m, r, e, src in rows:
        if current_year is not None and y != current_year:
            yr_r, yr_e = by_year[current_year]; yr_p = yr_r - yr_e
            rows_html.append(f'<tr class="year-sub"><td>{current_year} total</td><td>${yr_r:,.2f}</td><td>${yr_e:,.2f}</td><td class="{cls(yr_p)}">${yr_p:,.2f}</td><td></td></tr>')
        current_year = y
        period = f'{y}-{m:02d}'
        sf = (src or '').split(',')[0]
        fid = FILE_IDS.get(sf, '')
        drive = f'<a class="src" href="https://docs.google.com/spreadsheets/d/{fid}/edit" target="_blank">Drive ↗</a>' if fid else ''
        local = f'<a class="src" href="xlsx/{sf}.xlsx" target="_blank">XLSX</a>' if sf else ''
        profit = r - e
        rows_html.append(
            f'<tr><td>{period}</td>'
            f'<td>${r:,.2f}</td><td>${e:,.2f}</td><td class="{cls(profit)}">${profit:,.2f}</td>'
            f'<td>{drive} {local}</td></tr>'
        )
    # last year subtotal
    if current_year is not None:
        yr_r, yr_e = by_year[current_year]; yr_p = yr_r - yr_e
        rows_html.append(f'<tr class="year-sub"><td>{current_year} total</td><td>${yr_r:,.2f}</td><td>${yr_e:,.2f}</td><td class="{cls(yr_p)}">${yr_p:,.2f}</td><td></td></tr>')
    rows_html.append(f'<tr class="grand"><td>GRAND TOTAL</td><td>${grand_r:,.2f}</td><td>${grand_e:,.2f}</td><td class="{cls(grand_p)}">${grand_p:,.2f}</td><td></td></tr>')

    html = (HTML
            .replace('__KPIS__', kpis_html)
            .replace('__ROWS__', '\n'.join(rows_html)))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {OUT}  ({os.path.getsize(OUT)} bytes)')
    print(f'  months reported: {months_reported}')
    print(f'  rent  total: ${grand_r:,.2f}')
    print(f'  exp   total: ${grand_e:,.2f}')
    print(f'  net   total: ${grand_p:,.2f}')


if __name__ == '__main__':
    build()
