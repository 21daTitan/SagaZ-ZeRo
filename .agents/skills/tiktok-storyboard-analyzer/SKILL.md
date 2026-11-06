---
name: tiktok-storyboard-analyzer
description: Analyze TikTok/Shorts AI image-to-video references into reusable storyboards. Use when Codex needs to inspect a TikTok/Reels/Shorts URL or downloaded video, count likely image-base scenes rather than edit cuts, describe the video scene by scene, transcribe or summarize dialogue, compare viral mechanics, or adapt a reference format for Britinho/Zazito-style AI story videos.
---

# TikTok Storyboard Analyzer

## Workflow

Use this skill for AI-generated TikTok reference analysis, especially when the user asks "quantas cenas de imagem", "modelar esse video", "descrever cena a cena", "comparar potencial viral", or "adaptar para Britinho/Zazito".

1. Download or locate the video.
   - For Richard's reference-analysis workflow, prefer background terminal tools and local files. Do not open Chrome unless he requests it or a concrete access limitation requires discussing a browser fallback. This is a scoped workflow preference, not a restriction on unrelated tasks.
   - For TikTok URLs, use `yt-dlp` when available.
   - If `yt-dlp` fails, or downloads a video-only stream, run `scripts/fetch_tiktok_fallback.py`. Use its normal `play` stream for a copy with audio, then analyze that local file. Do not stop at the first extraction failure.
   - Prefer saving work files under the current workspace `work/` folder.
   - Do not treat TikTok's web page fetch failure as final; try `yt-dlp`.

2. Generate evidence artifacts.
   - Create a 1-second contact sheet.
   - Create a candidate-boundary contact sheet when possible; detector starts are not confirmed image anchors.
   - Extract audio and transcribe when practical.
   - Capture metadata: duration, dimensions, uploader, title, views, likes, comments, reposts.
   - When the requested deliverable includes a storyboard image or complete reusable report, create a reviewed manifest following `references/manifest-schema.md`, then run `scripts/render_storyboard_report.py`.

3. Validate the video's ontology before interpreting the plot.
   - Identify what the setting, characters, colors, props, transformations, and named entities literally or metaphorically represent.
   - Cross-check visual evidence, spoken dialogue, burned-in captions, title/description, and cause/effect continuity.
   - Do not infer the setting from visual style alone. A red organic environment may represent anatomy rather than hell; a glowing character may represent a substance rather than a chosen hero.
   - If the interpretation remains ambiguous, state the competing interpretations and the evidence for each. Never silently choose one and build the analysis on it.
   - Treat user-provided corrections about what an element represents as ground truth unless the source directly contradicts them.
   - Separate what is visible, what the dialogue/captions claim, and your interpretation. Do not invent medical or causal facts, or infer pregnancy from body shape, swelling, a transformation, or an ambiguous line. Attribute fictional/medical claims to the video instead of presenting them as facts.

4. Reconstruct **likely original image anchors**, distinguishing three levels.
   - **Anchor:** a likely source still/setup used to start an I2V generation. **Shot:** an edited continuous view, which may reuse an anchor. **Motion state/beat:** an event inside I2V, not another numbered anchor.
   - Do not split solely for prop-state changes, actions, transformations, expressions, character movement, payoff moments, punch-ins, pans, zooms, dissolves, or other edits. An I2V clip can create all of these from one still, including major changes.
   - Do not merge solely because the location, characters, narrative purpose, or color palette match. Two shots in the same room can require different source stills when their **initial stable compositions** differ: camera angle/distance, blocking, visible cast, prop arrangement, or focal action. Conversely, an actor entering a continuous shot is not by itself a new anchor.
   - At every apparent cut, compare the last stable frame before it with the first stable frame after it. Merge only when there is positive continuity evidence (continuous motion/camera move, matching spatial geometry and crop, or reuse of the same source setup). The fact that I2V *could theoretically* produce the later state is insufficient. Treat a new stable setup after an abrupt cut as a provisional split, then test whether an editorial crop or continuous animation explains it.
   - Audit every candidate boundary and dialogue-block change, especially pairs easy to over-merge: group shot versus single-character reaction, before/after another character joins, and wide harvesting versus close confrontation in the same room. Record disputed splits individually so the count/range is traceable.
   - Scene detection supplies review candidates only. Never tune a threshold toward a desired count or use the candidate count as the answer. A 1-second sheet can miss continuity and cannot settle ambiguous splits.
   - At disputed boundaries, inspect a local strip before/during/after the change (e.g. -0.6, -0.3, 0, +0.3, +0.6 seconds), expanding or playing the local interval when needed. Record the evidence for merge/split; keep uncertainty when evidence cannot decide.
   - Group recurring/reused setups under stable anchor IDs, listing every occurrence in chronological order. Distinguish unique anchors from shot/occurrence totals; do not claim identical generations merely from similar characters or settings.
   - The exact actual generation count is unknowable from the final video alone. Give a best estimate with confidence and a justified range for disputed splits, identifying which boundaries change the total. When the user supplies a firsthand shot-by-shot correction, reconcile it against the video and update the artifact; do not defend an earlier count by collapsing distinct compositions. Only source assets/project records can establish an exact count.
   - Keep **source reconstruction** separate from a **minimal-production plan**. The fewest images one could use to remake a story is not evidence of how the original was made; provide that plan only when requested.

