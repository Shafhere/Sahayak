"""Self-contained, multilingual, printable HTML action plan."""
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
from app.ui.labels import labels


def generate_html_report(profile, plan):
    t = labels(profile.language)

    def e(value):
        return escape(str(value), quote=True)

    # ---- Header ------------------------------------------------------------
    hero = f"""
    <header class="hero">
      <div class="brand">SAHAYAK</div>
      <h1>{e(t['title'])}</h1>
      {f'<p class="greeting">{e(plan.greeting)}</p>' if plan.greeting else ''}
      <p class="disclaimer">{e(t['verify'])}</p>
    </header>
    """

    # ---- "Start here" next steps ------------------------------------------
    start_section = ""
    if plan.next_steps:
        items = "".join(f"<li>{e(step)}</li>" for step in plan.next_steps)
        start_section = f"""
        <section class="start">
          <h2><span class="num">1</span> {e(t['next'])}</h2>
          <ol class="start-list">{items}</ol>
        </section>
        """

    # ---- Scheme / pathway cards -------------------------------------------
    cards = []
    for index, option in enumerate(plan.eligible_schemes, 1):
        # Source link
        if option.source_url.startswith(("https://", "http://")):
            url = option.source_url
            if option.source_page and ".pdf" in option.source_url:
                url += f"#page={option.source_page}"
            source_html = (
                f'<a href="{e(url)}" rel="noopener noreferrer">'
                f'{e(option.source_name or t["source"])}</a>'
            )
        else:
            source_html = e(t["missing"])

        page_html = (
            f'<span class="muted"> · p. {e(option.source_page)}</span>'
            if option.source_page else ""
        )
        edition_html = (
            f'<p class="muted">{e(option.source_edition)}</p>'
            if option.source_edition else ""
        )

        # Purpose: scheme vs mentor wording
        section_title = (
            t["scheme"] if profile.mode == "scheme" else t["mentor"]
        )

        cards.append(f"""
        <article class="card">
          <div class="card-head">
            <span class="badge">{index:02d}</span>
            <h2>{e(option.name)}</h2>
          </div>

          {f'<p class="benefits">{e(option.benefits)}</p>' if option.benefits else ''}

          {f'''
          <h3>{e(t['why'])}</h3>
          <p>{e(option.why_relevant)}</p>
          ''' if option.why_relevant else ''}

          {f'''
          <h3>{e(t['checks'])}</h3>
          <p>{e(option.eligibility_note)}</p>
          ''' if option.eligibility_note else ''}

          {f'''
          <p class="deadline"><strong>{e(t['deadline'])}:</strong>
             {e(option.deadline)}</p>
          ''' if option.deadline else ''}

          <details>
            <summary>{e(t['evidence'])}</summary>
            {f'<blockquote>{e(option.evidence_quote)}</blockquote>' if option.evidence_quote else ''}
            <p>{source_html}{page_html}</p>
            {edition_html}
          </details>
        </article>
        """)

    schemes_section = ""
    if cards:
        schemes_section = f"""
        <section class="schemes">
          <h2><span class="num">2</span>
            {e(t['scheme'] if profile.mode == 'scheme' else t['mentor'])}
          </h2>
          {''.join(cards)}
        </section>
        """

    # ---- Timeline ---------------------------------------------------------
    timeline_section = ""
    if plan.timeline:
        steps = []
        for i, step in enumerate(plan.timeline, 1):
            time_html = (
                f'<span class="time">{e(step.time_estimate)}</span>'
                if step.time_estimate else ''
            )
            steps.append(f"""
            <li class="roadmap-step">
              <span class="step-num">{i}</span>
              <div>
                <p class="step-text">{e(step.step)}</p>
                {time_html}
              </div>
            </li>
            """)
        timeline_section = f"""
        <section class="timeline">
          <h2><span class="num">3</span> {e(t['timeline'])}</h2>
          <ol class="roadmap">{''.join(steps)}</ol>
        </section>
        """

    # ---- Document checklist ----------------------------------------------
    docs_section = ""
    if plan.document_checklist:
        items = "".join(
            f'<label class="check"><input type="checkbox" />'
            f'<span>{e(item)}</span></label>'
            for item in plan.document_checklist
        )
        docs_section = f"""
        <section class="docs">
          <h2><span class="num">4</span> {e(t['docs'])}</h2>
          <div class="checklist">{items}</div>
        </section>
        """

    # ---- Footer -----------------------------------------------------------
    generated = datetime.now(ZoneInfo("Asia/Kolkata")).strftime(
        "%d %b %Y · %H:%M IST"
    )
    footer = f"""
    <footer>
      <p class="disclaimer">{e(t['verify'])}</p>
      <p class="muted">Generated {e(generated)}</p>
    </footer>
    """

    # ---- Assembled page ---------------------------------------------------
    return f"""<!doctype html>
<html lang="{e(profile.language)}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Sahayak · {e(t['title'])}</title>
<style>
:root {{
  color-scheme: light;
  --bg: #F5F3EE;
  --paper: #FFFFFF;
  --ink: #24342F;
  --muted: #6B7A73;
  --accent: #C87559;
  --accent-dark: #A85B42;
  --green: #174D49;
  --line: #E6E1D7;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "DM Sans", "Nirmala UI", "Segoe UI", system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.65;
}}
main {{
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}}

/* Header */
.hero {{
  background: var(--green);
  color: #FFFFFF;
  border-radius: 20px;
  padding: 36px 34px;
  margin-bottom: 26px;
}}
.brand {{
  font-size: 12px;
  letter-spacing: 4px;
  font-weight: 700;
  opacity: 0.85;
}}
.hero h1 {{
  font-family: "Lora", Georgia, serif;
  font-size: 34px;
  line-height: 1.25;
  margin: 14px 0 12px;
  font-weight: 600;
}}
.greeting {{
  font-size: 17px;
  line-height: 1.6;
  margin: 0 0 14px;
  color: #EDE9E1;
}}
.hero .disclaimer {{
  font-size: 12px;
  line-height: 1.55;
  color: #C8D5CF;
  margin: 16px 0 0;
}}

/* Section */
section {{
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 26px 28px;
  margin: 20px 0;
  break-inside: avoid;
}}
section h2 {{
  font-family: "Lora", Georgia, serif;
  font-size: 21px;
  font-weight: 600;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}}
.num {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--accent);
  color: #FFFFFF;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  font-family: "DM Sans", sans-serif;
}}

/* Start list */
.start {{ background: #F3EFE3; }}
.start-list {{
  padding-left: 20px;
  margin: 0;
}}
.start-list li {{
  padding: 8px 0;
  font-size: 16px;
  line-height: 1.55;
}}
.start-list li::marker {{
  color: var(--accent);
  font-weight: 700;
}}

/* Scheme cards */
.card {{
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 22px 22px;
  margin: 14px 0;
  background: #FCFBF7;
  break-inside: avoid;
}}
.card-head {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}}
.badge {{
  background: var(--accent);
  color: #FFFFFF;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
}}
.card h2 {{
  font-size: 19px;
  margin: 0;
}}
.card h3 {{
  font-size: 14px;
  margin: 16px 0 4px;
  color: var(--accent-dark);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}}
.card p {{
  margin: 0 0 8px;
  font-size: 15px;
  line-height: 1.6;
}}
.benefits {{
  font-weight: 500;
  color: var(--ink);
}}
.deadline {{
  margin-top: 12px;
  font-size: 14px;
  color: var(--muted);
}}

/* Details / evidence */
details {{
  margin-top: 14px;
  padding: 10px 14px;
  background: #F3EFE3;
  border-radius: 8px;
}}
summary {{
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-dark);
}}
blockquote {{
  border-left: 3px solid var(--accent);
  margin: 10px 0;
  padding: 6px 14px;
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--muted);
}}
details p {{
  font-size: 12.5px;
  color: var(--muted);
  margin: 6px 0;
}}
a {{
  color: var(--green);
  word-break: break-all;
  text-decoration: underline;
}}
.muted {{
  color: var(--muted);
  font-size: 12.5px;
}}

/* Timeline */
.roadmap {{
  list-style: none;
  padding: 0;
  margin: 0;
}}
.roadmap-step {{
  display: flex;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
  align-items: flex-start;
}}
.roadmap-step:last-child {{
  border-bottom: none;
}}
.step-num {{
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #EEE9DD;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  color: var(--green);
}}
.step-text {{
  margin: 0;
  font-weight: 500;
  font-size: 15px;
}}
.time {{
  display: inline-block;
  margin-top: 4px;
  font-size: 12.5px;
  color: var(--muted);
}}

/* Checklist */
.checklist {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.check {{
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 10px 14px;
  border: 1px dashed var(--line);
  border-radius: 10px;
  background: #FCFBF7;
}}
.check input {{
  margin-top: 4px;
  width: 18px;
  height: 18px;
  accent-color: var(--accent);
}}
.check span {{
  font-size: 15px;
}}

/* Footer */
footer {{
  padding: 26px 22px;
  text-align: center;
  color: var(--muted);
  font-size: 12.5px;
  line-height: 1.6;
}}
footer .disclaimer {{
  max-width: 620px;
  margin: 0 auto 10px;
}}

/* Buttons */
.toolbar {{
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-bottom: 16px;
}}
button {{
  border: 0;
  border-radius: 10px;
  background: var(--accent);
  color: #FFFFFF;
  padding: 12px 20px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(200,117,89,0.28);
}}
button:hover {{ background: var(--accent-dark); }}

/* Print */
@page {{ size: A4; margin: 14mm; }}
@media print {{
  body {{ background: #FFFFFF; font-size: 11pt; }}
  main {{ padding: 0; max-width: none; }}
  .toolbar {{ display: none; }}
  .hero {{
    background: #FFFFFF;
    color: var(--ink);
    border-bottom: 3px solid var(--green);
    border-radius: 0;
    padding: 0 0 18px;
  }}
  .hero .brand {{ color: var(--green); }}
  .hero .greeting {{ color: var(--ink); }}
  .hero .disclaimer {{ color: var(--muted); }}
  section, .card {{
    box-shadow: none;
    border: 1px solid var(--line);
  }}
  details {{ display: block; background: #F5F3EE; }}
  summary {{ display: none; }}
  details > blockquote, details > p {{ display: block; }}
}}
</style>
</head>
<body>
<main>
  <div class="toolbar">
    <button onclick="window.print()">{e(t['print'])}</button>
  </div>
  {hero}
  {start_section}
  {schemes_section}
  {timeline_section}
  {docs_section}
  {footer}
</main>
</body>
</html>"""