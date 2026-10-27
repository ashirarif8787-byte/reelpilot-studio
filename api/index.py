import os
import sys
import traceback

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

os.environ["VERCEL"] = "1"

try:
    from web_app import app
except Exception as e:
    err_tb = traceback.format_exc()
    from flask import Flask, Response
    app = Flask(__name__)
    
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return Response(
            f"<div style='background:#181818;color:#ff5555;padding:24px;font-family:monospace;border-radius:8px;'>"
            f"<h2>Flask Startup Error on Vercel:</h2><pre>{err_tb}</pre></div>",
            mimetype="text/html",
            status=500
        )
