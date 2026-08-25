# ============================================
# MuseMirror AI — Analysis Engine
# ============================================

import re
import json
import time
from google.genai import types
from pathlib import Path
import librosa
import numpy as np


# ============================================
# AUDIO LOADING
# ============================================

def load_audio(file_path):
    """
    Load an audio file and return the waveform,
    sample rate, time axis, and basic metadata.
    """

    # Load original sample rate and convert to mono
    y, sr = librosa.load(
        file_path,
        sr=None,
        mono=True
    )

    # Basic metadata
    duration_sec = librosa.get_duration(
        y=y,
        sr=sr
    )

    total_samples = len(y)

    time_axis = np.linspace(
        0,
        duration_sec,
        total_samples
    )

    audio_info = {
        "file_name": Path(file_path).name,
        "sample_rate": int(sr),
        "duration_sec": float(duration_sec),
        "total_samples": int(total_samples),
        "waveform_shape": tuple(y.shape),
        "peak_amplitude": float(
            np.max(np.abs(y))
        ),
        "mean_amplitude": float(
            np.mean(np.abs(y))
        )
    }

    return y, sr, time_axis, audio_info

# ============================================
# TEMPO ANALYSIS
# ============================================

def analyze_tempo(y, sr):
    """
    Detect the raw beat-tracker tempo and choose a
    more natural perceived pulse when appropriate.
    """

    # ----------------------------------------
    # Raw beat tracking
    # ----------------------------------------

    tempo_raw, beat_frames = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    tempo_raw_bpm = float(
        np.asarray(tempo_raw).item()
    )

    beat_times_sec = librosa.frames_to_time(
        beat_frames,
        sr=sr
    )


    # ----------------------------------------
    # Generate tempo candidates
    # ----------------------------------------

    tempo_candidates = {
        "half_time": tempo_raw_bpm / 2,
        "normal": tempo_raw_bpm,
        "double_time": tempo_raw_bpm * 2
    }


    # Keep musically reasonable values
    valid_tempo_candidates = {
        mode: float(bpm)
        for mode, bpm in tempo_candidates.items()
        if 40 <= bpm <= 220
    }


    # ----------------------------------------
    # Select perceived pulse
    # Prefer 60–125 BPM
    # ----------------------------------------

    preferred_candidates = {
        mode: bpm
        for mode, bpm in valid_tempo_candidates.items()
        if 60 <= bpm <= 125
    }

    if preferred_candidates:

        selected_mode, tempo_adjusted_bpm = min(
            preferred_candidates.items(),
            key=lambda item: abs(item[1] - 85)
        )

    else:

        selected_mode = "normal"
        tempo_adjusted_bpm = tempo_raw_bpm


    # ----------------------------------------
    # Interpret raw vs perceived tempo
    # ----------------------------------------

    tempo_ratio = (
        tempo_raw_bpm /
        (tempo_adjusted_bpm + 1e-10)
    )

    if abs(tempo_ratio - 1.0) < 0.15:

        tempo_mode = "normal"

        tempo_mode_note = (
            "Raw tempo already matches the perceived pulse"
        )

    elif abs(tempo_ratio - 2.0) < 0.25:

        tempo_mode = "double_time"

        tempo_mode_note = (
            "Double-time beat-tracker reading corrected"
        )

    elif abs(tempo_ratio - 0.5) < 0.15:

        tempo_mode = "half_time"

        tempo_mode_note = (
            "Half-time beat-tracker reading corrected"
        )

    else:

        tempo_mode = selected_mode

        tempo_mode_note = (
            "Closest musically reasonable pulse selected"
        )


    # ----------------------------------------
    # Structured output
    # ----------------------------------------

    tempo_summary = {
        "tempo_raw_bpm": float(tempo_raw_bpm),
        "tempo_adjusted_bpm": float(tempo_adjusted_bpm),
        "tempo_ratio": float(tempo_ratio),
        "tempo_mode": tempo_mode,
        "tempo_mode_note": tempo_mode_note,

        "tempo_candidates_bpm": {
            mode: round(bpm, 2)
            for mode, bpm
            in valid_tempo_candidates.items()
        },

        "num_detected_beats": int(
            len(beat_frames)
        ),

        "beat_times_sec": beat_times_sec.tolist()
    }

    return tempo_summary

# ============================================
# CORE AUDIO FEATURES
# ============================================

def extract_core_features(y, sr):
    """
    Extract frame-level RMS energy, spectral centroid,
    and zero-crossing rate, plus compact summary stats.
    """

    # ----------------------------------------
    # Frame-level features
    # ----------------------------------------

    rms_frames = librosa.feature.rms(
        y=y
    )[0]

    spectral_centroid_frames = librosa.feature.spectral_centroid(
        y=y,
        sr=sr
    )[0]

    zcr_frames = librosa.feature.zero_crossing_rate(
        y
    )[0]


    # ----------------------------------------
    # Summary statistics
    # ----------------------------------------

    core_features = {
        "rms_energy_mean": float(
            np.mean(rms_frames)
        ),

        "rms_energy_std": float(
            np.std(rms_frames)
        ),

        "spectral_centroid_mean": float(
            np.mean(spectral_centroid_frames)
        ),

        "spectral_centroid_std": float(
            np.std(spectral_centroid_frames)
        ),

        "zero_crossing_rate_mean": float(
            np.mean(zcr_frames)
        ),

        "zero_crossing_rate_std": float(
            np.std(zcr_frames)
        )
    }


    # ----------------------------------------
    # Keep raw frame data for later stages
    # ----------------------------------------

    frame_features = {
        "rms_frames": rms_frames,
        "spectral_centroid_frames": spectral_centroid_frames,
        "zcr_frames": zcr_frames
    }

    return core_features, frame_features

# ============================================
# TIMBRE + HARMONIC FEATURES
# ============================================

def extract_timbre_harmonic_features(y, sr):
    """
    Extract MFCC and chroma features and return
    compact timbre/harmonic summaries.
    """

    # ----------------------------------------
    # MFCCs
    # ----------------------------------------

    n_mfcc = 13

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=n_mfcc
    )

    mfcc_mean = np.mean(
        mfcc,
        axis=1
    )

    mfcc_std = np.std(
        mfcc,
        axis=1
    )


    # ----------------------------------------
    # Chroma
    # ----------------------------------------

    chroma = librosa.feature.chroma_stft(
        y=y,
        sr=sr
    )

    chroma_mean = np.mean(
        chroma,
        axis=1
    )

    chroma_std = np.std(
        chroma,
        axis=1
    )


    chroma_labels = [
        "C", "C#", "D", "D#",
        "E", "F", "F#", "G",
        "G#", "A", "A#", "B"
    ]


    # ----------------------------------------
    # MFCC summary
    # ----------------------------------------

    mfcc_summary = {
        f"mfcc_{i + 1}": {
            "mean": float(mfcc_mean[i]),
            "std": float(mfcc_std[i])
        }
        for i in range(n_mfcc)
    }


    # ----------------------------------------
    # Chroma summary
    # ----------------------------------------

    chroma_summary = {
        chroma_labels[i]: {
            "mean": float(chroma_mean[i]),
            "std": float(chroma_std[i])
        }
        for i in range(len(chroma_labels))
    }


    # ----------------------------------------
    # Compact structured output
    # ----------------------------------------

    timbre_harmonic_analysis = {
        "mfcc_summary": mfcc_summary,
        "chroma_summary": chroma_summary
    }


    # ----------------------------------------
    # Keep raw arrays for optional visuals
    # ----------------------------------------

    timbre_raw = {
        "mfcc": mfcc,
        "mfcc_mean": mfcc_mean,
        "mfcc_std": mfcc_std,
        "chroma": chroma,
        "chroma_mean": chroma_mean,
        "chroma_std": chroma_std
    }

    return timbre_harmonic_analysis, timbre_raw

