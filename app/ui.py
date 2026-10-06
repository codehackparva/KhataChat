import gradio as gr
from app import agent, tools
from google.genai import types

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;800&family=IBM+Plex+Mono:wght@500&family=Inter:wght@400;600&display=swap');

/* dark mode ko bhi light theme bana do */
.gradio-container, .dark .gradio-container, .dark {
  --body-background-fill:#f6f1e4; --background-fill-primary:#fffdf6;
  --background-fill-secondary:#f6f1e4; --block-background-fill:#fffdf6;
  --body-text-color:#14342b; --body-text-color-subdued:#5b6b63;
  --block-label-text-color:#14342b; --block-title-text-color:#14342b;
  --input-background-fill:#fffdf6; --border-color-primary:#cdbf9c;
  --button-secondary-background-fill:#fffdf6; --button-secondary-text-color:#14342b;
}
body, .gradio-container { background:#f6f1e4 !important; font-family:'Inter',sans-serif !important; max-width:100% !important; padding:0 24px !important; }
.gradio-container, .gradio-container * { color:#14342b; }

.mn-hero { background:#14342b; padding:22px 28px; border-radius:14px; border-bottom:5px solid #e08a1e; }
.mn-hero h1 { font-family:'Fraunces',serif; font-size:2.2rem; margin:0; color:#f6f1e4 !important; }
.mn-hero p { margin:4px 0 0; color:#f6f1e4 !important; opacity:.85; }
.mn-chip { display:inline-block; margin-top:10px; padding:3px 12px; border-radius:99px; background:#e08a1e; color:#14342b !important; font-size:.78rem; font-weight:600; }

.mn-paper { background:repeating-linear-gradient(#fffdf6,#fffdf6 31px,#d9e4dc 32px) !important; border:1px solid #cdbf9c !important; border-left:5px solid #b3423a !important; border-radius:8px; padding:12px 18px; min-height:260px; line-height:32px; }
.mn-paper, .mn-paper * { color:#14342b !important; }

.mn-cards { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.mn-card { background:#fffdf6; border:1px solid #cdbf9c; border-radius:10px; padding:12px 14px; }
.mn-card small { color:#5b6b63 !important; font-weight:600; text-transform:uppercase; letter-spacing:.05em; font-size:.7rem; }
.mn-card b { display:block; font-family:'IBM Plex Mono',monospace; font-size:1.35rem; color:#14342b !important; margin-top:2px; }
.mn-card.loss b { color:#b3423a !important; }
.mn-card.gain b { color:#1d7a4f !important; }

.mn-tbl { width:100%; margin-top:12px; background:#fffdf6; border:1px solid #cdbf9c; border-radius:10px; border-collapse:collapse; }
.mn-tbl th { text-align:left; padding:8px 12px; font-size:.7rem; letter-spacing:.05em; text-transform:uppercase; color:#5b6b63 !important; border-bottom:2px solid #14342b; }
.mn-tbl td { padding:8px 12px; border-bottom:1px dashed #d9cfae; color:#14342b !important; }
.mn-tbl td.amt { font-family:'IBM Plex Mono',monospace; text-align:right; color:#b3423a !important; font-weight:600; }
.mn-note { padding:10px; color:#5b6b63 !important; }

/* input box aur examples */
.gradio-container textarea, .gradio-container input[type=text] { background:#fffdf6 !important; color:#14342b !important; border:1px solid #cdbf9c !important; }
.gradio-container label span, .gradio-container .label-wrap { color:#14342b !important; }
.gradio-container [class*="example"] button, .gradio-container [class*="example"] td { background:#fffdf6 !important; color:#14342b !important; border:1px solid #cdbf9c !important; }
.gradio-container .block { background:#fffdf6; }
.mn-hero, .gradio-container .block:has(.mn-hero) { background:#14342b !important; border:none !important; }

/* buttons */
.mn-yes { background:#14342b !important; border:none !important; }
.mn-yes, .mn-yes * { color:#f6f1e4 !important; }
.mn-no { background:#fffdf6 !important; border:1px solid #b3423a !important; }
.mn-no, .mn-no * { color:#b3423a !important; }

/* table ke mote borders hatao, sirf halki dashed lines rakho */
.gradio-container table.mn-tbl, .gradio-container table.mn-tbl th, .gradio-container table.mn-tbl td { border:none !important; }
.gradio-container table.mn-tbl { border:1px solid #cdbf9c !important; border-collapse:separate !important; border-spacing:0; overflow:hidden; }
.gradio-container table.mn-tbl th { border-bottom:2px solid #14342b !important; }
.gradio-container table.mn-tbl td { border-bottom:1px dashed #d9cfae !important; }

/* hero: gol corners aur orange line wapas */
.gradio-container .block:has(.mn-hero), .gradio-container div:has(> .mn-hero) {
  border-radius:14px !important; overflow:hidden; box-shadow:0 5px 0 #e08a1e !important;
}
.mn-hero { border-radius:14px; }
</style>
"""
HEAD = """
<script>
(function () {
  var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">' +
    '<rect width="64" height="64" rx="14" fill="#e08a1e"/>' +
    '<rect x="6" y="6" width="52" height="52" rx="10" fill="#14342b"/>' +
    '<text x="32" y="45" font-size="38" font-weight="700" text-anchor="middle" fill="#f6f1e4" font-family="Arial,sans-serif">&#8377;</text>' +
    '</svg>';
  function setIcon() {
    document.querySelectorAll('link[rel*="icon"]').forEach(function (l) { l.remove(); });
    var link = document.createElement('link');
    link.rel = 'icon';
    link.href = 'data:image/svg+xml,' + encodeURIComponent(svg);
    document.head.appendChild(link);
  }
  setIcon();
  setTimeout(setIcon, 1500);
})();
.mn-paper code { background:#e9e2cc !important; color:#14342b !important; padding:2px 8px; border-radius:6px; font-family:'IBM Plex Mono',monospace; }
</script>
"""

HERO = """
<div class="mn-hero">
  <h1>मुनीम · Munim</h1>
  <p>Dukaan ka hisaab, apni bhasha mein: Gujarati, Hindi ya English.</p>
  <span class="mn-chip">SDG 8 · Demo ledger, sirf fake data</span>
</div>
"""


def money(x):
    return f"₹{x:,.0f}"


def render_stats():
    try:
        sales = tools.query_ledger("total_sales")["value"]
        exp = tools.query_ledger("total_expenses")["value"]
        profit = tools.query_ledger("profit")["value"]
        owed = tools.query_ledger("outstanding_credit")["owed_by_party"]
    except Exception:
        return "<div class='mn-note'>Ledger load nahi hua. Page refresh karo.</div>"
    pcls = "gain" if profit >= 0 else "loss"
    plabel = "Profit" if profit >= 0 else "Loss"
    rows = "".join(
        f"<tr><td>{n}</td><td class='amt'>{money(v)}</td></tr>"
        for n, v in sorted(owed.items(), key=lambda x: -x[1])
    ) or "<tr><td colspan='2'>Kisi ka baaki nahi.</td></tr>"
    return f"""
    <div class="mn-cards">
      <div class="mn-card"><small>Total sales</small><b>{money(sales)}</b></div>
      <div class="mn-card"><small>Total expenses</small><b>{money(exp)}</b></div>
      <div class="mn-card {pcls}"><small>{plabel}</small><b>{money(abs(profit))}</b></div>
      <div class="mn-card"><small>Udhaar baaki</small><b>{money(sum(owed.values()))}</b></div>
    </div>
    <table class="mn-tbl"><tr><th>Udhaar khata</th><th style="text-align:right">Baaki</th></tr>{rows}</table>
    """


def _add(history, user_text, reply):
    return history + [
        types.Content(role="user", parts=[types.Part(text=user_text)]),
        types.Content(role="model", parts=[types.Part(text=reply)]),
    ]


def send(text, history, pending, log):
    text = (text or "").strip()
    if not text:
        return "", history, pending, log, gr.update(visible=bool(pending)), render_stats()
    out = agent.run_turn(history, text)
    log += f"\n\n**Aap:** {text}"
    if out["kind"] == "confirm":
        a = out["args"]
        pending = a
        log += (f"\n\n**Munim:** Save karun? `{a.get('type')}` · "
                f"₹{a.get('amount_rupees')} · {a.get('party') or '-'} · {a.get('note') or '-'}")
        history = _add(history, text, "Confirmation maanga.")
    else:
        pending = None
        log += f"\n\n**Munim:** {out['text']}"
        history = _add(history, text, out["text"])
    return "", history, pending, log, gr.update(visible=bool(pending)), render_stats()


def decide(choice, pending, log):
    if pending and choice == "yes":
        ok = agent.save(pending).get("ok")
        log += "\n\n**Munim:** " + ("Khate mein likh diya. ✅" if ok else "Save nahi hua, error aaya.")
    elif pending:
        log += "\n\n**Munim:** Cancel kar diya."
    return None, log, gr.update(visible=False), render_stats()


with gr.Blocks(title="Munim · Digital Khata", head=HEAD) as demo:
    gr.HTML(CSS + HERO)
    history = gr.State([])
    pending = gr.State(None)
    with gr.Row():
        with gr.Column(scale=3):
            log = gr.Markdown("*Likhiye: \"Ramesh ne 500 ka maal udhaar liya\"*", elem_classes="mn-paper")
            msg = gr.Textbox(label="Entry ya sawaal likho (Gujarati / Hindi / English)", placeholder="jaise: aaj ka profit kitna hai?")
            with gr.Row(visible=False) as confirm_row:
                yes = gr.Button("✔ Haan, khate mein likho", elem_classes="mn-yes")
                no = gr.Button("✖ Nahi", elem_classes="mn-no")
            gr.Examples(
                ["Ramesh ne 500 ka maal udhaar liya", "paanch hazaar rent bhara",
                 "kis kis ka paisa baaki hai?", "aaj ka profit kitna hai?"],
                inputs=msg,
            )
        with gr.Column(scale=2):
            stats = gr.HTML(render_stats())

    msg.submit(send, [msg, history, pending, log], [msg, history, pending, log, confirm_row, stats])
    yes.click(lambda p, l: decide("yes", p, l), [pending, log], [pending, log, confirm_row, stats])
    no.click(lambda p, l: decide("no", p, l), [pending, log], [pending, log, confirm_row, stats])

import os

if __name__ == "__main__":
    demo.launch(favicon_path=os.path.join(os.path.dirname(__file__), "favicon.png"))