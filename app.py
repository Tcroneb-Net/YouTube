from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/get-url')
def get_url():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing URL'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'mp4[height<=360]',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            selected = next((f for f in formats if f.get('ext') == 'mp4' and f.get('height') == 360), None)

            if not selected:
                return jsonify({'error': 'No suitable format found'}), 404

            return jsonify({
                'title': info.get('title'),
                'directUrl': selected['url']
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return 'yt-dlp backend is running.'