# ============================================
# ENERGY PROFILE
# ============================================

def analyze_energy_profile(frame_features, audio_info):
    """
    Build the track-level energy profile from RMS frames.
    """

    # ----------------------------------------
    # Reuse RMS frames
    # ----------------------------------------

    rms_values = frame_features["rms_frames"]


    # ----------------------------------------
    # Core energy statistics
    # ----------------------------------------

    rms_mean = float(
        np.mean(rms_values)
    )

    rms_max = float(
        np.max(rms_values)
    )

    rms_min = float(
        np.min(rms_values)
    )


    rms_p10 = float(
        np.percentile(rms_values, 10)
    )

    rms_p25 = float(
        np.percentile(rms_values, 25)
    )

    rms_p50 = float(
        np.percentile(rms_values, 50)
    )

    rms_p75 = float(
        np.percentile(rms_values, 75)
    )

    rms_p90 = float(
        np.percentile(rms_values, 90)
    )


    rms_range = float(
        rms_max - rms_min
    )

    rms_iqr = float(
        rms_p75 - rms_p25
    )


    # ----------------------------------------
    # Energy variation
    # ----------------------------------------

    energy_variation_score = float(
        rms_p90 - rms_p10
    )


    # ----------------------------------------
    # Dynamic character
    # ----------------------------------------

    if rms_range > 0.50:
        dynamic_range_class = "high dynamic"

    elif rms_range > 0.30:
        dynamic_range_class = "moderate dynamic"

    else:
        dynamic_range_class = "flat to controlled"


    # ----------------------------------------
    # Climax strength
    # ----------------------------------------

    climax_strength_score = float(
        rms_max /
        (rms_mean + 1e-10)
    )


    # ----------------------------------------
    # Crest-factor-like proxy
    # ----------------------------------------

    peak_amplitude = audio_info[
        "peak_amplitude"
    ]

    crest_factor_proxy = float(
        peak_amplitude /
        (rms_mean + 1e-10)
    )


    # ----------------------------------------
    # Structured output
    # ----------------------------------------

    energy_profile = {
        "rms_mean": rms_mean,
        "rms_max": rms_max,
        "rms_min": rms_min,

        "rms_p10": rms_p10,
        "rms_p25": rms_p25,
        "rms_p50": rms_p50,
        "rms_p75": rms_p75,
        "rms_p90": rms_p90,

        "rms_range": rms_range,
        "rms_iqr": rms_iqr,

        "energy_variation_score":
            energy_variation_score,

        "dynamic_range_class":
            dynamic_range_class,

        "climax_strength_score":
            climax_strength_score,

        "peak_amplitude":
            float(peak_amplitude),

        "crest_factor_proxy":
            crest_factor_proxy
    }

    return energy_profile

# ============================================
# WINDOWED ENERGY ANALYSIS
# ============================================

def analyze_energy_windows(y, sr, window_sec=5, hop_sec=5):
    """
    Measure RMS energy across fixed time windows
    and identify the strongest sections.
    """

    # ----------------------------------------
    # Convert seconds to samples
    # ----------------------------------------

    window_length_samples = int(
        window_sec * sr
    )

    hop_length_samples = int(
        hop_sec * sr
    )


    # ----------------------------------------
    # Compute energy windows
    # ----------------------------------------

    energy_windows = []

    for start in range(
        0,
        len(y) - window_length_samples + 1,
        hop_length_samples
    ):

        end = start + window_length_samples

        segment = y[start:end]

        window_rms = float(
            np.sqrt(
                np.mean(segment ** 2)
            )
        )

        energy_windows.append({
            "start_sec": float(start / sr),
            "end_sec": float(end / sr),
            "duration_sec": float(window_sec),
            "rms": window_rms
        })


    # ----------------------------------------
    # Strongest windows
    # ----------------------------------------

    top_energy_windows = sorted(
        energy_windows,
        key=lambda item: item["rms"],
        reverse=True
    )[:5]


    strongest_window = (
        top_energy_windows[0]
        if top_energy_windows
        else None
    )


    # ----------------------------------------
    # Structured output
    # ----------------------------------------

    energy_window_analysis = {
        "window_sec": int(window_sec),
        "hop_sec": int(hop_sec),
        "num_windows": len(energy_windows),
        "windows": energy_windows,
        "top_5_windows": top_energy_windows,
        "strongest_window": strongest_window
    }

    return energy_window_analysis

# ============================================
# ENERGY BLOCK CLASSIFICATION
# ============================================

def classify_energy_blocks(energy_window_analysis):
    """
    Classify energy windows as strong, medium, or weak,
    then merge adjacent windows with the same label.
    """

    energy_windows = energy_window_analysis["windows"]


    # ----------------------------------------
    # Safety check
    # ----------------------------------------

    if not energy_windows:
        return {
            "strong_threshold": 0.0,
            "weak_threshold": 0.0,
            "classified_windows": [],
            "blocks": [],
            "num_strong_blocks": 0,
            "num_medium_blocks": 0,
            "num_weak_blocks": 0
        }


    # ----------------------------------------
    # Pull RMS values
    # ----------------------------------------

    rms_values_windows = np.array([
        window["rms"]
        for window in energy_windows
    ])


    # ----------------------------------------
    # Percentile thresholds
    # ----------------------------------------

    strong_threshold = float(
        np.percentile(
            rms_values_windows,
            80
        )
    )

    weak_threshold = float(
        np.percentile(
            rms_values_windows,
            30
        )
    )


    # ----------------------------------------
    # Classify each window
    # ----------------------------------------

    classified_windows = []

    for window in energy_windows:

        if window["rms"] >= strong_threshold:
            label = "strong"

        elif window["rms"] <= weak_threshold:
            label = "weak"

        else:
            label = "medium"

        classified_windows.append({
            **window,
            "label": label
        })


    # ----------------------------------------
    # Merge neighboring windows
    # ----------------------------------------

    def merge_energy_blocks(windows):

        if not windows:
            return []

        merged = []

        current = windows[0].copy()

        for window in windows[1:]:

            same_label = (
                window["label"]
                == current["label"]
            )

            directly_adjacent = (
                abs(
                    window["start_sec"]
                    - current["end_sec"]
                )
                < 1e-9
            )

            if same_label and directly_adjacent:

                current["end_sec"] = (
                    window["end_sec"]
                )

                current["duration_sec"] = (
                    current["end_sec"]
                    - current["start_sec"]
                )

                current["rms_values"] = (
                    current.get(
                        "rms_values",
                        [current["rms"]]
                    )
                    + [window["rms"]]
                )

            else:

                if "rms_values" not in current:
                    current["rms_values"] = [
                        current["rms"]
                    ]

                current["mean_rms"] = float(
                    np.mean(
                        current["rms_values"]
                    )
                )

                merged.append(current)

                current = window.copy()


        # Save final block
        if "rms_values" not in current:
            current["rms_values"] = [
                current["rms"]
            ]

        current["mean_rms"] = float(
            np.mean(
                current["rms_values"]
            )
        )

        merged.append(current)

        return merged


    energy_blocks = merge_energy_blocks(
        classified_windows
    )


    # ----------------------------------------
    # Count block types
    # ----------------------------------------

    strong_blocks = [
        block
        for block in energy_blocks
        if block["label"] == "strong"
    ]

    medium_blocks = [
        block
        for block in energy_blocks
        if block["label"] == "medium"
    ]

    weak_blocks = [
        block
        for block in energy_blocks
        if block["label"] == "weak"
    ]


    # ----------------------------------------
    # Structured output
    # ----------------------------------------

    energy_block_analysis = {
        "strong_threshold":
            strong_threshold,

        "weak_threshold":
            weak_threshold,

        "classified_windows":
            classified_windows,

        "blocks":
            energy_blocks,

        "num_strong_blocks":
            len(strong_blocks),

        "num_medium_blocks":
            len(medium_blocks),

        "num_weak_blocks":
            len(weak_blocks)
    }

    return energy_block_analysis

