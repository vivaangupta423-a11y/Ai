from flask import Flask, request, render_template_string, redirect, url_for
import urllib.parse
import logging
import os
from waitress import serve

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MAX_QUERY_LENGTH = 200

HTML = """
<!doctype html>
<title>Pin_Me</title>
<h1>Pin_Me</h1>
{% if error %}
    <p style="color:crimson;">{{ error }}</p>
{% endif %}
<form action="{{ url_for('pin') }}" method="get" autocomplete="off">
    <input type="text" name="q" placeholder="Pin..." value="{{ request.args.get('q', '')|e }}">
    <input type="submit" value="Pin">
</form>
"""

@app.after_request
def set_security_headers(response):
    # Basic security headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
    # Content Security Policy: allow self, disallow framing, allow form-action to Google for redirect intent
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'; form-action 'self' https://www.google.com")
    # HSTS only if running under HTTPS (Flask dev server is HTTP so skip unconditionally here)
    return response

@app.route("/")
def home():
    # show an error message when redirected back with ?error=...
    error = request.args.get("error")
    return render_template_string(HTML, error=error)

@app.route("/pin")
def pin():
    query = (request.args.get("q") or "").strip()
    if not query:
        return redirect(url_for("home", error="Please enter a search term."))
    if len(query) > MAX_QUERY_LENGTH:
        return redirect(url_for("home", error=f"Query must be at most {MAX_QUERY_LENGTH} characters."))
    # Encode safely for inclusion in a URL
    safe_q = urllib.parse.quote_plus(query)
    logging.info("Redirecting search query: %s", query)
    return redirect(f"https://www.google.com/search?q={safe_q}")

if __name__ == "__main__":
    # For production use Waitress WSGI server; PORT can be set via environment.
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)