import os
import re
import secrets
import requests
from flask import Flask, request, redirect, url_for, session, render_template_string, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Configure these in Render -> Environment. Do not commit real secrets to GitHub.
API_URL = os.environ.get("API_URL", "https://api.naxupdate.workers.dev/api/number-info")
API_KEY = os.environ.get("API_KEY", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "20"))

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
    PERMANENT_SESSION_LIFETIME=1800,
)

BASE_STYLE = """
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#080b13;color:#eef3ff;font:15px system-ui,Segoe UI,sans-serif;display:grid;place-items:center;padding:20px}
.card{width:min(100%,620px);background:#111827;border:1px solid #29364b;border-radius:20px;padding:28px;box-shadow:0 20px 70px #0008}
h1{margin:0 0 6px;color:#ff6682;font-size:clamp(22px,5vw,32px)}.muted{color:#9ba9bd}.tag{color:#55eadb;font-size:11px;letter-spacing:2px;margin-bottom:12px}
label{display:block;margin:18px 0 8px;color:#cbd5e1;font-weight:700}input{width:100%;padding:14px;border:1px solid #3b4b63;border-radius:10px;background:#080d16;color:white;font:inherit}
button{margin-top:16px;padding:13px 18px;border:0;border-radius:10px;background:linear-gradient(120deg,#ff4265,#c20e38);color:white;font-weight:800;cursor:pointer;width:100%}
.msg{padding:12px;border-radius:10px;background:#2a1821;border:1px solid #854057;margin:14px 0}.result{margin-top:18px;padding:16px;border:1px solid #2c665f;background:#0d2426;border-radius:12px}.result strong{color:#55eadb}
a{color:#55eadb}.foot{margin-top:20px;font-size:12px;color:#77869d;text-align:center}
</style>
"""

LOGIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Prabhanjan Exploits | Login</title>""" + BASE_STYLE + """</head><body><main class="card"><div class="tag">PRIVATE ADMIN CONSOLE</div><h1>PRABHANJAN EXPLOITS</h1><p class="muted">Sign in to access the authorized lookup dashboard.</p>{% with messages=get_flashed_messages() %}{% for m in messages %}<div class="msg">{{m}}</div>{% endfor %}{% endwith %}<form method="post"><label for="password">Admin password</label><input id="password" name="password" type="password" required autocomplete="current-password"><button type="submit">SIGN IN</button></form><div class="foot">Private access only · Session expires after 30 minutes</div></main></body></html>"""

DASHBOARD_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Prabhanjan Exploits | Dashboard</title>""" + BASE_STYLE + """</head><body><main class="card"><div class="tag">AUTHORIZED QUERY INTERFACE</div><h1>PRABHANJAN EXPLOITS</h1><p class="muted">Lookup dashboard. This page displays only the query status and record count; it does not expose returned personal records.</p><p><a href="{{url_for('logout')}}">Log out</a></p>{% with messages=get_flashed_messages() %}{% for m in messages %}<div class="msg">{{m}}</div>{% endfor %}{% endwith %}<form method="post" action="{{url_for('lookup')}}"><label for="number">10-digit number</label><input id="number" name="number" inputmode="numeric" pattern="[0-9]{10}" maxlength="10" placeholder="Enter 10-digit number" required><button type="submit">RUN LOOKUP</button></form>{% if result %}<div class="result"><p><strong>Request completed</strong></p><p>Query: {{result.query}}</p><p>Records found: {{'Yes' if result.found else 'No'}}</p><p>Record count: {{result.count}}</p></div>{% endif %}<div class="foot">PRABHANJAN EXPLOITS · Render Web Service</div></main></body></html>"""

@app.get("/")
def home():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template_string(DASHBOARD_PAGE, result=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    if not ADMIN_PASSWORD:
        return "Server setup incomplete: set ADMIN_PASSWORD in Render Environment.", 503
    if request.method == "POST":
        supplied = request.form.get("password", "")
        if secrets.compare_digest(supplied, ADMIN_PASSWORD):
            session.clear()
            session.permanent = True
            session["authenticated"] = True
            return redirect(url_for("home"))
        flash("Incorrect password.")
    return render_template_string(LOGIN_PAGE)

@app.post("/lookup")
def lookup():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    number = (request.form.get("number") or "").strip()
    if not re.fullmatch(r"[0-9]{10}", number):
        flash("Enter exactly 10 digits.")
        return redirect(url_for("home"))
    if not API_KEY:
        flash("API_KEY is not configured in Render Environment.")
        return redirect(url_for("home"))
    try:
        response = requests.get(
            API_URL,
            params={"key": API_KEY, "number": number},
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", payload) if isinstance(payload, dict) else {}
        if not isinstance(data, dict):
            raise ValueError("Unexpected API response format")
        found = bool(data.get("found", False))
        try:
            count = int(data.get("count", 0) or 0)
        except (TypeError, ValueError):
            count = 0
        result = {"query": number, "found": found, "count": count}
        return render_template_string(DASHBOARD_PAGE, result=result)
    except requests.Timeout:
        flash("API request timed out. Try again later.")
    except requests.RequestException:
        flash("Could not reach the API. Check API URL and network settings.")
    except (ValueError, TypeError):
        flash("The API returned an unsupported response.")
    return redirect(url_for("home"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    print(f"Starting Prabhanjan Exploits on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
