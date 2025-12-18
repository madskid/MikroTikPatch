#!/usr/bin/python3
import sys
import os
import subprocess
from urllib.parse import parse_qs

# Konfigurasi
CUSTOM_KEY = "9DBC845E9018537810FDAE62824322EEE1B12BAD81FCA28EC295FB397C61CE0B"

# Header wajib
print("Content-Type: text/html\n")

# Logic ambil data POST
swid = ""
mode = "licgenros"
try:
    content_length = int(os.environ.get('CONTENT_LENGTH', 0))
    if content_length > 0:
        post_data = sys.stdin.read(content_length)
        fields = parse_qs(post_data)
        swid = fields.get('swid', [''])[0].strip()
        mode = fields.get('mode', ['licgenros'])[0]
except Exception:
    pass

license_output = ""
if swid:
    try:
        process = subprocess.run(
            ['python3', 'license.py', mode, swid, CUSTOM_KEY],
            capture_output=True,
            text=True,
            timeout=10
        )
        license_output = process.stdout.strip() if process.stdout else process.stderr.strip()
    except Exception as e:
        license_output = f"Error: {str(e)}"

# Template HTML dengan Perbaikan UI
print(f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MikroTik License Generator</title>
    <style>
        :root {{
            --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --dim: #94a3b8;
            --accent: #3b82f6; --input: #334155; --success: #22c55e;
        }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
        .card {{ background: var(--card); padding: 30px; border-radius: 16px; width: 100%; max-width: 480px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        
        header {{ text-align: center; margin-bottom: 25px; }}
        h2 {{ margin: 0; font-size: 24px; color: var(--text); }}
        .desc {{ font-size: 12px; color: var(--dim); margin-top: 8px; line-height: 1.5; }}
        .desc a {{ color: var(--accent); text-decoration: none; }}

        label {{ display: block; margin-bottom: 8px; font-size: 14px; color: var(--dim); font-weight: 600; }}
        select, input {{ width: 100%; padding: 12px; margin-bottom: 20px; background: var(--input); border: 1px solid #475569; border-radius: 8px; color: white; box-sizing: border-box; font-size: 16px; outline: none; }}
        select:focus, input:focus {{ border-color: var(--accent); }}

        .btn-gen {{ width: 100%; padding: 14px; background: var(--accent); color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 16px; transition: 0.2s; }}
        .btn-gen:hover {{ background: #2563eb; }}

        /* PERBAIKAN TAMPILAN COPY */
        .result-container {{ margin-top: 25px; }}
        .result-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 10px; 
        }}
        .result-label {{ font-size: 14px; color: var(--dim); font-weight: 600; }}
        
        .btn-copy {{ 
            background: #475569; 
            color: white; 
            border: none; 
            padding: 6px 12px; 
            border-radius: 6px; 
            font-size: 12px; 
            cursor: pointer; 
            font-weight: 600;
            transition: 0.2s;
        }}
        .btn-copy:hover {{ background: #64748b; }}
        .btn-copy:active {{ transform: scale(0.95); }}

        .result {{ 
            background: #000; 
            color: var(--success); 
            padding: 15px; 
            border-radius: 8px; 
            font-family: 'Fira Code', 'Consolas', monospace; 
            font-size: 13px; 
            white-space: pre-wrap; 
            border: 1px solid #334155; 
            line-height: 1.6;
            word-break: break-all;
        }}
        
        #toast {{
            position: fixed; bottom: 20px; background: var(--success); color: white;
            padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600;
            display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="card">
        <header>
            <h2>License Generator</h2>
            <div class="desc">
                This generator only works from the source<br>
                <a href="https://github.com/madskid/MikrotikPatch" target="_blank">https://github.com/madskid/MikrotikPatch</a>
            </div>
        </header>
        
        <form method="post">
            <label>License Type</label>
            <select name="mode">
                <option value="licgenros" {"selected" if mode == "licgenros" else ""}>RouterOS (x86)</option>
                <option value="licgenchr" {"selected" if mode == "licgenchr" else ""}>Cloud Hosted Router (CHR)</option>
            </select>

            <label>Software ID</label>
            <input type="text" name="swid" value="{swid}" placeholder="Contoh: CJYL-85QJ atau pjLQ21gHzfI" required>
            
            <button type="submit" class="btn-gen">Generate License</button>
        </form>

        {f'''
        <div class="result-container">
            <div class="result-header">
                <span class="result-label">Result ({mode}):</span>
                <button class="btn-copy" onclick="copyText()">Copy Key</button>
            </div>
            <div id="lt" class="result">{license_output}</div>
        </div>
        ''' if license_output else ""}
    </div>

    <div id="toast">Key copied to clipboard!</div>

    <script>
    function copyText() {{
        const text = document.getElementById("lt").innerText;
        const toast = document.getElementById("toast");
        
        // Fungsi salin yang bekerja di HTTP/HTTPS
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {{
            document.execCommand('copy');
            // Tampilkan Toast
            toast.style.display = "block";
            setTimeout(() => {{ toast.style.display = "none"; }}, 2500);
        }} catch (err) {{
            alert("Gagal menyalin!");
        }}
        document.body.removeChild(textArea);
    }}
    </script>
</body>
</html>
""")
