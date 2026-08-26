# ============================================
# MuseMirror AI — Streamlit App
# Visual Shell V2
# ============================================

import html
from pathlib import Path
import streamlit as st

# ============================================
# APP BACKEND IMPORTS
# ============================================

import os
import tempfile
from dotenv import load_dotenv
from google import genai

from musemirror_engine import (
    analyze_audio,
    transcribe_lyrics,
    analyze_lyrics,
    build_observations,
    run_vibe_check
)
from musemirror_runtime import build_gemini_client, MUSEMIRROR_MODEL


# --------------------------------------------
# Page config
# --------------------------------------------

st.set_page_config(
    page_title="MuseMirror AI",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------
# Paths
# --------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
CSS_PATH = PROJECT_ROOT / "styles.css"

# ============================================
# GEMINI CONFIGURATION
# ============================================

load_dotenv(PROJECT_ROOT / ".env")


def get_gemini_api_key():
    """
    Use Streamlit Cloud secrets when deployed,
    otherwise fall back to the local .env file.
    """

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


GEMINI_API_KEY = get_gemini_api_key()

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key not found."
    )
    st.stop()


gemini_client = build_gemini_client(GEMINI_API_KEY)

GEMINI_MODEL = MUSEMIRROR_MODEL


# --------------------------------------------
# Load CSS
# --------------------------------------------

st.html(CSS_PATH)

def render_html(html):
    st.html(html)


# ============================================
# HERO SECTION
# ============================================

col1, col2 = st.columns(
    [1.15, 1],
    gap="large"
)


# --------------------------------------------
# LEFT — Main MuseMirror message
# --------------------------------------------

with col1:

    render_html(
        """
        <div style="padding-top: 1.6rem;">

            <div class="mm-eyebrow">
                ◉ CREATOR-SIDE MUSIC INTELLIGENCE
            </div>

            <div style="height: 1.5rem;"></div>

            <h1>
                Hear what your track
                <br>
                is
                <span class="mm-gradient-text">
                    really doing.
                </span>
            </h1>

            <p class="mm-subtitle">
                MuseMirror listens beneath the surface —
                reading rhythm, energy, structure and lyrics,
                then turning the evidence into feedback
                you can actually use in the studio.
            </p>

        </div>
        """
    )


    # ----------------------------------------
    # Feature chips
    # ----------------------------------------

    st.markdown(
        "<div style='height: 1rem;'></div>",
        unsafe_allow_html=True
    )

    chip_col1, chip_col2, chip_col3 = st.columns(3)

    with chip_col1:

        render_html(
            """
            <div class="mm-mini-chip">
                ⚡ ENERGY MAP
            </div>
            """
        )

    with chip_col2:

        render_html(
            """
            <div class="mm-mini-chip">
                🎙 LYRIC INTEL
            </div>
            """
        )

    with chip_col3:

        render_html(
            """
            <div class="mm-mini-chip">
                🧠 VIBE CHECK
            </div>
            """
        )


# --------------------------------------------
# RIGHT — Music poster / visual identity
# --------------------------------------------

with col2:

    render_html(
        """
        <div class="mm-poster-card">

            <div class="mm-poster-glow mm-glow-1"></div>
            <div class="mm-poster-glow mm-glow-2"></div>
            <div class="mm-poster-glow mm-glow-3"></div>

            <div class="mm-poster-content">

                <div class="mm-poster-kicker">
                    NOW PLAYING IN THE MIRROR
                </div>

                <div class="mm-poster-title">
                    MuseMirror
                </div>

                <div class="mm-poster-subtitle">
                    Rhythm. Energy. Lyrics.
                    <br>
                    One track, reflected differently.
                </div>

                <div class="mm-wave-wrap">

                    <div class="mm-wave-bar short"></div>

                    <div class="mm-wave-bar med"></div>

                    <div class="mm-wave-bar tall"></div>

                    <div class="mm-wave-bar"></div>

                    <div class="mm-wave-bar short"></div>

                    <div class="mm-wave-bar tall"></div>

                    <div class="mm-wave-bar med"></div>

                    <div class="mm-wave-bar short"></div>

                    <div class="mm-wave-bar tall"></div>

                    <div class="mm-wave-bar"></div>

                    <div class="mm-wave-bar med"></div>

                    <div class="mm-wave-bar short"></div>

                    <div class="mm-wave-bar tall"></div>

                    <div class="mm-wave-bar med"></div>

                </div>

            </div>

        </div>
        """
    )


