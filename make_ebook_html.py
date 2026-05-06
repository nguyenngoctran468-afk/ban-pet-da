import markdown
import sys
import re

with open("AI_Affiliate_Blueprint.md", "r", encoding="utf-8") as f:
    md_content = f.read()

# remove the first title and TOC if any
md_content = re.sub(r'^# Ebook: AI Affiliate Blueprint.*?\n', '', md_content, flags=re.DOTALL|re.MULTILINE)

# Generate HTML
html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Fix anchor links for TOC
toc_items = [
    ("DISCLAIMER", "#disclaimer", "02"),
    ("LỜI MỞ ĐẦU", "#loi-mo-dau", "03"),
    ("Phần 1: Hiểu Cuộc Chơi Trước Khi Đốt Tiền", "#phan-1-hieu-cuoc-choi-truoc-khi-dot-tien", "04"),
    ("Phần 2: Chuẩn Bị Vũ Khí Để Tàng Hình", "#phan-2-chuan-bi-vu-khi-de-tang-hinh", "05"),
    ("Phần 3: Vượt Ải Account Verification 2026", "#phan-3-vuot-ai-account-verification-2026", "06"),
    ("Phần 4: Build Nhà Máy Content Bằng AI", "#phan-4-build-nha-may-content-bang-ai", "07"),
    ("Phần 5: Hai Công Thức Content Chắc Chắn Ra Đơn", "#phan-5-hai-cong-thuc-content-chac-chan-ra-don", "09"),
    ("Phần 6: Launch, Rút Tiền Và Checklist", "#phan-6-launch-rut-tien-va-checklist", "10"),
    ("FAQ: Những Câu Hỏi Thường Gặp", "#faq-nhung-cau-hoi-thuong-gap", "12"),
    ("Resource List", "#resource-list", "14"),
    ("Về Tác Giả", "#ve-tac-gia", "15")
]

# We need to manually add ids to h2 tags so the TOC links work with proper encoding
html_body = html_body.replace('<h2>DISCLAIMER</h2>', '<h2 id="disclaimer">DISCLAIMER</h2>')
html_body = html_body.replace('<h2>LỜI MỞ ĐẦU</h2>', '<h2 id="loi-mo-dau">LỜI MỞ ĐẦU</h2>')
html_body = html_body.replace('<h2>Phần 1: Hiểu Cuộc Chơi Trước Khi Đốt Tiền</h2>', '<h2 id="phan-1-hieu-cuoc-choi-truoc-khi-dot-tien">Phần 1: Hiểu Cuộc Chơi Trước Khi Đốt Tiền</h2>')
html_body = html_body.replace('<h2>Phần 2: Chuẩn Bị Vũ Khí Để Tàng Hình</h2>', '<h2 id="phan-2-chuan-bi-vu-khi-de-tang-hinh">Phần 2: Chuẩn Bị Vũ Khí Để Tàng Hình</h2>')
html_body = html_body.replace('<h2>Phần 3: Vượt Ải Account Verification 2026</h2>', '<h2 id="phan-3-vuot-ai-account-verification-2026">Phần 3: Vượt Ải Account Verification 2026</h2>')
html_body = html_body.replace('<h2>Phần 4: Build Nhà Máy Content Bằng AI</h2>', '<h2 id="phan-4-build-nha-may-content-bang-ai">Phần 4: Build Nhà Máy Content Bằng AI</h2>')
html_body = html_body.replace('<h2>Phần 5: Hai Công Thức Content Chắc Chắn Ra Đơn</h2>', '<h2 id="phan-5-hai-cong-thuc-content-chac-chan-ra-don">Phần 5: Hai Công Thức Content Chắc Chắn Ra Đơn</h2>')
html_body = html_body.replace('<h2>Phần 6: Launch, Rút Tiền Và Checklist</h2>', '<h2 id="phan-6-launch-rut-tien-va-checklist">Phần 6: Launch, Rút Tiền Và Checklist</h2>')
html_body = html_body.replace('<h2>FAQ: Những Câu Hỏi Thường Gặp</h2>', '<h2 id="faq-nhung-cau-hoi-thuong-gap">FAQ: Những Câu Hỏi Thường Gặp</h2>')
html_body = html_body.replace('<h2>Resource List</h2>', '<h2 id="resource-list">Resource List</h2>')
html_body = html_body.replace('<h2>Về Tác Giả</h2>', '<h2 id="ve-tac-gia">Về Tác Giả</h2>')

