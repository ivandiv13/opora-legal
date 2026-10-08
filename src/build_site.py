#!/usr/bin/env python3
"""Собирает статический сайт с юридическими страницами Opora для GitHub Pages.

Из корня папки legal/:  python3 src/build_site.py
Пересобирает index.html, privacy/, terms/, safety/, support/ из src/*.md.
Тексты правь в src/PRIVACY.md, src/TERMS.md, src/SAFETY.md; руками HTML не трогай — перезапишется.
"""

import re
from pathlib import Path

import markdown

# ─────────────────────────────────────────────────────────────
CONFIG = {
    "GITHUB_USER": "ivandiv13",
    "REPO": "opora-legal",
    "SUPPORT_EMAIL": "ivandiv13@gmail.com",
    "EFFECTIVE_DATE": "6 October 2026",
    # TODO(Иван): регион базы — Supabase → Project Settings → General → Region
    "SUPABASE_REGION": "[SUPABASE_REGION]",
    # TODO(Иван): у кого арендован VPS в Нидерландах (Hetzner, Aeza, …)
    "VPS_PROVIDER": "[VPS_PROVIDER]",
}
CONFIG["WEBSITE"] = f"https://{CONFIG['GITHUB_USER']}.github.io/{CONFIG['REPO']}"
# ─────────────────────────────────────────────────────────────

SRC = Path(__file__).parent          # src/
OUT = SRC.parent                     # корень сайта

# Цвета — из AppColor приложения: чёрный фон, белый текст, зелёный positive как акцент
CSS = """
:root {
  --bg: #000000; --surface: #121212; --text: #FFFFFF; --muted: rgba(255,255,255,.62);
  --line: rgba(255,255,255,.12); --accent: #A3CE72; --accent-dim: rgba(163,206,114,.45);
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 400 17px/1.65 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 44rem; margin: 0 auto; padding: 0 1.25rem 6rem; }
header.site {
  border-bottom: 1px solid var(--line); margin-bottom: 3rem;
  padding: 1.5rem 0; position: sticky; top: 0;
  background: rgba(0,0,0,.86); backdrop-filter: saturate(180%) blur(14px);
}
header.site .wrap { padding-bottom: 0; display: flex; align-items: baseline; gap: 1.5rem; flex-wrap: wrap; }
.brand { font-weight: 700; font-size: 1.15rem; letter-spacing: -.01em; color: var(--text); text-decoration: none; border: 0; }
.brand:hover { color: var(--accent); }
.hero { font-size: 2.6rem; font-weight: 700; letter-spacing: -.03em; margin: 0 0 .5rem; }
nav a { color: var(--muted); text-decoration: none; font-size: .95rem; margin-right: 1.1rem; border: 0; }
nav a:hover, nav a[aria-current] { color: var(--accent); }
h1 { font-size: 2rem; line-height: 1.2; letter-spacing: -.02em; margin: 0 0 .5rem; }
h2 { font-size: 1.35rem; line-height: 1.3; letter-spacing: -.01em; margin: 3rem 0 .75rem; padding-top: 1.25rem; border-top: 1px solid var(--line); }
h3 { font-size: 1.08rem; margin: 2rem 0 .5rem; color: var(--text); }
p, li { color: var(--text); }
a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-dim); }
a:hover { border-bottom-color: var(--accent); }
strong { font-weight: 650; }
hr { display: none; }
ul, ol { padding-left: 1.35rem; }
li { margin: .35rem 0; }
code { font: 500 .88em/1 ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--surface); padding: .15em .4em; border-radius: 4px; color: var(--accent); }
table { width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: .93rem; display: block; overflow-x: auto; }
th, td { text-align: left; padding: .6rem .75rem; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: .82rem; text-transform: uppercase; letter-spacing: .04em; white-space: nowrap; }
.meta { color: var(--muted); font-size: .93rem; margin: 0 0 2.5rem; }
.meta strong { color: var(--text); font-weight: 500; }
footer.site { border-top: 1px solid var(--line); margin-top: 4rem; padding-top: 1.5rem; color: var(--muted); font-size: .88rem; }
footer.site a { color: var(--muted); border-bottom-color: var(--line); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 1.25rem 1.5rem; margin: 1rem 0; }
.card h3 { margin-top: 0; }
.card p:last-child { margin-bottom: 0; }
@media (max-width: 640px) { body { font-size: 16px; } h1 { font-size: 1.6rem; } .wrap { padding: 0 1rem 4rem; } }
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="dark">
<style>{css}</style>
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{base}/">Opora</a>
  <nav>
    <a href="{base}/privacy/"{privacy_cur}>Privacy</a>
    <a href="{base}/terms/"{terms_cur}>Terms</a>
    <a href="{base}/safety/"{safety_cur}>Safety</a>
    <a href="{base}/support/"{support_cur}>Support</a>
  </nav>
</div></header>
<main class="wrap">
{body}
<footer class="site">
  <p>Opora — Individual Entrepreneur Ivan Bannikov, Georgia · <a href="mailto:{email}">{email}</a></p>
</footer>
</main>
</body>
</html>
"""

PAGES = ("privacy", "terms", "safety", "support")


def fill(text: str) -> str:
    for key, value in CONFIG.items():
        text = text.replace(f"[{key}]", value)
    return text


def render(md_text: str) -> str:
    html = markdown.markdown(
        md_text,
        extensions=["tables", "attr_list", "sane_lists", "md_in_html"],
        output_format="html5",
    )
    # «**Effective date:** …» в шапке -> компактный блок .meta с разделителями
    def meta(m: re.Match) -> str:
        inner = m.group(1).strip().replace("\n", " · ")
        return f'<p class="meta">{inner}</p>'

    html = re.sub(
        r"<p>(<strong>Effective date:.*?)</p>", meta, html, count=1, flags=re.S
    )
    return html