# ============================================
# SECTION INTELLIGENCE
# ============================================

def analyze_sections(
    audio_info,
    energy_block_analysis,
    energy_window_analysis
):
    """
    Infer heuristic structural regions from the
    track's energy shape.

    These are energy-based interpretations,
    not semantic section labels.
    """

    song_duration_sec = audio_info[
        "duration_sec"
    ]

    blocks = energy_block_analysis[
        "blocks"
    ]

    strong_blocks = [
        block
        for block in blocks
        if block["label"] == "strong"
    ]

    weak_blocks = [
        block
        for block in blocks
        if block["label"] == "weak"
    ]


    # ----------------------------------------
    # 1. Intro
    # ----------------------------------------

    first_block = (
        blocks[0]
        if blocks
        else None
    )

    if first_block:

        intro_length_sec = float(
            first_block["end_sec"]
            - first_block["start_sec"]
        )

        intro_energy_label = (
            first_block["label"]
        )

    else:

        intro_length_sec = 0.0
        intro_energy_label = "unknown"


    if intro_energy_label == "weak":

        intro_character = "restrained"

    elif intro_energy_label == "medium":

        intro_character = "moderately active"

    else:

        intro_character = "immediately strong"


    # ----------------------------------------
    # 2. Breakdown candidate
    # ----------------------------------------

    candidate_breakdowns = []

    for block in weak_blocks:

        starts_late_enough = (
            block["start_sec"]
            >= 0.15 * song_duration_sec
        )

        ends_early_enough = (
            block["end_sec"]
            <= 0.95 * song_duration_sec
        )

        long_enough = (
            block["duration_sec"]
            >= 15
        )

        if (
            starts_late_enough
            and ends_early_enough
            and long_enough
        ):

            candidate_breakdowns.append(
                block
            )


    if candidate_breakdowns:

        breakdown_block = max(
            candidate_breakdowns,
            key=lambda item:
                item["duration_sec"]
        )

        breakdown_detected = True

        breakdown_start_sec = float(
            breakdown_block["start_sec"]
        )

        breakdown_end_sec = float(
            breakdown_block["end_sec"]
        )

        breakdown_description = (
            f"{breakdown_start_sec:.1f}s–"
            f"{breakdown_end_sec:.1f}s "
            f"({breakdown_block['duration_sec']:.1f}s "
            f"weak-energy drop)"
        )

    else:

        breakdown_detected = False
        breakdown_start_sec = None
        breakdown_end_sec = None

        breakdown_description = (
            "No major breakdown detected"
        )


    # ----------------------------------------
    # 3. Climax zone
    # ----------------------------------------

    top_windows = (
        energy_window_analysis[
            "top_5_windows"
        ]
    )

    strongest_window = (
        energy_window_analysis[
            "strongest_window"
        ]
    )


    if strongest_window:

        climax_center = (
            strongest_window["start_sec"]
            + strongest_window["end_sec"]
        ) / 2


        nearby_peak_windows = [
            window
            for window in top_windows
            if abs(
                (
                    (
                        window["start_sec"]
                        + window["end_sec"]
                    ) / 2
                )
                - climax_center
            ) <= 15
        ]


        climax_start_sec = float(
            min(
                window["start_sec"]
                for window
                in nearby_peak_windows
            )
        )

        climax_end_sec = float(
            max(
                window["end_sec"]
                for window
                in nearby_peak_windows
            )
        )

        climax_description = (
            f"{climax_start_sec:.1f}s–"
            f"{climax_end_sec:.1f}s"
        )

    else:

        climax_start_sec = None
        climax_end_sec = None

        climax_description = (
            "No clear climax zone detected"
        )


    # ----------------------------------------
    # 4. Ending
    # ----------------------------------------

    last_block = (
        blocks[-1]
        if blocks
        else None
    )


    if last_block:

        ending_energy_label = (
            last_block["label"]
        )

        if ending_energy_label == "weak":

            ending_type = (
                "low-energy resolution"
            )

        elif ending_energy_label == "medium":

            ending_type = (
                "controlled resolution"
            )

        else:

            ending_type = (
                "strong-impact ending"
            )

    else:

        ending_energy_label = "unknown"
        ending_type = "unknown"


    # ----------------------------------------
    # Structured output
    # ----------------------------------------

    section_intelligence = {

        "intro": {
            "length_sec":
                float(intro_length_sec),

            "energy_label":
                intro_energy_label,

            "character":
                intro_character
        },

        "breakdown": {
            "detected":
                breakdown_detected,

            "start_sec":
                breakdown_start_sec,

            "end_sec":
                breakdown_end_sec,

            "description":
                breakdown_description
        },

        "climax": {
            "start_sec":
                climax_start_sec,

            "end_sec":
                climax_end_sec,

            "description":
                climax_description
        },

        "ending": {
            "energy_label":
                ending_energy_label,

            "type":
                ending_type
        }
    }

    return section_intelligence

# ============================================
# GEMINI LYRICS TRANSCRIPTION
# ============================================

