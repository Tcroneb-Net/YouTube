from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import yt_dlp

app = FastAPI()

@app.get("/")
async def proxy_download(url: str, country: str = "US"):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
        'geo_bypass': True,
        'geo_bypass_country': country.upper(),  # Example: "ID", "IN", "US"
        # Optionally add proxy: 'geo_verification_proxy': 'socks5://proxy_host:port',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info['url']
            return RedirectResponse(direct_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract video: {str(e)}")
