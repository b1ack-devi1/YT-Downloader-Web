from flask import Flask, render_template, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

def list_formats(url):
    ydl_opts = {
        'quiet': True,
        'forcejson': True,
        'simulate': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info.get('formats', []):
            size = f.get('filesize') or f.get('filesize_approx')
            size_mb = f"{round(size / 1024 / 1024, 2)}" if size else "-"
            bitrate = f"{round(f.get('tbr', 0))}kbps" if f.get('tbr') else "-"
            formats.append({
                'id': f['format_id'],
                'ext': f['ext'],
                'resolution': f.get('resolution', 'audio'),
                'size': size_mb,
                'bitrate': bitrate,
                'note': f.get('format_note', ''),
                'url': f.get('url')  # Direct YouTube URL for browser download
            })
    return info['title'], formats

@app.route("/", methods=["GET", "POST"])
def index():
    title = None
    formats = []
    url = ""
    if request.method == "POST":
        url = request.form["url"].strip()
        title, formats = list_formats(url)
    return render_template("index.html", url=url, title=title, formats=formats)

@app.route("/direct-url", methods=["POST"])
def get_direct_url():
    url = request.form["url"]
    format_id = request.form["format_id"]

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': format_id,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({"direct_url": info["url"]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