def transcribe_lyrics(
    file_path,
    gemini_client,
    model_name="gemini-3.7-flash"
):
    """
    Transcribe sung/spoken lyrics using Gemini.

    Returns a MuseMirror-compatible transcription
    object with lyric lines and approximate timestamps.
    """

    # ----------------------------------------
    # Upload audio to Gemini
    # ----------------------------------------

    audio_file = gemini_client.files.upload(
        file=file_path
    )


    # ----------------------------------------
    # Structured response schema
    # ----------------------------------------

    transcription_schema = {
        "type": "OBJECT",

        "properties": {

            "detected_language": {
                "type": "STRING"
            },

            "segments": {
                "type": "ARRAY",

                "items": {
                    "type": "OBJECT",

                    "properties": {

                        "start_sec": {
                            "type": "NUMBER"
                        },

                        "end_sec": {
                            "type": "NUMBER"
                        },

                        "text": {
                            "type": "STRING"
                        }
                    },

                    "required": [
                        "start_sec",
                        "end_sec",
                        "text"
                    ]
                }
            }
        },

        "required": [
            "detected_language",
            "segments"
        ]
    }


    # ----------------------------------------
    # Transcription prompt
    # ----------------------------------------

    transcription_prompt = """
    Transcribe the sung or spoken lyrics in this song.

    Rules:

    1. Transcribe only words that are actually audible.
    2. Preserve the wording exactly as heard.
    3. Do not rewrite lyrics for grammar or style.
    4. Preserve repeated lyrics.
    5. If something is genuinely unclear, write [unclear].
    6. Do not invent lyrics.
    7. Ignore purely instrumental sections.
    8. Break the transcription into natural lyric lines.
    9. Give an approximate start and end time in seconds
       for each lyric line.
    10. Detect the primary language of the vocals.

    The timestamps are approximate and must not be treated
    as exact musical ground truth.
    """


    # ----------------------------------------
    # Run Gemini
    # ----------------------------------------

    fallback_model = "gemini-3.6-flash"

    transient_error_terms = (
        "503",
        "unavailable",
        "high demand",
        "429",
        "resource_exhausted",
        "resource exhausted"
    )

    model_used = model_name
    response = None
    primary_error = None


    # ----------------------------------------
    # Try primary model twice
    # ----------------------------------------

    for attempt in range(2):

        try:

            response = gemini_client.models.generate_content(

                model=model_name,

                contents=[
                    audio_file,
                    transcription_prompt
                ],

                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=transcription_schema
                )
            )

            model_used = model_name

            break


        except Exception as exc:

            primary_error = exc

            error_text = str(
                exc
            ).lower()

            is_transient = any(
                term in error_text
                for term in transient_error_terms
            )


            # Non-temporary errors should not be silently
            # disguised as model-capacity problems.

            if not is_transient:
                raise


            # Retry the primary model once.

            if attempt == 0:

                time.sleep(
                    1
                )


    # ----------------------------------------
    # Fall back if primary stayed unavailable
    # ----------------------------------------

    if response is None:

        try:

            response = gemini_client.models.generate_content(

                model=fallback_model,

                contents=[
                    audio_file,
                    transcription_prompt
                ],

                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=transcription_schema
                )
            )

            model_used = fallback_model


        except Exception as fallback_error:

            raise RuntimeError(
                "MuseMirror could not transcribe the lyrics "
                "because both Gemini transcription models "
                "are temporarily unavailable. "
                "Please try again shortly."
            ) from fallback_error


    # ----------------------------------------
    # Parse Gemini response
    # ----------------------------------------

    gemini_transcription = json.loads(
        response.text
    )

    raw_segments = gemini_transcription.get(
        "segments",
        []
    )


    transcript_segments = []
    transcript_lines = []


    for segment in raw_segments:

        text = segment.get(
            "text",
            ""
        ).strip()

        start_sec = float(
            segment.get(
                "start_sec",
                0.0
            )
        )

        end_sec = float(
            segment.get(
                "end_sec",
                start_sec
            )
        )


        # Prevent invalid negative duration
        if end_sec < start_sec:
            end_sec = start_sec


        if text:

            transcript_segments.append({
                "start_sec": start_sec,
                "end_sec": end_sec,

                "duration_sec":
                    end_sec - start_sec,

                "text": text
            })

            transcript_lines.append(
                text
            )


    # ----------------------------------------
    # MuseMirror transcription object
    # ----------------------------------------

    transcription_analysis = {

        "model_used":
            model_used,

        "provider":
            "Google Gemini",

        "detected_language":
            gemini_transcription.get(
                "detected_language",
                "unknown"
            ),

        "num_segments":
            len(transcript_segments),

        "num_lines":
            len(transcript_lines),

        "lines":
            transcript_lines,

        "segments":
            transcript_segments,

        "full_text":
            "\n".join(
                transcript_lines
            ).strip(),

        "timestamps_are_approximate":
            True
    }


    return transcription_analysis

# ============================================
# LYRICS INTELLIGENCE
# ============================================

def analyze_lyrics(transcription_analysis):
    """
    Build lightweight lyrics/transcription intelligence
    from Gemini's draft transcription.

    Confidence is only a heuristic proxy based on
    explicit [unclear] markers — not Gemini confidence.
    """

    lines = transcription_analysis.get(
        "lines",
        []
    )

    segments = transcription_analysis.get(
        "segments",
        []
    )


    # ----------------------------------------
    # Basic text statistics
    # ----------------------------------------

    num_lines = len(lines)

    word_counts = [
        len(line.split())
        for line in lines
    ]

    total_words = sum(
        word_counts
    )

    avg_words_per_line = (
        total_words /
        (num_lines + 1e-10)
    )


    # ----------------------------------------
    # Approximate segment timing statistics
    # ----------------------------------------

    segment_durations = [
        segment.get(
            "duration_sec",
            0.0
        )
        for segment in segments
    ]


    avg_segment_duration_sec = (
        float(
            np.mean(segment_durations)
        )
        if segment_durations
        else 0.0
    )


    median_segment_duration_sec = (
        float(
            np.median(segment_durations)
        )
        if segment_durations
        else 0.0
    )


    # ----------------------------------------
    # Approximate gaps
    # ----------------------------------------

    segment_gaps = []

    for i in range(
        1,
        len(segments)
    ):

        previous_end = segments[
            i - 1
        ]["end_sec"]

        current_start = segments[
            i
        ]["start_sec"]

        gap = max(
            0.0,
            current_start - previous_end
        )

        segment_gaps.append(
            gap
        )


    avg_gap_sec = (
        float(np.mean(segment_gaps))
        if segment_gaps
        else 0.0
    )

    max_gap_sec = (
        float(np.max(segment_gaps))
        if segment_gaps
        else 0.0
    )

    num_long_gaps = int(
        sum(
            gap > 1.5
            for gap in segment_gaps
        )
    )


    # ----------------------------------------
    # Lyric density
    # ----------------------------------------

    if avg_words_per_line > 8:

        lyric_density_label = "dense"

    elif avg_words_per_line > 4:

        lyric_density_label = "moderate"

    else:

        lyric_density_label = "sparse"


    # ----------------------------------------
    # Explicit unclear-line detection
    # ----------------------------------------

    unclear_lines = [
        line
        for line in lines
        if "[unclear]" in line.lower()
    ]

    num_unclear_lines = len(
        unclear_lines
    )

    unclear_ratio = (
        num_unclear_lines /
        num_lines
        if num_lines
        else 0.0
    )


    # ----------------------------------------
    # Heuristic confidence proxy
    # NOT true Gemini confidence
    # ----------------------------------------

    if unclear_ratio == 0:

        transcription_confidence_proxy = (
            "moderate_to_high"
        )

        confidence_note = (
            "No lines were explicitly marked unclear, "
            "but the transcription still requires "
            "creator verification."
        )

    elif unclear_ratio <= 0.15:

        transcription_confidence_proxy = (
            "moderate"
        )

        confidence_note = (
            "Most lines appear usable, but a few "
            "phrases were explicitly marked unclear "
            "and should be reviewed."
        )

    else:

        transcription_confidence_proxy = (
            "low_to_moderate"
        )

        confidence_note = (
            "Several lines were explicitly marked "
            "unclear, so creator review is especially "
            "important before critique."
        )


    # ----------------------------------------
    # Human verification state
    # ----------------------------------------

    lyrics_verification = {
        "status": "pending_user_review",
        "verified": False
    }


    # ----------------------------------------
    # Structured output
    # ----------------------------------------

    transcription_intelligence = {

        "num_lines":
            int(num_lines),

        "total_words":
            int(total_words),

        "avg_words_per_line":
            float(avg_words_per_line),

        "avg_segment_duration_sec":
            float(
                avg_segment_duration_sec
            ),

        "median_segment_duration_sec":
            float(
                median_segment_duration_sec
            ),

        "avg_gap_sec":
            float(avg_gap_sec),

        "max_gap_sec":
            float(max_gap_sec),

        "num_long_gaps":
            int(num_long_gaps),

        "lyric_density_label":
            lyric_density_label,

        "num_unclear_lines":
            int(num_unclear_lines),

        "unclear_ratio":
            float(unclear_ratio),

        "transcription_confidence_proxy":
            transcription_confidence_proxy,

        "confidence_note":
            confidence_note,

        "verification_status":
            lyrics_verification["status"]
    }


    return (
        transcription_intelligence,
        lyrics_verification
    )