# --------------------------------------------
# Space after hero
# --------------------------------------------

st.markdown(
    "<div style='height: 2rem;'></div>",
    unsafe_allow_html=True
)


# ============================================
# UPLOAD BLOCK
# ============================================

st.markdown(
    """
    <div class="mm-card">
        <div class="mm-step-label">STEP 01</div>
        <div class="mm-section-title">Drop Your Track 🎧</div>
        <div class="mm-section-copy">
            Give MuseMirror something to listen to.
            Upload an MP3 or WAV and let the mirror wake up.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload your track",
    type=["mp3", "wav"],
    label_visibility="collapsed"
)


# ============================================
# POST-UPLOAD PREVIEW
# ============================================

if uploaded_file is not None:
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="mm-card">
            <div class="mm-step-label">TRACK LOADED</div>
            <div class="mm-track-name">{uploaded_file.name}</div>
            <div class="mm-track-copy">
                Cue it up. Your track is ready for the mirror.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    st.audio(uploaded_file)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if st.button("⚡ Read My Song"):

        temp_file_path = None

        try:
            # ----------------------------------------
            # Save uploaded Streamlit file temporarily
            # ----------------------------------------

            file_suffix = Path(
                uploaded_file.name
            ).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=file_suffix
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_file_path = temp_file.name


            # ----------------------------------------
            # 1. Deterministic audio analysis
            # ----------------------------------------

            with st.spinner(
                "Peeking under the hood..."
            ):

                analysis_result, visual_data = (
                    analyze_audio(
                        temp_file_path
                    )
                )


            # ----------------------------------------
            # 2. Gemini lyrics transcription
            # ----------------------------------------

            with st.spinner(
                "Catching the words 🎙️"
            ):

                transcription_analysis = (
                    transcribe_lyrics(
                        temp_file_path,
                        gemini_client,
                        model_name=GEMINI_MODEL
                    )
                )


            # ----------------------------------------
            # 3. Lyrics intelligence
            # ----------------------------------------

            (
                transcription_intelligence,
                lyrics_verification
            ) = analyze_lyrics(
                transcription_analysis
            )


            # ----------------------------------------
            # Store results across Streamlit reruns
            # ----------------------------------------

            st.session_state[
                "analysis_result"
            ] = analysis_result

            st.session_state[
                "visual_data"
            ] = visual_data

            st.session_state[
                "transcription_analysis"
            ] = transcription_analysis

            st.session_state[
                "transcription_intelligence"
            ] = transcription_intelligence

            st.session_state[
                "lyrics_verification"
            ] = lyrics_verification

            st.session_state[
                "edited_lyrics"
            ] = transcription_analysis[
                "full_text"
            ]

            st.session_state[
                "lyrics_editor"
            ] = transcription_analysis[
                "full_text"
            ]

            st.session_state[
                "lyrics_verified"
            ] = False

            st.session_state[
                "vibe_check"
            ] = None


            st.success(
                "Track read successfully ⚡"
            )


        except Exception as error:

            st.error(
                f"MuseMirror hit a snag: {error}"
            )


        finally:

            if (
                temp_file_path
                and os.path.exists(
                    temp_file_path
                )
            ):

                os.remove(
                    temp_file_path
                )

    # ============================================
    # LYRICS REVIEW
    # ============================================

    if "transcription_analysis" in st.session_state:

        st.markdown(
            """
            <div class="mm-step-label">
                LYRICS INTELLIGENCE
            </div>

            <div class="mm-section-title">
                Here's what we heard...
            </div>

            <div class="mm-section-copy">
                Give the transcription a quick check.
                Fix anything MuseMirror misheard before
                we use the lyrics for the Vibe Check.
            </div>
            """,
            unsafe_allow_html=True
        )


        edited_lyrics = st.text_area(
            "Review lyrics",
            key="lyrics_editor",
            height=360,
            label_visibility="collapsed"
        )


        if st.button(
            "✓ Lyrics Look Good",
            use_container_width=True
        ):

            verified_lyrics = (
                edited_lyrics.strip()
            )

            if not verified_lyrics:

                st.warning(
                    "Add or confirm some lyrics before continuing."
                )

            else:

                st.session_state[
                    "edited_lyrics"
                ] = verified_lyrics

                st.session_state[
                    "verified_lyrics"
                ] = verified_lyrics

                st.session_state[
                    "lyrics_verified"
                ] = True

                st.session_state[
                    "lyrics_verification"
                ] = {
                    "status": "verified_by_user",
                    "verified": True
                }

                st.success(
                    "Lyrics locked in ✓"
                )

                st.rerun()

    # ============================================
    # RUN THE VIBE CHECK
    # ============================================

    if st.session_state.get(
        "lyrics_verified",
        False
    ):

        st.markdown(
            """
            <div class="mm-step-label">
                CREATOR FEEDBACK
            </div>

            <div class="mm-section-title">
                Lyrics locked. Let's read the track.
            </div>

            <div class="mm-section-copy">
                MuseMirror will combine the energy,
                pacing, structure and verified lyrics
                into a creator-side studio critique.
            </div>
            """,
            unsafe_allow_html=True
        )


        if st.button(
            "🔥 Run the Vibe Check",
            use_container_width=True
        ):

            try:

                # ----------------------------------------
                # Pull stored analysis
                # ----------------------------------------

                analysis_result = st.session_state[
                    "analysis_result"
                ]

                transcription_intelligence = (
                    st.session_state[
                        "transcription_intelligence"
                    ]
                )

                verified_lyrics = st.session_state[
                    "verified_lyrics"
                ]


                # ----------------------------------------
                # Build grounded observations
                # ----------------------------------------

                observations = build_observations(

                    tempo_summary=
                        analysis_result["rhythm"],

                    energy_profile=
                        analysis_result["energy"][
                            "profile"
                        ],

                    transcription_intelligence=
                        transcription_intelligence,

                    section_intelligence=
                        analysis_result["structure"],

                    energy_block_analysis=
                        analysis_result["energy"][
                            "blocks"
                        ],

                    energy_window_analysis=
                        analysis_result["energy"][
                            "windows"
                        ],

                    audio_info=
                        analysis_result[
                            "audio_info"
                        ]
                )


                # ----------------------------------------
                # Run Gemini creator-side critique
                # ----------------------------------------

                with st.spinner(
                    "Reading the vibe... 🔥"
                ):

                    vibe_check = run_vibe_check(

                        analysis_result=
                            analysis_result,

                        transcription_intelligence=
                            transcription_intelligence,

                        verified_lyrics=
                            verified_lyrics,

                        observations=
                            observations,

                        gemini_client=
                            gemini_client,

                        model_name=
                            GEMINI_MODEL
                    )


                # ----------------------------------------
                # Store results
                # ----------------------------------------

                st.session_state[
                    "observations"
                ] = observations

                st.session_state[
                    "vibe_check"
                ] = vibe_check


                st.success(
                    "Vibe Check complete 🔥"
                )


            except Exception as error:

                st.error(
                    f"Vibe Check hit a snag: {error}"
                )

# ============================================
# TRACK DECLASSIFIED
# ============================================

if st.session_state.get("vibe_check"):

    vibe_check = st.session_state["vibe_check"]
    analysis_result = st.session_state["analysis_result"]


    # --------------------------------------------------------
    # Safe HTML helper
    # --------------------------------------------------------

    def build_vibe_list(items):

        return "".join(
            f"<li>{html.escape(str(item))}</li>"
            for item in items
        )


    whats_hitting_html = build_vibe_list(
        vibe_check["whats_hitting"]
    )

    needs_love_html = build_vibe_list(
        vibe_check["needs_a_little_love"]
    )

    studio_moves_html = build_vibe_list(
        vibe_check["studio_moves"]
    )

    big_picture_html = html.escape(
        vibe_check["big_picture"]
    )


    # --------------------------------------------------------
    # Track fingerprint values
    # --------------------------------------------------------

    perceived_bpm = analysis_result[
        "rhythm"
    ].get(
        "tempo_adjusted_bpm",
        0
    )

    climax_zone = analysis_result[
        "structure"
    ].get(
        "climax",
        {}
    ).get(
        "description",
        "Not detected"
    )

    dynamic_range = analysis_result[
        "energy"
    ][
        "profile"
    ].get(
        "dynamic_range_class",
        "unknown"
    )

    strong_blocks = analysis_result[
        "energy"
    ][
        "blocks"
    ].get(
        "num_strong_blocks",
        0
    )

    medium_blocks = analysis_result[
        "energy"
    ][
        "blocks"
    ].get(
        "num_medium_blocks",
        0
    )

    weak_blocks = analysis_result[
        "energy"
    ][
        "blocks"
    ].get(
        "num_weak_blocks",
        0
    )


    # --------------------------------------------------------
    # Real track energy arc from analyzed RMS frames
    # --------------------------------------------------------

    rms_frames = st.session_state[
        "visual_data"
    ][
        "frame_features"
    ][
        "rms_frames"
    ]

    rms_values = [
        float(value)
        for value in rms_frames
    ]

    num_wave_bars = 256
    sampled_energy = []

    if rms_values:

        total_frames = len(rms_values)

        for index in range(num_wave_bars):

            start = (
                index * total_frames
                // num_wave_bars
            )

            end = (
                (index + 1) * total_frames
                // num_wave_bars
            )

            segment = rms_values[
                start:end
            ]

            if segment:

                sampled_energy.append(
                    sum(segment)
                    / len(segment)
                )

            else:

                sampled_energy.append(
                    0.0
                )


        max_energy = max(
            sampled_energy
        )


        if max_energy > 0:

            waveform_heights = [

                int(
                    18
                    + 82
                    * (
                        energy
                        / max_energy
                    )
                )

                for energy
                in sampled_energy
            ]

        else:

            waveform_heights = (
                [18] * num_wave_bars
            )

    else:

        waveform_heights = (
            [18] * num_wave_bars
        )

    waveform_html = "".join(
        f"""
        <span
            class="mm-wave-bar"
            style="
                --wave-height: {height}%;
                --wave-delay: {index * 0.045}s;
            "
        ></span>
        """
        for index, height
        in enumerate(waveform_heights)
    )
    # MUSEMIRROR_ENERGY_TIMELINE_V2

    duration_sec = float(
        analysis_result[
            "audio_info"
        ][
            "duration_sec"
        ]
    )


    duration_whole_sec = max(
        0,
        int(
            round(
                duration_sec
            )
        )
    )


    timeline_seconds = list(
        range(
            0,
            duration_whole_sec + 1,
            20
        )
    )


    # Always include the real song endpoint.

    if (
        not timeline_seconds
        or timeline_seconds[-1]
        != duration_whole_sec
    ):

        timeline_seconds.append(
            duration_whole_sec
        )


    def format_energy_time(
        total_seconds
    ):

        total_seconds = int(
            total_seconds
        )

        minutes = (
            total_seconds
            // 60
        )

        seconds = (
            total_seconds
            % 60
        )

        return (
            f"{minutes}:"
            f"{seconds:02d}"
        )


    timeline_html = "".join(

        (
            '<div class="mm-energy-tick" '
            'style="left: '
            f'{((second / duration_sec) * 100.0) if duration_sec else 0.0:.6f}'
            '%;">'
            '<span class="mm-energy-tick-mark"></span>'
            '<span class="mm-energy-tick-label">'
            f'{format_energy_time(second)}'
            '</span>'
            '</div>'
        )

        for second
        in timeline_seconds
    )




    # --------------------------------------------------------
    # Render premium Vibe Check
    # --------------------------------------------------------

    render_html(
        f"""
        <div class="mm-declassified-wrap">

            <!-- AMBIENT GRAPHICS -->

            <div class="mm-result-orb mm-result-orb-one"></div>
            <div class="mm-result-orb mm-result-orb-two"></div>
            <div class="mm-result-orb mm-result-orb-three"></div>


            <!-- HEADER -->

            <div class="mm-declassified-header">

                <div class="mm-step-label">
                    MUSEMIRROR VIBE CHECK
                </div>

                <div class="mm-declassified-title-row">

                    <div class="mm-declassified-lock">
                        🔓
                    </div>

                    <div class="mm-section-title mm-declassified-title">
                        TRACK DECLASSIFIED
                    </div>

                </div>

                <div class="mm-section-copy">
                    MuseMirror connected the track's pacing,
                    energy, structure and verified lyrics.
                    Here's the creative fingerprint it found.
                </div>

            </div>


            <!-- DECORATIVE AUDIO VISUALIZER -->

            <div class="mm-result-visualizer">

                <div class="mm-energy-arc-shell">
                <div class="mm-visualizer-copy">

                    <span class="mm-visualizer-dot"></span>

                    YOUR TRACK ENERGY ARC

                </div>

                <div class="mm-waveform">
                    {waveform_html}
                </div>

                    <div class="mm-energy-timeline">
                        {timeline_html}
                    </div>
                </div>

            </div>


            <!-- TRACK FINGERPRINT -->

            <div class="mm-fingerprint-label">
                TRACK FINGERPRINT
            </div>

            <div class="mm-fingerprint-grid">

                <div class="mm-fingerprint-chip">

                    <div class="mm-fingerprint-icon">
                        🥁
                    </div>

                    <div>
                        <div class="mm-fingerprint-value">
                            {perceived_bpm:.0f}
                        </div>

                        <div class="mm-fingerprint-name">
                            PERCEIVED BPM
                        </div>
                    </div>

                </div>


                <div class="mm-fingerprint-chip">

                    <div class="mm-fingerprint-icon">
                        ⚡
                    </div>

                    <div>
                        <div class="mm-fingerprint-value mm-small-value">
                            {html.escape(str(climax_zone))}
                        </div>

                        <div class="mm-fingerprint-name">
                            CLIMAX ZONE
                        </div>
                    </div>

                </div>


                <div class="mm-fingerprint-chip">

                    <div class="mm-fingerprint-icon">
                        📈
                    </div>

                    <div>
                        <div class="mm-fingerprint-value mm-small-value">
                            {html.escape(str(dynamic_range)).upper()}
                        </div>

                        <div class="mm-fingerprint-name">
                            DYNAMIC PROFILE
                        </div>
                    </div>

                </div>


                <div class="mm-fingerprint-chip">

                    <div class="mm-fingerprint-icon">
                        ◉
                    </div>

                    <div>
                        <div class="mm-fingerprint-value">
                            {strong_blocks} · {medium_blocks} · {weak_blocks}
                        </div>

                        <div class="mm-fingerprint-name">
                            STRONG · MID · LOW
                        </div>
                    </div>

                </div>

            </div>


            <!-- DIVIDER -->

            <div class="mm-result-divider">

                <div class="mm-result-divider-line"></div>

                <div class="mm-result-divider-symbol">
                    ✦
                </div>

                <div class="mm-result-divider-line"></div>

            </div>


            <!-- MAIN VIBE CARDS -->

            <div class="mm-vibe-grid">


                <!-- WHAT'S HITTING -->

                <div class="mm-vibe-card mm-vibe-card-hit">

                    <div class="mm-card-glow mm-card-glow-hit"></div>

                    <div class="mm-vibe-badge mm-badge-hit">
                        🔥 SIGNAL DETECTED
                    </div>

                    <div class="mm-vibe-card-title">
                        What's Hitting
                    </div>

                    <div class="mm-card-mini-line"></div>

                    <ul class="mm-vibe-list">
                        {whats_hitting_html}
                    </ul>

                </div>


                <!-- NEEDS LOVE -->

                <div class="mm-vibe-card mm-vibe-card-love">

                    <div class="mm-card-glow mm-card-glow-love"></div>

                    <div class="mm-vibe-badge mm-badge-love">
                        💛 GROWTH ZONE
                    </div>

                    <div class="mm-vibe-card-title">
                        Needs a Little Love
                    </div>

                    <div class="mm-card-mini-line"></div>

                    <ul class="mm-vibe-list">
                        {needs_love_html}
                    </ul>

                </div>


                <!-- STUDIO MOVES -->

                <div
                    class="mm-vibe-card
                           mm-vibe-card-moves
                           mm-studio-moves-wide"
                >

                    <div class="mm-card-glow mm-card-glow-moves"></div>

                    <div class="mm-vibe-badge mm-badge-moves">
                        🛠 TRY THIS NEXT
                    </div>

                    <div class="mm-vibe-card-title">
                        Studio Moves
                    </div>

                    <div class="mm-card-mini-line"></div>

                    <ul class="mm-vibe-list mm-studio-list">
                        {studio_moves_html}
                    </ul>

                </div>

            </div>


            <!-- BIG PICTURE -->

            <div class="mm-big-picture-card">

                <div class="mm-big-picture-orb"></div>

                <div class="mm-big-picture-title">
                    💭 FINAL REFLECTION
                </div>

                <div class="mm-big-picture-heading">
                    The Big Picture
                </div>

                <div class="mm-big-picture-line"></div>

                <p class="mm-big-picture-text">
                    {big_picture_html}
                </p>

            </div>


            <!-- FOOTER GRAPHIC -->

            <div class="mm-vibe-footer">

                <span></span>

                <div>
                    MUSEMIRROR · CREATOR-SIDE MUSIC INTELLIGENCE
                </div>

                <span></span>

            </div>

        </div>
        """
    )