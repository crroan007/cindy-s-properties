"""
Build a single-pane PE-grade rental portfolio dashboard from
lauren_way_rental.db. Output: index.html (self-contained, no server, no CDN).

Embeds:
  - files        : 57 source workbooks (with Drive fileIds for deep-link)
  - totals       : monthly_totals per (property, month, source)
  - entries      : ledger line items (property + line_item + debit + credit)
  - year_end     : raw cell dump of the three annual-summary files
  - PROPS        : canonical property list / display order
"""
import sqlite3, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(ROOT, "lauren_way_rental.db")
OUT  = os.path.join(ROOT, "index.html")

FILE_IDS = {
    "2016-09":     "1epQ-UPfEPtNm9lvRwMBuoO_bX5LhSnrIA8LXach5JJo",
    "2016-10":     "1KwiGtaF9DUFTZqdg8RTJcOoi9l9RKLfYFGNoAp5OA84",
    "2016-11":     "15bJVfAh7NC-Xf4DjNuPc6GXt87hmTLr9ntYbXm3IbL0",
    "2016-12":     "1oQozxVU4jgUsSeAuR-OzuDWh76-KYQRxFbDz83FMTTE",
    "2016-totals": "17R9jAanE7-dQeO77NaGTb-aexc2PsaWT5iFYDB3HTD0",
    "2017-01":     "1VA8PrPRWLjJNTUnnHYsjcRrXfVKk5S1KublYyWKvra0",
    "2017-01b":    "1TylkuionSC8enCZFOnnHV9t9foaRXiTaIAOlwnJ7d1k",
    "2017-02":     "1PmIPxGXKff7Ev_HVSwoOzjXolGabOqRgOEVZ_q0K9ZM",
    "2017-03":     "1O-9pzpwXaJ7RCspbFrExhrvsimcdq682ZmmSoEABljc",
    "2017-04":     "10YRkHA7gsiyawEa8cYhbNvT0IvGMVk_4cNOntmbJUzc",
    "2017-05":     "1BsDHxR27ZRPnWh0_cRVOak8BFPRX82zlY0BLhVIpKYo",
    "2017-06":     "1MKW_CVNIr9YwkarkB79Rdq7mAmUqG9Q390zAWGALGNY",
    "2017-07":     "1RByPv0V96ESDZX2ygdRywN3TXu1QISqVXIUbsVuf6ts",
    "2017-08":     "1bfoqeTIurc8x3xNLjDs6fXHSiwPt870hfC8a62LEFns",
    "2017-09":     "1c34zYlAktHI5v__rj6ehdiSUr6dd6Gv9EYiFqJpLnJw",
    "2017-10":     "19sG6iGh0P1c23N-Hb4ceRnX3awgHbYNOed5idMvJbls",
    "2017-11":     "1Kx9OFW2NJfa4KdXkRxHmZZx8YKAoclyhl6T1hGr_M9g",
    "2017-12":     "1mHqkH1vuaicEqPDiRK9X1NiktgoEzrbLzpoBtIGh7ck",
    "2017-totals": "1umlbbZLQ3q3IZVrFt7LER2aOIsSSrgJgmz_8D6wDsm4",
    "2018-01":     "15o9NWTbHf6meo-V6qQ8-JTALNY-GBiwXJjh8JNXsqd0",
    "2018-02":     "1B984xEsXf75Uh2S0TXknk1usci_ItntfxXuwudebneQ",
    "2018-03":     "13RPzrykK0VHuq3Ob7nsdf07cBFM1PPV2DIuWS4OnyNU",
    "2018-04":     "10hY5Mzax-XefrukbRTR7Tb2lmhsxWS-AVszYqfIh3w4",
    "2018-05":     "1D_4RuY0kUAq1ZPMWNLdhnvQV1udjdou54kg_3Q1Kfps",
    "2018-06":     "1LtnowLCEEJh8VBpRpToRXiz8Wimvkh82QrxtZPNCNLE",
    "2018-07":     "1Xfj1CnxzsxMOmj-DZ8S6BZ2ywpvGrO7MJolRbF1ZSYg",
    "2018-08":     "1e-dRZQEu2Zdn6QslESjmaCnb95X7eMeN5lAE9qHb2ho",
    "2018-09":     "1jff4yikbbZVaDTzncnerFMkuG8pXHjKADuLq7d1SK3Q",
    "2018-10":     "1ovT-vTvG97Mc6dlO3KQy5NTttaZNIybBQgskAA3tkJ0",
    "2018-11":     "1uqiEmuMazaSx83T0iWwITP9xJwbFYfMwQfI0W4K7aEM",
    "2018-12":     "1y_EgIql3HO_un5sG-iE9UOhOiRHTu8zbf_d0cDEF86s",
    "2018-totals": "10WJ9VmoJS7xtT-VyaKZokFB6_YkP4KkaU2-jpUj85Gg",
    "2019-01":     "1-XmjCevVp7vC-35YY2cPyiMBgHUQU0NG6mJ_kcg8v14",
    "2019-02":     "18oIDcZdyI-ooI-O2FjV3huVl8TWO4dTw1mNkuuBRMM8",
    "2019-03":     "1DMTPqA4ee0txts67ZZuOoNN5CMqWuqWptyvxQwHTzTw",
    "2019-04":     "1bYleTWVfgkRgd1ySLVzeEc-ha3UjDzAKbzWPotmmWO4",
    "2019-05":     "1pGR41xhSWS070nyWaBQgxxi4ElFWtW5SM0_S1UP3MOg",
    "2019-05b":    "194f62YjTJcqCTOp0IM4KF_sbwLQF12-yyp3VdDxVeAo",
    "2019-06":     "1pL2OqZ3PYBRhaqIE4n-hei9tVsbtJdMuDSmqqTl5s-w",
    "2019-07":     "1hHd7lwg79sLqRoDfUhZjlAoe_3M2DvwyG1WAONzMsew",
    "2019-08":     "10YTplEW98U7--TT-b_gYi9IcxsjEnesefghATcFN-uw",
    "2019-09":     "1HkXni4P2mBNqJeFelq6eay2zhn7vZpKsdXHay9A16yU",
    "2019-10":     "1GhEg9ahKmb1rjX55IblpxD6NoiXB_2y_050_PVYgLew",
    "2019-11":     "14osA8eHobwlCbDBIxSGeUBqycjsvLQGk5Od7Y6ysdYs",
    "2019-12":     "1yKHrODCjYomiXSJRJSBe8vwP31evOmMqXcx2E1Kt164",
    "2020-01":     "1K1d0Hm_n0cLQbAMhgAWOPz5o8uKEbSmb4wZnn4po5To",
    "2020-02":     "1UQMmrnqSFX2-BFvt2P5KLaZpjDL5WOZYgqJ7AAcBYBI",
    "2020-03":     "1SrFoZcOTjbLRHtd9ftV-CfWOFr1q0_019aFAiBS-KvQ",
    "2020-04":     "1ZTL_wGKcQYTiRn_RL71OIeL5fT7KyhhFtyUu_4PgnnY",
    "2020-05":     "1uOPpMif1Ltd0TK7_7afBfEas77wwOar9-o32Xv_IPvM",
    "2020-06":     "1kcqhXXGChqDrlHggQkShvTevlOMvDEwrYj6s0sly2VA",
    "2020-07":     "16QFMlkS4qcWXJrhlK86dWhkJyJRe5P1OhAdMo9joRmY",
    "2020-08":     "1MsfEtvHHjr7g_WcW1zTqxm8o2qYP-RakLQ2d4THeqXM",
    "2020-09":     "1a6mt4pJnXCGkNvV2cqDnJcuwyOrHntv_Vhl_nTEb1gk",
    "2020-10":     "17_8Fq50mNHkxp3sYHHyuxxUQ8GGC3DITdeSMQxsk3cU",
    "2020-11":     "12qi3FoUeuKUBqpocythE6cuazCPDVcBHWycYP2sFA3A",
    "2020-12":     "1vIgUddd05I393Or2zlTG7xBAmzQcR9wFnDBIw8NGYCo",
}

PROPS = [
    "1120 Lauren Way",
    "260 East Taylors Crossing",
    "4645 Valais Ct",
    "5525 Taylor Road",
    "115 Peachtree Memorial Drive",
]


