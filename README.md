# MuseMirror AI V2

Creator-side music intelligence that turns measurable audio evidence,
song structure, and verified lyrics into grounded studio feedback.

> MuseMirror calculates evidence first, then asks the generative layer
> to reason from that evidence.

## Status

**MuseMirror AI V2.0 - Feature Complete**

Current milestone:

```text
V2 complete
    ->
GitHub release
    ->
Streamlit Community Cloud
    ->
Public portfolio demo
```

## Live Demo

https://musemirror-ai.streamlit.app/

---

## What MuseMirror Does

MuseMirror analyzes an uploaded MP3 or WAV file using deterministic
audio processing before involving an LLM.

It then combines the measured audio evidence with user-verified lyrics
to produce creator-facing feedback.

The workflow is:

```text
Upload Audio
     |
     v
Deterministic Audio Analysis
     |
     +--> Tempo
     +--> Core Features
     +--> Timbre / Harmonic Features
     +--> RMS Energy
     +--> Energy Windows
     +--> Energy Blocks
     +--> Structural Heuristics
     +--> Climax Detection
     |
     v
Gemini Lyrics Transcription
     |
     +--> Retry on temporary API failure
     +--> Fallback model
     |
     v
User Reviews Lyrics
     |
     v
Verified Lyrics
     |
     v
Grounded Evidence Package
     |
     v
Gemini Vibe Check
     |
     v
Grounding Validator
     |
     v
Creator-Facing Feedback
```

---

## V2 Features

### Audio Intelligence

MuseMirror currently analyzes:

- raw tracker BPM
- perceived BPM
- RMS energy
- dynamic range
- energy variation
- energy windows
- strong / medium / low energy blocks
- climax region
- structural heuristics
- core spectral features
- timbre and harmonic features

Audio measurements are calculated before LLM interpretation.

### Real Track Energy Arc

The V2 interface includes a real RMS-driven visualization with:

- 256 timeline-distributed energy bars
- static waveform geometry
- full centered waveform appearance
- animated cyan / violet / pink gradient flow
- 20-second timeline intervals
- exact final song timestamp
- aligned waveform and timeline endpoints

Only the colors animate.

The waveform shape itself remains static.

### Lyrics Intelligence

Gemini processes the uploaded song and returns structured transcription
data including:

- detected language
- lyric lines
- approximate timestamps
- complete transcription text

Before the final Vibe Check, the user can manually correct the
transcription and explicitly verify the lyrics.

### API Reliability

The transcription pipeline currently uses:

```text
gemini-3.7-flash
        |
        | temporary 503 / 429
        v
retry gemini-3.7-flash
        |
        | still unavailable
        v
gemini-3.6-flash
```

The Vibe Check generation pipeline also includes retry and fallback
protection for temporary Gemini availability failures.

---

## Grounded Vibe Check

MuseMirror's final creator critique contains exactly:

- 5 What's Hitting observations
- 3 Needs a Little Love observations
- 5 Studio Moves
- 1 Big Picture reflection

The LLM receives a constrained evidence package instead of unrestricted
access to make musical assumptions.

---

## Hallucination Control

MuseMirror deliberately prevents unsupported claims about:

- instrumentation
- genre
- musical key
- chord progression
- unsupported mix decisions
- unsupported arrangement details
- double-time elements inferred only from BPM mathematics
- half-time elements inferred only from BPM mathematics

For example:

```text
raw tracker BPM: 160
perceived BPM: 80
```

does not prove that the arrangement contains double-time musical
elements.

Tempo interpretation is treated as numerical evidence rather than
arrangement evidence.

---

## Creator-Facing Interface

The Streamlit V2 product includes:

- premium dark-neon UI
- audio upload
- built-in audio player
- Read My Song workflow
- editable lyrics review
- explicit lyric verification
- Run the Vibe Check workflow
- Track Declassified results
- real Track Energy Arc
- track fingerprint cards
- What's Hitting
- Needs a Little Love
- Studio Moves
- Big Picture

The Track Fingerprint currently surfaces:

- perceived BPM
- climax zone
- dynamic profile
- strong / medium / low energy blocks

---

## Tech Stack

### Application

- Python
- Streamlit

### Audio Analysis

- Librosa
- NumPy
- Pandas
- SoundFile
- Matplotlib

