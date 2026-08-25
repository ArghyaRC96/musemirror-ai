# MuseMirror AI - Project State

Last updated: 2026-08-25

## Current Version

MuseMirror AI V2.0

## Current Status

Feature development is complete.

MuseMirror V2 has been tested successfully with multiple songs through the full workflow:

Upload
-> deterministic audio analysis
-> Gemini lyric transcription
-> user lyric verification
-> grounded Vibe Check
-> creator-facing results

The remaining work is release and deployment:

1. Final documentation
2. GitHub V2 release
3. Streamlit Community Cloud deployment
4. Add the public application URL to the README

## Production Files

- app.py
- musemirror_engine.py
- styles.css
- README.md
- requirements.txt
- .gitignore

## Development Notebooks

- notebooks/MuseMirror_AI_V1.ipynb
- notebooks/MuseMirror_AI_V1_1.ipynb
- notebooks/MuseMirror_AI_V2.ipynb

## Current Application Flow

1. User uploads an MP3 or WAV file.
2. MuseMirror displays the uploaded track and audio player.
3. User clicks Read My Song.
4. Deterministic audio analysis runs.
5. Gemini transcribes the lyrics from the uploaded audio.
6. Temporary Gemini availability failures trigger retry and fallback behavior.
7. MuseMirror displays the transcription in an editable lyrics field.
8. User corrects any transcription mistakes.
9. User explicitly verifies the lyrics.
10. MuseMirror builds an evidence package from audio analysis and verified lyrics.
11. User runs the Vibe Check.
12. Gemini generates structured creator-facing feedback.
13. Grounding validation checks the generated response.
14. MuseMirror renders the Track Declassified interface.

## Deterministic Analysis Pipeline

The production engine currently includes:

- load_audio
- analyze_tempo
- extract_core_features
- extract_timbre_harmonic_features
- analyze_energy_profile
- analyze_energy_windows
- classify_energy_blocks
- analyze_sections
- analyze_lyrics
- build_observations
- analyze_audio

## Generative AI Pipeline

MuseMirror uses Google Gemini for two main tasks:

### Lyrics Transcription

Primary model:

gemini-3.7-flash

Fallback model:

gemini-3.6-flash

Current temporary-failure behavior:

Primary attempt
-> retry primary once
-> fallback model

Temporary failures include conditions such as:

- HTTP 503
- model unavailable
- high demand
- HTTP 429
- resource exhausted

The transcription response contains:

- detected language
- lyric segments
- approximate timestamps
- full transcription

The transcription is always shown to the user for verification before the final critique.

### Vibe Check

The Vibe Check uses the deterministic evidence and verified lyrics.

The required output structure is exactly:

- 5 What's Hitting observations
- 3 Needs a Little Love observations
- 5 Studio Moves
- 1 Big Picture paragraph

The Vibe Check pipeline also contains retry and fallback protection.

## Grounding Rules

MuseMirror must not invent musical facts that are unsupported by the supplied evidence.

Current protections include unsupported claims about:

- specific instruments
- genre
- musical key
- chord progressions
- unsupported mix decisions
- unsupported arrangement details
- double-time musical elements inferred only from BPM mathematics
- half-time musical elements inferred only from BPM mathematics

Tempo mode describes numerical interpretation only.

It must not be treated as proof of arrangement style.

## Current UI

The Streamlit interface includes:

- premium dark-neon visual design
- creator-side landing section
- audio uploader
- built-in audio player
- Read My Song button
- lyric intelligence section
- editable transcription
- Lyrics Look Good verification
- Run the Vibe Check button
- Track Declassified result section
- Track Fingerprint cards
- What's Hitting card
- Needs a Little Love card
- Studio Moves card
- Big Picture card

## Track Fingerprint

Current fingerprint metrics include:

- perceived BPM
- climax zone
- dynamic profile
- strong / medium / low energy-block counts

## Track Energy Arc

The final V2 energy visualization uses real analyzed RMS data.

Current implementation:

- 256 energy bars
- static waveform shape
- full centered waveform appearance
- animated gradient colors
- left-to-right color movement
- 20-second timeline intervals
- exact song endpoint
- waveform and timeline start alignment
- waveform and timeline end alignment
- YOUR TRACK ENERGY ARC label

Only the colors animate.

The waveform geometry itself remains static.

## Key Analysis Philosophy

Tempo is not emotion.

Raw tracker BPM is not arrangement evidence.

Spectral centroid alone is not treated as brightness.

Zero-crossing rate alone is not treated as distortion, aggression, or heaviness.

Structural section detection from mixed audio is heuristic.

Gemini transcription timestamps are approximate.

Audio measurements are evidence and clues rather than absolute musical truth.

User-verified lyrics are preferred over blindly trusting machine transcription.

## Known Limitations

- Lyrics transcription can still fail if both Gemini models are unavailable.
- Gemini timestamps are approximate.
- Structural section labels are heuristic.
- No definitive genre detection is used.
- No definitive key or chord detection is used in the final critique.
- No production-grade instrument identification is used.
- Originality and song-similarity analysis are outside V2 scope.
- Public V2 currently has no authentication layer.
- The portfolio deployment depends on Gemini API availability.

## Security

The Gemini API key must never be committed to GitHub.

Local development uses:

.env

Production deployment will use:

Streamlit Secrets

Expected secret name:

GEMINI_API_KEY

## Deployment Target

Streamlit Community Cloud

Expected application entrypoint:

app.py

Deployment will be connected directly to the GitHub repository.

## GitHub Release Target

Planned release:

v2.0.0

The final release should include:

- production application
- analysis engine
- custom styles
- updated README
- project continuity documentation
- deployment requirements

## Next Steps

1. Update docs/build_log.md
2. Validate requirements.txt and deployment dependencies
3. Run final Python syntax checks
4. Inspect git status
5. Commit MuseMirror AI V2
6. Push to GitHub main
7. Create v2.0.0 Git tag
8. Deploy to Streamlit Community Cloud
9. Add the live Streamlit URL to README.md

## Next Development Phase

No additional V2 feature development is currently required.

Future work should be treated as either:

- bug fixes
- deployment maintenance
- documentation improvements
- MuseMirror V3 features

Core MuseMirror AI V2 development is complete.