# ============================================
# OBSERVATIONS ENGINE
# ============================================

def build_observations(
    tempo_summary,
    energy_profile,
    transcription_intelligence,
    section_intelligence,
    energy_block_analysis,
    energy_window_analysis,
    audio_info
):
    """
    Convert MuseMirror's technical analysis into
    grounded, human-readable observations.

    These observations are evidence for the later
    Gemini Vibe Check — not final artistic judgments.
    """

    observations = []


    # ----------------------------------------
    # Pull required values
    # ----------------------------------------

    tempo_raw_bpm = tempo_summary[
        "tempo_raw_bpm"
    ]

    tempo_adjusted_bpm = tempo_summary[
        "tempo_adjusted_bpm"
    ]

    tempo_mode = tempo_summary[
        "tempo_mode"
    ]


    rms_range = energy_profile[
        "rms_range"
    ]

    energy_variation_score = energy_profile[
        "energy_variation_score"
    ]

    dynamic_range_class = energy_profile[
        "dynamic_range_class"
    ]

    climax_strength_score = energy_profile[
        "climax_strength_score"
    ]

    crest_factor_proxy = energy_profile[
        "crest_factor_proxy"
    ]


    num_lines = transcription_intelligence[
        "num_lines"
    ]

    lyric_density_label = transcription_intelligence[
        "lyric_density_label"
    ]

    confidence_proxy = transcription_intelligence[
        "transcription_confidence_proxy"
    ]


    intro_info = section_intelligence[
        "intro"
    ]

    breakdown_info = section_intelligence[
        "breakdown"
    ]

    climax_info = section_intelligence[
        "climax"
    ]

    ending_info = section_intelligence[
        "ending"
    ]


    num_strong_blocks = energy_block_analysis[
        "num_strong_blocks"
    ]

    num_medium_blocks = energy_block_analysis[
        "num_medium_blocks"
    ]

    num_weak_blocks = energy_block_analysis[
        "num_weak_blocks"
    ]


    strongest_window = energy_window_analysis[
        "strongest_window"
    ]

    song_duration_sec = audio_info[
        "duration_sec"
    ]


    # ----------------------------------------
    # 1. Tempo observation
    # ----------------------------------------

    if tempo_mode == "double_time":

        observations.append(
            f"The beat tracker returned {tempo_raw_bpm:.2f} BPM, "
            f"while MuseMirror selected {tempo_adjusted_bpm:.2f} BPM "
            f"as the more natural perceived pulse. The raw reading "
            f"is roughly double the selected pulse."
        )

    elif tempo_mode == "half_time":

        observations.append(
            f"The beat tracker returned {tempo_raw_bpm:.2f} BPM, "
            f"while MuseMirror selected {tempo_adjusted_bpm:.2f} BPM "
            f"as the more natural perceived pulse. The raw reading "
            f"is roughly half the selected pulse."
        )

    else:

        observations.append(
            f"The detected and perceived pulse align around "
            f"{tempo_adjusted_bpm:.2f} BPM."
        )


    # ----------------------------------------
    # 2. Dynamic contrast observation
    # ----------------------------------------

    if dynamic_range_class == "high dynamic":

        observations.append(
            f"The track shows strong contrast between quieter "
            f"and higher-energy moments, with an RMS range of "
            f"{rms_range:.3f}."
        )

    elif dynamic_range_class == "moderate dynamic":

        observations.append(
            f"The track shows noticeable energy movement across "
            f"the timeline, with an RMS range of "
            f"{rms_range:.3f}."
        )

    else:

        observations.append(
            f"The track maintains a comparatively controlled "
            f"energy profile, with an RMS range of "
            f"{rms_range:.3f}."
        )


    # ----------------------------------------
    # 3. Energy variation observation
    # ----------------------------------------

    if energy_variation_score > 0.25:

        observations.append(
            f"The energy variation score is "
            f"{energy_variation_score:.3f}, showing substantial "
            f"movement between lower- and higher-energy moments."
        )

    else:

        observations.append(
            f"The energy variation score is "
            f"{energy_variation_score:.3f}, suggesting a more "
            f"consistent overall energy shape."
        )


    # ----------------------------------------
    # 4. Climax strength observation
    # ----------------------------------------

    if climax_strength_score > 2.0:

        observations.append(
            f"The strongest local energy peak is substantially "
            f"above the track's average level "
            f"(climax strength score = "
            f"{climax_strength_score:.2f})."
        )

    else:

        observations.append(
            f"The strongest local energy peak rises above the "
            f"average level, but not by an extreme margin "
            f"(climax strength score = "
            f"{climax_strength_score:.2f})."
        )


    # ----------------------------------------
    # 5. Peak-to-average character
    # ----------------------------------------

    if crest_factor_proxy > 8:

        observations.append(
            f"The signal retains pronounced peaks relative to "
            f"its average energy "
            f"(crest-factor proxy = "
            f"{crest_factor_proxy:.2f})."
        )

    elif crest_factor_proxy > 5:

        observations.append(
            f"The signal shows a moderate separation between "
            f"peaks and average energy "
            f"(crest-factor proxy = "
            f"{crest_factor_proxy:.2f})."
        )

    else:

        observations.append(
            f"The signal shows relatively limited separation "
            f"between peaks and average energy "
            f"(crest-factor proxy = "
            f"{crest_factor_proxy:.2f})."
        )


    # ----------------------------------------
    # 6. Intro observation
    # ----------------------------------------

    observations.append(
        f"The opening energy block lasts about "
        f"{intro_info['length_sec']:.1f} seconds and is "
        f"classified as {intro_info['character']}."
    )


    # ----------------------------------------
    # 7. Breakdown observation
    # ----------------------------------------

    if breakdown_info["detected"]:

        observations.append(
            f"A sustained lower-energy region appears around "
            f"{breakdown_info['description']}. This may function "
            f"as a breakdown, reset, or structural pullback."
        )

    else:

        observations.append(
            "The energy analysis does not detect a major "
            "sustained breakdown region."
        )


    # ----------------------------------------
    # 8. Climax location observation
    # ----------------------------------------

    if (
        climax_info["start_sec"] is not None
        and strongest_window is not None
    ):

        peak_midpoint = (
            strongest_window["start_sec"]
            + strongest_window["end_sec"]
        ) / 2

        peak_ratio = (
            peak_midpoint /
            (song_duration_sec + 1e-10)
        )

        if peak_ratio < 0.33:
            peak_position_desc = "early"

        elif peak_ratio < 0.66:
            peak_position_desc = (
                "in the middle portion"
            )

        else:
            peak_position_desc = "late"

        observations.append(
            f"The main energy climax appears around "
            f"{climax_info['description']}, placing the "
            f"highest local impact {peak_position_desc} "
            f"in the track."
        )


    # ----------------------------------------
    # 9. Ending observation
    # ----------------------------------------

    observations.append(
        f"The final energy region is classified as a "
        f"{ending_info['type']}."
    )


    # ----------------------------------------
    # 10. Energy block distribution
    # ----------------------------------------

    observations.append(
        f"The energy map contains "
        f"{num_strong_blocks} strong block(s), "
        f"{num_medium_blocks} medium block(s), and "
        f"{num_weak_blocks} weak block(s)."
    )


    # ----------------------------------------
    # 11. Lyric density observation
    # ----------------------------------------

    if lyric_density_label == "dense":

        observations.append(
            f"The draft transcription contains dense lyrical "
            f"phrasing across {num_lines} lines."
        )

    elif lyric_density_label == "moderate":

        observations.append(
            f"The draft transcription contains moderate "
            f"lyrical density across {num_lines} lines."
        )

    else:

        observations.append(
            f"The draft transcription contains relatively "
            f"sparse lyrical phrasing across "
            f"{num_lines} lines."
        )


    # ----------------------------------------
    # 12. Transcription reliability proxy
    # ----------------------------------------

    observations.append(
        f"The transcription confidence proxy is "
        f"{confidence_proxy.replace('_', ' ')}. "
        f"This is only a heuristic based on explicit unclear "
        f"markers, so the creator should verify the lyrics "
        f"before the Vibe Check."
    )


    return observations

