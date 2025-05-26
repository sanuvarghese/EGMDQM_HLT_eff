import os

# Target directory (change as needed)
# directory = "/eos/user/s/savarghe/www/EGMDQM/2025/plots_step_eff_single"
# web_base = "https://savarghe.web.cern.ch/EGMDQM/2025/plots_step_eff_single"
directory = "/eos/user/s/savarghe/www/EGMDQM/2025/plots_filter_eff"
web_base = "https://savarghe.web.cern.ch/EGMDQM/2025/plots_filter_eff"
image_extensions = [".png", ".jpg", ".jpeg"]

# Collect image files
image_files = sorted([f for f in os.listdir(directory) if os.path.splitext(f)[1] in image_extensions])

# HTML content
html = """<!DOCTYPE html>
<html>
<head>
  <title>Step Filter Efficiencies</title>
  <style>
    body { font-family: Arial, sans-serif; }
    .image-row { display: flex; flex-wrap: wrap; }
    .image-box {
      width: 30%;
      margin: 1%;
      text-align: center;
    }
    img {
      width: 100%;
      height: auto;
      border: 1px solid #ccc;
    }
    a {
      text-decoration: none;
      color: #004080;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <h1>Step-by-Step Filter Efficiencies</h1>
<p>
  <a href="../" style="
    display: inline-block;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: bold;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 6px;
    text-decoration: none;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
  "> Back to Parent Directory
  </a>
</p>
"""

html += """  <div class="image-row">\n"""

for img in image_files:
    img_path = f"{web_base}/{img}"
    html += f"""    <div class="image-box">
      <a href="{img_path}" target="_blank">{img}</a><br>
      <a href="{img_path}" target="_blank"><img src="{img}" alt="{img}"></a>
    </div>\n"""

html += """  </div>
</body>
</html>
"""

# Save the HTML
with open(os.path.join(directory, "index.html"), "w") as f:
    f.write(html)

print(f"index.html created with {len(image_files)} images in grid layout.")

