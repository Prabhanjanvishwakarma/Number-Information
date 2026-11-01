import html
import re
import shutil
import subprocess
import threading
import time
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# API configuration from your original script
API_URL = "https://api.naxupdate.workers.dev/api/number-info"
API_KEY = "30Day"
API_PARAM = "number"
API_HEADERS = {}
TIMEOUT = 30
PORT = 8000

# This dashboard is for authorized lookups only. It hides highly sensitive fields.
FIELDS = [
    ("name", "Name"),
    ("father_name", "Father"),
    ("mobile", "Mobile"),
    ("alt_mobile", "Alt Mobile"),
    ("aadhaar", "Aadhaar"),
    ("circle", "Circle"),
    ("email", "Email"),
    ("address", "Address"),
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#080a10">
<title>Prabhanjan Exploits | Intelligence Console</title>
<style>
:root{color-scheme:dark;--bg:#070910;--panel:rgba(14,19,31,.86);--line:#273349;--red:#ff3157;--cyan:#52f6e8;--text:#edf4ff;--muted:#8c9bb1}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;background:var(--bg);color:var(--text);font:15px/1.55 Inter,ui-sans-serif,system-ui,Segoe UI,sans-serif;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(#263b5b22 1px,transparent 1px),linear-gradient(90deg,#263b5b22 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(to bottom,#000,transparent 88%);z-index:-2}
.glow{position:fixed;width:480px;height:480px;border-radius:50%;filter:blur(100px);opacity:.15;pointer-events:none;z-index:-1;animation:float 12s ease-in-out infinite alternate}
.g1{background:#ff174e;top:-180px;left:-150px}.g2{background:#00d7cb;right:-180px;top:35%;animation-delay:-5s}
@keyframes float{to{transform:translate(65px,70px) scale(1.2)}}
@keyframes reveal{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{50%{box-shadow:0 0 0 7px #ff31571b,0 0 28px #ff315766}}
@keyframes scan{from{transform:translateY(-100%)}to{transform:translateY(700%)}}
.wrap{max-width:1050px;margin:auto;padding:34px 18px 20px}.top{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:30px;animation:reveal .7s ease both}
.brand{display:flex;align-items:center;gap:15px}.emblem{height:62px;width:62px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#28101b,#101827);border:1px solid #8b2b46;box-shadow:0 0 30px #ff31571b;color:#ff5575;font-weight:1000;font-size:23px;position:relative;overflow:hidden}
.emblem:after{content:"";position:absolute;inset:-60% 0;background:linear-gradient(transparent,#ffffff22,transparent);transform:rotate(30deg);animation:scan 4s linear infinite}
h1{font-size:clamp(23px,4vw,38px);letter-spacing:.04em;line-height:1.12;margin:0;font-weight:950;background:linear-gradient(90deg,#fff,#ff6682 55%,#ff3157);color:transparent;background-clip:text}
.tagline{color:var(--muted);font-size:12px;letter-spacing:.17em;text-transform:uppercase;margin-top:8px}
.status{border:1px solid #1c655e;background:#0b2526;color:var(--cyan);padding:8px 12px;border-radius:999px;font-size:11px;letter-spacing:.12em;white-space:nowrap}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--cyan);margin-right:8px;box-shadow:0 0 12px var(--cyan);animation:blink 1.5s infinite}
@keyframes blink{50%{opacity:.3}}
.hero{border:1px solid var(--line);border-radius:22px;background:linear-gradient(120deg,#151b2aeb,#0d121deb);padding:clamp(20px,4vw,34px);position:relative;overflow:hidden;box-shadow:0 20px 80px #0005;animation:reveal .7s .1s ease both}
.hero:after{content:"";position:absolute;width:3px;top:0;bottom:0;left:0;background:linear-gradient(transparent,var(--red),var(--cyan),transparent);opacity:.9}
.eyebrow{font-size:11px;letter-spacing:.2em;color:var(--cyan);font-weight:800;text-transform:uppercase;margin-bottom:10px}
h2{font-size:20px;margin:0 0 8px}.desc{color:var(--muted);margin:0 0 23px;max-width:650px}
label{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#c5d0e1;font-weight:800;margin-bottom:9px}
.formrow{display:flex;gap:12px}.inputwrap{flex:1;min-width:0;position:relative}
input{width:100%;padding:15px 16px;background:#080d16;border:1px solid #35445b;border-radius:12px;color:white;font:inherit;outline:none;transition:.2s}
input:focus{border-color:var(--cyan);box-shadow:0 0 0 3px #52f6e81a}
button{border:0;border-radius:12px;background:linear-gradient(135deg,#ff4265,#c20e38);padding:0 23px;color:white;font-weight:900;letter-spacing:.03em;font-size:13px;cursor:pointer;box-shadow:0 8px 28px #ff315726;transition:transform .2s,filter .2s;min-height:52px}
button:hover{transform:translateY(-2px);filter:brightness(1.12)}button:disabled{opacity:.65;cursor:wait;transform:none}
.tiny{font-size:12px;color:var(--muted);margin-top:12px}
.alert{margin-top:18px;border:1px solid #853047;background:#2a111b;color:#ffdce4;padding:14px 16px;border-radius:12px;animation:reveal .3s ease both}
.results{margin-top:20px;animation:reveal .55s ease both}
.sectionhead{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 13px}
.sectionhead h2{margin:0}.chip{font-size:10px;letter-spacing:.12em;color:var(--cyan);border:1px solid #23615e;padding:5px 9px;border-radius:7px}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:13px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:16px;backdrop-filter:blur(10px)}
.stat small{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.15em}.stat strong{display:block;font-size:clamp(16px,2.5vw,23px);margin-top:7px;overflow-wrap:anywhere}
.record{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:19px;margin-top:12px;position:relative;overflow:hidden;backdrop-filter:blur(10px);animation:reveal .45s ease both}
.record:before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;background:linear-gradient(var(--red),var(--cyan))}
.record h3{margin:0 0 13px;font-size:12px;letter-spacing:.13em;color:#ff7b94;text-transform:uppercase}
.fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 22px}.field{padding:10px 0;border-top:1px solid #253044;overflow-wrap:anywhere}.field b{display:block;font-size:10px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin-bottom:3px}.field span{font-size:14px}
.empty{border:1px dashed #3b485d;border-radius:14px;text-align:center;padding:26px;color:var(--muted);background:#0b1019}
footer{text-align:center;padding:30px 0 10px;color:#66758d;font-size:11px;letter-spacing:.08em}
@media(max-width:650px){.top{align-items:flex-start;flex-direction:column}.status{align-self:flex-start}.formrow{flex-direction:column}button{padding:14px}.stats{grid-template-columns:1fr}.fields{grid-template-columns:1fr}.wrap{padding-top:22px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;scroll-behavior:auto!important;transition:none!important}}
</style></head>
<body><div class="glow g1"></div><div class="glow g2"></div><main class="wrap">
<header class="top">
<div class="brand"><div class="emblem">PE</div><div><h1>PRABHANJAN EXPLOITS</h1><div class="tagline">Intelligence Console / Local API</div></div></div>
<div class="status"><span class="dot"></span>SYSTEM READY</div>
</header>
<section class="hero">
<div class="eyebrow">◆ Secure Query Interface</div><h2>Number Info Lookup</h2>
<p class="desc">Submit a number to view the API response in a clean, structured console. Use only data and services you are authorized to access.</p>
<form method="post" id="lookupForm">
<label for="number">Target number · 10 digits</label>
<div class="formrow"><div class="inputwrap"><input id="number" name="number" inputmode="numeric" autocomplete="off" maxlength="10" pattern="[0-9]{10}" placeholder="Enter 10-digit number" value="{{ number }}" required></div>
<button id="submitBtn" type="submit">⌕ &nbsp; RUN LOOKUP</button></div>
<div class="tiny">API key stays on the Python backend. Dashboard is designed for localhost use.</div>
</form>
</section>
{% if error %}<div class="alert">⚠ &nbsp; {{ error }}</div>{% endif %}
{% if data %}
<section class="results">
<div class="sectionhead"><h2>Query Results</h2><span class="chip">RESPONSE RECEIVED</span></div>
<div class="stats">
<div class="stat"><small>Query number</small><strong>{{ data.get('number', number) }}</strong></div>
<div class="stat"><small>Records found</small><strong>{{ 'YES' if data.get('found', False) else 'NO' }}</strong></div>
<div class="stat"><small>Total records</small><strong>{{ data.get('count', 0) }}</strong></div>
</div>
{% if not data.get('found', False) %}<div class="empty">No records found for this query.</div>{% endif %}
{% for rec in data.get('result', []) %}
<article class="record" style="animation-delay:{{ loop.index0 * 70 }}ms"><h3>▰ Record {{ loop.index }} / API DATA</h3><div class="fields">
{% for key,label in fields %}{% if rec.get(key) %}<div class="field"><b>{{ label }}</b><span>{{ rec.get(key) }}</span></div>{% endif %}{% endfor %}
</div></article>
{% endfor %}
</section>
{% endif %}
<footer>PRABHANJAN EXPLOITS &nbsp; · &nbsp; LOCAL INTELLIGENCE CONSOLE</footer>
</main>
<script>
document.getElementById('lookupForm').addEventListener('submit',function(){
 const b=document.getElementById('submitBtn');b.disabled=true;b.textContent='CONNECTING…';
});
</script>
</body></html>"""

def start_cloudflare():
    """Start a temporary Cloudflare Quick Tunnel and print its public URL."""
    if not shutil.which("cloudflared"):
        print("[Cloudflare] cloudflared not found. Install it and ensure it is on PATH.")
        print("[Cloudflare] Local site still available at http://127.0.0.1:8000")
        return
    try:
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{PORT}", "--no-autoupdate"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in proc.stdout:
            print("[Cloudflare]", line.rstrip())
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                print("\n" + "=" * 64)
                print("PUBLIC URL:", match.group(0))
                print("=" * 64 + "\n")
    except Exception as exc:
        print(f"[Cloudflare] Could not start tunnel: {exc}")

@app.route("/", methods=["GET", "POST"])
def index():
    number = ""
    data = None
    error = None
    if request.method == "POST":
        number = (request.form.get("number") or "").strip()
        if not re.fullmatch(r"\d{10}", number):
            error = "Invalid input. Please enter exactly 10 digits."
        else:
            try:
                response = requests.get(
                    API_URL,
                    params={"key": API_KEY, API_PARAM: number},
                    headers=API_HEADERS,
                    timeout=TIMEOUT,
                )
                response.raise_for_status()
                payload = response.json()
                data = payload.get("data", payload)
                if not isinstance(data, dict):
                    data = None
                    error = "The API response format was not recognized."
            except requests.exceptions.Timeout:
                error = "API timeout. Please try again later."
            except requests.exceptions.ConnectionError:
                error = "Could not connect to the API."
            except requests.exceptions.HTTPError:
                error = f"API returned HTTP status {response.status_code}."
            except ValueError:
                error = "The API did not return valid JSON."
            except requests.exceptions.RequestException:
                error = "API request failed. Check connection and API configuration."
    return render_template_string(PAGE, number=number, data=data, error=error, fields=FIELDS)

if __name__ == "__main__":
    print("Starting Prabhanjan Exploits local dashboard...")
    print(f"Local URL: http://127.0.0.1:{PORT}")
    threading.Thread(target=start_cloudflare, daemon=True).start()
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