# ============================================
# COMPLETE AUDIO ANALYSIS PIPELINE
# ============================================

def analyze_audio(file_path):
    """
    Run MuseMirror's complete deterministic
    audio-analysis pipeline.

    This function handles:
    - audio loading
    - tempo
    - core audio features
    - MFCC + chroma
    - energy profile
    - windowed energy
    - energy block classification
    - section intelligence

    Gemini transcription and the Vibe Check
    are handled separately.
    """

    # ----------------------------------------
    # 1. Load audio
    # ----------------------------------------

    y, sr, time_axis, audio_info = load_audio(
        file_path
    )


    # ----------------------------------------
    # 2. Tempo analysis
    # ----------------------------------------

    tempo_summary = analyze_tempo(
        y,
        sr
    )


    # ----------------------------------------
    # 3. Core audio features
    # ----------------------------------------

    core_features, frame_features = (
        extract_core_features(
            y,
            sr
        )
    )


    # ----------------------------------------
    # 4. Timbre + harmonic features
    # ----------------------------------------

    (
        timbre_harmonic_analysis,
        timbre_raw
    ) = extract_timbre_harmonic_features(
        y,
        sr
    )


    # ----------------------------------------
    # 5. Energy profile
    # ----------------------------------------

    energy_profile = analyze_energy_profile(
        frame_features,
        audio_info
    )


    # ----------------------------------------
    # 6. Windowed energy analysis
    # ----------------------------------------

    energy_window_analysis = (
        analyze_energy_windows(
            y,
            sr
        )
    )


    # ----------------------------------------
    # 7. Energy block classification
    # ----------------------------------------

    energy_block_analysis = (
        classify_energy_blocks(
            energy_window_analysis
        )
    )


    # ----------------------------------------
    # 8. Section intelligence
    # ----------------------------------------

    section_intelligence = analyze_sections(
        audio_info,
        energy_block_analysis,
        energy_window_analysis
    )


    # ----------------------------------------
    # Structured production result
    # ----------------------------------------

    analysis_result = {

        "audio_info":
            audio_info,

        "rhythm":
            tempo_summary,

        "core_features":
            core_features,

        "timbre_harmonic":
            timbre_harmonic_analysis,

        "energy": {

            "profile":
                energy_profile,

            "windows":
                energy_window_analysis,

            "blocks":
                energy_block_analysis
        },

        "structure":
            section_intelligence
    }


    # ----------------------------------------
    # Raw data for Streamlit visuals
    # ----------------------------------------

    visual_data = {

        "waveform":
            y,

        "sample_rate":
            sr,

        "time_axis":
            time_axis,

        "frame_features":
            frame_features,

        "timbre_raw":
            timbre_raw
    }


    return analysis_result, visual_data

# ============================================
# VIBE CHECK GROUNDING VALIDATOR
# ============================================

def validate_vibe_check_grounding(vibe_check):
    """
    Check Gemini's critique for claims that MuseMirror
    does not have enough evidence to support.

    Raises a ValueError if a grounding violation is found.
    """

    # ----------------------------------------
    # Combine all generated feedback
    # ----------------------------------------

    all_text_parts = []

    all_text_parts.extend(
        vibe_check.get(
            "whats_hitting",
            []
        )
    )

    all_text_parts.extend(
        vibe_check.get(
            "needs_a_little_love",
            []
        )
    )

    all_text_parts.extend(
        vibe_check.get(
            "studio_moves",
            []
        )
    )

    all_text_parts.append(
        vibe_check.get(
            "big_picture",
            ""
        )
    )

    full_text = " ".join(
        all_text_parts
    ).lower()


    # ----------------------------------------
    # Forbidden tempo interpretations
    # ----------------------------------------

    forbidden_tempo_phrases = [
        "double-time elements",
        "double time elements",
        "half-time elements",
        "half time elements",
        "double-time feel",
        "double time feel",
        "half-time feel",
        "half time feel",
        "double-time rhythm",
        "double time rhythm",
        "half-time rhythm",
        "half time rhythm"
    ]


    for phrase in forbidden_tempo_phrases:

        if phrase in full_text:

            raise ValueError(
                "Vibe Check grounding violation: "
                f"unsupported tempo interpretation detected: "
                f"'{phrase}'."
            )


    # ----------------------------------------
    # Unsupported instrument references
    # ----------------------------------------

    unsupported_instruments = [
        "drum",
        "drums",
        "percussion",
        "guitar",
        "guitars",
        "bass",
        "synth",
        "synths",
        "piano",
        "keyboard",
        "keyboards",
        "strings",
        "violin",
        "cello",
        "kick",
        "snare",
        "hi-hat",
        "hi-hats",
        "hihat",
        "hihats",
        "cymbal",
        "cymbals"
    ]


    for instrument in unsupported_instruments:

        pattern = rf"\b{re.escape(instrument)}\b"

        if re.search(
            pattern,
            full_text
        ):

            raise ValueError(
                "Vibe Check grounding violation: "
                f"unsupported instrument reference detected: "
                f"'{instrument}'."
            )


    # ----------------------------------------
    # Passed validation
    # ----------------------------------------

    return True

