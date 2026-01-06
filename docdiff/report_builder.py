from typing import List, Dict, Any
import html
import json
import logging
import re
from difflib import SequenceMatcher
from .heuristics_ai import analyze_change, generate_ai_summary

_LOGGER = logging.getLogger(__name__)

STYLE = """
<style>
/* ---------- LIGHT MODE ---------- */
:root {
  --bg: #f7f7f8;
  --panel: #ffffff;
  --muted: #666;
  --text: #111;
  --accent: #007bff;
  --card-border: #e0e0e0;
  --chip-bg: #fff;
  --added-bg: #e6fbde;
  --deleted-bg: #ffecec;
  --changed-bg: #fff7e0;
  --unchanged-bg: #ffffff;
}
body {
  font-family: "Inter", "Segoe UI", Arial, sans-serif;
  margin: 20px;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}
.container { max-width: 1100px; margin: 0 auto; }
.header { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:16px; }
.controls { margin-bottom:12px; }
.chip {
  border:1px solid #ccc;
  padding:6px 10px;
  border-radius:16px;
  margin:4px;
  cursor:pointer;
  display:inline-block;
  background:var(--chip-bg);
  transition:all 0.2s ease;
}
.chip:hover { transform: translateY(-1px); box-shadow:0 2px 4px rgba(0,0,0,0.1); }
.chip.active { background:#007bff; color:#fff; border-color:#007bff; }

.score { font-weight:bold; padding:2px 6px; border-radius:6px; margin-left:8px; font-size:0.9em; }
.score.low { background:#d4fcbc; color:#083; }
.score.med { background:#fcebb6; color:#6a4a00; }
.score.high { background:#f8b4b4; color:#7a0000; }

.toc {
  margin-bottom:12px;
  background:var(--panel);
  padding:8px;
  border-radius:6px;
  border:1px solid var(--card-border);
}
.toc a {
  text-decoration:none;
  margin-right:6px;
  color:var(--accent);
  font-size:0.9em;
}
.toc a:hover { text-decoration:underline; }

.card {
  background:var(--panel);
  padding:10px;
  border-radius:8px;
  border:1px solid var(--card-border);
  margin-bottom:10px;
}

.added { background-color: var(--added-bg); }
.deleted { background-color: var(--deleted-bg); }
.changed { background-color: var(--changed-bg); }
.unchanged { background-color: var(--unchanged-bg); color: #777; }

table { border-collapse: collapse; margin-bottom: 10px; width:100%; }
td, th { border: 1px solid #d0d0d0; padding: 6px; vertical-align: top; }
pre.diff { background: #f4f4f4; padding: 8px; overflow: auto; border-radius:6px; }

.meta { color: var(--muted); font-size: 0.9em; margin-bottom:6px; display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.badge { font-size:0.85em; padding:3px 6px; border-radius:6px; background:#f1f1f1; margin-right:6px; }
.small { font-size:0.9em; color:#444; }

.ai-section {
  background:#f9fafb;
  border-left:4px solid #007bff;
  padding:8px 10px;
  border-radius:6px;
  margin:8px 0;
}

button.collapse-toggle {
  background:var(--chip-bg);
  border:1px solid #ccc;
  border-radius:6px;
  cursor:pointer;
  padding:6px 12px;
  transition:all 0.2s ease;
}
button.collapse-toggle:hover {
  background:#f0f0f0;
}

/* ---------- DARK MODE (better contrast & accessibility) ---------- */
body.dark {
  --bg: #0e1117;
  --panel: #161b22;
  --muted: #b6bbc2;
  --text: #e6edf3;
  --accent: #58a6ff;
  --card-border: #30363d;
  --chip-bg: #1c2128;
  --added-bg: #113417;
  --deleted-bg: #3d1b1b;
  --changed-bg: #3a351b;
  --unchanged-bg: #161b22;
}

body.dark .card { border-color: #2a2f36; }
body.dark .chip { border-color: #3d444d; color: #c9d1d9; }
body.dark .chip:hover { background:#21262d; border-color:#58a6ff; }
body.dark .chip.active { background:#58a6ff; color:#0d1117; }
body.dark .badge { background:#2d333b; color:#f0f6fc; border:1px solid #3b434c; }
body.dark .ai-section {
  background:#20262d;
  border-left-color:#58a6ff;
  color:#e6edf3;
}
body.dark pre.diff {
  background:#1f242a;
  color:#e6edf3;
  border:1px solid #30363d;
}
body.dark table, body.dark td, body.dark th { border-color:#30363d; }
body.dark a { color:#58a6ff; }
body.dark .dark-toggle {
  background:#1f242a;
  color:#f0f6fc;
  border:1px solid #30363d;
}
body.dark .dark-toggle:hover {
  background:#2d333b;
}
body.dark .score.low { background:#164a22; color:#9be9a8; }
body.dark .score.med { background:#3f3b17; color:#f1e05a; }
body.dark .score.high { background:#5c1f1f; color:#ffa198; }

body.dark .added { background-color: var(--added-bg); color:#afffaf; }
body.dark .deleted { background-color: var(--deleted-bg); color:#ffbcbc; }
body.dark .changed { background-color: var(--changed-bg); color:#f9f1bb; }
body.dark .unchanged { background-color: var(--unchanged-bg); color:#8b949e; }

body.dark del {
  background: #6e1a1a;
  color: #ffbaba;
  text-decoration: line-through;
  padding: 0 2px;
  border-radius:2px;
}
body.dark ins {
  background: #1a522a;
  color: #c8ffda;
  padding: 0 2px;
  border-radius:2px;
}
</style>
"""


