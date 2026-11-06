# Install in Codex

1. Extract the ZIP.
2. Copy the entire `tiktok-storyboard-analyzer` folder into the target Codex skills directory:
   - Windows: `%USERPROFILE%\.codex\skills\`
   - macOS/Linux: `~/.codex/skills/`
3. Restart Codex or start a new task so the skill catalog is refreshed.
4. Invoke it with: `Use $tiktok-storyboard-analyzer neste video: <URL>`.

For evidence generation, the machine should have Python 3, `ffmpeg`, and `ffprobe` available on `PATH`. The first analysis can install Python dependencies locally:

```powershell
python scripts/analyze_tiktok.py "<URL>" --out .\work\run --install-deps
```

The skill prefers background/local analysis and does not need to open Chrome. TikTok access can vary by region and time; the included fallback downloader provides a second route when `yt-dlp` fails.
