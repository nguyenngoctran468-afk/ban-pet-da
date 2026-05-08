import os

base_dir = "/Users/nguyenngoctran/Documents/Antigravity Projects/Day 2 - Build landing page/ke-hoach-kinh-doanh/"

template = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Phaodr Asset</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #050505;
            --surface: #121212;
            --primary: #00ff88;
            --text: #ffffff;
            --text-dim: #a0a0a0;
            --border: rgba(255, 255, 255, 0.1);
        }}
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.8;
            padding: 4rem 2rem;
            max-width: 900px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            font-family: 'Playfair Display', serif;
            color: var(--primary);
            margin-top: 2.5rem;
            margin-bottom: 1rem;
        }}
        h1 {{ font-size: 3rem; border-bottom: 2px solid var(--primary); padding-bottom: 1rem; margin-top: 0; }}
        p {{ margin-bottom: 1.5rem; color: var(--text-dim); }}
        ul, ol {{ margin-bottom: 1.5rem; padding-left: 2rem; color: var(--text-dim); }}
        li {{ margin-bottom: 0.5rem; }}
        code {{ background: rgba(255, 255, 255, 0.05); padding: 0.2rem 0.5rem; border-radius: 4px; color: var(--primary); }}
        pre {{ background: #1a1a1a; padding: 1.5rem; border-radius: 12px; overflow-x: auto; border: 1px solid var(--border); margin: 2rem 0; white-space: pre-wrap; }}
        blockquote {{ border-left: 4px solid var(--primary); padding-left: 1.5rem; font-style: italic; margin: 2rem 0; color: #fff; }}
        table {{ width: 100%; border-collapse: collapse; margin: 2rem 0; border: 1px solid var(--border); }}
        th, td {{ padding: 1rem; border: 1px solid var(--border); text-align: left; }}
        th {{ background: rgba(0, 255, 136, 0.1); color: var(--primary); }}
        .back-btn {{
            position: fixed;
            top: 2rem;
            left: 2rem;
            padding: 0.8rem 1.5rem;
            background: var(--surface);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            border: 1px solid var(--border);
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s;
            z-index: 100;
        }}
        .back-btn:hover {{ border-color: var(--primary); background: var(--primary); color: #000; }}
    </style>
</head>
<body>
    <a href="index.html" class="back-btn">← Dashboard</a>
    <article>
        {content}
    </article>
</body>
</html>"""

def convert_md_line(line):
    line = line.strip()
    if not line: return ""
    
    # Inline formatting
    import re
    line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
    line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color:var(--primary);">\1</a>', line)
    
    if line.startswith("# "): return f"<h1>{line[2:]}</h1>"
    if line.startswith("## "): return f"<h2>{line[3:]}</h2>"
    if line.startswith("### "): return f"<h3>{line[4:]}</h3>"
    if line.startswith("- "): return f"<li>{line[2:]}</li>"
    if line.startswith("|"): return line # Handle table separately
    
    return f"<p>{line}</p>"

files = [
    "01-avatar.md", "02-brand-voice.md", "03-hero-mechanism.md", "04-money-model.md",
    "05-offer.md", "06-hvco-leadmagnet.md", "07-funnel-blueprint.md", "08-ads-copy.md",
    "09-vsl-script.md", "10-email-sequence.md", "11-follow-up.md", "12-sales-script.md",
    "13-roadmap-asks.md"
]

for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        html_body = []
        in_list = False
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list: html_body.append("</ul>"); in_list = False
                if in_table: html_body.append("</table>"); in_table = False
                continue
            
            if line.startswith("- "):
                if not in_list: html_body.append("<ul>"); in_list = True
                html_body.append(convert_md_line(line))
            elif line.startswith("|"):
                if not in_table: html_body.append("<table>"); in_table = True
                if "---" in line: continue
                cells = [c.strip() for c in line.split("|") if c.strip()]
                row = "".join([f"<td>{c}</td>" for c in cells])
                html_body.append(f"<tr>{row}</tr>")
            else:
                if in_list: html_body.append("</ul>"); in_list = False
                if in_table: html_body.append("</table>"); in_table = False
                html_body.append(convert_md_line(line))
                
        if in_list: html_body.append("</ul>")
        if in_table: html_body.append("</table>")
        
        final_content = "\n".join(html_body)
        # Using simple replace for template
        final_html = template.replace("{title}", f.replace(".md", "")).replace("{content}", final_content)
        
        with open(path.replace(".md", ".html"), 'w', encoding='utf-8') as out:
            out.write(final_html)
        print(f"Done: {f}")
