# MuseMirror AI - Build Log

Last updated: 2026-08-25

# Project Evolution

MuseMirror started as an experimental music-analysis notebook and evolved into a deployable creator-side AI application.

The project was developed in three major stages:

- V1
- V1.1
- V2

---

# V1 - Initial Proof of Concept

The first version established the core idea:

Analyze a song using measurable audio features and convert those measurements into creator-facing observations.

Initial analysis included:

- tempo
- MFCC
- chroma
- RMS
- spectral centroid
- zero-crossing rate
- waveform visualization
- transcription
- simple heuristic interpretation

The original implementation primarily lived inside:

notebooks/MuseMirror_AI_V1.ipynb

## Key Lesson From V1

Low-level audio features should not be treated as direct musical truth.

Examples:

- spectral centroid alone does not prove perceived brightness
- zero-crossing rate alone does not prove distortion or aggression
- tempo alone does not determine emotion

These limitations shaped the evidence-first philosophy used in later versions.

---

# V1.1 - Expanded Evidence Layer

V1.1 improved both analysis depth and interpretability.

Primary notebook:

notebooks/MuseMirror_AI_V1_1.ipynb

Major additions included:

- raw tempo versus adjusted tempo
- half-tempo / double-tempo interpretation
- richer RMS statistics
- RMS percentile analysis
- five-second energy windows
- energy-curve analysis
- top-energy windows
- additional timbre features
- improved visual diagnostics
- structured song report output
- stronger documentation of feature limitations

## Important Design Change

Tempo adjustment was treated as a numerical interpretation.

For example:

raw BPM approximately 160

and

perceived BPM approximately 80

does not prove that the arrangement contains double-time instrumentation.

This distinction later became an explicit grounding rule in V2.

---

# V2 - Productization

V2 converted MuseMirror from a notebook experiment into a portfolio-ready AI application.

Primary notebook:

notebooks/MuseMirror_AI_V2.ipynb

Production files:

- app.py
- musemirror_engine.py
- styles.css

V2 development followed a notebook-to-production workflow:

Notebook experimentation
-> reusable Python functions
-> production engine
-> Streamlit application
-> grounded generative layer
-> deployment preparation

---

# Production Analysis Engine

The deterministic analysis pipeline was moved into:

musemirror_engine.py

Core production functions include:

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

The deterministic analysis runs independently of Gemini.

This means MuseMirror does not rely on an LLM to calculate the core audio measurements.

---

# Audio Analysis Design

The final V2 pipeline includes:

## Tempo

- raw tracker BPM
- perceived BPM
- tempo-mode interpretation
- explanatory tempo note

Tempo mode is numerical evidence only.

It is not used as proof of rhythmic arrangement.

## Energy

- RMS frame analysis
- dynamic range
- energy variation
- five-second windows
- strong / medium / low block classification
- climax-region analysis

## Structure

Structural sections are estimated using energy and temporal heuristics.

These are intentionally treated as approximate structural clues rather than definitive verse / chorus / bridge labels.

## Timbre and Harmonic Features

Additional audio measurements are retained as evidence while avoiding unsupported semantic claims.

---

# Gemini Lyrics Transcription

V2 moved lyric transcription to Gemini multimodal audio processing.

Production function:

transcribe_lyrics

The transcription response includes:

- detected language
- lyric segments
- approximate start timestamps
- approximate end timestamps
- full lyric text

Gemini timestamps are explicitly treated as approximate.

---

# Human Lyric Verification

One of the major V2 design decisions was to avoid blindly trusting machine transcription.

The Streamlit workflow now:

1. transcribes the uploaded song
2. displays the transcription in an editable field
3. allows the creator to correct mistakes
4. requires explicit confirmation
5. stores the corrected lyrics as verified lyrics
6. uses only those verified lyrics for the final Vibe Check

This keeps human verification inside the AI pipeline where transcription errors could materially affect the critique.

---

# Gemini Reliability

Temporary Gemini availability failures were observed during development, especially HTTP 503 high-demand errors.

The system therefore added retry and fallback protection.

Primary model:

gemini-3.7-flash

Fallback model:

gemini-3.6-flash

## Vibe Check Reliability

The Vibe Check pipeline retries temporary failures and falls back to the secondary model when necessary.

## Lyrics Transcription Reliability

The initial transcription pipeline was later upgraded to follow the same resilience pattern:

Primary model
-> retry primary once
-> fallback model

Temporary failure detection includes cases such as:

- 503
- UNAVAILABLE
- high demand
- 429
- RESOURCE_EXHAUSTED

The actual model that succeeds is recorded in the returned transcription analysis.

---

# Grounded Vibe Check

The Vibe Check was designed as a creator-side studio companion rather than a generic song-review chatbot.

The final output contract requires exactly:

- 5 What's Hitting observations
- 3 Needs a Little Love observations
- 5 Studio Moves
- 1 Big Picture paragraph

The model receives a constrained evidence package containing:

- tempo evidence
- energy measurements
- structural observations
- energy-block counts
- verified lyrics
- lyric-density information
- deterministic observations

---

# Grounding Rules

The Vibe Check prompt and validator were strengthened to prevent unsupported musical claims.

MuseMirror must not invent:

- instruments
- genre
- musical key
- chords
- unsupported mix decisions
- unsupported arrangement details

Special tempo protections were also added.

The model must not convert:

double_time

or

half_time

tempo-mode values into claims such as:

- double-time elements
- double-time feel
- double-time rhythm
- half-time elements
- half-time feel
- half-time rhythm

unless separate evidence supports such claims.

---

# Grounding Validator

Production function:

validate_vibe_check_grounding

