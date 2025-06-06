import os
import unicodedata
import time
import re

base_dir = "/eos/user/s/savarghe/www/EGMDQM"
web_root = "https://savarghe.web.cern.ch/EGMDQM"
image_extensions = [".png", ".jpg", ".jpeg"]

def clean_filename(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()

# Step 1: Create style.css if missing
style_path = os.path.join(base_dir, "style.css")
if not os.path.exists(style_path):
    with open(style_path, "w") as f:
        f.write("""
body { font-family: Arial, sans-serif; margin: 20px; }
h1 { font-size: 22px; }
.box { margin: 10px 0; padding: 12px; border: 1px solid #ccc; border-radius: 8px; background: #f5f5f5; }
.box a { text-decoration: none; font-weight: bold; font-size: 17px; color: #0066cc; }
.box a:hover { text-decoration: underline; }
.image-box { width: 31%; margin: 0.5% 0.5% 0.5% 0.5%; float: left; text-align: center; }
.image-box img { width: 100%; border: 1px solid #ccc; margin-bottom: 6px; }
.filter-box { clear: both; margin-top: 20px; }
.breadcrumb { font-size: 18px; font-weight: bold; margin-bottom: 16px; line-height: 1.4; }
.breadcrumb a { margin-right: 6px; color: #4B0082; text-decoration: none; font-weight: 700; }
.breadcrumb a:hover { text-decoration: underline; }
""")

# Step 2: Clean filenames
for root, dirs, files in os.walk(base_dir, topdown=True):
    for i, d in enumerate(dirs):
        new_d = clean_filename(d)
        if new_d != d:
            os.rename(os.path.join(root, d), os.path.join(root, new_d))
            dirs[i] = new_d
    for f in files:
        new_f = clean_filename(f)
        if new_f != f:
            os.rename(os.path.join(root, f), os.path.join(root, new_f))

# Step 3: Generate index.html
for root, dirs, files in os.walk(base_dir):
    rel_path = os.path.relpath(root, base_dir)
    web_base = f"{web_root}/{rel_path}" if rel_path != "." else web_root

    subdirs_raw = [d for d in dirs if not d.startswith(".")]
    numeric_dirs = [d for d in subdirs_raw if re.fullmatch(r'\d+', d)]
    non_numeric_dirs = [d for d in subdirs_raw if not re.fullmatch(r'\d+', d)]
    subdirs = sorted(numeric_dirs, key=int, reverse=True) + sorted(non_numeric_dirs)

    images = sorted(f for f in files if os.path.splitext(f)[1].lower() in image_extensions)

    parts = rel_path.split(os.sep) if rel_path != "." else []
    breadcrumb = f'<a href="{web_root}">EGMDQM</a>'
    for i, part in enumerate(parts):
        link = "/".join(parts[:i+1])
        breadcrumb += f' / <a href="{web_root}/{link}">{part}</a>'

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Index of /{rel_path}</title>
  <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <link rel="stylesheet" href="/EGMDQM/style.css">
  <script>
    function getQueryParam(param) {{
      const urlParams = new URLSearchParams(window.location.search);
      return urlParams.get(param);
    }}

    function filterImages() {{
      const raw = document.getElementById("filterInput").value.toLowerCase();
      const terms = raw.split(",").map(x => x.trim()).filter(x => x.length > 0);
      const boxes = document.getElementsByClassName("image-box");

      for (let box of boxes) {{
        const alt = box.querySelector("img").alt.toLowerCase();
        let matched = terms.length === 0;
        for (let t of terms) {{
          if (alt.includes(t)) {{
            matched = true;
            break;
          }}
        }}
        box.style.display = matched ? "block" : "none";
      }}
    }}

    window.onload = function() {{
      const filterValue = getQueryParam("filter");
      if (filterValue) {{
        const input = document.getElementById("filterInput");
        input.value = filterValue;
        filterImages();
      }}
    }}
  </script>
</head>
<body>
  <div class="breadcrumb">{breadcrumb}</div>
"""

    if subdirs:
        html += "<h2>Subdirectories</h2>\n"
        for d in subdirs:
            sub_path = os.path.join(root, d)
            mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(sub_path)))
            html += f'<div class="box"> <a href="{d}/">{d}/</a><div style="font-size: 12px; color: #666;">Last modified: {mtime}</div></div>\n'

    if images:
        html += """<div class="filter-box">
  <label for="filterInput"><strong>Filter:</strong></label>
  <input type="text" id="filterInput" onkeyup="filterImages()" placeholder="e.g. EBplus,EEminus"
         style="font-size: 18px; padding: 6px 10px; width: 300px;">
</div>\n"""
        html += "<div style='clear: both'></div><div>\n"

        for img in images:
            img_path = os.path.join(root, img)
            base_name, ext = os.path.splitext(img)
            pdf_name = base_name + ".pdf"
            root_name = base_name + ".root"
            pdf_path = os.path.join(root, pdf_name)
            root_path = os.path.join(root, root_name)

            has_pdf = os.path.exists(pdf_path)
            has_root = os.path.exists(root_path)

            mtime_raw = os.path.getmtime(img_path)

            html += f"""<div class="image-box">
  <a href="{img}?t={int(mtime_raw)}" target="_blank">
    <img src="{img}?t={int(mtime_raw)}" alt="{img}">
  </a>
  <div style="margin-top: 2px; margin-bottom: 0px; display: flex; justify-content: center; align-items: center; gap: 6px;">
"""

            if has_pdf:
                html += f"""<a href="{pdf_name}" target="_blank" style="
        padding: 3px 6px;
        background-color: #28a745;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;"> PDF</a>"""

            html += f"""<span style="font-size: 12px; font-weight: bold;">{img}</span>"""

            if has_root:
                root_rel_url = (
                    f"https://cernbox.cern.ch/rootjs/eos/user/s/savarghe/www/EGMDQM/{rel_path}/{root_name}"
                    f"?contextRouteName=files-spaces-generic"
                    f"&contextRouteParams.driveAliasAndItem=eos/user/s/savarghe/www/EGMDQM/{rel_path}"
                )
                html += f"""<a href="{root_rel_url}" target="_blank" style="
        padding: 3px 6px;
        background-color: #6c757d;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;"> ROOT Viewer</a>"""

            html += "</div>\n</div>\n"

        html += "</div>"

    html += "</body>\n</html>"

    index_path = os.path.join(root, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    os.utime(index_path, None)