def fetch_data():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    c = con.cursor()

    files = []
    for r in c.execute("SELECT source_file,kind,year,month,variant,tab_names FROM files ORDER BY source_file"):
        files.append({
            "source_file": r["source_file"], "kind": r["kind"],
            "year": r["year"], "month": r["month"], "variant": r["variant"],
            "tabs": r["tab_names"].split("|") if r["tab_names"] else [],
            "file_id": FILE_IDS.get(r["source_file"], ""),
        })

    totals = []
    for r in c.execute("SELECT source_file,year,month,variant,property,total_debits,total_credits,net FROM monthly_totals ORDER BY year,month,source_file,property"):
        totals.append({
            "source_file": r["source_file"], "year": r["year"], "month": r["month"], "variant": r["variant"],
            "property": r["property"], "debits": r["total_debits"], "credits": r["total_credits"], "net": r["net"],
        })

    entries = []
    for r in c.execute("SELECT source_file,year,month,variant,property,line_item,debit,credit FROM ledger_entries ORDER BY year,month,source_file,property,line_item"):
        entries.append({
            "source_file": r["source_file"], "year": r["year"], "month": r["month"], "variant": r["variant"],
            "property": r["property"], "line_item": r["line_item"], "debit": r["debit"], "credit": r["credit"],
        })

    year_end = []
    for r in c.execute("SELECT source_file,tab,row,col,value FROM raw_cells WHERE source_file LIKE '%-totals' ORDER BY source_file,tab,row,col"):
        year_end.append({
            "source_file": r["source_file"], "tab": r["tab"], "row": r["row"], "col": r["col"], "value": r["value"],
        })

    con.close()
    return {"files": files, "totals": totals, "entries": entries, "year_end_cells": year_end, "props": PROPS}


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Wong Portfolio — STR Investment Dashboard</title>
<style>
  :root {
    --bg:#0a0d13; --panel:#12161f; --panel2:#1a2030; --panel3:#222a3d;
    --border:#262e42; --text:#e6e9ef; --muted:#7c8499; --dim:#5b6378;
    --accent:#5aa9ff; --accent2:#7ed4ff;
    --pos:#4ade80; --neg:#f87171; --warn:#fbbf24;
    --cat-rev:#4ade80; --cat-mortgage:#a78bfa; --cat-hoa:#fb923c;
    --cat-util:#60a5fa; --cat-maint:#fbbf24; --cat-ins:#f472b6;
    --cat-tax:#34d399; --cat-furn:#22d3ee; --cat-other:#94a3b8;
  }
  * { box-sizing:border-box; }
  body { margin:0; font:13px/1.45 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); }
  header { padding:14px 22px; background:linear-gradient(180deg,var(--panel),var(--bg)); border-bottom:1px solid var(--border); }
  header .row { display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
  header h1 { margin:0; font-size:19px; font-weight:700; letter-spacing:-0.01em; }
  header .sub { color:var(--muted); font-size:12px; }
  header .crumbs { color:var(--muted); font-size:11px; margin-top:4px; }
  header .crumbs b { color:var(--text); font-weight:600; }

  .filters { padding:10px 22px; background:var(--panel); border-bottom:1px solid var(--border); display:flex; gap:18px; align-items:flex-start; flex-wrap:wrap; }
  .filter-group { display:flex; flex-direction:column; gap:4px; }
  .filter-group .lbl { font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:600; }
  .chips { display:flex; gap:5px; flex-wrap:wrap; }
  .chip { background:var(--panel2); color:var(--muted); padding:4px 9px; border-radius:99px; font-size:11px; cursor:pointer; border:1px solid transparent; user-select:none; }
  .chip:hover { color:var(--text); border-color:var(--border); }
  .chip.on { background:var(--accent); color:#0a0d13; font-weight:600; }
  .chip.on.cat-rev { background:var(--cat-rev); }
  .chip.on.cat-mortgage { background:var(--cat-mortgage); }
  .chip.on.cat-hoa { background:var(--cat-hoa); }
  .chip.on.cat-util { background:var(--cat-util); }
  .chip.on.cat-maint { background:var(--cat-maint); }
  .chip.on.cat-ins { background:var(--cat-ins); }
  .chip.on.cat-tax { background:var(--cat-tax); }
  .chip.on.cat-furn { background:var(--cat-furn); }
  .chip.on.cat-other { background:var(--cat-other); color:#0a0d13; }
  .filter-group .search { background:var(--bg); color:var(--text); border:1px solid var(--border); border-radius:5px; padding:4px 8px; font:inherit; min-width:180px; }
  .filter-group .btn { background:var(--panel2); color:var(--text); border:1px solid var(--border); border-radius:5px; padding:4px 12px; font:inherit; cursor:pointer; }
  .filter-group .btn:hover { background:var(--panel3); }

  main { padding:18px 22px; display:flex; flex-direction:column; gap:18px; max-width:1800px; margin:0 auto; }
  section { background:var(--panel); border:1px solid var(--border); border-radius:9px; padding:14px 16px; }
  section h2 { margin:0 0 12px; font-size:12px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
  section h2 .sub { color:var(--dim); font-weight:400; text-transform:none; letter-spacing:0; font-size:11px; margin-left:8px; }
  .grid-cards { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:10px; }
  .kpi { background:var(--panel2); border:1px solid var(--border); border-radius:7px; padding:10px 12px; }
  .kpi .label { color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px; }
  .kpi .value { font-size:22px; font-weight:700; font-variant-numeric:tabular-nums; line-height:1.1; }
  .kpi .delta { color:var(--muted); font-size:11px; margin-top:2px; }
  .kpi .delta.pos { color:var(--pos); }
  .kpi .delta.neg { color:var(--neg); }
  .kpi .spark { margin-top:6px; height:24px; }
  .kpi.wide { grid-column:span 2; }

  .prop-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(290px, 1fr)); gap:12px; }
  .prop-card { background:var(--panel2); border:1px solid var(--border); border-radius:7px; padding:12px 14px; }
  .prop-card h3 { margin:0 0 4px; font-size:13px; }
  .prop-card .meta { color:var(--muted); font-size:11px; margin-bottom:8px; }
  .prop-card .stats { display:grid; grid-template-columns:repeat(2,1fr); gap:6px 12px; font-size:11px; }
  .prop-card .stats .row { display:flex; justify-content:space-between; }
  .prop-card .stats .row .lbl { color:var(--muted); }
  .prop-card .spark { margin-top:8px; height:42px; }

  table { width:100%; border-collapse:collapse; font-size:12.5px; }
  th, td { padding:6px 9px; border-bottom:1px solid var(--border); text-align:right; vertical-align:top; }
  th:first-child, td:first-child { text-align:left; }
  th { color:var(--muted); font-weight:600; font-size:10.5px; text-transform:uppercase; letter-spacing:.04em; }
  tr:hover td { background:var(--panel2); }
  .num { font-variant-numeric:tabular-nums; }
  .pos { color:var(--pos); }
  .neg { color:var(--neg); }
  .muted { color:var(--muted); }
  .dim { color:var(--dim); }
  .pill { display:inline-block; padding:1px 6px; border-radius:99px; font-size:10px; border:1px solid var(--border); color:var(--muted); }
  a { color:var(--accent); text-decoration:none; }
  a:hover { text-decoration:underline; }
  .clickable { cursor:pointer; }
  .clickable:hover { background:var(--panel2); }

  /* Heatmap */
  .heat { display:grid; gap:1px; background:var(--border); padding:1px; border-radius:5px; }
  .heat .cell { background:var(--panel); padding:4px 6px; font-size:10px; min-height:22px; text-align:right; }
  .heat .cell.head { background:var(--panel2); color:var(--muted); font-size:10px; text-transform:uppercase; text-align:right; }
  .heat .cell.label { text-align:left; }
  .heat .cell.empty { background:var(--panel); color:var(--dim); }

  /* Year grid */
  .year-block { margin-top:14px; }
  .year-block h3 { font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; margin:0 0 6px; }
  .year-block .summary { color:var(--muted); font-size:11px; margin-bottom:6px; }

  details { background:var(--panel2); border:1px solid var(--border); border-radius:6px; padding:8px 12px; margin-top:6px; }
  details summary { cursor:pointer; color:var(--muted); font-size:12px; }

  .legend { display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:var(--muted); margin-bottom:8px; }
  .legend .item { display:inline-flex; align-items:center; gap:5px; }
  .legend .sw { width:10px; height:10px; border-radius:2px; }

  .modal { position:fixed; inset:0; background:rgba(0,0,0,.65); display:none; align-items:center; justify-content:center; padding:24px; z-index:20; }
  .modal.open { display:flex; }
  .modal .box { background:var(--panel); border:1px solid var(--border); border-radius:8px; max-width:980px; width:100%; max-height:90vh; overflow:auto; padding:18px; }
  .modal h3 { margin:0 0 4px; font-size:15px; }
  .modal .close { float:right; cursor:pointer; color:var(--muted); padding:2px 8px; }
  .badges { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
  .badge { background:var(--panel2); padding:3px 8px; border-radius:4px; font-size:11px; border:1px solid var(--border); }
  .badge a { color:var(--accent); }

  .twocol { display:grid; grid-template-columns: 1fr 1fr; gap:18px; }
  @media (max-width: 1200px) { .twocol { grid-template-columns: 1fr; } }

  .src-links a { padding:1px 6px; border:1px solid var(--border); border-radius:4px; font-size:11px; margin-right:4px; }
  footer { padding:14px 22px; color:var(--dim); font-size:11px; border-top:1px solid var(--border); text-align:center; }
</style>
</head>
<body>

<header>
  <div class="row">
    <h1>Wong Portfolio — STR Investment Dashboard</h1>
    <span class="sub">Atlanta-area short-term rental P&amp;L · 2016–2020</span>
  </div>
  <div class="crumbs">
    <b id="hd-files">0</b> source workbooks ·
    <b id="hd-months">0</b> months of P&amp;L ·
    <b id="hd-props">5</b> properties ·
    <b id="hd-entries">0</b> line items ·
    <b id="hd-totals">0</b> monthly totals ·
    DB: <code>lauren_way_rental.db</code>
  </div>
</header>

<div class="filters">
  <div class="filter-group">
    <span class="lbl">Properties</span>
    <div class="chips" id="f-prop"></div>
  </div>
  <div class="filter-group">
    <span class="lbl">Years</span>
    <div class="chips" id="f-year"></div>
  </div>
  <div class="filter-group">
    <span class="lbl">Expense category</span>
    <div class="chips" id="f-cat"></div>
  </div>
  <div class="filter-group">
    <span class="lbl">Search line item</span>
    <input id="f-search" class="search" placeholder="e.g. mortgage, water">
  </div>
  <div class="filter-group">
    <span class="lbl">&nbsp;</span>
    <button class="btn" id="f-reset">Reset filters</button>
  </div>
  <div class="filter-group" style="margin-left:auto">
    <span class="lbl">Match</span>
    <span class="muted" id="match-info" style="font-size:11px">—</span>
  </div>
</div>

<main>

  <!-- KPI strip -->
  <section>
    <h2>Executive KPIs <span class="sub">— current filter scope</span></h2>
    <div class="grid-cards" id="kpis"></div>
  </section>

  <!-- Per-property cards -->
  <section>
    <h2>Property performance <span class="sub">— per-property scorecard with trend sparkline</span></h2>
    <div class="prop-grid" id="prop-cards"></div>
  </section>

  <!-- Cash-flow + expense breakdown -->
  <div class="twocol">
    <section>
      <h2>Monthly cash-flow <span class="sub">— revenue, expenses, net over time</span></h2>
      <div id="cashflow-legend" class="legend"></div>
      <div id="cashflow-chart"></div>
    </section>
    <section>
      <h2>Expense composition by year <span class="sub">— click a year's stack for category breakdown</span></h2>
      <div id="expense-legend" class="legend"></div>
      <div id="expense-chart"></div>
    </section>
  </div>

  <div class="twocol">
    <section>
      <h2>Revenue contribution by property <span class="sub">— concentration risk view</span></h2>
      <div id="contrib-chart"></div>
    </section>
    <section>
      <h2>Cumulative net P&amp;L <span class="sub">— wealth-creation trajectory per property</span></h2>
      <div id="cumchart"></div>
    </section>
  </div>

  <!-- Heatmap -->
  <section>
    <h2>Net heatmap <span class="sub">— green = profit, red = loss, intensity = magnitude</span></h2>
    <div id="heatmap"></div>
  </section>

  <!-- Year tables -->
  <section>
    <h2>Year-grouped monthly Net <span class="sub">— click a cell for line items + source link</span></h2>
    <div id="grid"></div>
  </section>

  <!-- Annual rollups -->
  <div class="twocol">
    <section>
      <h2>Annual portfolio rollup</h2>
      <table id="t-year"></table>
    </section>
    <section>
      <h2>Per-property annual rollup</h2>
      <table id="t-prop-year"></table>
    </section>
  </div>

  <!-- Line items drill -->
  <section>
    <h2>Line items <span class="sub">— filtered by all the above + line-item search</span></h2>
    <div id="lineitems"></div>
  </section>

  <!-- Source workbooks -->
  <section>
    <h2>Source workbooks <span class="sub">— links to Google Drive + local XLSX</span></h2>
    <table id="t-files"></table>
  </section>

  <!-- Year-end annual files -->
  <section>
    <h2>Year-end summary files <span class="sub">— different layout, captured as raw cells</span></h2>
    <div id="year-end"></div>
  </section>

</main>

<div class="modal" id="modal"><div class="box">
  <span class="close" onclick="closeModal()">✕ close</span>
  <h3 id="m-title"></h3>
  <div class="badges" id="m-badges"></div>
  <div id="m-body"></div>
</div></div>

<footer>
  Self-contained dashboard — open offline. Source-of-truth links to Drive use the user's authenticated session.
</footer>

<script>
/* =================================================================
 * DATA + CONSTANTS
 * ================================================================= */
const DATA = __DATA__;
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

const CATEGORIES = [
  ['Revenue',                'cat-rev',      '#4ade80'],
  ['Mortgage',               'cat-mortgage', '#a78bfa'],
  ['HOA',                    'cat-hoa',      '#fb923c'],
  ['Utilities',              'cat-util',     '#60a5fa'],
  ['Maintenance',            'cat-maint',    '#fbbf24'],
  ['Insurance',              'cat-ins',      '#f472b6'],
  ['Taxes',                  'cat-tax',      '#34d399'],
  ['Furnishings & Supplies', 'cat-furn',     '#22d3ee'],
  ['Other',                  'cat-other',    '#94a3b8'],
];
const CAT_COLOR = Object.fromEntries(CATEGORIES.map(c => [c[0], c[2]]));
const CAT_CLASS = Object.fromEntries(CATEGORIES.map(c => [c[0], c[1]]));

function categorize(line_item) {
  const l = String(line_item||'').toLowerCase().trim();
  if (!l) return 'Other';
  if (/(rental|^rent$|^rent\b|^rent\s)/.test(l)) return 'Revenue';
  if (/mortgage/.test(l)) return 'Mortgage';
  if (/\bhoa\b/.test(l)) return 'HOA';
  if (/(gas\b|electric|trash|water|sewer|internet|cable|cobb|util|waste\s*mgmt|republic)/.test(l)) return 'Utilities';
  if (/(lawn|pest|pool|repair|renovation|design|maintenance|paint|nest|a\/c|heat|window|faucet|toilet|tile)/.test(l)) return 'Maintenance';
  if (/insurance/.test(l)) return 'Insurance';
  if (/\btax/.test(l)) return 'Taxes';
  if (/(home goods|cleaning|supplies|furniture|tv\b|sofa|desk|covers)/.test(l)) return 'Furnishings & Supplies';
  return 'Other';
}

// pre-classify all entries
DATA.entries.forEach(e => {
  e.category = (e.credit && (e.debit == null || e.debit === 0)) ? 'Revenue' : categorize(e.line_item);
  e.amount = (e.debit || 0) || (e.credit ? -e.credit : 0); // for expense sums (positive = cost). For revenue we still keep as 'Revenue' category.
});

/* =================================================================
 * FORMATTERS
 * ================================================================= */
const fmt0 = v => (v===null||v===undefined) ? '—' : '$' + Math.round(Number(v)).toLocaleString();
const fmt2 = v => (v===null||v===undefined) ? '—' : '$' + Number(v).toLocaleString(undefined,{minimumFractionDigits:2, maximumFractionDigits:2});
const fmtK = v => {
  if (v===null||v===undefined) return '—';
  const n = Number(v); const abs = Math.abs(n);
  if (abs >= 1000) return '$' + (n/1000).toFixed(abs>=10000?0:1) + 'k';
  return '$' + n.toFixed(0);
};
const fmtPct = v => v===null||v===undefined||isNaN(v) ? '—' : (v*100).toFixed(1) + '%';
const fmtSignK = v => {
  if (v==null) return '<span class="dim">·</span>';
  const cls = v<0 ? 'neg' : (v>0 ? 'pos' : 'dim');
  return `<span class="${cls} num">${fmtK(v)}</span>`;
};
const fmtSign = (v, fmtFn=fmt0) => {
  if (v==null) return '<span class="dim">·</span>';
  const cls = v<0 ? 'neg' : (v>0 ? 'pos' : 'dim');
  return `<span class="${cls} num">${fmtFn(v)}</span>`;
};
const driveLink = id => id ? `https://docs.google.com/spreadsheets/d/${id}/edit` : '';
const localLink = name => `xlsx/${name}.xlsx`;

/* =================================================================
 * FILTER STATE
 * ================================================================= */
const STATE = {
  props: new Set(DATA.props),
  years: new Set([...new Set(DATA.totals.filter(t=>t.year).map(t=>t.year))]),
  cats:  new Set(CATEGORIES.map(c => c[0])),
  q: '',
};

function renderFilters() {
  const propChips = document.getElementById('f-prop');
  propChips.innerHTML = DATA.props.map(p =>
    `<span class="chip ${STATE.props.has(p)?'on':''}" data-kind="prop" data-val="${p}">${p}</span>`).join('');
  const yrs = [...new Set(DATA.totals.filter(t=>t.year).map(t=>t.year))].sort();
  document.getElementById('f-year').innerHTML = yrs.map(y =>
    `<span class="chip ${STATE.years.has(y)?'on':''}" data-kind="year" data-val="${y}">${y}</span>`).join('');
  document.getElementById('f-cat').innerHTML = CATEGORIES.map(([name,cls]) =>
    `<span class="chip ${cls} ${STATE.cats.has(name)?'on':''}" data-kind="cat" data-val="${name}">${name}</span>`).join('');
  document.querySelectorAll('.chip').forEach(el => el.onclick = () => {
    const k = el.dataset.kind, v = el.dataset.val;
    const set = k==='prop' ? STATE.props : (k==='year' ? STATE.years : STATE.cats);
    const val = k==='year' ? Number(v) : v;
    if (set.has(val)) set.delete(val); else set.add(val);
    renderFilters(); render();
  });
}
document.getElementById('f-search').oninput = e => { STATE.q = e.target.value.trim().toLowerCase(); render(); };
document.getElementById('f-reset').onclick = () => {
  STATE.props = new Set(DATA.props);
  STATE.years = new Set([...new Set(DATA.totals.filter(t=>t.year).map(t=>t.year))]);
  STATE.cats  = new Set(CATEGORIES.map(c => c[0]));
  STATE.q = '';
  document.getElementById('f-search').value = '';
  renderFilters(); render();
};

/* =================================================================
 * FILTERING
 * ================================================================= */
function filteredEntries() {
  return DATA.entries.filter(e =>
    STATE.props.has(e.property) &&
    STATE.years.has(e.year) &&
    STATE.cats.has(e.category) &&
    (!STATE.q || String(e.line_item||'').toLowerCase().includes(STATE.q))
  );
}
function filteredTotals() {
  // monthly_totals is property-aggregated already; we filter by year & property
  return DATA.totals.filter(t => t.year != null && STATE.years.has(t.year) &&
    (t.property === 'ALL' || STATE.props.has(t.property)));
}

/* =================================================================
 * AGGREGATIONS
 * ================================================================= */
function sumBy(arr, keyFn, valFn) {
  const m = new Map();
  arr.forEach(x => {
    const k = keyFn(x), v = valFn(x) || 0;
    m.set(k, (m.get(k) || 0) + v);
  });
  return m;
}

function entryRevenue(e) { return e.category === 'Revenue' ? (e.credit || 0) : 0; }
function entryExpense(e) { return e.category === 'Revenue' ? 0 : (e.debit || 0); }

function computeKpis() {
  const E = filteredEntries();
  const totalRev = E.reduce((s,e)=>s+entryRevenue(e), 0);
  const totalExp = E.reduce((s,e)=>s+entryExpense(e), 0);
  const totalNet = totalRev - totalExp;
  // Months reported = unique (year, month, property) covered in filtered entries (any cat)
  const monthsByProp = new Map();
  E.forEach(e => {
    const k = e.property;
    if (!monthsByProp.has(k)) monthsByProp.set(k, new Set());
    monthsByProp.get(k).add(`${e.year}-${e.month}`);
  });
  const totalPropMonths = [...monthsByProp.values()].reduce((s,set)=>s+set.size, 0);
  const monthsAny = new Set();
  E.forEach(e => monthsAny.add(`${e.year}-${e.month}`));
  const months = monthsAny.size;
  const activeProps = [...STATE.props].filter(p => E.some(e => e.property===p)).length;

  // monthly revenue sequence (sparkline)
  const monthlyRevMap = sumBy(E, e => `${e.year}-${String(e.month).padStart(2,'0')}`, entryRevenue);
  const monthlyExpMap = sumBy(E, e => `${e.year}-${String(e.month).padStart(2,'0')}`, entryExpense);
  const ymKeys = [...new Set([...monthlyRevMap.keys(), ...monthlyExpMap.keys()])].sort();
  const monthlyRev = ymKeys.map(k => monthlyRevMap.get(k) || 0);
  const monthlyExp = ymKeys.map(k => monthlyExpMap.get(k) || 0);
  const monthlyNet = ymKeys.map((k,i) => monthlyRev[i] - monthlyExp[i]);
  const avgMoRev = months > 0 ? totalRev / months : 0;
  const avgMoNet = months > 0 ? totalNet / months : 0;
  const opexRatio = totalRev > 0 ? totalExp / totalRev : null;

  // best / worst month (net)
  let bestMo=null, worstMo=null;
  ymKeys.forEach((k,i) => {
    if (bestMo === null || monthlyNet[i] > monthlyNet[bestMo]) bestMo = i;
    if (worstMo === null || monthlyNet[i] < monthlyNet[worstMo]) worstMo = i;
  });
  const bestMoLabel = bestMo!=null ? ymKeys[bestMo] : '—';
  const worstMoLabel = worstMo!=null ? ymKeys[worstMo] : '—';

  // top / bottom property by net
  const propNet = new Map();
  E.forEach(e => {
    const k = e.property;
    propNet.set(k, (propNet.get(k) || 0) + entryRevenue(e) - entryExpense(e));
  });
  const propsBy = [...propNet.entries()].sort((a,b) => b[1]-a[1]);
  const top = propsBy[0] || ['—', 0];
  const bot = propsBy[propsBy.length-1] || ['—', 0];

  // YoY (compare latest filtered year to prior)
  const yrs = [...STATE.years].sort();
  const yrNet = new Map();
  E.forEach(e => yrNet.set(e.year, (yrNet.get(e.year)||0) + entryRevenue(e) - entryExpense(e)));
  const yrRev = new Map();
  E.forEach(e => yrRev.set(e.year, (yrRev.get(e.year)||0) + entryRevenue(e)));
  let yoyNet = null, yoyRev = null;
  if (yrs.length >= 2) {
    const last = yrs[yrs.length-1], prev = yrs[yrs.length-2];
    if (yrNet.get(prev)) yoyNet = (yrNet.get(last) - yrNet.get(prev)) / Math.abs(yrNet.get(prev));
    if (yrRev.get(prev)) yoyRev = (yrRev.get(last) - yrRev.get(prev)) / Math.abs(yrRev.get(prev));
  }

  return { totalRev, totalExp, totalNet, months, activeProps, totalPropMonths,
           monthlyRev, monthlyExp, monthlyNet, ymKeys,
           avgMoRev, avgMoNet, opexRatio,
           bestMoLabel, bestMoNet: bestMo!=null?monthlyNet[bestMo]:null,
           worstMoLabel, worstMoNet: worstMo!=null?monthlyNet[worstMo]:null,
           top, bot, yoyNet, yoyRev };
}

/* =================================================================
 * SVG CHART HELPERS
 * ================================================================= */
function sparkline(values, opts={}) {
  if (!values.length) return '';
  const w = opts.w || 140, h = opts.h || 24;
  const min = Math.min(...values, 0), max = Math.max(...values, 0);
  const range = max - min || 1;
  const pts = values.map((v,i) => [i * (w-2) / Math.max(values.length-1,1) + 1, h - 1 - ((v - min) / range) * (h-2)]);
  const d = pts.map((p,i) => (i===0?'M':'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ');
  const zeroY = h - 1 - ((0 - min) / range) * (h-2);
  const last = values[values.length-1];
  const color = (opts.color) || (last >= 0 ? '#4ade80' : '#f87171');
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" preserveAspectRatio="none">
    <line x1="0" x2="${w}" y1="${zeroY.toFixed(1)}" y2="${zeroY.toFixed(1)}" stroke="#262e42" stroke-width="0.5"/>
    <path d="${d}" stroke="${color}" stroke-width="1.4" fill="none"/>
  </svg>`;
}

function lineChartMulti(series, opts={}) {
  // series: [{name, values:[{x,y}...], color}]
  const w = opts.w || 700, h = opts.h || 260;
  const padL=42, padR=12, padT=12, padB=28;
  const innerW = w - padL - padR, innerH = h - padT - padB;
  const xs = [...new Set(series.flatMap(s => s.values.map(v => v.x)))].sort();
  if (!xs.length) return '<div class="muted" style="padding:20px;text-align:center">No data in current filter.</div>';
  const allY = series.flatMap(s => s.values.map(v => v.y));
  const minY = Math.min(...allY, 0), maxY = Math.max(...allY, 0);
  const yRange = maxY - minY || 1;
  const xMap = new Map(xs.map((x,i) => [x, i]));
  const xPos = i => padL + (xs.length<=1 ? innerW/2 : i * innerW / (xs.length - 1));
  const yPos = y => padT + innerH - ((y - minY) / yRange) * innerH;

  // gridlines (5 horizontal)
  let grid = '';
  for (let i=0; i<=4; i++) {
    const y = padT + i * innerH / 4;
    const v = maxY - i * yRange / 4;
    grid += `<line x1="${padL}" x2="${w-padR}" y1="${y}" y2="${y}" stroke="#262e42" stroke-width="0.5"/>`;
    grid += `<text x="${padL-4}" y="${y+3}" font-size="9" fill="#7c8499" text-anchor="end">${fmtK(v)}</text>`;
  }
  // zero line
  if (minY < 0 && maxY > 0) {
    const yz = yPos(0);
    grid += `<line x1="${padL}" x2="${w-padR}" y1="${yz}" y2="${yz}" stroke="#5b6378" stroke-width="0.7" stroke-dasharray="3,3"/>`;
  }

  // x axis labels (year boundaries)
  let xax = '';
  let lastYr = '';
  xs.forEach((x,i) => {
    const yr = x.slice(0,4);
    if (yr !== lastYr) {
      xax += `<line x1="${xPos(i)}" x2="${xPos(i)}" y1="${padT}" y2="${padT+innerH}" stroke="#262e42" stroke-width="0.5"/>`;
      xax += `<text x="${xPos(i)+3}" y="${h-padB+12}" font-size="10" fill="#7c8499">${yr}</text>`;
      lastYr = yr;
    }
  });

  // paths
  let paths = '';
  series.forEach(s => {
    const vmap = new Map(s.values.map(v => [v.x, v.y]));
    const pts = xs.filter(x => vmap.has(x)).map(x => [xPos(xMap.get(x)), yPos(vmap.get(x))]);
    if (!pts.length) return;
    const d = pts.map((p,i) => (i===0?'M':'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ');
    paths += `<path d="${d}" stroke="${s.color}" stroke-width="1.6" fill="none"/>`;
  });

  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:${h}px">${grid}${xax}${paths}</svg>`;
}

function stackedBars(rows, cats, opts={}) {
  // rows: [{label, values:{cat:val,...}}]
  const w = opts.w || 700, h = opts.h || 260;
  const padL=46, padR=12, padT=12, padB=24;
  const innerW = w - padL - padR, innerH = h - padT - padB;
  if (!rows.length) return '<div class="muted" style="padding:20px;text-align:center">No data.</div>';
  const sums = rows.map(r => cats.reduce((s,c) => s + (r.values[c]||0), 0));
  const maxY = Math.max(...sums, 1);
  const bw = innerW / rows.length;

  let grid='';
  for (let i=0;i<=4;i++) {
    const y = padT + i*innerH/4;
    const v = maxY - i*maxY/4;
    grid += `<line x1="${padL}" x2="${w-padR}" y1="${y}" y2="${y}" stroke="#262e42" stroke-width="0.5"/>`;
    grid += `<text x="${padL-4}" y="${y+3}" font-size="9" fill="#7c8499" text-anchor="end">${fmtK(v)}</text>`;
  }

  let bars='', labels='';
  rows.forEach((r, i) => {
    let acc = 0;
    cats.forEach(c => {
      const v = r.values[c] || 0;
      if (v <= 0) return;
      const yTop = padT + innerH - ((acc + v) / maxY) * innerH;
      const yBot = padT + innerH - (acc / maxY) * innerH;
      const x = padL + i*bw + 4;
      bars += `<rect x="${x.toFixed(1)}" y="${yTop.toFixed(1)}" width="${(bw-8).toFixed(1)}" height="${(yBot-yTop).toFixed(1)}" fill="${CAT_COLOR[c]}"><title>${r.label} · ${c}: ${fmtK(v)}</title></rect>`;
      acc += v;
    });
    labels += `<text x="${(padL + i*bw + bw/2).toFixed(1)}" y="${h-padB+12}" font-size="10" fill="#7c8499" text-anchor="middle">${r.label}</text>`;
    labels += `<text x="${(padL + i*bw + bw/2).toFixed(1)}" y="${padT+innerH-((sums[i]/maxY)*innerH)-3}" font-size="10" fill="#e6e9ef" text-anchor="middle">${fmtK(sums[i])}</text>`;
  });

  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:${h}px">${grid}${bars}${labels}</svg>`;
}

function donut(values, opts={}) {
  // values: [{label, value, color}]
  const r = opts.r || 100, ir = opts.ir || 60, w = r*2 + 240, h = r*2 + 20;
  const cx = r + 10, cy = r + 10;
  const total = values.reduce((s,v)=>s+v.value, 0);
  if (total <= 0) return '<div class="muted" style="padding:20px;text-align:center">No revenue in current filter.</div>';
  let acc = 0, slices = '';
  values.forEach(v => {
    const a0 = acc / total * Math.PI * 2 - Math.PI/2;
    const a1 = (acc + v.value) / total * Math.PI * 2 - Math.PI/2;
    const large = (a1-a0) > Math.PI ? 1 : 0;
    const x0=cx+r*Math.cos(a0), y0=cy+r*Math.sin(a0);
    const x1=cx+r*Math.cos(a1), y1=cy+r*Math.sin(a1);
    const x2=cx+ir*Math.cos(a1), y2=cy+ir*Math.sin(a1);
    const x3=cx+ir*Math.cos(a0), y3=cy+ir*Math.sin(a0);
    slices += `<path d="M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1} L ${x2} ${y2} A ${ir} ${ir} 0 ${large} 0 ${x3} ${y3} Z" fill="${v.color}"><title>${v.label}: ${fmtK(v.value)} (${fmtPct(v.value/total)})</title></path>`;
    acc += v.value;
  });
  let legend = '';
  values.forEach((v,i) => {
    legend += `<g transform="translate(${r*2+24}, ${10 + i*22})">
      <rect width="12" height="12" rx="2" fill="${v.color}"/>
      <text x="18" y="10" font-size="11" fill="#e6e9ef">${v.label}</text>
      <text x="220" y="10" font-size="11" fill="#7c8499" text-anchor="end">${fmtK(v.value)} (${fmtPct(v.value/total)})</text>
    </g>`;
  });
  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;max-width:${w}px;height:auto">${slices}${legend}
    <text x="${cx}" y="${cy-5}" font-size="11" fill="#7c8499" text-anchor="middle">Total</text>
    <text x="${cx}" y="${cy+12}" font-size="14" fill="#e6e9ef" text-anchor="middle" font-weight="600">${fmtK(total)}</text>
  </svg>`;
}

/* =================================================================
 * RENDERERS
 * ================================================================= */
function renderKpis() {
  const k = computeKpis();
  const el = document.getElementById('kpis');
  const cards = [
    { label:'Gross Revenue',  value:fmtK(k.totalRev),  delta:k.yoyRev!=null ? (k.yoyRev>=0?`+${fmtPct(k.yoyRev)} YoY`:`${fmtPct(k.yoyRev)} YoY`) : '', dClass:k.yoyRev>=0?'pos':'neg', spark:sparkline(k.monthlyRev,{color:'#4ade80'}) },
    { label:'Operating Expense',value:fmtK(k.totalExp), delta:`OpEx ratio ${fmtPct(k.opexRatio)}`, dClass:'', spark:sparkline(k.monthlyExp,{color:'#f87171'}) },
    { label:'Net P&L',         value:fmtK(k.totalNet),  delta:k.yoyNet!=null ? (k.yoyNet>=0?`+${fmtPct(k.yoyNet)} YoY`:`${fmtPct(k.yoyNet)} YoY`) : '', dClass:k.yoyNet>=0?'pos':'neg', spark:sparkline(k.monthlyNet) },
    { label:'Avg monthly Net', value:fmtK(k.avgMoNet),  delta:`across ${k.months} months`, dClass:'', spark:'' },
    { label:'Active properties',value:k.activeProps,    delta:`${k.totalPropMonths} property-months`, dClass:'', spark:'' },
    { label:'Best month',      value:fmtK(k.bestMoNet),  delta:k.bestMoLabel, dClass:'pos', spark:'' },
    { label:'Worst month',     value:fmtK(k.worstMoNet), delta:k.worstMoLabel, dClass:'neg', spark:'' },
    { label:'Top performer',   value:k.top[0].split(' ')[0]+' '+(k.top[0].split(' ')[1]||''), delta:fmtK(k.top[1]), dClass:'pos', spark:'' },
    { label:'Weakest performer',value:k.bot[0].split(' ')[0]+' '+(k.bot[0].split(' ')[1]||''), delta:fmtK(k.bot[1]), dClass:k.bot[1]<0?'neg':'', spark:'' },
  ];
  el.innerHTML = cards.map(c => `<div class="kpi">
    <div class="label">${c.label}</div>
    <div class="value">${c.value}</div>
    <div class="delta ${c.dClass}">${c.delta||'&nbsp;'}</div>
    ${c.spark ? `<div class="spark">${c.spark}</div>` : ''}
  </div>`).join('');
}

function renderPropCards() {
  const el = document.getElementById('prop-cards');
  const E = filteredEntries();
  const T = filteredTotals();
  const props = DATA.props.filter(p => STATE.props.has(p));
  el.innerHTML = props.map(p => {
    const PE = E.filter(e => e.property === p);
    const PT = T.filter(t => t.property === p);
    const rev = PE.reduce((s,e)=>s+entryRevenue(e), 0);
    const exp = PE.reduce((s,e)=>s+entryExpense(e), 0);
    const net = rev - exp;
    const months = new Set(PE.map(e => `${e.year}-${e.month}`)).size;
    const incMonths = new Set(PE.filter(e => entryRevenue(e) > 0).map(e => `${e.year}-${e.month}`)).size;
    const occ = months > 0 ? incMonths / months : null;
    const avgRev = months > 0 ? rev / months : 0;
    const opex = rev > 0 ? exp / rev : null;
    // monthly net sparkline
    const m = new Map();
    PE.forEach(e => {
      const k = `${e.year}-${String(e.month).padStart(2,'0')}`;
      m.set(k, (m.get(k)||0) + entryRevenue(e) - entryExpense(e));
    });
    const seq = [...m.keys()].sort().map(k => m.get(k));
    return `<div class="prop-card">
      <h3>${p}</h3>
      <div class="meta">${months} months · ${incMonths} producing revenue · occ-proxy ${fmtPct(occ)}</div>
      <div class="stats">
        <div class="row"><span class="lbl">Revenue</span><span class="num">${fmtK(rev)}</span></div>
        <div class="row"><span class="lbl">Avg/mo</span><span class="num">${fmtK(avgRev)}</span></div>
        <div class="row"><span class="lbl">Expense</span><span class="num">${fmtK(exp)}</span></div>
        <div class="row"><span class="lbl">OpEx ratio</span><span class="num">${fmtPct(opex)}</span></div>
        <div class="row" style="grid-column:span 2;border-top:1px solid var(--border);padding-top:4px;margin-top:2px"><span class="lbl">Net P&L</span><span>${fmtSign(net, fmtK)}</span></div>
      </div>
      <div class="spark">${sparkline(seq,{h:42})}</div>
    </div>`;
  }).join('');
}

function renderCashflow() {
  // monthly revenue / expense / net across the filter
  const E = filteredEntries();
  const revMap = sumBy(E, e => `${e.year}-${String(e.month).padStart(2,'0')}`, entryRevenue);
  const expMap = sumBy(E, e => `${e.year}-${String(e.month).padStart(2,'0')}`, entryExpense);
  const xs = [...new Set([...revMap.keys(), ...expMap.keys()])].sort();
  const series = [
    { name:'Revenue', color:'#4ade80', values: xs.map(x => ({x, y: revMap.get(x)||0})) },
    { name:'Expense', color:'#f87171', values: xs.map(x => ({x, y: expMap.get(x)||0})) },
    { name:'Net',     color:'#5aa9ff', values: xs.map(x => ({x, y: (revMap.get(x)||0) - (expMap.get(x)||0)})) },
  ];
  document.getElementById('cashflow-legend').innerHTML = series.map(s =>
    `<span class="item"><span class="sw" style="background:${s.color}"></span>${s.name}</span>`).join('');
  document.getElementById('cashflow-chart').innerHTML = lineChartMulti(series, {w:780, h:260});
}

function renderExpense() {
  const E = filteredEntries();
  const cats = CATEGORIES.map(c => c[0]).filter(c => c !== 'Revenue' && STATE.cats.has(c));
  const years = [...new Set(E.map(e => e.year).filter(y=>y))].sort();
  const rows = years.map(y => {
    const yE = E.filter(e => e.year === y && e.category !== 'Revenue');
    const v = {};
    cats.forEach(c => v[c] = yE.filter(e => e.category===c).reduce((s,e)=>s+(e.debit||0), 0));
    return { label: y, values: v };
  });
  document.getElementById('expense-legend').innerHTML = cats.map(c =>
    `<span class="item"><span class="sw" style="background:${CAT_COLOR[c]}"></span>${c}</span>`).join('');
  document.getElementById('expense-chart').innerHTML = stackedBars(rows, cats, {w:780, h:260});
}

function renderContrib() {
  const E = filteredEntries();
  const propPalette = ['#5aa9ff','#a78bfa','#fb923c','#34d399','#f472b6'];
  const vals = DATA.props.filter(p => STATE.props.has(p)).map((p,i) => ({
    label: p, color: propPalette[i % propPalette.length],
    value: E.filter(e => e.property === p).reduce((s,e)=>s+entryRevenue(e), 0),
  })).filter(v => v.value > 0).sort((a,b)=>b.value-a.value);
  document.getElementById('contrib-chart').innerHTML = donut(vals);
}

function renderCumulative() {
  const E = filteredEntries();
  const propPalette = {
    '1120 Lauren Way':'#5aa9ff', '260 East Taylors Crossing':'#a78bfa',
    '4645 Valais Ct':'#fb923c', '5525 Taylor Road':'#34d399',
    '115 Peachtree Memorial Drive':'#f472b6',
  };
  const series = DATA.props.filter(p => STATE.props.has(p)).map(p => {
    const PE = E.filter(e => e.property === p);
    const monthlyMap = sumBy(PE, e => `${e.year}-${String(e.month).padStart(2,'0')}`, e => entryRevenue(e) - entryExpense(e));
    const xs = [...monthlyMap.keys()].sort();
    let acc = 0;
    return {
      name: p, color: propPalette[p] || '#94a3b8',
      values: xs.map(x => ({ x, y: (acc += monthlyMap.get(x)) }))
    };
  });
  document.getElementById('cumchart').innerHTML = lineChartMulti(series, {w:780, h:260})
    + `<div class="legend" style="margin-top:6px">${series.map(s=>`<span class="item"><span class="sw" style="background:${s.color}"></span>${s.name}</span>`).join('')}</div>`;
}

function renderHeatmap() {
  const E = filteredEntries();
  const props = DATA.props.filter(p => STATE.props.has(p));
  const years = [...STATE.years].sort();
  // collect cells: net per (property, year-month)
  const cellMap = new Map(); // `${p}|${ym}` -> net
  E.forEach(e => {
    const ym = `${e.year}-${String(e.month).padStart(2,'0')}`;
    const k = `${e.property}|${ym}`;
    cellMap.set(k, (cellMap.get(k)||0) + entryRevenue(e) - entryExpense(e));
  });
  // determine y-axis: list of year-month
  const yms = [];
  years.forEach(y => { for (let m=1;m<=12;m++) yms.push(`${y}-${String(m).padStart(2,'0')}`); });
  const allVals = [...cellMap.values()].filter(v => v !== 0);
  const maxAbs = Math.max(1, ...allVals.map(v => Math.abs(v)));
  // grid: cols = props+label, rows = yms+header
  const cols = 1 + props.length;
  let html = `<div class="heat" style="grid-template-columns:90px repeat(${props.length}, minmax(60px,1fr))">`;
  html += `<div class="cell head label">Month</div>`;
  props.forEach(p => html += `<div class="cell head" title="${p}">${p.split(' ').slice(0,2).join(' ')}</div>`);
  yms.forEach(ym => {
    const [y,m] = ym.split('-');
    html += `<div class="cell label">${MONTHS[+m-1]} ${y.slice(2)}</div>`;
    props.forEach(p => {
      const v = cellMap.get(`${p}|${ym}`);
      if (v === undefined) {
        html += `<div class="cell empty">·</div>`;
      } else {
        const intensity = Math.min(1, Math.abs(v) / maxAbs);
        const color = v >= 0
          ? `rgba(74, 222, 128, ${0.10 + 0.80*intensity})`
          : `rgba(248, 113, 113, ${0.10 + 0.80*intensity})`;
        html += `<div class="cell" style="background:${color};color:#0a0d13;font-weight:600" title="${p} ${ym}: ${fmt0(v)}">${fmtK(v)}</div>`;
      }
    });
  });
  html += '</div>';
  document.getElementById('heatmap').innerHTML = html;
}

function renderYearGrid() {
  // Same logical layout as before, but driven by ledger_entries so the filters apply.
  // Each cell = Net (per property/month) computed from filtered ledger.
  const E = filteredEntries();
  const props = DATA.props.filter(p => STATE.props.has(p));
  const years = [...STATE.years].sort();
  let html = '';
  years.forEach(year => {
    const yE = E.filter(e => e.year === year);
    if (!yE.length) return;
    const monthsHere = new Set(yE.map(e => e.month));
    const propsHere = props.filter(p => yE.some(e => e.property === p));
    html += `<div class="year-block"><h3>${year}</h3>`;
    html += '<div style="overflow-x:auto"><table><thead><tr><th>Property</th>';
    for (let m=1;m<=12;m++) html += `<th class="num">${MONTHS[m-1]}</th>`;
    html += '<th class="num" style="border-left:2px solid var(--border)">Year</th></tr></thead><tbody>';
    let allMonth = Array(12).fill(0), anyAll = Array(12).fill(false), allYear = 0;
    propsHere.forEach(p => {
      html += `<tr><td>${p}</td>`;
      let yearNet=0, anyMonth=false;
      for (let m=1;m<=12;m++) {
        const cellE = yE.filter(e => e.property===p && e.month===m);
        if (!cellE.length) { html += `<td class="dim num">·</td>`; continue; }
        const rev = cellE.reduce((s,e)=>s+entryRevenue(e),0);
        const exp = cellE.reduce((s,e)=>s+entryExpense(e),0);
        const net = rev - exp;
        yearNet += net; anyMonth = true;
        allMonth[m-1] += net; anyAll[m-1] = true; allYear += net;
        const cls = net<0?'neg':(net>0?'pos':'dim');
        const sf = cellE[0].source_file;
        const title = `${p} · ${MONTHS[m-1]} ${year}\nRev ${fmtK(rev)} · Exp ${fmtK(exp)} · Net ${fmtK(net)}\nfrom ${sf}`;
        html += `<td class="num clickable ${cls}" title="${title}" onclick='showCell(${JSON.stringify(sf)}, ${JSON.stringify(p)})'>${fmtK(net)}</td>`;
      }
      html += `<td class="num" style="border-left:2px solid var(--border);font-weight:600">${anyMonth?fmtSign(yearNet,fmtK):'<span class="dim">·</span>'}</td></tr>`;
    });
    html += `<tr style="background:var(--panel2);font-weight:600;border-top:2px solid var(--border)"><td>All selected (sum of rows)</td>`;
    for (let m=1;m<=12;m++) html += anyAll[m-1] ? `<td class="num">${fmtSign(allMonth[m-1],fmtK)}</td>` : `<td class="dim num">·</td>`;
    html += `<td class="num" style="border-left:2px solid var(--border)">${fmtSign(allYear,fmtK)}</td></tr>`;
    html += '</tbody></table></div></div>';
  });
  document.getElementById('grid').innerHTML = html || '<div class="muted" style="padding:20px;text-align:center">No rows match the current filter.</div>';
}

function renderTYear() {
  const E = filteredEntries();
  const yrs = [...STATE.years].sort();
  let html = '<thead><tr><th>Year</th><th>Revenue</th><th>Expense</th><th>Net</th><th>OpEx ratio</th><th>Active props</th></tr></thead><tbody>';
  let tr=0,te=0,tn=0;
  yrs.forEach(y => {
    const yE = E.filter(e => e.year===y);
    const r = yE.reduce((s,e)=>s+entryRevenue(e),0);
    const x = yE.reduce((s,e)=>s+entryExpense(e),0);
    const n = r - x;
    tr+=r; te+=x; tn+=n;
    const ap = new Set(yE.map(e=>e.property)).size;
    html += `<tr><td>${y}</td><td class="num">${fmt0(r)}</td><td class="num">${fmt0(x)}</td><td>${fmtSign(n)}</td><td class="num">${fmtPct(r>0?x/r:null)}</td><td class="num">${ap}</td></tr>`;
  });
  html += `<tr style="font-weight:700"><td>Total</td><td class="num">${fmt0(tr)}</td><td class="num">${fmt0(te)}</td><td>${fmtSign(tn)}</td><td class="num">${fmtPct(tr>0?te/tr:null)}</td><td></td></tr></tbody>`;
  document.getElementById('t-year').innerHTML = html;
}

function renderTPropYear() {
  const E = filteredEntries();
  const props = DATA.props.filter(p => STATE.props.has(p));
  const yrs = [...STATE.years].sort();
  let html = '<thead><tr><th>Property</th>';
  yrs.forEach(y => html += `<th>${y} Net</th>`);
  html += '<th>Total Net</th></tr></thead><tbody>';
  props.forEach(p => {
    let total = 0;
    html += `<tr><td>${p}</td>`;
    yrs.forEach(y => {
      const yE = E.filter(e => e.year===y && e.property===p);
      if (!yE.length) { html += '<td class="dim num">·</td>'; return; }
      const n = yE.reduce((s,e)=>s + entryRevenue(e) - entryExpense(e), 0);
      total += n;
      html += `<td>${fmtSign(n)}</td>`;
    });
    html += `<td style="border-left:2px solid var(--border);font-weight:600">${fmtSign(total)}</td></tr>`;
  });
  html += '</tbody>';
  document.getElementById('t-prop-year').innerHTML = html;
}

function renderLineItems() {
  const E = filteredEntries();
  const wrap = document.getElementById('lineitems');
  // group by category, then list a top-N by amount
  const byCat = new Map();
  E.forEach(e => {
    if (!byCat.has(e.category)) byCat.set(e.category, []);
    byCat.get(e.category).push(e);
  });
  const cats = [...byCat.keys()].sort((a,b)=>{
    const ai = CATEGORIES.findIndex(c=>c[0]===a), bi = CATEGORIES.findIndex(c=>c[0]===b);
    return ai - bi;
  });
  let html = '';
  cats.forEach(c => {
    const rows = byCat.get(c).slice().sort((a,b) => {
      const av = (a.debit||0) + (a.credit||0);
      const bv = (b.debit||0) + (b.credit||0);
      return bv - av;
    });
    const subtotalD = rows.reduce((s,r)=>s+(r.debit||0),0);
    const subtotalC = rows.reduce((s,r)=>s+(r.credit||0),0);
    html += `<details><summary><span class="pill ${CAT_CLASS[c]}" style="background:${CAT_COLOR[c]};color:#0a0d13;border:none">${c}</span> &nbsp; ${rows.length} entries · Debit ${fmt0(subtotalD)} · Credit ${fmt0(subtotalC)}</summary>`;
    html += '<table style="margin-top:6px"><thead><tr><th>Period</th><th>Property</th><th>Line item</th><th>Debit</th><th>Credit</th><th>Source</th></tr></thead><tbody>';
    rows.forEach(r => {
      const f = DATA.files.find(f => f.source_file === r.source_file);
      const src = f ? `<a href="${driveLink(f.file_id)}" target="_blank">${r.source_file}</a>` : r.source_file;
      html += `<tr><td>${r.year}-${String(r.month).padStart(2,'0')}${r.variant||''}</td><td>${r.property}</td><td>${r.line_item}</td><td class="num">${fmt2(r.debit)}</td><td class="num">${fmt2(r.credit)}</td><td>${src}</td></tr>`;
    });
    html += '</tbody></table></details>';
  });
  wrap.innerHTML = html || '<div class="muted" style="padding:20px;text-align:center">No line items match.</div>';
}

function renderFilesTable() {
  let html = '<thead><tr><th>Period</th><th>Kind</th><th>Tabs</th><th>Source</th></tr></thead><tbody>';
  DATA.files.forEach(f => {
    const drive = f.file_id ? `<a href="${driveLink(f.file_id)}" target="_blank">Drive ↗</a>` : '';
    const local = `<a href="${localLink(f.source_file)}" target="_blank">XLSX</a>`;
    html += `<tr>
      <td>${f.source_file}</td>
      <td><span class="pill">${f.kind}</span></td>
      <td class="muted" style="text-align:left">${f.tabs.length} tab${f.tabs.length===1?'':'s'}: ${f.tabs.join(' · ')}</td>
      <td class="src-links">${drive} ${local}</td>
    </tr>`;
  });
  html += '</tbody>';
  document.getElementById('t-files').innerHTML = html;
}

function renderYearEnd() {
  const bySf = {};
  DATA.year_end_cells.forEach(c => {
    if (!bySf[c.source_file]) bySf[c.source_file] = {};
    if (!bySf[c.source_file][c.tab]) bySf[c.source_file][c.tab] = [];
    bySf[c.source_file][c.tab].push(c);
  });
  let html = '';
  Object.keys(bySf).sort().forEach(sf => {
    const fId = (DATA.files.find(f => f.source_file===sf) || {}).file_id || '';
    const drive = fId ? `<a href="${driveLink(fId)}" target="_blank">Drive ↗</a>` : '';
    html += `<details><summary><b>${sf}</b> &nbsp; ${drive} &nbsp; <a href="${localLink(sf)}" target="_blank">XLSX</a></summary>`;
    Object.keys(bySf[sf]).forEach(tab => {
      const cells = bySf[sf][tab];
      const maxRow = Math.max(...cells.map(c=>c.row));
      const maxCol = Math.max(...cells.map(c=>c.col));
      const grid = Array.from({length:maxRow}, () => Array(maxCol).fill(''));
      cells.forEach(c => grid[c.row-1][c.col-1] = c.value);
      html += `<div style="margin-top:8px"><b style="color:var(--muted);font-size:11px">tab: ${tab}</b><table style="margin-top:4px">`;
      grid.forEach(row => html += '<tr>' + row.map(v => `<td>${v===''?'<span class="dim">·</span>':v}</td>`).join('') + '</tr>');
      html += '</table></div>';
    });
    html += '</details>';
  });
  document.getElementById('year-end').innerHTML = html;
}

function showCell(source_file, property) {
  const f = DATA.files.find(f => f.source_file === source_file);
  const lines = DATA.entries.filter(e => e.source_file === source_file && (property === 'ALL' || e.property === property));
  const totals = DATA.totals.filter(t => t.source_file === source_file && (property === 'ALL' ? t.property === 'ALL' : t.property === property));
  document.getElementById('m-title').textContent = `${source_file} — ${property}`;
  const drive = f && f.file_id ? `<a href="${driveLink(f.file_id)}" target="_blank">Open in Google Drive ↗</a>` : '';
  let html = `<div class="badges">
    <span class="badge">source: ${source_file}</span>
    <span class="badge">${drive}</span>
    <span class="badge"><a href="${localLink(source_file)}" target="_blank">Local XLSX</a></span>
  </div>`;
  if (totals.length) {
    html += `<h4 style="margin:8px 0 4px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em">Totals (from workbook)</h4>
    <table><thead><tr><th>Property</th><th>Debits</th><th>Credits</th><th>Net</th></tr></thead><tbody>`;
    totals.forEach(t => html += `<tr><td>${t.property}</td><td class="num">${fmt2(t.debits)}</td><td class="num">${fmt2(t.credits)}</td><td>${fmtSign(t.net,fmt2)}</td></tr>`);
    html += '</tbody></table>';
  }
  html += `<h4 style="margin:14px 0 4px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em">Line items (${lines.length})</h4>`;
  if (!lines.length) {
    html += '<p class="muted">No structured line items captured. Open the source to inspect.</p>';
  } else {
    html += '<table><thead><tr><th>Property</th><th>Category</th><th>Line item</th><th>Debit</th><th>Credit</th></tr></thead><tbody>';
    lines.forEach(l => html += `<tr><td>${l.property}</td><td><span class="pill" style="background:${CAT_COLOR[l.category||'Other']};color:#0a0d13;border:none">${l.category||'Other'}</span></td><td>${l.line_item}</td><td class="num">${fmt2(l.debit)}</td><td class="num">${fmt2(l.credit)}</td></tr>`);
    html += '</tbody></table>';
  }
  document.getElementById('m-body').innerHTML = html;
  document.getElementById('modal').classList.add('open');
}
function closeModal() { document.getElementById('modal').classList.remove('open'); }
document.getElementById('modal').onclick = e => { if (e.target.id === 'modal') closeModal(); };
document.addEventListener('keyup', e => { if (e.key === 'Escape') closeModal(); });

/* =================================================================
 * MAIN RENDER
 * ================================================================= */
function render() {
  const E = filteredEntries();
  document.getElementById('match-info').textContent = `${E.length} line items · ${STATE.props.size} properties · ${STATE.years.size} years`;
  renderKpis();
  renderPropCards();
  renderCashflow();
  renderExpense();
  renderContrib();
  renderCumulative();
  renderHeatmap();
  renderYearGrid();
  renderTYear();
  renderTPropYear();
  renderLineItems();
}

// header crumbs
document.getElementById('hd-files').textContent = DATA.files.length;
document.getElementById('hd-months').textContent = DATA.files.filter(f=>f.kind==='monthly').length;
document.getElementById('hd-props').textContent = DATA.props.length;
document.getElementById('hd-entries').textContent = DATA.entries.length;
document.getElementById('hd-totals').textContent = DATA.totals.length;

renderFilesTable();
renderYearEnd();
renderFilters();
render();
</script>
</body>
</html>
"""


def build():
    data = fetch_data()
    out = HTML_TEMPLATE.replace("__DATA__", json.dumps(data, default=str))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    size_kb = os.path.getsize(OUT) // 1024
    print(f"Wrote {OUT}  ({size_kb} KB)")
    print(f"  files:             {len(data['files'])}")
    print(f"  monthly totals:    {len(data['totals'])}")
    print(f"  ledger entries:    {len(data['entries'])}")
    print(f"  year-end raw cells:{len(data['year_end_cells'])}")


if __name__ == "__main__":
    build()