# ============================================
# GEMINI VIBE CHECK
# ============================================

def run_vibe_check(
    analysis_result,
    transcription_intelligence,
    verified_lyrics,
    observations,
    gemini_client,
    model_name="gemini-3.7-flash",
    fallback_model_name="gemini-3.6-flash",
    max_retries=2
):
    """
    Generate MuseMirror's creator-side Vibe Check
    using verified lyrics and grounded technical evidence.
    """

    # ----------------------------------------
    # Safety check
    # ----------------------------------------

    if not verified_lyrics or not verified_lyrics.strip():
        raise ValueError(
            "Verified lyrics are required before running the Vibe Check."
        )


    # ----------------------------------------
    # Pull analysis layers
    # ----------------------------------------

    tempo_summary = analysis_result["rhythm"]

    energy_profile = analysis_result[
        "energy"
    ]["profile"]

    energy_block_analysis = analysis_result[
        "energy"
    ]["blocks"]

    section_intelligence = analysis_result[
        "structure"
    ]


    # ----------------------------------------
    # Build grounded critique evidence
    # ----------------------------------------

    critique_evidence = {

        "tempo": {
            "perceived_bpm":
                tempo_summary["tempo_adjusted_bpm"],

            "raw_tracker_bpm":
                tempo_summary["tempo_raw_bpm"],

            "tempo_mode":
                tempo_summary["tempo_mode"],

            "tempo_note":
                tempo_summary["tempo_mode_note"]
        },


        "energy": {
            "dynamic_range_class":
                energy_profile["dynamic_range_class"],

            "energy_variation_score":
                energy_profile["energy_variation_score"],

            "climax_strength_score":
                energy_profile["climax_strength_score"],

            "crest_factor_proxy":
                energy_profile["crest_factor_proxy"]
        },


        "structure":
            section_intelligence,


        "energy_blocks": {
            "strong":
                energy_block_analysis["num_strong_blocks"],

            "medium":
                energy_block_analysis["num_medium_blocks"],

            "weak":
                energy_block_analysis["num_weak_blocks"]
        },


        "lyrics": {
            "verified_lyrics":
                verified_lyrics,

            "lyric_density":
                transcription_intelligence[
                    "lyric_density_label"
                ]
        },


        "observations":
            observations
    }


    # ----------------------------------------
    # Locked MuseMirror V2 prompt
    # ----------------------------------------

    vibe_check_prompt = f"""
You are MuseMirror's creator-side studio companion.

Talk to the artist like a perceptive, encouraging friend sitting beside
them in the studio — someone who genuinely enjoys discovering what works
in their music and wants to help the track become even stronger.

Your feedback should make the artist excited to keep creating.

TONE:
- Warm, energetic, curious and supportive.
- Celebrate specific things that genuinely work.
- Sound human and conversational, not academic or clinical.
- Never talk down to the creator.
- Never make the artist feel that their song is "bad" or has failed.
- Do not use empty praise. Every compliment must be supported by evidence.
- Frame weaknesses as opportunities, experiments or places with more potential.
- Prefer language such as:
  "You could try..."
  "This might hit even harder if..."
  "Worth experimenting with..."
  "There's an opportunity here to..."
- Avoid harsh language such as:
  "bad", "poor", "failure", "wrong", "problem", "weak songwriting".
Be supportive, but candid.

MuseMirror should feel like a trusted musician friend:
excited when something genuinely works,
comfortable pointing out what is holding the track back,
and always offering a constructive way forward.

Do not soften criticism so much that the insight disappears.

IMPORTANT:
Use ONLY the evidence supplied below.

When discussing tempo:
- Treat the adjusted BPM as the perceived pulse.
- Treat the raw BPM only as the beat tracker's original reading.
- The tempo_mode field describes how MuseMirror interpreted the
  beat tracker's numerical reading. It does NOT describe the song's
  rhythmic arrangement.
- A tempo_mode value such as "double_time" means only that the raw
  tracker BPM was approximately twice the selected perceived pulse.
- A tempo_mode value such as "half_time" means only that the raw
  tracker BPM was approximately half the selected perceived pulse.
- Never describe this as:
  "double-time elements",
  "half-time elements",
  "double-time feel",
  "half-time feel",
  or evidence of faster/slower rhythmic subdivisions.
- Do not recommend rhythmic subdivisions based only on the relationship
  between the raw BPM and adjusted BPM.

INSTRUMENTATION GROUNDING:
- MuseMirror has NOT identified individual instruments unless they are
  explicitly named in the supplied evidence.
- Therefore, do not mention or recommend changes to specific instruments
  such as drums, percussion, guitar, bass, synth, piano, strings,
  cymbals, kick, snare or hi-hats unless that instrument is explicitly
  present in the evidence.
- Do not infer instrumentation from energy, tempo, MFCC, chroma,
  crest factor or other audio-analysis metrics.
- When instrumentation is unknown, keep suggestions at the evidence
  level using language such as:
  "rhythmic activity",
  "energy",
  "arrangement density",
  "section contrast",
  "pacing",
  or "vocal phrasing",
  only when those ideas are supported by the evidence.

Never guarantee that a suggestion will improve the song.
Use language such as "could", "might", "worth trying",
or "may help" for creative recommendations.

Do not invent:
- instruments that are not explicitly known
- production techniques unsupported by the evidence
- emotions purely from tempo
- genre
- key or chord progression
- vocal characteristics that are unsupported
- mix problems that cannot be supported by the evidence

The audio-analysis metrics are clues and heuristics, not absolute musical truth.

Translate technical measurements into natural musical language.
Use exact numbers only when they genuinely help the artist understand
something; the technical dashboard already displays the raw metrics.


WHAT'S HITTING
- Exactly 5 points.
- These should feel enthusiastic.
- Tell the artist what MuseMirror genuinely liked about the track.
- Explain WHY each quality works.

NEEDS A LITTLE LOVE
- Exactly 3 points.
- Never present these as failures.
- Describe them as areas that could potentially become even stronger.
- Respect the possibility that the creator made these choices intentionally.

STUDIO MOVES
- Exactly 5 practical experiments the artist could try.
- Make them feel playful and optional rather than corrective.
- Encourage experimentation.

BIG PICTURE
- One short paragraph.
- Give a balanced overall assessment of the track.
- Mention:
  1. the strongest thing about the song,
  2. one important tradeoff or limitation,
  3. the main opportunity that could elevate it further.
- Connect pacing, energy, structure and lyrics together.
- Stay warm and encouraging, but do not avoid critique.
- Do not end with generic praise such as
  "I can't wait to hear where you take it" or
  "this is an amazing track."
- End with a concrete creative direction rather than encouragement alone.

Here is the MuseMirror evidence:

{json.dumps(critique_evidence, indent=2)}
"""


    # ----------------------------------------
    # Structured Gemini output schema
    # ----------------------------------------

    vibe_check_schema = {
        "type": "OBJECT",

        "properties": {

            "whats_hitting": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                }
            },

            "needs_a_little_love": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                }
            },

            "studio_moves": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                }
            },

            "big_picture": {
                "type": "STRING"
            }
        },

        "required": [
            "whats_hitting",
            "needs_a_little_love",
            "studio_moves",
            "big_picture"
        ]
    }

    # ----------------------------------------
    # Run Gemini with retry + fallback
    # ----------------------------------------

    # ----------------------------------------
    # Gemini call helper
    # ----------------------------------------

    def call_gemini(
        current_model,
        prompt_text
    ):

        return gemini_client.models.generate_content(

            model=current_model,

            contents=prompt_text,

            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=vibe_check_schema
            )
        )


    # ----------------------------------------
    # Retryable API errors
    # ----------------------------------------

    def is_retryable_error(error):

        error_text = str(error).lower()

        retryable_signals = [
            "503",
            "unavailable",
            "high demand",
            "429",
            "resource_exhausted"
        ]

        return any(
            signal in error_text
            for signal in retryable_signals
        )


    # ----------------------------------------
    # Protected Gemini generation
    # ----------------------------------------

    def generate_with_retry(
        prompt_text,
        primary_model,
        fallback_model=None,
        attempts=2
    ):

        models_to_try = [
            primary_model
        ]

        if (
            fallback_model
            and fallback_model != primary_model
        ):

            models_to_try.append(
                fallback_model
            )


        last_error = None


        for current_model in models_to_try:

            # Primary model gets retries.
            # Fallback gets one attempt.
            current_attempts = (
                attempts
                if current_model == primary_model
                else 1
            )


            for attempt in range(
                1,
                current_attempts + 1
            ):

                try:

                    response = call_gemini(
                        current_model,
                        prompt_text
                    )

                    return (
                        response,
                        current_model
                    )


                except Exception as error:

                    last_error = error


                    if not is_retryable_error(
                        error
                    ):
                        raise


                    if attempt < current_attempts:

                        wait_seconds = (
                            2 ** (attempt - 1)
                        )

                        time.sleep(
                            wait_seconds
                        )


        raise RuntimeError(
            "Gemini is temporarily busy. "
            "MuseMirror couldn't refresh the Vibe Check "
            "right now. Please try again shortly."
        ) from last_error


    # ----------------------------------------
    # Generate initial Vibe Check
    # ----------------------------------------

    response, model_used = generate_with_retry(

        prompt_text=
            vibe_check_prompt,

        primary_model=
            model_name,

        fallback_model=
            fallback_model_name,

        attempts=
            max_retries
    )


    # ----------------------------------------
    # Parse Gemini response
    # ----------------------------------------

    gemini_critique = json.loads(
        response.text
    )


    # ----------------------------------------
    # Grounding validation + one repair attempt
    # ----------------------------------------

    try:

        validate_vibe_check_grounding(
            gemini_critique
        )


    except ValueError as grounding_error:

        correction_prompt = f"""
    You are correcting a MuseMirror Vibe Check that violated
    one or more grounding rules.

    The original MuseMirror instructions and evidence were:

    {vibe_check_prompt}


    The previous response was:

    {json.dumps(gemini_critique, indent=2)}


    The grounding validator detected this issue:

    {str(grounding_error)}


    CORRECTION RULES:

    - Rewrite the complete Vibe Check.
    - Keep the same overall insight wherever it is supported.
    - Remove or replace only unsupported claims.
    - Do not invent instruments.
    - Do not infer instrumentation from audio metrics.
    - Do not describe tempo_mode as evidence of a musical
    half-time or double-time arrangement.
    - Raw BPM is only the beat tracker's original numerical reading.
    - Adjusted BPM is the selected perceived pulse.
    - Do not infer rhythmic subdivisions from the difference
    between raw BPM and adjusted BPM.
    - Use only the MuseMirror evidence supplied above.

    The corrected response must still contain:

    - Exactly 5 What's Hitting points.
    - Exactly 3 Needs a Little Love points.
    - Exactly 5 Studio Moves.
    - One short Big Picture paragraph.

    Return only the required structured response.
    """


        corrected_response, repaired_model_used = (
            generate_with_retry(

                prompt_text=
                    correction_prompt,

                primary_model=
                    model_used,

                fallback_model=
                    fallback_model_name,

                attempts=
                    max_retries
            )
        )


        # Track the model that actually produced
        # the final repaired response.
        model_used = repaired_model_used


        gemini_critique = json.loads(
            corrected_response.text
        )


        # ----------------------------------------
        # Validate corrected response again
        # ----------------------------------------

        try:

            validate_vibe_check_grounding(
                gemini_critique
            )

        except ValueError as second_grounding_error:

            raise RuntimeError(
                "MuseMirror generated feedback that could not "
                "be grounded safely in the available audio evidence. "
                "Please try the Vibe Check again."
            ) from second_grounding_error


    # ----------------------------------------
    # Validate required 5 / 3 / 5 format
    # ----------------------------------------

    if len(gemini_critique["whats_hitting"]) != 5:
        raise ValueError(
            "Gemini did not return exactly 5 What's Hitting points."
        )

    if len(gemini_critique["needs_a_little_love"]) != 3:
        raise ValueError(
            "Gemini did not return exactly 3 Needs a Little Love points."
        )

    if len(gemini_critique["studio_moves"]) != 5:
        raise ValueError(
            "Gemini did not return exactly 5 Studio Moves."
        )

    if not gemini_critique["big_picture"].strip():
        raise ValueError(
            "Gemini returned an empty Big Picture."
        )


    # ----------------------------------------
    # MuseMirror compatibility object
    # ----------------------------------------

    critique_report = {

        "strengths":
            gemini_critique["whats_hitting"],

        "risks":
            gemini_critique["needs_a_little_love"],

        "improvements":
            gemini_critique["studio_moves"],

        "big_picture":
            gemini_critique["big_picture"],

        "engine":
            model_used
    }


    # ----------------------------------------
    # Final Vibe Check object for Streamlit
    # ----------------------------------------

    vibe_check = {

        "whats_hitting":
            critique_report["strengths"],

        "needs_a_little_love":
            critique_report["risks"],

        "studio_moves":
            critique_report["improvements"],

        "big_picture":
            critique_report["big_picture"],

        "engine":
            critique_report["engine"]
    }


    return vibe_check