# -------------------------
# Statistics and scoring
# -------------------------
def compute_stats_and_scores(block_diffs: List[Dict[str, Any]]) -> Dict[str, Any]:
    stats: Dict[str, Any] = {"added": 0, "deleted": 0, "changed": 0, "unchanged": 0, "by_type": {}}
    scored: List[tuple] = []

    for idx, b in enumerate(block_diffs):
        ch = b.get("change", "unknown")
        stats[ch] = stats.get(ch, 0) + 1

        typ = b.get("type") or (b.get("new", {}).get("type") or b.get("old", {}).get("type") or "unknown")
        stats["by_type"].setdefault(typ, {"added": 0, "deleted": 0, "changed": 0, "unchanged": 0})
        cat = ch if ch in ("added", "deleted", "changed", "unchanged") else "changed"
        stats["by_type"][typ][cat] += 1

        # scoring
        score = 0.0
        if ch in ("added", "deleted"):
            score += 2.5
        if ch == "changed":
            old_text = (b.get("old", {}).get("text") or "")
            new_text = (b.get("new", {}).get("text") or "")
            ratio = SequenceMatcher(None, old_text, new_text).ratio()
            score += (1.0 - ratio) * 6.0
            combined = (old_text + " " + new_text)
            if re.search(r"\d", combined):
                score += 0.8
            if re.search(r"\b(kg|m|mm|cm|%|km|PLN|EUR|kW)\b", combined, re.I):
                score += 0.8
            if re.search(r"\b(19|20)\d{2}\b", combined):
                score += 0.6
        if typ in ("image", "table"):
            score += 2.0

        score = round(max(0.0, min(10.0, score)), 2)
        b["_score"] = score
        scored.append((score, idx))

    # sort descending by score, TOC will later be sorted by AI semantic score if available
    scored.sort(reverse=True)
    stats["top_changes"] = [i for _, i in scored if block_diffs[i].get("change") in ("changed", "added", "deleted")]
    return stats


# -------------------------
# Render helpers
# -------------------------
def _render_ai_info(f, b: Dict[str, Any]):
    """AI section — rendered if data is present."""
    labels = b.get("_ai_labels") or []
    sem = b.get("_ai_sem_score", None)
    typ = b.get("_ai_type", "")
    conf = b.get("_ai_conf", None)

    # if none present, render nothing
    if not (labels or sem is not None or typ or conf):
        return

    f.write("<div class='ai-section'><b>🧠 <span data-i18n='ai_summary'>AI Summary</span>:</b> ")
    if labels:
        f.write(" ".join(f"<span class='badge'>{html.escape(l)}</span>" for l in labels))
    if typ:
        f.write(f"<span class='badge'><span data-i18n='type'>Type</span>: {html.escape(typ)}</span>")
    if sem is not None:
        f.write(f" <span class='badge'><span data-i18n='relevance'>Relevance</span>: {sem}/10</span>")
    if conf is not None:
        f.write(f" <span class='badge'><span data-i18n='confidence'>Confidence</span>: {conf}</span>")
    f.write("</div>")


