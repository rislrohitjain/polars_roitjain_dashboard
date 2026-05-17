import streamlit as st
import polars as pl
import plotly.express as px
import time
import psutil
import os
import re
from datetime import datetime
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. Page Configuration for cross-device viewports (Mobile to Projector)
st.set_page_config(
    page_title="Advanced Tech AI Workspace | Rohit Jain",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS injection to guarantee layout responsiveness and add smooth anchor scrolling
st.markdown("""
    <style>
        html { scroll-behavior: smooth; }
        .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; max-width: 100%; }
        div[data-testid="stHeader"] { height: 0px !important; background: transparent !important; }
        footer { visibility: hidden; }
        
        .header-title-main {
            font-size: clamp(1.2rem, 2.5vw, 2.2rem);
            font-weight: bold;
            color: #ffffff;
            margin: 0;
            line-height: 1.2;
        }
        
        .stMetric { background: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; }
        div[data-testid="stFileUploader"] { padding: 0 !important; margin-bottom: 10px !important; }
        
        .custom-marquee {
            background-color: #1e293b;
            color: #38bdf8;
            padding: 6px;
            font-weight: bold;
            font-size: 0.9rem;
            border-radius: 6px;
            border: 1px solid #334155;
            margin-bottom: 15px;
        }
        
        .scrollbox {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #1e293b;
            padding: 15px;
            border-radius: 6px;
            background-color: #0f172a;
        }
        .branding-text { font-size: 0.85rem; line-height: 1.4; color: #cbd5e1; }
        .section-watermark { font-size: 0.85rem; color: #38bdf8; font-weight: bold; margin-bottom: 5px; }
        div.stDownloadButton button { width: auto !important; white-space: nowrap !important; }
        
        .nav-link-btn {
            display: block;
            text-align: center;
            background-color: #1e293b;
            color: #38bdf8 !important;
            padding: 8px;
            margin: 5px 0;
            border-radius: 6px;
            border: 1px solid #334155;
            font-weight: bold;
            text-decoration: none !important;
            font-size: 0.85rem;
            transition: background 0.3s ease;
        }
        .nav-link-btn:hover { background-color: #334155; color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# Define path routing keys
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
PHOTO_PATH = STATIC_DIR / "images" / "RohitPhoto.jpg"
RESUME_PATH = STATIC_DIR / "Resume_Original_Rohit_Jain.pdf"
SAMPLE_EXCEL_PATH = STATIC_DIR / "sample_for_dashboard.xlsx"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- INITIALIZE SYSTEM SESSION STATES FOR PERSISTENT DATA STORAGE ---
if "filter_count" not in st.session_state:
    st.session_state.filter_count = 1
if "cached_df" not in st.session_state:
    st.session_state.cached_df = None
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

# --- SIDEBAR BRANDING & ADVANCED ASSET MANAGEMENT LAYER ---
with st.sidebar:
    st.markdown("### 🛠️ Platform Architect")
    
    if PHOTO_PATH.exists():
        st.image(str(PHOTO_PATH), caption="Rohit Jain", use_container_width=True)
    else:
        st.warning("⚠️ Profile Image asset missing inside 'static/images/RohitPhoto.jpg'")
        
    st.markdown("""
    <div class="branding-text">
        <strong>Rohit Jain</strong><br>
        <span style="color: #38bdf8; font-size:0.85rem;">Senior Full-Stack Developer | AI Automation Architect</span>
        <hr style="margin: 8px 0; border-color: #334155;">
        🎯 AI Architecture & Workflows<br>
        💻 Enterprise Full-Stack Engineering<br>
        📞 +91 89469 19241<br>
        ✉️ engrohitjain5@gmail.com<br>
        🌐 <a href="https://rohitjain-resume.vercel.app/" target="_blank" style="color:#38bdf8; font-weight:bold;">Digital Portfolio Resume</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload Working Excel Sheet (.xlsx, .xls)", type=["xlsx", "xls"])
    
    # Instant sample data path setup
    if SAMPLE_EXCEL_PATH.exists():
        if st.button("🚀 Work with Sample Data Instantly", use_container_width=True):
            try:
                # Instantly cache the sample layout dataframe in session memory
                st.session_state.cached_df = pl.read_excel(str(SAMPLE_EXCEL_PATH), engine="calamine")
                st.session_state.last_uploaded = "sample_for_dashboard.xlsx"
                st.toast("⚡ Loaded system sample context instantly!")
            except Exception as e:
                st.sidebar.error(f"Failed to load sample: {e}")
    else:
        st.caption("⚠️ Sample file missing for instant simulation path.")
    
    st.markdown("### 🗺️ Quick Workspace Navigation")
    st.markdown('<a class="nav-link-btn" href="#top-anchor">⬆️ Scroll To Top Banner</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#profile-section">🖥️ Jump To Architect Profile</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#filter-section">🔍 Jump To Query Matrix</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#table-section">📊 Jump To Data Preview</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#graphics-section">📈 Jump To Visual Studio</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#ai-section">🧠 Jump To ML Analytics</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#diagnostics-section">🛠️ Jump To Hardware Footer</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📥 Developer Assets & Utilities")
    
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

# --- STRUCTURAL PURE-HTML TOP SCROLL ANCHOR ---
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# --- STRUCTURAL PURE-HTML FIXED RESPONSIVE HEADER PATTERN ---
if SAMPLE_EXCEL_PATH.exists():
    with open(SAMPLE_EXCEL_PATH, "rb") as top_excel_file:
        excel_bytes = top_excel_file.read()
    
    header_col, btn_col = st.columns([4, 1])
    with header_col:
        st.markdown('<h1 class="header-title-main">⚡ Advanced Tech Business Intelligence Suite</h1>', unsafe_allow_html=True)
        st.markdown("<div class='section-watermark'>Designed & Engineered by Rohit Jain</div>", unsafe_allow_html=True)
    with btn_col:
        st.download_button(
            label="📥 Download Sample Excel",
            data=excel_bytes,
            file_name="sample_for_dashboard.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="top_bar_download_btn"
        )
else:
    st.markdown('<h1 class="header-title-main">⚡ Advanced Tech Business Intelligence Suite</h1>', unsafe_allow_html=True)
    st.markdown("<div class='section-watermark'>Designed & Engineered by Rohit Jain</div>", unsafe_allow_html=True)

# Interactive pure HTML scrolling marquee asset
st.markdown("""
    <div class="custom-marquee">
        <marquee behavior="scroll" direction="left" scrollamount="6">
            📢 Please upload a valid sample excel file to check the power of the website.
        </marquee>
    </div>
""", unsafe_allow_html=True)

# Clock engine processing baseline
t_start = time.perf_counter()

# --- ARTIFACT FILE COLD UPLOAD MEMORY INTERCEPTOR ---
if uploaded_file is not None:
    # Check if this is a newly introduced file, if so overwrite session cache
    if st.session_state.last_uploaded != uploaded_file.name:
        file_bytes = uploaded_file.read()
        
        # Save a timestamped copy locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(UPLOAD_DIR / f"{timestamp}_{uploaded_file.name}", "wb") as f:
            f.write(file_bytes)
            
        # Parse and write to stable session storage memory
        st.session_state.cached_df = pl.read_excel(file_bytes, engine="calamine")
        st.session_state.last_uploaded = uploaded_file.name
        st.balloons()

# --- VERIFY DATAFRAME PRESENCE VIA PERSISTENT CACHE ---
if st.session_state.cached_df is not None:
    try:
        raw_df = st.session_state.cached_df
        all_columns = raw_df.columns
        
        # --- PRESENTATION SECTION: PLATFORM ARCHITECTURE DEPLOYMENT PROFILE ---
        st.markdown('<div id="profile-section"></div>', unsafe_allow_html=True)
        st.success("✅ Active Working Memory Dataset Context Loaded Successfully!")
        with st.chat_message("assistant", avatar="🛠️"):
            st.markdown("""
            ### 🖥️ Platform Architecture Deployment Profile
            **This ultra-fast analytics engine workspace solution was fully engineered and optimized by:**
            
            #### **Rohit Jain**
            *Senior Full-Stack Developer | AI Automation Architect*
            
            *   🎯 **AI Architecture & Workflows**
            *   💻 **Enterprise Full-Stack Engineering**
            *   📞 **+91 89469 19241**
            *   ✉️ **engrohitjain5@gmail.com**
            *   🌐 [**Digital Portfolio Resume**](https://rohitjain-resume.vercel.app/)
            """, unsafe_allow_html=True)

        # --- SECTION 1: COLLAPSIBLE FILTER MATRIX PANEL ---
        st.markdown('<div id="filter-section"></div>', unsafe_allow_html=True)
        with st.expander("🔍 1. Filter Data Your Way (Dynamic Query Matrix)", expanded=True):
            st.markdown("<div class='section-watermark'>Pipeline Layer: Smart Query Filter Engine by Rohit Jain</div>", unsafe_allow_html=True)
            st.info("Construct layered matching arrays immediately. Use conditions like like, regex, inequalities, or exact equivalence values.")
            
            st.markdown('<div class="scrollbox" style="max-height: 250px;">', unsafe_allow_html=True)
            f_btn_col1, f_btn_col2 = st.columns([2, 10])
            with f_btn_col1:
                if st.button("➕ Add Rule", use_container_width=True):
                    if st.session_state.filter_count < len(all_columns):
                        st.session_state.filter_count += 1
            with f_btn_col2:
                if st.button("❌ Drop Rule", use_container_width=True):
                    if st.session_state.filter_count > 1:
                        st.session_state.filter_count -= 1

            active_filters = []
            for i in range(st.session_state.filter_count):
                col_f, col_op, col_val = st.columns([3, 2, 5])
                with col_f:
                    f_col = st.selectbox(f"Field Reference #{i+1}", all_columns, key=f"f_col_{i}")
                with col_op:
                    f_op = st.selectbox(f"Operation Type #{i+1}", ["=", "not equal", "like", "%like%", "regex", ">", "<"], key=f"f_op_{i}")
                with col_val:
                    f_val = st.text_input(f"Target Value #{i+1}", key=f"f_val_{i}")
                    
                if f_val:
                    active_filters.append({"column": f_col, "operator": f_op, "value": f_val})
            st.markdown('</div>', unsafe_allow_html=True)

        # Execution evaluation pipeline over vector configurations
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
                st.sidebar.error(f"Filter tracking layout context mismatch: {e}")

        # --- SECTION 2: COLLAPSIBLE ARCHITECTURAL TABLE MATRIX ---
        st.markdown('<div id="table-section"></div>', unsafe_allow_html=True)
        with st.expander(f"📊 2. Data Table Preview ({filtered_df.shape[0]} Rows Matching Active Scope)", expanded=True):
            st.markdown("<div class='section-watermark'>Data Grid Layer: Optimized Rendering Engine by Rohit Jain</div>", unsafe_allow_html=True)
            st.markdown('<div class="scrollbox">', unsafe_allow_html=True)
            st.dataframe(filtered_df.to_pandas(), use_container_width=True, height=350)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- SECTION 3: COLLAPSIBLE PLOTLY DATA STUDIO GRAPHICAL PRESENTATION CANVAS ---
        st.markdown('<div id="graphics-section"></div>', unsafe_allow_html=True)
        with st.expander("📈 3. Comprehensive Graphics Presentation Canvas", expanded=True):
            st.markdown("<div class='section-watermark'>Visualization Layer: Interactive Plotly Studio by Rohit Jain</div>", unsafe_allow_html=True)
            st.info("Map metrics to structural elements instantly. Toggle Frequency Counter mode to calculate item distribution volumes instantly.")
            
            numeric_cols = [col for col in all_columns if raw_df[col].dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]]
            
            g_col1, g_col2 = st.columns([1, 2])
            with g_col1:
                st.markdown("#### Axis Binding Configuration")
                x_target = st.selectbox("Horizontal Target (X Axis)", all_columns, index=0)
                use_count = st.toggle("Show Total Row Count (Frequency Matrix)", value=False)
                
                if use_count:
                    st.caption("ℹ️ *Y-Axis parameter configurations locked to calculated row distribution counts*")
                    y_target = "Total Count"
                else:
                    y_target = st.selectbox("Vertical Target (Y Axis Value)", numeric_cols if numeric_cols else all_columns, index=0)
                    
                chart_type = st.radio("Active Layout Target", ["Simple Line Graph", "Simple Pie Chart", "Bar Chart Trend", "Scatter Matrix"])

            with g_col2:
                st.markdown('<div class="scrollbox" style="max-height: 440px;">', unsafe_allow_html=True)
                if filtered_df.shape[0] > 0:
                    if use_count:
                        plot_df = filtered_df.group_by(x_target).agg(pl.len().alias("Total Count")).sort("Total Count", descending=True)
                        pandas_view = plot_df.to_pandas()
                    else:
                        pandas_view = filtered_df.to_pandas()
                    
                    if chart_type == "Simple Line Graph":
                        fig = px.line(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Line Matrix — {y_target} Analysis across {x_target}")
                    elif chart_type == "Simple Pie Chart":
                        fig = px.pie(pandas_view, names=x_target, values=y_target, template="plotly_dark", title=f"Pie Allocation Breakdown Ratio — {y_target}")
                    elif chart_type == "Bar Chart Trend":
                        fig = px.bar(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Bar Chart Volumes Metrics Comparison — {y_target}")
                    elif chart_type == "Scatter Matrix":
                        fig = px.scatter(pandas_view, x=x_target, y=y_target, size=y_target if use_count else None, template="plotly_dark", title="Scatter Vector Core Mapping Layout")
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Empty structural scope. Refine filters to render visualization plots.")
                st.markdown('</div>', unsafe_allow_html=True)

        # --- SECTION 4: COLLAPSIBLE ADVANCED PREDICTIVE AI ENGINE MATRIX ---
        st.markdown('<div id="ai-section"></div>', unsafe_allow_html=True)
        with st.expander("🧠 4. Predictive Machine Learning Insight Array", expanded=True):
            st.markdown("<div class='section-watermark'>AI Layer: Scikit-Learn Cluster Engine by Rohit Jain</div>", unsafe_allow_html=True)
            st.info("Unsupervised pattern grouping engine scans multidimensional features and assigns records into colored mathematical relationship matrices.")
            
            if len(numeric_cols) >= 2 and filtered_df.shape[0] >= 5:
                ml_col1, ml_col2 = st.columns([1, 2])
                with ml_col1:
                    features = st.multiselect("Dimensions for AI Analysis", numeric_cols, default=numeric_cols[:2])
                    clusters = st.slider("Target Allocation Groups (K-Means)", 2, 6, 3)
                with ml_col2:
                    st.markdown('<div class="scrollbox" style="max-height: 440px;">', unsafe_allow_html=True)
                    if st.button("Run Smart AI Discovery Grouping") and features:
                        ml_data = filtered_df.select(features).drop_nulls()
                        if ml_data.shape[0] > clusters:
                            X_scaled = StandardScaler().fit_transform(ml_data.to_numpy())
                            kmeans = KMeans(n_clusters=clusters, random_state=42).fit(X_scaled)
                            
                            plot_ml_df = ml_data.with_columns(pl.Series("Discovered Group ID", kmeans.labels_).cast(pl.String))
                            fig_ml = px.scatter(plot_ml_df.to_pandas(), x=features[0], y=features[1], color="Discovered Group ID", template="plotly_dark", title="AI Automatically Resolved Distribution Clusters")
                            st.plotly_chart(fig_ml, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Upload standard numerical feature metrics records to unlock algorithmic cluster analytics arrays.")

    except Exception as general_err:
        st.error(f"Spreadsheet Parsing Conflict Interruption Layer: {general_err}")
else:
    st.info("System Engine Listening. Drop an Excel spreadsheet into the sidebar or click the instant sample button above to run workflows.")

# --- SECTION 5: COLLAPSIBLE COMPUTATIONAL AND RESOURCE MONITORING TOOLBOX ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div id="diagnostics-section"></div>', unsafe_allow_html=True)
with st.expander("🛠️ 5. Real-Time Compute & Engine Execution Profile Diagnostics", expanded=True):
    st.markdown("<div class='section-watermark'>Diagnostics Layer: Low-Level Profiling Core by Rohit Jain</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="scrollbox" style="max-height: 180px; background-color: #020617;">', unsafe_allow_html=True)
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

st.markdown(
    "<div style='text-align: center; color: #38bdf8; padding-top: 15px; font-size: 0.85rem; font-weight: bold;'>"
    "Designed & Developed by Rohit Jain • Optimized for Mobile Phones, Tablets, and 4K Office Projectors"
    "</div>", 
    unsafe_allow_html=True
)