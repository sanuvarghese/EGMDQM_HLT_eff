import os
import unicodedata
import time

# Base path and URL
base_dir = "/eos/user/s/savarghe/www/EGMDQM"
web_root = "https://savarghe.web.cern.ch/EGMDQM"
image_extensions = [".png", ".jpg", ".jpeg"]

def clean_filename(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()

# Step 1: Create central style.css
css_path = os.path.join(base_dir, "style.css")
if not os.path.exists(css_path):
    with open(css_path, "w") as f:
        f.write("""
body { font-family: Arial, sans-serif; margin: 20px; }
h1 { font-size: 22px; }
.box { margin: 10px 0; padding: 12px; border: 1px solid #ccc; border-radius: 8px; background: #f5f5f5; }
.box a { text-decoration: none; font-weight: bold; font-size: 17px; color: #0066cc; }
.box a:hover { text-decoration: underline; }
.image-box { width: 30%; margin: 1%; float: left; text-align: center; }
.image-box img { width: 100%; border: 1px solid #ccc; }
.filter-box { clear: both; margin-top: 20px; }
.breadcrumb { font-size: 14px; margin-bottom: 10px; }
.meta { font-size: 12px; color: #666; }
""")

# Step 2: Clean non-ASCII names
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

# Step 3: Generate index.html files
for root, dirs, files in os.walk(base_dir):
    rel_path = os.path.relpath(root, base_dir)
    web_base = f"{web_root}/{rel_path}" if rel_path != "." else web_root

    subdirs = sorted(d for d in dirs if not d.startswith("."))
    images = sorted(f for f in files if os.path.splitext(f)[1].lower() in image_extensions)

    # Breadcrumb
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
  <link rel="stylesheet" href="{web_root}/style.css">
  <script>
    function filterImages() {{
      const filter = document.getElementById("filterInput").value.toLowerCase();
      const boxes = document.getElementsByClassName("image-box");
      for (let box of boxes) {{
        const alt = box.querySelector("img").alt.toLowerCase();
        box.style.display = alt.includes(filter) ? "block" : "none";
      }}
    }}
  </script>
</head>
<body>
  <div class="breadcrumb">{breadcrumb}</div>
  <h1>Contents of /{rel_path if rel_path != '.' else ''}</h1>
"""

    # Subdirectories
    if subdirs:
        html += "<h2>Subdirectories</h2>\n"
        for d in subdirs:
            sub_path = os.path.join(root, d)
            mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(sub_path)))
            html += f'<div class="box"><a href="{d}/">{d}/</a><div class="meta">Last modified: {mtime}</div></div>\n'

    # Image listing with filter
    if images:
        html += """<div class="filter-box">
  <label for="filterInput"><strong>Filter:</strong></label>
  <input type="text" id="filterInput" onkeyup="filterImages()" placeholder="e.g. EBplus">
</div>\n"""
        html += "<div style='clear: both'></div><div>\n"
        for img in images:
            img_path = os.path.join(root, img)
            mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(img_path)))
            size_kb = os.path.getsize(img_path) // 1024
            html += f"""<div class="image-box">
  <a href="{img}" target="_blank"><img src="{img}" alt="{img}"></a><br>{img}
  <div class="meta">Size: {size_kb} KB | Modified: {mtime}</div>
</div>\n"""
        html += "</div>"

    html += "</body>\n</html>"

    # Write index.html
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"index.html created in {root}")
