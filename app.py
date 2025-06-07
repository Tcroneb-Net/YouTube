from flask import Flask, request, jsonify
import yt_dlp
import re

app = Flask(__name__)

# Regex to detect direct downloadable URLs from savetube.su or similar sites
DIRECT_URL_PATTERN = re.compile(r"https?://(?:cdn\d*\.savetube\.su|savetube\.su)/download-direct/video/.*")

@app.route('/get-url')
def get_url():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    # If it's already a direct download URL from savetube.su, just return it directly
    if DIRECT_URL_PATTERN.match(video_url):
        return jsonify({
            'title': 'Direct download link',
            'directUrl': video_url
        })

    # Otherwise, assume it's a YouTube or other video URL and use yt-dlp
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'mp4[height<=360]/best[height<=360]/best',
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            # Try to get 360p mp4, else fallback to best <=360p
            selected = None
            for f in formats:
                if f.get('ext') == 'mp4' and f.get('height') == 360:
                    selected = f
                    break
            if not selected:
                # fallback to best format with height <=360
                for f in sorted(formats, key=lambda x: (x.get('height') or 0), reverse=True):
                    if f.get('height') and f.get('height') <= 360:
                        selected = f
                        break

            if not selected:
                return jsonify({'error': 'No suitable 360p or lower mp4 format found'}), 404

            return jsonify({
                'title': info.get('title'),
                'directUrl': selected['url']
            })

    except yt_dlp.utils.DownloadError as e:
        err_str = str(e)
        if "Video unavailable" in err_str:
            return jsonify({'error': 'Video unavailable, private, removed, or blocked.'}), 404
        return jsonify({'error': err_str}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    return "YouTube & SaveTube Downloader API is running."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
