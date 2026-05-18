import base64
from datetime import datetime
import os
from pathlib import Path
import random
import re
import time

import plotly.express as px
import polars as pl
import psutil
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import streamlit as st

# ==========================================
# 1. IMMEDIATE PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Advanced Tech AI Workspace | Rohit Jain",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hard Injection to override head element titles during low-level DOM construction
st.markdown("""
    <head>
        <title>Advanced Tech AI Workspace | Rohit Jain</title>
    </head>
""", unsafe_allow_html=True)

# FORCE FIXED DARK THEME CONFIGURATION VIA CSS OVERRIDES
st.markdown("""
    <style>
        /* 1. Force absolute dark background onto all main structural containers */
        html, body, [data-testid="stAppViewContainer"], .stApp { 
            background-color: #0b0f19 !important; 
            color: #e2e8f0 !important; 
        }
        
        /* 2. Force Sidebar to lock into dark mode layout independently */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
            border-right: 1px solid #1e293b !important;
        }

        /* 3. Enforce light-colored typography over all standard labels and texts globally */
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, [data-testid="stWidgetLabel"] p { 
            color: #ffffff !important; 
        }
        
        /* 4. Smooth scrolling physics configuration */
        html { scroll-behavior: smooth; }
        
        /* Maximize vertical screen real estate - remove extra top space */
        .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; max-width: 100%; }
        div[data-testid="stHeader"] { height: 0px !important; background: transparent !important; }
        footer { visibility: hidden; }
        
        /* Bulletproof Responsive Header Layout Fix */
        .responsive-header-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
            width: 100%;
        }
        .header-title-wrapper { flex: 1; min-width: 280px; }
        .header-title-main {
            font-size: clamp(1.2rem, 2.5vw, 2.2rem); 
            font-weight: bold;
            color: #ffffff !important;
            margin: 0;
            line-height: 1.2;
        }
        
        /* Scientific telemetry cards locked to dark styling */
        .stMetric { background: #111827 !important; padding: 12px; border-radius: 8px; border: 1px solid #1f2937 !important; }
        div[data-testid="stMetricValue"] > div { color: #ffffff !important; }
        div[data-testid="stMetricLabel"] > div { color: #94a3b8 !important; }
        
        /* Compact file uploader styling spacing */
        div[data-testid="stFileUploader"] { padding: 0 !important; margin-bottom: 10px !important; }
        
        /* Custom styled marquee container */
        .custom-marquee {
            background-color: #111827 !important;
            color: #06b6d4 !important;
            padding: 6px;
            font-weight: bold;
            font-size: 0.9rem;
            border-radius: 6px;
            border: 1px solid #1f2937 !important;
            margin-bottom: 15px;
        }
        
        /* Enforce internal scrollable zones inside each expander layout block */
        .scrollbox {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #1e293b !important;
            padding: 15px;
            border-radius: 6px;
            background-color: #030712 !important;
        }
        .branding-text { font-size: 0.85rem; line-height: 1.4; color: #cbd5e1 !important; }
        .section-watermark { font-size: 0.85rem; color: #06b6d4 !important; font-weight: bold; margin-bottom: 5px; }
        .section-watermark a { color: #06b6d4 !important; text-decoration: none; }
        
        /* Target and shrink button wrappers natively to avoid sizing bloat */
        div.stDownloadButton button { width: auto !important; white-space: nowrap !important; }
        
        /* Native Pure-CSS Sidebar Jump Controllers */
        .nav-link-btn {
            display: block;
            text-align: center;
            background-color: #1e293b !important;
            color: #06b6d4 !important;
            padding: 8px;
            margin: 5px 0;
            border-radius: 6px;
            border: 1px solid #334155 !important;
            font-weight: bold;
            text-decoration: none !important;
            font-size: 0.85rem;
            transition: background 0.3s ease;
        }
        .nav-link-btn:hover { background-color: #334155 !important; color: #ffffff !important; }

        /* Scientific Custom Loader Animations */
        .loader-box {
            background: #0f172a !important;
            border-left: 4px solid #06b6d4 !important;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
        .loader-spin {
            width: 24px;
            height: 24px;
            border: 3px solid #334155 !important;
            border-top: 3px solid #06b6d4 !important;
            border-radius: 50%;
            display: inline-block;
            animation: spin 0.8s linear infinite;
            vertical-align: middle;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .sidebar-inspect-box {
            background-color: #030712 !important;
            border: 1px dashed #334155 !important;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }

        /* 3D Scientific Profile Image Matrix Box */
        .profile-card-3d {
            perspective: 1000px;
            max-width: 140px;
            margin: 0 auto 15px auto;
        }
        .profile-img-3d {
            width: 100%;
            max-width: 140px;
            height: auto;
            border-radius: 12px;
            border: 2px solid #06b6d4;
            box-shadow: 0px 10px 20px rgba(6, 182, 212, 0.15), 
                        0px 4px 6px rgba(0, 0, 0, 0.3);
            transform: rotateX(10deg) rotateY(-10deg);
            transition: transform 0.5s ease, box-shadow 0.5s ease;
        }
        .profile-img-3d:hover {
            transform: rotateX(0deg) rotateY(0deg) scale(1.04);
            box-shadow: 0px 15px 25px rgba(6, 182, 212, 0.3), 
                        0px 6px 10px rgba(6, 182, 212, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

# Define path routing keys
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
PHOTO_PATH = STATIC_DIR / "images" / "RohitPhoto.jpg"
RESUME_PATH = STATIC_DIR / "Resume_Original_Rohit_Jain.pdf"
SAMPLE_EXCEL_PATH = STATIC_DIR / "sample_for_dashboard.xlsx"

# Guarantee local folders are present
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Session State Variables
if "filter_count" not in st.session_state:
    st.session_state.filter_count = 1
if "filter_version" not in st.session_state:
    st.session_state.filter_version = 0
if "use_sample_data" not in st.session_state:
    st.session_state.use_sample_data = False


# ==========================================
# 2. MODAL POPUP GATEWAYS (DIALOGS)
# ==========================================
@st.dialog("📬 Direct Communications Matrix — Rohit Jain", width="large")
def show_contact_modal():
    st.markdown("""
    Feel free to reach out directly via any of the technical gateway routes below:
    
    * **Direct Contact Hotkey:** `+91 89469 19241`
    * **Production Email Inquiries:** `engrohitjain5@gmail.com`
    * **Digital Resourcing Node:** [Explore Digital Portfolio](https://rohitjain-resume.vercel.app/)
    * **Core Specialty Focus:** AI Solutions Architectures, RAG Orchestration, and Enterprise Full-Stack Microservices.
    
    ---
    *Click outside or use the top right 'X' to close this view.*
    """)


@st.dialog("🖥️ Platform Architecture Deployment Profile", width="large")
def show_profile_modal():
    col1, col2 = st.columns([1.5, 3.5])
    with col1:
        if PHOTO_PATH.exists():
            try:
                with open(PHOTO_PATH, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode()
                st.markdown(f"""
                <div class="profile-card-3d">
                    <img src="data:image/jpeg;base64,{b64_string}" class="profile-img-3d" alt="Rohit Jain"/>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.image(str(PHOTO_PATH), use_container_width=True)
        else:
            st.warning("⚠️ Profile Image missing.")
    with col2:
        st.markdown("""
        ### **Rohit Jain**
        *AI Solutions Architect & Full Stack Architect | AI & Data Solutions*
        
        This workspace represents a production-grade optimization tier leveraging local compute, low-latency parsing engines, and fluid rendering.
        
        * 🎯 **AI Architecture & Advanced Workflows** — LLMs, Agentic Pipelines, & Enterprise Automation.
        * 💻 **Enterprise Full-Stack Engineering** — Highly optimized data microservices and real-time computing dashboards.
        * 📞 **+91 89469 19241** | ✉️ **engrohitjain5@gmail.com**
        * 🌐 [**Explore Digital Portfolio Resume**](https://rohitjain-resume.vercel.app/) — Technical project repositories and engineering background.
        """)


# ==========================================
# 3. SIDEBAR BRANDING & ASSET INFRASTRUCTURE
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ Platform Architect", help="System Architect profile details and rapid communication management console.")
    
    st.markdown("""
    <div class="branding-text">
        <strong>Rohit Jain</strong><br>
        <span style="color: #06b6d4; font-size:0.85rem;">AI Solutions Architect & Full Stack Architect</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🖥️ View Deployment Profile", use_container_width=True, help="Launches a secure popup detailing architectural specifications."):
        show_profile_modal()

    if st.button("📞 Quick Contact Portal", use_container_width=True, help="Launches a secure popup displaying communication paths."):
        show_contact_modal()
        
    st.markdown("---")
    
    # File Ingestion Mechanisms
    uploaded_file = st.file_uploader("Upload Working Excel/CSV Sheet", type=["xlsx", "xls", "csv"], help="Drop local enterprise data files here to pipeline into the Polars analysis model.")
    st.caption("10 GB per file • XLSX, XLS, CSV")
    
    if uploaded_file is not None:
        st.session_state.use_sample_data = False
    
    # Fast path: instant sample data trigger button
    if SAMPLE_EXCEL_PATH.exists():
        if st.button("🚀 Work with Sample Data Instantly", use_container_width=True, help="Triggers instant data injection using system-backup datasets."):
            with st.spinner("Injecting Sample Framework Environment..."):
                st.session_state.use_sample_data = True
                time.sleep(0.2)  
                st.rerun()
    else:
        st.caption("⚠️ Sample file missing for instant simulation path.")

    # --- DYNAMIC SIDEBAR DATA INSPECTION NODE ---
    if uploaded_file is not None or st.session_state.use_sample_data:
        st.markdown("#### 📂 Active File Inspector Node", help="Quick access tab validating file integrity schemas.")
        with st.container():
            st.markdown('<div class="sidebar-inspect-box">', unsafe_allow_html=True)
            if uploaded_file is not None:
                st.caption(f"📁 **Filename:** `{uploaded_file.name}`")
                st.caption(f"⚖️ **Allocated Stream Size:** {uploaded_file.size / 1024:.2f} KB")
            else:
                st.caption("📁 **Filename:** `sample_for_dashboard.xlsx (System Cache)`")
            st.markdown('<a class="nav-link-btn" href="#table-section" style="padding:4px; font-size:0.75rem;">🔍 Jump Directly To Attached Grid view</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- PURE-CSS JUMP SCROLL UTILITY INTERFACE ---
    st.markdown("### 🗺️ Quick Workspace Navigation", help="Use these anchors to fluidly shift your viewport focus.")
    st.markdown('<a class="nav-link-btn" href="#top-anchor">⬆️ Scroll To Top Banner</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#filter-section">🔍 Jump To Query Matrix</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#table-section">📊 Jump To Data Preview</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#graphics-section">📈 Jump To Visual Studio</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#ai-section">🧠 Jump To ML Analytics</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#diagnostics-section">🛠️ Jump To Hardware Footer</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📥 Developer Assets & Utilities", help="Download official distribution copies of engineering blueprints.")
    
    # Binary download handler for CV
    if RESUME_PATH.exists():
        with open(RESUME_PATH, "rb") as pdf_file:
            st.download_button(
                label="📄 Download Professional Resume",
                data=pdf_file.read(),
                file_name="Resume_Original_Rohit_Jain.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="sidebar_resume_btn"
            )
    else:
        st.caption("❌ Resume PDF asset missing in static folder.")
        
    # Sidebar secondary download handler
    if SAMPLE_EXCEL_PATH.exists():
        with open(SAMPLE_EXCEL_PATH, "rb") as excel_file:
            st.download_button(
                label="📊 Download Sample Excel Dataset",
                data=excel_file.read(),
                file_name="sample_for_dashboard.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="sidebar_sample_btn"
            )

# --- STRUCTURAL SCROLL ANCHOR ---
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# ==========================================
# 4. MAIN INTERFACE HEADER DISPLAY
# ==========================================
if SAMPLE_EXCEL_PATH.exists():
    with open(SAMPLE_EXCEL_PATH, "rb") as top_excel_file:
        excel_bytes = top_excel_file.read()
    
    st.markdown("""
    <div class="responsive-header-container">
        <div class="header-title-wrapper">
            <h1 class="header-title-main">⚡ Advanced Tech Business Intelligence Suite</h1>
            <div class='section-watermark'>Designed & Engineered by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4; text-decoration:none;'>Rohit Jain</a></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Sample Excel Template",
        data=excel_bytes,
        file_name="sample_for_dashboard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=False,
        key="top_bar_download_btn"
    )
else:
    st.markdown("""
    <div class="responsive-header-container">
        <div class="header-title-wrapper">
            <h1 class="header-title-main">⚡ Advanced Polars Business Intelligence Suite</h1>
            <div class='section-watermark'>Designed & Engineered by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4; text-decoration:none;'>Rohit Jain</a></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="custom-marquee">
        <marquee behavior="scroll" direction="left" scrollamount="6">
            📢 Processing Engine Online. Ingest a functional spreadsheet or CSV via the left sidebar console to trigger structural telemetry evaluations. 
            | 📢 प्रोसेसिंग इंजन ऑनलाइन है। संरचनात्मक टेलीमेट्री मूल्यांकन शुरू करने के लिए बाएं साइडबार कंसोल के माध्यम से एक स्प्रेडशीट या CSV फ़ाइल अपलोड करें।
        </marquee>
    </div>
""", unsafe_allow_html=True)

# Clock engine processing baseline
t_start = time.perf_counter()

# Resolve active data selection path context
active_bytes = None
is_csv_format = False

if uploaded_file is not None:
    active_bytes = uploaded_file.read()
    if uploaded_file.name.lower().endswith('.csv'):
        is_csv_format = True
        
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(UPLOAD_DIR / f"{timestamp}_{uploaded_file.name}", "wb") as f:
            f.write(active_bytes)
        st.session_state.last_uploaded = uploaded_file.name
        
        funny_quotes = [
            "Massaging dataset to eliminate inconvenient data patterns...",
            "Consulting local LLM agents to invent missing numerical fields...",
            "Overfitting the optimization parameters until accuracy claims look impressive...",
            "Adjusting random_state seeds to make sure p-values look completely intentional...",
            "Discarding critical experimental anomalies to prevent presentation disasters...",
            "Brewing coffee while vectorized matrix multiplication loops occupy server hardware..."
        ]
        
        loader_placeholder = st.empty()
        random.shuffle(funny_quotes)
        
        for index, phrase in enumerate(funny_quotes[:4]):
            for weight_factor in range(1, 101, 23):
                loader_placeholder.markdown(f"""
                <div class="loader-box">
                    <div class="loader-spin"></div>
                    <span style="color:#06b6d4; font-weight:bold; font-family:monospace;">
                        [CALCULATING NEURAL MATRIX WEIGHTS... {weight_factor + (index*2.5):.1f}% Complete]
                    </span>
                    <br><small style="color:#cbd5e1; font-style:italic; margin-left:34px;">🔬 {phrase}</small>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.08)
                
        loader_placeholder.empty()
        st.toast("🎯 Data stream synchronized into computation core successfully!", icon="✅")
        
elif st.session_state.use_sample_data:
    with open(SAMPLE_EXCEL_PATH, "rb") as sf:
        active_bytes = sf.read()


# ==========================================
# 5. CORE COMPUTE & DATA COMPILATION PIPELINE
# ==========================================
if active_bytes is not None:
    try:
        if is_csv_format:
            try:
                temp_csv_path = UPLOAD_DIR / "stream_processing_buffer.csv"
                with open(temp_csv_path, "wb") as f:
                    f.write(active_bytes)
                    
                raw_df = (
                    pl.scan_csv(
                        temp_csv_path,
                        infer_schema_length=10000,
                        ignore_errors=False,
                        quote_char=None,
                        encoding="utf-8-lossy",
                        truncate_ragged_lines=True
                    )
                    .collect(streaming=True)
                )
            except Exception:
                raw_df = pl.read_csv(
                    active_bytes, 
                    infer_schema_length=10000, 
                    quote_char=None, 
                    encoding="utf-8-lossy",
                    truncate_ragged_lines=True
                )
        else:
            raw_df = pl.read_excel(active_bytes, engine="calamine", raise_if_empty=False)
        
        all_columns = raw_df.columns

        # --- SECTION 1: FILTER MATRIX PANEL ---
        st.markdown('<div id="filter-section"></div>', unsafe_allow_html=True)
        with st.expander("🔍 1. Filter Data Your Way (Dynamic Query Matrix)", expanded=True):
            st.markdown("<div class='section-watermark'>Pipeline Layer: Smart Query Filter Engine by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
            
            if "filter_cols" not in st.session_state or len(st.session_state.filter_cols) != st.session_state.filter_count:
                st.session_state.filter_cols = [all_columns[0]] * st.session_state.filter_count
            if "filter_ops" not in st.session_state or len(st.session_state.filter_ops) != st.session_state.filter_count:
                st.session_state.filter_ops = ["="] * st.session_state.filter_count
            if "filter_vals" not in st.session_state or len(st.session_state.filter_vals) != st.session_state.filter_count:
                st.session_state.filter_vals = [""] * st.session_state.filter_count

            f_btn_col1, f_btn_col2, f_btn_col3, f_btn_col4 = st.columns([1.5, 1.5, 3, 6])
            with f_btn_col1:
                if st.button("➕ Add Rule", use_container_width=True):
                    with st.spinner("Appending structural matrix node..."):
                        if st.session_state.filter_count < len(all_columns):
                            st.session_state.filter_count += 1
                            st.session_state.filter_cols.append(all_columns[0])
                            st.session_state.filter_ops.append("=")
                            st.session_state.filter_vals.append("")
                            st.rerun()
            with f_btn_col2:
                if st.button("❌ Drop Rule", use_container_width=True):
                    with st.spinner("Removing query node constraints..."):
                        if st.session_state.filter_count > 1:
                            st.session_state.filter_count -= 1
                            st.session_state.filter_cols.pop()
                            st.session_state.filter_ops.pop()
                            st.session_state.filter_vals.pop()
                            st.rerun()
            with f_btn_col3:
                if st.button("🧹 Reset Only Filters", use_container_width=True, help="Flushes rule inputs while preserving active file matrix context."):
                    with st.spinner("Clearing query array scopes..."):
                        st.session_state.filter_count = 1
                        st.session_state.filter_cols = [all_columns[0]]
                        st.session_state.filter_ops = ["="]
                        st.session_state.filter_vals = [""]
                        st.session_state.filter_version += 1  # Increments version suffix to clear all frontend inputs natively
                        for key in list(st.session_state.keys()):
                            if key.startswith(("f_col_", "f_op_", "f_val_")):
                                del st.session_state[key]
                        st.rerun()
            with f_btn_col4:
                if st.button("🔄 Reset Matrix & Flow", use_container_width=False, help="Flushes out all rules, disengages datasets, and runs a complete reset lifecycle."):
                    with st.spinner("Purging total processing stack memory..."):
                        st.session_state.filter_count = 1
                        st.session_state.filter_cols = [all_columns[0]]
                        st.session_state.filter_ops = ["="]
                        st.session_state.filter_vals = [""]
                        st.session_state.use_sample_data = False
                        st.session_state.filter_version += 1
                        for key in list(st.session_state.keys()):
                            if key.startswith(("f_col_", "f_op_", "f_val_", "last_uploaded")):
                                del st.session_state[key]
                        st.rerun()

            st.markdown('<div class="scrollbox" style="max-height: 250px;">', unsafe_allow_html=True)
            active_filters = []
            for i in range(st.session_state.filter_count):
                col_f, col_op, col_val = st.columns([3, 2, 5])
                
                # Append version key suffix to force widget reconstruction on reset triggers
                ver = st.session_state.filter_version
                
                with col_f:
                    f_col = st.selectbox(f"Field Reference #{i+1}", all_columns, key=f"f_col_{i}_{ver}")
                    st.session_state.filter_cols[i] = f_col
                with col_op:
                    f_op = st.selectbox(f"Operation Type #{i+1}", ["=", "not equal", "like", "%like%", "regex", ">", "<"], key=f"f_op_{i}_{ver}")
                    st.session_state.filter_ops[i] = f_op
                with col_val:
                    f_val = st.text_input(f"Target Evaluation Value #{i+1}", value=st.session_state.filter_vals[i], key=f"f_val_{i}_{ver}")
                    st.session_state.filter_vals[i] = f_val
                    
                if f_val.strip() != "":
                    active_filters.append({"column": f_col, "operator": f_op, "value": f_val})
            st.markdown('</div>', unsafe_allow_html=True)

        # Execution evaluation pipeline over vector configurations
        with st.spinner("Re-evaluating dynamic dataset criteria matrix filters..."):
            filtered_df = raw_df
            for rule in active_filters:
                col, op, val = rule["column"], rule["operator"], rule["value"]
                try:
                    is_numeric = filtered_df[col].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]
                    if op == "=":
                        filtered_df = filtered_df.filter(pl.col(col) == float(val)) if is_numeric else filtered_df.filter(pl.col(col) == str(val))
                    elif op == "not equal":
                        filtered_df = filtered_df.filter(pl.col(col) != float(val)) if is_numeric else filtered_df.filter(pl.col(col) != str(val))
                    elif op == "like":
                        filtered_df = filtered_df.filter(pl.col(col).cast(pl.String).str.contains(re.escape(val)))
                    elif op == "%like%":
                        filtered_df = filtered_df.filter(pl.col(col).cast(pl.String).str.contains(val))
                    elif op == "regex":
                        filtered_df = filtered_df.filter(pl.col(col).cast(pl.String).str.contains(val))
                    elif op == ">":
                        filtered_df = filtered_df.filter(pl.col(col) > float(val))
                    elif op == "<":
                        filtered_df = filtered_df.filter(pl.col(col) < float(val))
                except Exception as e:
                    st.sidebar.error(f"Filter evaluation error: {e}")

        # --- SECTION 2: DATAGRID FRAME LAYER ---
        st.markdown('<div id="table-section"></div>', unsafe_allow_html=True)
        with st.expander(f"📊 2. Data Table Preview ({filtered_df.shape[0]} Rows Matching Active Scope)", expanded=True):
            st.markdown("<div class='section-watermark'>Data Grid Layer: Optimized Rendering Engine by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
            st.markdown('<div class="scrollbox">', unsafe_allow_html=True)
            st.dataframe(filtered_df.to_pandas(), use_container_width=True, height=350)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- SECTION 3: PLOTLY GRAPHICAL CANVAS ---
        st.markdown('<div id="graphics-section"></div>', unsafe_allow_html=True)
        with st.expander("📈 3. Comprehensive Graphics Presentation Canvas", expanded=True):
            st.markdown("<div class='section-watermark'>Visualization Layer: Interactive Plotly Studio by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
            
            numeric_cols = [col for col in all_columns if raw_df[col].dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]]
            
            g_col1, g_col2 = st.columns([1, 2])
            with g_col1:
                st.markdown("#### Axis Binding Configuration")
                x_target = st.selectbox("Horizontal Target (X Axis)", all_columns, index=0, key="viz_stable_x_target")
                use_count = st.toggle("Show Total Row Count (Frequency Matrix)", value=False, key="viz_stable_use_count")
                
                if use_count:
                    st.caption("ℹ️ *Y-Axis configuration locked to calculated row distribution counts*")
                    y_target = "Total Count"
                else:
                    y_target = st.selectbox("Vertical Target (Y Axis Value)", numeric_cols if numeric_cols else all_columns, index=0, key="viz_stable_y_target")
                    
                chart_type = st.radio("Active Layout Target", ["Simple Line Graph", "Simple Pie Chart", "Bar Chart Trend", "Scatter Matrix"], key="viz_stable_chart_layout")

            with g_col2:
                st.markdown('<div class="scrollbox" style="max-height: 440px;">', unsafe_allow_html=True)
                if filtered_df.shape[0] > 0:
                    with st.spinner("Rendering graphical rendering matrices..."):
                        if use_count:
                            plot_df = filtered_df.group_by(x_target).agg(pl.len().alias("Total Count")).sort("Total Count", descending=True)
                            pandas_view = plot_df.to_pandas()
                        else:
                            pandas_view = filtered_df.to_pandas()
                        
                        color_scale = px.colors.sequential.Electric
                        
                        # Plotly configuration remains hard-anchored to dark templates
                        if chart_type == "Simple Line Graph":
                            fig = px.line(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Line Matrix — {y_target} Analysis across {x_target}")
                            fig.update_traces(line=dict(color="#06b6d4", width=2.5))
                        elif chart_type == "Simple Pie Chart":
                            fig = px.pie(pandas_view, names=x_target, values=y_target, template="plotly_dark", title=f"Pie Allocation Breakdown Ratio — {y_target}", color_discrete_sequence=color_scale)
                        elif chart_type == "Bar Chart Trend":
                            fig = px.bar(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Bar Chart Volumes Metrics Comparison — {y_target}", color_discrete_sequence=["#06b6d4"])
                        elif chart_type == "Scatter Matrix":
                            fig = px.scatter(pandas_view, x=x_target, y=y_target, size=y_target if use_count else None, template="plotly_dark", title="Scatter Vector Core Mapping Layout", color_discrete_sequence=["#10b981"])
                        
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Empty structural scope. Refine filters to render visualization plots.")
                st.markdown('</div>', unsafe_allow_html=True)

        # --- SECTION 4: PREDICTIVE AI ENGINE MATRIX ---
        st.markdown('<div id="ai-section"></div>', unsafe_allow_html=True)
        with st.expander("🧠 4. Predictive Machine Learning Insight Array", expanded=True):
            st.markdown("<div class='section-watermark'>AI Layer: Scikit-Learn Cluster Engine by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
            
            if len(numeric_cols) >= 2 and filtered_df.shape[0] >= 5:
                ml_col1, ml_col2 = st.columns([1, 2])
                with ml_col1:
                    features = st.multiselect("Dimensions for AI Analysis", numeric_cols, default=numeric_cols[:2], key="ml_stable_features")
                    clusters = st.slider("Target Allocation Groups (K-Means)", 2, 6, 3, key="ml_stable_clusters")
                with ml_col2:
                    st.markdown('<div class="scrollbox" style="max-height: 440px;">', unsafe_allow_html=True)
                    if st.button("Run Smart AI Discovery Grouping", key="ml_stable_run_btn") and features:
                        with st.spinner("Fitting data into mathematical vector cluster space bounds..."):
                            ml_data = filtered_df.select(features).drop_nulls()
                            if ml_data.shape[0] > clusters:
                                X_scaled = StandardScaler().fit_transform(ml_data.to_numpy())
                                kmeans = KMeans(n_clusters=clusters, random_state=42).fit(X_scaled)
                                
                                plot_ml_df = ml_data.with_columns(pl.Series("Discovered Group ID", kmeans.labels_).cast(pl.String))
                                fig_ml = px.scatter(plot_ml_df.to_pandas(), x=features[0], y=features[1], color="Discovered Group ID", template="plotly_dark", title="AI Automatically Resolved Distribution Clusters", color_discrete_sequence=px.colors.qualitative.Vivid)
                                fig_ml.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                                st.plotly_chart(fig_ml, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Upload standard numerical feature metrics records to unlock algorithmic cluster analytics arrays.")

    except Exception as general_err:
        st.error(f"Spreadsheet Parsing Conflict Interruption Layer: {general_err}")
else:
    st.info("""
    System Engine Listening. Drop an Excel or CSV spreadsheet into the sidebar or click the instant sample button above to run workflows.
    | सिस्टम इंजन सक्रिय है। वर्कफ़्लो चलाने के लिए साइडबार में एक्सेल या CSV स्प्रेडशीट डालें या ऊपर दिए गए इंस्टेंट सैंपल बटन पर क्लिक करें।
    """)

# --- SECTION 5: ENGINE PERFORMANCE & TELEMETRY DIAGNOSTICS ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div id="diagnostics-section"></div>', unsafe_allow_html=True)
with st.expander("🛠️ 5. Real-Time Compute & Engine Execution Profile Diagnostics", expanded=True):
    st.markdown("<div class='section-watermark'>Diagnostics Layer: Low-Level Profiling Core by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
    st.markdown('<div class="scrollbox" style="max-height: 180px; background-color: #020617 !important;">', unsafe_allow_html=True)
    
    process = psutil.Process(os.getpid())
    execution_delta = time.perf_counter() - t_start
    rss_memory_mb = process.memory_info().rss / (1024 * 1024)
    system_cpu = psutil.cpu_percent()
    system_ram = psutil.virtual_memory().percent
    
    foot_1, foot_2, foot_3, foot_4 = st.columns(4)
    with foot_1:
        st.metric(label="⏱️ Engine Computational Time", value=f"{execution_delta:.4f}s", delta="Polars Ultra-Fast Execution")
    with foot_2:
        st.metric(label="💾 Application Dedicated RAM", value=f"{rss_memory_mb:.1f} MB", delta="Minimized Memory Allocation")
    with foot_3:
        st.metric(label="🎛️ Active Server Core Load", value=f"{system_cpu}%", delta="Dynamic Scaling Enabled")
    with foot_4:
        st.metric(label="🧠 Global System Memory Load", value=f"{system_ram}%", delta="Optimal Platform Performance")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer Layout Zone with Anchor Nodes
st.markdown(
    "<div style='text-align: center; color: #cbd5e1 !important; padding-top: 15px; font-size: 0.85rem; font-weight: bold;'>"
    "Designed & Developed by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4 !important; text-decoration:none;'>Rohit Jain</a> • Optimized for Mobile Phones, Tablets, and 4K Office Projectors"
    "</div>",
    unsafe_allow_html=True
)