toc_html = ""
for title, anchor, page in toc_items:
    toc_html += f"""
        <div class="toc-item">
            <a href="{anchor}" class="toc-link">
                <span class="toc-title">{title}</span>
                <span class="toc-dots"></span>
                <span class="toc-page">{page}</span>
            </a>
        </div>
    """

# Custom HTML Template
html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Affiliate Blueprint</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #FAF7F2; /* Cream Light Mode */
            --text-color: #1A1A1A; /* Black text */
            --accent-color: #8B5CF6; /* Purple */
            --accent-secondary: #06b6d4; /* Cyan */
            --heading-color: #1A1A1A;
            --card-bg: #FFFFFF;
            --border-color: #E2E8F0;
        }}

        @page {{
            size: A4;
            margin: 25mm;
            @bottom-center {{
                content: "AI Affiliate Blueprint - Trang " counter(page);
                font-family: 'Inter', sans-serif;
                font-size: 10pt;
                color: #64748b;
            }}
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.8;
            font-size: 13pt;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        /* Print Specific Styles */
        @media print {{
            body {{
                background-color: var(--bg-color) !important;
            }}
            .cover-page {{
                min-height: calc(100vh - 40mm);
                box-sizing: border-box;
                display: flex !important;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                page-break-after: always;
                margin-bottom: 0 !important;
            }}
            h2 {{
                page-break-before: always;
            }}
            table {{
                page-break-inside: avoid;
            }}
            a {{
                text-decoration: none;
                color: var(--accent-color);
            }}
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Playfair Display', serif;
            color: var(--heading-color);
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}

        h2 {{
            font-size: 24pt;
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 10px;
            color: var(--accent-color);
        }}

        h3 {{
            font-size: 16pt;
            color: #334155;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }}

        p {{
            margin-bottom: 1.2em;
        }}

        /* Cover Page */
        .cover-page {{
            text-align: center;
            padding: 40px 20px;
            box-sizing: border-box;
            background-color: #FFFFFF;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
            min-height: calc(100vh - 40mm);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        /* Gradient circle visual */
        .cover-visual {{
            position: absolute;
            top: -100px;
            right: -100px;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%);
            z-index: 0;
        }}
        .cover-visual-2 {{
            position: absolute;
            bottom: -50px;
            left: -50px;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            z-index: 0;
        }}

        .cover-content {{
            position: relative;
            z-index: 1;
        }}

        .cover-badge {{
            display: inline-block;
            background-color: var(--accent-color);
            color: white;
            font-size: 10pt;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 20px;
            margin-bottom: 20px;
            letter-spacing: 1px;
        }}

        .cover-title {{
            font-size: 36pt; /* Reduced from 48pt */
            font-weight: 700;
            color: var(--accent-color);
            margin-bottom: 10px;
            line-height: 1.2;
        }}
        .cover-subtitle {{
            font-family: 'Inter', sans-serif;
            font-size: 16pt;
            color: #475569;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .cover-tagline {{
            font-family: 'Inter', sans-serif;
            font-size: 13pt;
            color: #64748b;
            margin-bottom: 50px;
            font-style: italic;
        }}
        .cover-author {{
            font-size: 14pt;
            color: #334155;
            font-weight: 600;
        }}
        .cover-website {{
            font-size: 11pt;
            color: #64748b;
            margin-top: 10px;
        }}

        /* Table of Contents */
        .toc {{
            background-color: var(--card-bg);
            padding: 40px;
            border-radius: 8px;
            margin-bottom: 40px;
            page-break-after: always;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .toc h2 {{
            margin-top: 0;
            font-size: 24pt;
            color: var(--accent-color);
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 15px;
            page-break-before: avoid; /* TOC shouldn't page break if it's the first thing */
        }}
        
        .toc-item {{
            margin-bottom: 12px;
            font-size: 12pt;
        }}
        .toc-link {{
            display: flex;
            align-items: baseline;
            color: var(--text-color);
            text-decoration: none;
            transition: color 0.2s;
        }}
        .toc-link:hover {{
            color: var(--accent-color);
        }}
        .toc-title {{
            font-weight: 500;
        }}
        .toc-dots {{
            flex-grow: 1;
            border-bottom: 2px dotted #cbd5e1;
            margin: 0 10px;
            position: relative;
            top: -4px;
        }}
        .toc-page {{
            font-weight: 600;
            color: var(--accent-color);
        }}

        /* Content Styling */
        .content-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 11pt;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            page-break-inside: avoid;
        }}
        th, td {{
            padding: 14px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background-color: #F8FAFC;
            color: #334155;
            font-weight: 600;
        }}

        /* Code blocks / Prompts */
        pre {{
            background-color: #F1F5F9;
            color: #334155;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--accent-color);
            overflow-x: auto;
            font-family: monospace;
            font-size: 10.5pt;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        code {{
            background-color: #F1F5F9;
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--accent-color);
            font-size: 0.9em;
            font-weight: 600;
        }}

        /* Blockquotes / Key Takeaways */
        blockquote {{
            margin: 30px 0;
            padding: 25px;
            background-color: #F3E8FF; /* Light purple bg */
            border: 1px solid #D8B4FE;
            border-left: 6px solid var(--accent-color);
            border-radius: 8px;
            color: #4C1D95; /* Dark purple text */
            font-weight: 500;
            page-break-inside: avoid;
        }}
        blockquote p {{
            margin-bottom: 10px;
        }}
        blockquote p:last-child {{
            margin-bottom: 0;
        }}
        
        ul, ol {{
            padding-left: 25px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 8px;
            line-height: 1.6;
        }}

        /* Checklist boxes */
        li:contains("[ ]"), li:contains("[x]") {{
            list-style-type: none;
        }}
        
        hr {{
            border: 0;
            height: 1px;
            background: var(--border-color);
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <div class="content-container">
        <!-- Cover Page -->
        <div class="cover-page">
            <div class="cover-visual"></div>
            <div class="cover-visual-2"></div>
            <div class="cover-content">
                <div class="cover-badge">2026 EDITION</div>
                <h1 class="cover-title">AI Affiliate Blueprint</h1>
                <div class="cover-subtitle">Kiếm USD từ TikTok US Bằng AI (No-Face, No-English)</div>
                <div class="cover-tagline">Lộ trình 14 ngày từ Zero đến đơn đầu tiên</div>
                <div style="margin-top: 80px;">
                    <div class="cover-author">Tác giả: Tran Thu Nhat</div>
                    <div class="cover-website">Website: phaodr.com</div>
                    <div class="cover-website">© Copyright 2026</div>
                </div>
            </div>
        </div>

        <!-- Table of Contents -->
        <div class="toc">
            <h2 style="page-break-before: avoid;">Mục Lục</h2>
            {toc_html}
        </div>

        <!-- Main Content -->
        {html_body}
        
    </div>
    
    <script>
        // Clean up checklist styling visually
        document.querySelectorAll('li').forEach(li => {{
            if (li.textContent.includes('[ ]')) {{
                li.innerHTML = li.innerHTML.replace('[ ]', '⬜ ');
                li.style.listStyleType = 'none';
            }}
            if (li.textContent.includes('[-]')) {{
                li.innerHTML = li.innerHTML.replace('[-]', '✅ ');
                li.style.listStyleType = 'none';
            }}
        }});
    </script>
</body>
</html>
"""

with open("ai_affiliate_blueprint.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Ebook HTML generated successfully: ai_affiliate_blueprint.html")