The validator checks generated text for unsupported claims.

If a grounding violation is detected:

1. MuseMirror identifies the violation.
2. A correction request is sent to Gemini.
3. The corrected response is validated again.
4. The workflow fails safely if the corrected response still violates the grounding contract.

---

# Streamlit V2 Application

The creator-facing application was built in:

app.py

The custom visual system lives in:

styles.css

Major UI stages include:

## Landing Experience

- MuseMirror hero section
- creator-side positioning
- feature chips
- premium dark-neon visual language

## Upload

- MP3 / WAV uploader
- track-loaded state
- built-in Streamlit audio playback
- Read My Song button

## Lyrics Intelligence

- transcription display
- editable lyrics
- Lyrics Look Good confirmation

## Creator Feedback

- Run the Vibe Check
- completion state
- Track Declassified interface

## Final Results

- Track Fingerprint
- What's Hitting
- Needs a Little Love
- Studio Moves
- Big Picture

---

# Track Energy Arc

The original visualizer began as a decorative waveform.

It was later upgraded to use actual analyzed RMS data.

Final V2 implementation:

- 256 RMS-derived bars
- static waveform geometry
- full centered waveform appearance
- animated cyan / violet / pink gradient
- gradient movement from left to right
- no height animation
- 20-second timeline intervals
- exact final song timestamp
- aligned waveform and timeline start
- aligned waveform and timeline end
- YOUR TRACK ENERGY ARC label

The waveform and timeline share the same horizontal geometry so their endpoints remain aligned across different songs.

---

# Multi-Song Validation

V2 was tested using multiple original tracks.

Testing verified that:

- different song durations are handled correctly
- timelines adapt automatically
- energy arcs change according to the analyzed RMS signal
- lyric transcription works across tracks
- verified lyrics feed correctly into the Vibe Check
- grounding validation remains active
- the final interface renders consistently

A second full test using Highway Soul successfully completed the complete production workflow.

---

# Unicode / Mojibake Recovery

During late-stage UI development, several source strings became corrupted through encoding reinterpretation.

Examples included broken:

- emojis
- apostrophes
- dashes
- UI symbols
- card icons

The issue was traced to mojibake caused by Unicode text being interpreted through incompatible encodings during source-file rewrites.

The source was repaired and normalized to UTF-8.

## Permanent Development Rule

Future scripts that modify MuseMirror text files should:

- explicitly read using UTF-8
- explicitly write using UTF-8
- avoid Get-Content plus full-file PowerShell rewrites for Unicode source files
- prefer Python Path.read_text with encoding="utf-8"
- prefer Python Path.write_text with encoding="utf-8"
- validate source structure before writing when possible

Temporary backup files created during debugging were removed after V2 stabilization.

---

# V2 Completion Status

MuseMirror AI V2 successfully supports:

Upload Audio
-> Audio Analysis
-> Gemini Transcription
-> User Lyric Verification
-> Evidence Construction
-> Grounded Gemini Vibe Check
-> Grounding Validation
-> Creator-Facing Results

Core feature development is complete.

---

# Remaining Release Work

The remaining V2 tasks are:

1. finalize documentation
2. validate deployment dependencies
3. run final syntax checks
4. commit the final release
5. push to GitHub
6. tag v2.0.0
7. deploy to Streamlit Community Cloud
8. configure GEMINI_API_KEY using Streamlit Secrets
9. test the public application
10. add the public URL to README.md

After these steps, MuseMirror AI V2 is considered fully shipped.

---

# Future V3 Ideas

Potential future work includes:

- improved structural segmentation
- richer musical feature evidence
- optional source separation
- originality analysis
- similarity analysis
- stronger evaluation datasets
- production authentication
- saved analysis history
- exportable reports

These are intentionally outside the V2 release scope.

---

# Final V2 Positioning

MuseMirror AI V2 demonstrates an end-to-end AI engineering workflow combining:

- audio signal processing
- multimodal generative AI
- structured outputs
- human-in-the-loop verification
- grounding and hallucination control
- model retry / fallback resilience
- stateful Streamlit UX
- custom frontend styling
- deployment-oriented engineering

The central design principle remains:

Calculate the evidence first.

Then make the generative layer accountable to it.


---

# Public Deployment

MuseMirror AI V2 was deployed successfully to Streamlit Community Cloud.

Public application:

https://musemirror-ai.streamlit.app/

The deployed application is connected to the GitHub main branch and uses Streamlit Secrets for the Gemini API credential.

The public deployment supports the complete V2 workflow:

Upload Audio
-> Audio Analysis
-> Gemini Transcription
-> Lyric Verification
-> Grounded Vibe Check
-> Track Declassified Results

## Final Release Status

MuseMirror AI V2 is publicly available and portfolio ready.

Live application:

https://musemirror-ai.streamlit.app/

### 2026-08-26 - Runtime latency and resilience update

Implemented and validated a simplified Gemini execution policy for MuseMirror AI V2.

Changes:
- Added Streamlit-independent `musemirror_runtime.py`.
- Standardized transcription and Vibe Check on `gemini-3.6-flash`.
- Removed the Gemini 3.7 -> 3.6 fallback chain.
- Added one retry for transcription.
- Added one retry for Vibe Check.
- Transcription retries use a fresh Gemini Files upload.
- Increased Gemini client timeout from 30 seconds to 45 seconds per request.
- Preserved existing prompts, grounding logic, correction flow, audio-analysis pipeline, and frontend behavior.
- UTF-8-safe patching and Python syntax validation were used throughout.
- Live Bengali-song test completed quickly after the optimization.

Result: MuseMirror now has a simpler, faster, and more predictable production inference path.
