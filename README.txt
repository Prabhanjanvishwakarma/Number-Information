PRABHANJAN EXPLOITS — Animated Localhost Dashboard + Cloudflare Quick Tunnel

Run:
  pip install -r requirements.txt
  python app.py

Open local dashboard:
  http://127.0.0.1:5000

For a public URL:
  1. Install cloudflared from Cloudflare's official documentation.
  2. Ensure `cloudflared` is available in your terminal/PATH.
  3. Run `python app.py`.
  4. Look in the terminal for `PUBLIC URL: https://....trycloudflare.com`.

The tunnel is temporary and only stays available while this process runs.
Do not share the Python file publicly because it contains an API key.
Public tunnels can expose the app to anyone with the URL; use only for authorized data access.