### Generative AI

- Google Gemini API
- Google GenAI Python SDK

### Development

- VS Code
- Google Colab
- Git
- GitHub

### Deployment

- Streamlit Community Cloud

---

## Repository Structure

```text
musemirror-ai/
|
|-- app.py
|-- musemirror_engine.py
|-- styles.css
|-- README.md
|-- requirements.txt
|-- .gitignore
|
|-- notebooks/
|   |-- MuseMirror_AI_V1.ipynb
|   |-- MuseMirror_AI_V1_1.ipynb
|   `-- MuseMirror_AI_V2.ipynb
|
|-- sample_outputs/
|   |-- v1_1/
|   `-- v2/
|
|-- assets/
|
`-- docs/
    |-- project_state.md
    `-- build_log.md
```

---

## Production Architecture

### app.py

Controls the Streamlit product experience:

- upload workflow
- audio playback
- session state
- lyric review
- lyric verification
- Vibe Check execution
- final result rendering

### musemirror_engine.py

Contains the production analysis pipeline.

Major functions include:

```python
load_audio()
analyze_tempo()
extract_core_features()
extract_timbre_harmonic_features()
analyze_energy_profile()
analyze_energy_windows()
classify_energy_blocks()
analyze_sections()
transcribe_lyrics()
analyze_lyrics()
build_observations()
analyze_audio()
validate_vibe_check_grounding()
run_vibe_check()
```

### styles.css

Contains MuseMirror's custom Streamlit visual system.

---

## Run Locally

Clone the repository:

```bash
git clone https://github.com/ArghyaRC96/musemirror-ai.git
cd musemirror-ai
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```text
GEMINI_API_KEY=your_api_key_here
```

Run MuseMirror:

```bash
streamlit run app.py
```

Never commit `.env` or Streamlit secret files.

---

## Important Limitations

MuseMirror intentionally avoids overstating what individual audio
features can prove.

### Tempo

Tempo does not determine emotion.

Raw BPM and perceived BPM are numerical interpretations rather than
proof of arrangement style.

### Spectral Centroid

Spectral centroid alone is not treated as musical brightness.

### Zero-Crossing Rate

Zero-crossing rate alone is not treated as distortion, aggression,
or heaviness.

### Song Structure

Detected structural regions are heuristic estimates rather than
definitive verse, chorus, bridge, or breakdown labels.

### Lyrics

Gemini timestamps are approximate.

The user verifies lyrics before they are used as evidence for the
final critique.

### Musical Semantics

V2 intentionally avoids definitive claims about:

- genre
- key
- chords
- instrumentation
- originality
- song similarity

unless appropriate evidence exists.

---

## Project Evolution

### V1

Initial proof of concept covering:

- tempo
- MFCC
- chroma
- RMS
- spectral centroid
- zero-crossing rate
- transcription
- early creator-feedback heuristics

### V1.1

Expanded the evidence layer with:

- improved tempo interpretation
- richer RMS statistics
- energy windows
- energy curves
- timbre analysis
- structured reports
- clearer feature limitations

### V2

Converted MuseMirror into a portfolio-ready AI product with:

- production Python engine
- Streamlit application
- Gemini multimodal transcription
- lyric verification
- API retry and fallback
- grounded Vibe Check
- hallucination validation
- real RMS energy visualization
- adaptive timeline
- creator-facing interface

---

## Engineering Principles

### Evidence Before Generation

Audio signal processing happens before LLM interpretation.

### Human Verification

Lyrics are reviewed before becoming trusted evidence.

### Constrained Generative AI

The LLM is prevented from freely inventing musical facts.

### Graceful API Failure

Temporary model failures trigger retry and fallback behavior.

### Creator-Side Feedback

MuseMirror provides observations and experiments rather than pretending
to provide absolute musical truth.

---

## Portfolio Value

MuseMirror demonstrates practical experience with:

- audio signal processing
- multimodal generative AI
- structured LLM outputs
- prompt engineering
- grounding and hallucination control
- API resilience
- Streamlit application development
- session-state management
- product UX
- deployment-oriented engineering

---

## Current Version

**MuseMirror AI V2.0**

Feature development complete.

Next milestone:

**Public Streamlit deployment complete.**