def page(name: str, title: str, desc: str, body: str) -> None:
    target = OUT / name if name else OUT
    target.mkdir(parents=True, exist_ok=True)
    current = {f"{p}_cur": ' aria-current="page"' if name == p else "" for p in PAGES}
    (target / "index.html").write_text(
        PAGE.format(
            title=title,
            desc=desc,
            css=CSS,
            base=CONFIG["WEBSITE"],
            body=body,
            email=CONFIG["SUPPORT_EMAIL"],
            **current,
        ),
        encoding="utf-8",
    )
    print(f"  {CONFIG['WEBSITE']}/{name}")


def main() -> None:
    print("Собираю:")

    page(
        "privacy",
        "Privacy Policy — Opora",
        "How Opora collects, uses and protects your personal data.",
        render(fill((SRC / "PRIVACY.md").read_text(encoding="utf-8"))),
    )
    page(
        "terms",
        "Terms of Use — Opora",
        "The terms that govern your use of the Opora app.",
        render(fill((SRC / "TERMS.md").read_text(encoding="utf-8"))),
    )
    page(
        "safety",
        "Safety — Opora",
        "Opora is not therapy or a crisis service. Where to get help right now.",
        render(fill((SRC / "SAFETY.md").read_text(encoding="utf-8"))),
    )
    page(
        "support",
        "Support — Opora",
        "Get help with Opora: subscriptions, account deletion, reporting a problem.",
        render(fill(SUPPORT_MD)),
    )
    page(
        "",
        "Opora — AI journal and companion",
        "Opora — an AI journal and companion. Legal, safety and support pages.",
        render(fill(INDEX_MD)),
    )

    # .nojekyll — иначе GitHub Pages прогоняет всё через Jekyll и может съесть файлы с _
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    left = sorted(
        {m for p in OUT.rglob("index.html") for m in re.findall(r"\[[A-Z_]{4,}\]", p.read_text())}
    )
    if left:
        print(f"\nНе заполнено: {', '.join(left)} — допиши в CONFIG и пересобери.")
    print("\nГотово. Закоммить и запушь — GitHub Pages подхватит сам.")


SUPPORT_MD = """
# Support

Something not working, or a question about your account? Email
**[SUPPORT_EMAIL]** and you will get a reply from a human, usually within
two business days.

If you are struggling right now, please see our [Safety page]([WEBSITE]/safety)
— it lists where to get help immediately.

## Frequently asked

### How do I cancel my subscription?

Subscriptions are billed by Apple, so they are cancelled on your device:
**Settings → your name → Subscriptions → Opora → Cancel Subscription**.
Cancel at least 24 hours before the period ends. You keep access until the
end of the period you have already paid for.

### I was charged after the free trial. Can I get a refund?

Refunds are handled by Apple, not by us. Request one at
[reportaproblem.apple.com](https://reportaproblem.apple.com).

### I restored my purchase and it did not come back.

Make sure you are signed in with the same Apple Account that made the
purchase, then tap **Restore Purchases** on the subscription screen. If it
still does not appear, email us with the date of purchase and we will sort
it out.

### I got a new phone. How do I keep my journal?

Link **Sign in with Apple** in the app, then sign in with the same Apple
Account on the new phone. Without it, your journal is tied to the app on
your current device and cannot be recovered after the app is deleted.

### Who can read what I write?

Nobody at Opora reads your conversations or your journal. Opora's replies are
generated by AI models: to answer you, the conversation and the name you asked
Opora to call you are sent to the AI provider — never your email or account — and the provider
may not train on it.

We do not keep your conversations, either. The full text is deleted within
72 hours; Opora keeps only short summaries and notes so it can remember you.
Details are in the [Privacy Policy]([WEBSITE]/privacy).

### Can I turn off reminders, or hide them from my lock screen?

Yes: **Settings → Notifications → Opora**. Turn notifications off, or set
**Show Previews** to *When Unlocked* or *Never*.

### How do I delete my account?

In the app: **Settings → Delete account**. This permanently deletes your
account and your whole journal. It cannot be undone, and it does not cancel
an active subscription — cancel that separately as described above.

### Opora said something wrong or hurtful.

Please tell us at **[SUPPORT_EMAIL]**. Describe what happened; you do not
need to send the whole conversation.

## Legal

[Privacy Policy]([WEBSITE]/privacy) · [Terms of Use]([WEBSITE]/terms) · [Safety]([WEBSITE]/safety)

## Contact

**Ivan Bannikov**, Individual Entrepreneur

- Nino and Ilia Nakashidze Str. N1, Building N3, Apt. 3, Krtsanisi District, Tbilisi, Georgia
- Identification number: 304675625
- Email: **[SUPPORT_EMAIL]**
"""

INDEX_MD = """
<p class="hero">Opora</p>

An AI journal and companion. Talk about your day — what weighs on you and
what went well — and get support, reflection, and insight over time.

<div class="card" markdown="1">

### Documents

[Privacy Policy]([WEBSITE]/privacy) — what we collect, why, and what you can ask us to do about it.

[Terms of Use]([WEBSITE]/terms) — the agreement that governs your use of the app.

[Safety]([WEBSITE]/safety) — Opora is not therapy or a crisis service. Where to get help right now.

[Support]([WEBSITE]/support) — subscriptions, account deletion, and how to reach a human.

</div>

## Contact

Opora is made by **Ivan Bannikov**, Individual Entrepreneur registered in Georgia
(identification number 304675625).

Email: **[SUPPORT_EMAIL]**
"""

if __name__ == "__main__":
    main()