def _render_paragraph(f, b, cls):
    f.write(f"<div class='card {cls}'>")
    f.write("<div class='meta'>")
    f.write("<span class='badge' data-i18n='paragraph'>PARAGRAPH</span>")
    f.write("</div>")
    _render_ai_info(f, b)

    if b.get("change") == "changed":
        oldt = html.escape(b.get("old", {}).get("text", "") or "")
        newt = html.escape(b.get("new", {}).get("text", "") or "")
        f.write(f"<p class='small'><b><span data-i18n='old'>Old</span>:</b> {oldt}</p>")
        f.write(f"<p class='small'><b><span data-i18n='new'>New</span:</b> {newt}</p>")
        inline = b.get("inline_html")
        if inline:
            # inline_html already contains <del>/<ins> - insert unescaped
            f.write(f"<div class='small'><b><span data-i18n='inline'>Inline diff</span>:</b><div class='pre diff'>{inline}</div></div>")
    else:
        text = html.escape(b.get("text") or b.get("old", {}).get("text") or "")
        f.write(f"<p class='small'>{text}</p>")

    f.write("</div>")


def _render_table(f, b, cls):
    f.write(f"<div class='card {cls}'>")
    f.write("<div class='meta'><span class='badge' data-i18n='table'>TABLE</span></div>")
    _render_ai_info(f, b)

    # if we have table_changes (cell-level diffs), use them; otherwise, regular table
    table_changes = b.get("table_changes")
    if table_changes:
        rows = table_changes
    else:
        # older format: table may be a list of rows (strings)
        rows = b.get("table") or b.get("new", {}).get("table") or []

    f.write("<table>")
    for row in rows:
        f.write("<tr>")
        for cell in row:
            if isinstance(cell, dict):
                if cell.get("type") == "same":
                    # escape plain text
                    f.write(f"<td>{html.escape(cell.get('text',''))}</td>")
                else:
                    # inline_html has <del>/<ins>
                    f.write(f"<td>{cell.get('inline_html','')}</td>")
            else:
                # cell is plain string
                f.write(f"<td>{html.escape(str(cell))}</td>")
        f.write("</tr>")
    f.write("</table></div>")


def _render_image(f, b, cls):
    sha = b.get("sha1") or b.get("new", {}).get("sha1") or ""
    f.write(f"<div class='card {cls}'>")
    f.write("<div class='meta'><span class='badge' data-i18n='image'>IMAGE</span></div>")
    _render_ai_info(f, b)
    f.write(f"<p class='small'>SHA1={html.escape((sha or '')[:12])}...</p>")
    f.write("</div>")

