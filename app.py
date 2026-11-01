<div class="tiny">API key stays on the Python backend. Use only with authorized data and a protected deployment.</div>
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
<footer>PRABHANJAN EXPLOITS &nbsp; · &nbsp; WEB INTELLIGENCE CONSOLE</footer>
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
        print("[Cloudflare] Local site still available at http://127.0.0.1:5000")
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
    # Render requires the app to listen on all interfaces and its assigned PORT.
    # Render already provides a public HTTPS URL; a separate Cloudflare tunnel
    # is not required for a Render Web Service.
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
