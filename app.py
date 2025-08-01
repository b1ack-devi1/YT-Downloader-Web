from flask import Flask, render_template, request, send_file
import os
from yt_dlp import YoutubeDL
import tempfile

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
                'note': f.get('format_note', '')
            })
    return info['title'], formats

def download_format(url, format_id):
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        for file in os.listdir(temp_dir):
            return os.path.join(temp_dir, file)  # Return the first file path

@app.route("/", methods=["GET", "POST"])
def index():
    title = None
    formats = []
    url = ""
    if request.method == "POST":
        url = request.form["url"].strip()
        title, formats = list_formats(url)
    return render_template("index.html", url=url, title=title, formats=formats)

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    format_id = request.form["format_id"]
    file_path = download_format(url, format_id)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False)