# -------------------------
# Main render
# -------------------------
def generate_html_report(block_diffs: List[Dict[str, Any]], output_path: str = "report.html") -> None:
    # 1) basic statistics and scoring
    stats = compute_stats_and_scores(block_diffs)

    # 2) AI analysis (for "changed") — fills _ai_* fields
    for b in block_diffs:
        if b.get("change") == "changed":
            try:
                ai = analyze_change(b)
                b["_ai_labels"] = ai.get("labels")
                b["_ai_sem_score"] = ai.get("semantic_score")
                b["_ai_type"] = ai.get("change_type")
                b["_ai_conf"] = ai.get("confidence")
            except Exception:
                _LOGGER.exception("AI analyze_change error", exc_info=True)
                b["_ai_labels"] = []
                b["_ai_sem_score"] = None
                b["_ai_type"] = ""
                b["_ai_conf"] = None

    # 3) prepare TOC sorted by ai_score (fallback to _score)
    # We want the most significant first
    indexed = list(range(len(block_diffs)))

    def sort_key(i):
        ai_s = block_diffs[i].get("_ai_sem_score")
        score = block_diffs[i].get("_score", 0)
        # if ai_s is None -> use score * 0.6 to still include
        if ai_s is None:
            return score * 0.6
        return ai_s + (score * 0.1)

    # filter to include only changed/added/deleted
    toc_items = [i for i in indexed if block_diffs[i].get("change") in ("changed", "added", "deleted")]
    toc_items.sort(key=sort_key, reverse=True)

    summary_html = generate_ai_summary(block_diffs)

    # 4) generate file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>")
        f.write(STYLE)

        # JS (deferred / DOMContentLoaded)
        f.write("""
        <script defer>
        function toggleClass(el, cls){ el.classList.toggle(cls); }
        function filterBy(){
          document.querySelectorAll('[data-change]').forEach(function(n){
            const ch = n.dataset.change;
            const typ = n.dataset.type;
            let show = true;
            if(window.filterChange.length && window.filterChange.indexOf(ch) === -1) show = false;
            if(window.filterType.length && window.filterType.indexOf(typ) === -1) show = false;
            n.style.display = show ? '' : 'none';
          });
        }
        function initFilters(){
          window.filterChange = [];
          window.filterType = [];
          document.querySelectorAll('.chip.change').forEach(function(c){
            c.addEventListener('click', function(){
              toggleClass(c,'active');
              const v = c.dataset.val;
              if(c.classList.contains('active')) window.filterChange.push(v);
              else window.filterChange = window.filterChange.filter(x=>x!==v);
              filterBy();
            });
          document.querySelectorAll(".lang-btn").forEach(btn=>{
              btn.addEventListener("click", function(){
                setLang(this.dataset.lang);
              });
            });
          });
          document.querySelectorAll('.chip.type').forEach(function(c){
            c.addEventListener('click', function(){
              toggleClass(c,'active');
              const v = c.dataset.val;
              if(c.classList.contains('active')) window.filterType.push(v);
              else window.filterType = window.filterType.filter(x=>x!==v);
              filterBy();
            });
          });
        
          var collBtn = document.querySelector('.collapse-toggle');
          if(collBtn){
            collBtn.addEventListener('click', function(){
              // check if currently collapsed (all unchanged hidden)
              var unchanged = Array.from(document.querySelectorAll('.unchanged'));
              var anyVisible = unchanged.some(x => x.style.display !== 'none');
              if (anyVisible) {
                  unchanged.forEach(x => x.style.display = 'none');
                  this.dataset.state = "hidden";
                  this.textContent = I18N[CURRENT_LANG].show_unchanged;
                } else {
                  unchanged.forEach(x => x.style.display = '');
                  this.dataset.state = "shown";
                  this.textContent = I18N[CURRENT_LANG].hide_unchanged;
                }
            });
          }
        
          // dark mode toggle
          var dmBtn = document.querySelector('.dark-toggle');
          if(dmBtn){
            dmBtn.addEventListener('click', function(){
              document.body.classList.toggle('dark');
              dmBtn.textContent = document.body.classList.contains('dark')
              ? I18N[CURRENT_LANG].mode_dark
              : I18N[CURRENT_LANG].mode_light;
            });
          }
        
          // smooth anchor scroll for TOC links
          document.querySelectorAll('.toc a').forEach(function(a){
            a.addEventListener('click', function(e){
              e.preventDefault();
              var id = this.getAttribute('href').slice(1);
              var el = document.getElementById(id);
              if(el) el.scrollIntoView({behavior:'smooth', block:'center'});
            });
          });
        
        } // end initFilters
        
        document.addEventListener('DOMContentLoaded', initFilters);
        </script>
        """)
        f.write("""
        <script>
        const I18N = {
          en: {
            added: "added", 
            deleted: "deleted", 
            changed: "changed", 
            unchanged: "unchanged",
            paragraph: "Paragraph",
            table: "Table",
            image: "Image",
            score: "Score",
            back: "Back to DocDiff",
            title: "Document Comparison Report",
            total: "Total blocks",
            ai_summary: "AI Summary",
            toc: "Most Significant Changes (TOC)",
            hide_unchanged: "Hide unchanged",
            show_unchanged: "Show unchanged",
            mode_light: "Mode: light",
            mode_dark: "Mode: dark",
            change: "change",
            old: "Old",
            new: "New",
            inline: "Inline diff",
            relevance: "Relevance",
            confidence: "Confidence",
            type: "Type"
          },
          pl: {
            added: "dodane", 
            deleted: "usunięte", 
            changed: "zmienione", 
            unchanged: "bez zmian",
            paragraph: "Akapit",
            table: "Tabela",
            image: "Obraz",
            score: "Wynik",
            back: "Powrót do DocDiff",
            title: "Raport porównania dokumentów",
            total: "Łączna liczba bloków",
            ai_summary: "Podsumowanie AI",
            toc: "Najistotniejsze zmiany",
            hide_unchanged: "Ukryj bez zmian",
            show_unchanged: "Pokaż bez zmian",
            mode_light: "Tryb: jasny",
            mode_dark: "Tryb: ciemny",
            change: "zmiana",
            old: "Stare",
            new: "Nowe",
            inline: "Różnice",
            relevance: "Istotność",
            confidence: "Pewność",
            type: "Typ"
          }
        };

        let CURRENT_LANG = "en";

        function setLang(lang){
          CURRENT_LANG = lang;
    
          document.querySelectorAll("[data-i18n]").forEach(el=>{
            const key = el.dataset.i18n;
            if(I18N[lang][key]){
              el.textContent = I18N[lang][key];
            }
          });
    
          const dmBtn = document.querySelector(".dark-toggle");
          if (dmBtn) {
            dmBtn.textContent = document.body.classList.contains("dark")
              ? I18N[lang].mode_dark
              : I18N[lang].mode_light;
          }
    
          const collapseBtn = document.querySelector(".collapse-toggle");
            if (collapseBtn) {
              const hidden = collapseBtn.dataset.state === "hidden";
              collapseBtn.textContent = hidden
                ? I18N[CURRENT_LANG].show_unchanged
                : I18N[CURRENT_LANG].hide_unchanged;
            }
        }
        
        document.addEventListener("DOMContentLoaded", function () {
          setLang(CURRENT_LANG);
        });
        </script>
        """)

        # body start
        f.write("</head><body><div class='container'>")
        f.write("""
        <div style="margin-bottom:12px;font-size:1.1em; display:flex; justify-content:space-between; align-items:center;">
          <a href="/docdiff/" style="text-decoration:none;color:var(--accent);">
            ← <span data-i18n="back">Back to DocDiff</span>
          </a>
          <div>
            <button class="chip lang-btn" data-lang="en">EN</button>
            <button class="chip lang-btn" data-lang="pl">PL</button>
          </div>
        </div>
        """)
        f.write("<div class='header'><div>")
        f.write("<h1 data-i18n='title'>Document Comparison Report</h1>")
        f.write(f"<div class='small'><span data-i18n='total'>Total blocks</span>: {len(block_diffs)}</div>")
        f.write("</div>")

        # right side header: dark mode button
        f.write("<div style='display:flex;align-items:center;gap:8px;'>")
        f.write("<button class='chip dark-toggle'>Mode: light</button>")
        f.write("</div></div>")  # header end

        # AI summary card
        f.write(f"""
        <div class='card'>
          <b data-i18n="ai_summary">AI Summary</b>:
          <div class='small'>{summary_html}</div>
        </div>
        """)

        # controls (chips)
        f.write("<div class='controls card'>")
        for ch in ("added", "deleted", "changed", "unchanged"):
            f.write(f"<span class='chip change' data-val='{ch}' data-i18n='{ch}'>{ch}</span>")
        for t in stats["by_type"]:
            f.write(f"<span class='chip type' data-val='{html.escape(t)}' data-i18n='{html.escape(t)}'>{html.escape(t)}</span>")
        f.write("</div>")

        # TOC sorted by AI score
        f.write("""
        <div class='toc card'>
          <b data-i18n="toc">Most Significant Changes (TOC)</b>:
        """)
        for i in toc_items[:200]:
            b = block_diffs[i]
            name = html.escape(str(b.get("type") or "blk"))
            aisc = b.get("_ai_sem_score")
            score = b.get("_score", 0)
            label = f"{aisc}/10" if aisc is not None else f"s={score}"
            f.write(f"<a href='#blk{i}'>#{i}({name}) {label}</a>")
        f.write("</div>")

        # collapse toggle
        f.write("<div style='margin-bottom:10px;'><button class='collapse-toggle chip' data-i18n='hide_unchanged'>Hide unchanged</button></div>")

        # render blocks
        for i, b in enumerate(block_diffs):
            ch = html.escape(str(b.get("change", "unknown")))
            typ = b.get("type") or b.get("new", {}).get("type") or b.get("old", {}).get("type") or "unknown"
            typ = str(typ)
            score = b.get("_score", 0)
            score_cls = "low" if score < 3 else ("med" if score < 6 else "high")
            # wrapper with attributes
            f.write(f"<div id='blk{i}' class='card {html.escape(ch)}' data-change='{html.escape(ch)}' data-type='{html.escape(typ)}'>")
            f.write("<div class='meta'>")
            f.write(f"<span class='badge' data-i18n='{html.escape(typ)}>{html.escape(typ).upper()}</span>")
            f.write(f"<span class='small'>change: {html.escape(str(b.get('change','')))}</span>")
            f.write(f"<span class='score {score_cls}'>s={score}</span>")
            f.write("</div>")  # meta end

            # render by type
            if typ == "paragraph":
                _render_paragraph(f, b, html.escape(ch))
            elif typ == "table":
                _render_table(f, b, html.escape(ch))
            elif typ == "image":
                _render_image(f, b, html.escape(ch))
            else:
                f.write(f"<div class='small'><pre>{html.escape(str(b))}</pre></div>")

            f.write("</div>")  # block wrapper

        # footer / close
        f.write("</div></body></html>")


# -------------------------
# JSON export
# -------------------------
def generate_json_report(block_diffs: List[Dict[str, Any]], output_path: str = "report.json") -> None:
    """Save the comparison report as JSON."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(block_diffs, f, ensure_ascii=False, indent=2)
    except Exception:
        _LOGGER.exception("Error while writing JSON report")
        raise