5. Describe the video and build a reusable storyboard.
   - Give the best-estimate unique-anchor count, confidence, and disputed-split range first, explicitly labeled as source reconstruction.
   - For each anchor, extract and display one representative image near its initial stable setup. Do not choose climax frames or make a separate representative for every movement. Label the actual timestamp; if the source still is not visible, call it a proxy frame. Candidate-sheet images are not automatically approved representatives.
   - Provide a real storyboard, not only a scene list. For every anchor include: ID, occurrence timestamps, representative image, initial still composition, characters/props, dialogue or narration, image-to-video action, transition/contextual link, narrative purpose, and merge/split confidence where disputed.
   - Provide a separate **image-to-video motion** block. For each image-base scene, describe what the generated video does after the still image: character movement, camera movement, prop/action changes, facial/mouth motion, effects, transitions, and cause/effect continuity. This is different from the still-image composition and should explain how the scene is animated.
   - Preserve all narrative beats in the anchor's ordered I2V field, including transformations and payoffs, rather than creating extra numbered anchors. Connect subsequent shots to previous actions when the source supports that relationship; mark merely implied links as interpretation, not established causation.
   - Summarize the context/narrative arc.
   - Transcribe the full dialogue when audio exists, independently for each video. Use timestamped ASR, listen to uncertain intervals, and cross-check all speech against available burned-in captions. Preserve extra caption-only text separately and identify audio/caption disagreements; do not silently replace speech with captions. Clearly mark only the specific uncertain words and unverified spans; do not claim full verification without checking, omit late lines, or substitute a summary for the transcript.
   - If accurate transcription is requested, try a local ASR model and caption cross-check before answering. Report a real technical limitation if transcription cannot be completed.
   - For Portuguese slang, names, one-word burned captions, overlapping speakers, or synthetic voices, compare ASR against the visible word sequence. Correct only what the evidence supports and mark the exact uncertain wording instead of labeling the whole transcript uncertain.
   - A complete local deliverable should normally include: one chronological storyboard JPG built from proxy frames, a readable HTML report, and a Markdown report. The reports must contain the count/range, context, ontology, causal chain, still-image descriptions, separate I2V blocks, full transcript, and uncertainty notes.

6. Stay inside the requested scope.
   - Do not add Britinho/Zazito adaptation, viral scoring, prompt writing, or other derivative work unless the user asks for it in the current request.

7. Adapt for Britinho/Zazito only when explicitly requested.
   - Read `references/britinho-zazito.md` before making adaptation recommendations.
   - Prefer extracting mechanics over copying surface IP.
   - Identify hook, conflict, escalation, payoff, second payoff, and what should become a material/cartoon consequence.

## Script

Run `scripts/analyze_tiktok.py` to automate the boring parts:

```powershell
python C:\Users\User\.codex\skills\tiktok-storyboard-analyzer\scripts\analyze_tiktok.py "https://www.tiktok.com/@user/video/123" --out .\work\tiktok-analysis
```

Useful options:

- `--install-deps`: install Python dependencies into a local `.deps` folder inside the output directory.
- `--name slug`: set the output basename.
- `--no-transcribe`: skip Whisper transcription.
- `--scene-threshold 26`: fixed ContentDetector sensitivity, independent of resulting count. The OpenCV fallback uses its own fixed score scale, not this threshold.
- `--boundary-times 4.2 9.8`: additionally make local before/during/after strips at disputed timestamps (seconds).
- `--language pt`: force the ASR language when auto-detection is unreliable.
- `--model base`: select the installed faster-whisper model.
- `--initial-prompt "Baniel, Bananilso"`: supply names or vocabulary that are already evidenced by captions/context.

Fallback download without opening a browser:

```powershell
python scripts/fetch_tiktok_fallback.py "https://www.tiktok.com/@user/video/123" --out .\work\run --name user_123
python scripts/analyze_tiktok.py .\work\run\user_123.mp4 --out .\work\run --name user_123 --language pt
```

After manual anchor review, render the portable deliverables:

```powershell
python scripts/render_storyboard_report.py .\work\user_123_anchors.json --video .\work\run\user_123.mp4 --metadata .\work\run\user_123_tikwm.json --out .\outputs
```

The script produces:

- downloaded `.mp4` and `.info.json` when URL download works;
- `*_1s_sheet.jpg`;
- `*_detected_scenes.jpg`;
- `*_scene_starts.txt`;
- `*_audio.wav`;
- `*_transcript.json` when `faster-whisper` is installed or `--install-deps` is used.
- `*_boundary_strips.jpg` when `--boundary-times` is supplied.

Legacy names `*_detected_scenes.jpg`, `*_scene_starts.txt`, and summary fields `scene_starts`/`detected_scene_sheet` remain for callers. They contain **unreviewed candidate boundaries**, not anchors; C labels on sheets identify candidates, not storyboard numbering. ASR output is likewise unverified until audio/caption review. Missing samples are labeled, not silently represented as blank evidence.

Always inspect the sheets yourself before answering. The script cannot reliably know whether two adjacent clips came from one generated image or two, and its early sample is only a starting point for choosing a stable representative.

## Response Shape

For a single video, answer in this order:

1. "Minha melhor estimativa e N ancoras unicas de imagem-base (confianca ..., faixa ...)." Explain disputed boundaries and distinguish reconstruction from a production plan.
2. One short context paragraph.
3. A one-sentence ontology/context statement explaining what the setting and main figures represent.
4. Representative images, one per anchor, and a storyboard table: `ID / reuso`, `Tempo(s)`, `Imagem / composição inicial`, `Fala`, `Image-to-video / beats em ordem`, `Função / ligação contextual`, `Confiança`. List chronological occurrences when an anchor returns.
5. A complete timestamped transcription, with a translation only when useful to the user.
6. Context and cause/effect notes that are easy to miss.
7. Adaptation notes only if explicitly requested.

For multiple URLs, complete this entire output independently for each URL in the supplied order, including its images, contextual chain, and complete verified/uncertainty-marked transcript. A combined table must not replace either storyboard. Add comparison, viral scoring, Britinho/Zazito fit, or modeling priority only when requested.
