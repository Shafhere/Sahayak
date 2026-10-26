"""Self-contained, multilingual, printable HTML action plan."""
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
from app.ui.labels import labels


def generate_html_report(profile, plan):
    t = labels(profile.language)
    e = lambda value: escape(str(value), quote=True)
    cards = []
    for index, option in enumerate(plan.eligible_schemes, 1):
        source = e(option.source_name)
        if option.source_url.startswith(("https://", "http://")):
            url = option.source_url + (f"#page={option.source_page}" if option.source_page and ".pdf" in option.source_url else "")
            source = f'<a href="{e(url)}" rel="noopener noreferrer">{source or e(t["source"])}</a>'
        else:
            source = e(t["missing"])
        cards.append(f"""<article class="card"><span class="number">{index:02d}</span>
          <h2>{e(option.name)}</h2><p>{e(option.benefits)}</p>
          <h3>{e(t['why'])}</h3><p>{e(option.why_relevant)}</p>
          <h3>{e(t['checks'])}</h3><p>{e(option.eligibility_note)}</p>
          <p class="muted">{e(t['deadline'])}: {e(option.deadline or t['unknown'])}</p>
          <details open><summary>{e(t['evidence'])}</summary><blockquote>{e(option.evidence_quote)}</blockquote>
          <p>{source} {(' · p. ' + str(option.source_page)) if option.source_page else ''}</p>
          <p class="muted">{e(option.source_edition)}</p></details></article>""")
    steps = ''.join(f'<li>{e(step)}</li>' for step in plan.next_steps)
    timeline = ''.join(f'<li><strong>{e(step.step)}</strong><p class="muted">{e(step.time_estimate)}</p></li>' for step in plan.timeline)
    documents = ''.join(f'<label class="check"><input type="checkbox"> <span>{e(item)}</span></label>' for item in plan.document_checklist)
    sections = ''
    if steps:
        sections += f'<section class="start"><h2>{e(t["next"])}</h2><ol>{steps}</ol></section>'
    sections += ''.join(cards)
    if timeline:
        sections += f'<section><h2>{e(t["timeline"])}</h2><ol class="roadmap">{timeline}</ol></section>'
    if documents:
        sections += f'<section><h2>{e(t["docs"])}</h2>{documents}</section>'
    return f"""<!doctype html><html lang="{e(profile.language)}"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1"><title>Sahayak · {e(t['title'])}</title>
    <style>
    :root{{color-scheme:light}}*{{box-sizing:border-box}}body{{margin:0;background:#f6f4ee;color:#183c3b;font-family:'Nirmala UI','Segoe UI',sans-serif;font-size:16px;line-height:1.65}}
    main{{max-width:880px;margin:auto;padding:36px 24px 64px}}header{{background:#174d49;color:white;padding:36px;border-radius:22px;margin-bottom:24px}}
    .brand{{font-size:12px;letter-spacing:3px;font-weight:700}}h1{{font-size:34px;line-height:1.3;margin:16px 0}}h2{{font-size:23px;line-height:1.4}}h3{{font-size:15px;margin-bottom:2px}}
    section,.card{{padding:28px;background:white;border:1px solid #dce4df;border-radius:18px;margin:20px 0;break-inside:avoid}}
    .start{{background:#e5f0e7}}.number{{color:#b45d3f;font-weight:700;font-size:14px}}.muted{{color:#60716c;font-size:13px}}
    li{{padding:6px 0}}.roadmap li{{padding:10px}}.check{{display:flex;gap:10px;margin:14px 0;align-items:flex-start}}input{{width:18px;height:18px;margin-top:5px;accent-color:#174d49}}
    a{{color:#17655e;overflow-wrap:anywhere}}blockquote{{border-left:3px solid #c98a6c;margin:12px 0;padding:8px 16px;color:#4d625c;font-size:14px}}
    summary{{cursor:pointer;font-weight:600}}button{{border:0;border-radius:10px;background:#d8805c;color:#132f2d;padding:12px 18px;font:inherit;font-weight:600;cursor:pointer}}
    footer{{padding:20px;color:#60716c;font-size:13px}}@media(max-width:600px){{main{{padding:16px}}header,.card,section{{padding:22px}}h1{{font-size:28px}}}}
    @page{{size:A4;margin:16mm}}@media print{{body{{background:white;font-size:11pt}}main{{padding:0;max-width:none}}button{{display:none}}header{{background:white;color:#174d49;border-bottom:3px solid #174d49;border-radius:0;padding:0 0 20px}}section,.card{{box-shadow:none}}details{{display:block}}summary{{display:none}}}}
    </style></head><body><main><header><div class="brand">SAHAYAK</div><h1>{e(t['title'])}</h1>
    <p>{e(plan.greeting)}</p><button onclick="window.print()">{e(t['print'])}</button></header>
    {sections}<footer>{e(t['verify'])}<p>{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d %b %Y · %H:%M IST')}</p></footer>
    </main></body></html>"""
