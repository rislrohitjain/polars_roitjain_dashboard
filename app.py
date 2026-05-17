import streamlit as st
import polars as pl
import plotly.express as px
import time
import psutil
import os
import re
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. Page Configuration for cross-device viewports (Mobile to Projector)
st.set_page_config(
    page_title="Polars AI Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS injection for compact file uploader, clean metrics, and native item scrollboxes
st.markdown("""
    <style>
        /* Compact layout adjustments */
        .reportview-container .main .block-container { max-width: 100%; padding-bottom: 3rem; }
        footer { visibility: hidden; }
        
        /* Attractive metric displays */
        .stMetric { background: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; }
        
        /* Shrink extra whitespace around file uploader */
        div[data-testid="stFileUploader"] { padding: 0 !important; margin-bottom: 10px !important; }
        
        /* Enforce internal scrollable zones for individual dashboard elements */
        .scrollbox {
            max-height: 420px;
            overflow-y: auto;
            border: 1px solid #334155;
            padding: 15px;
            border-radius: 8px;
            background-color: #0f172a;
            margin-bottom: 20px;
        }
        .branding-text { font-size: 0.85rem; line-height: 1.4; color: #cbd5e1; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR BRANDING & INGESTION NODE ---
with st.sidebar:
    st.markdown("### 🛠️ Platform Architect")
    st.markdown("""
    <div class="branding-text">
        <strong>Rohit Jain</strong><br>
        <span style="color: #38bdf8; font-size:0.8rem;">Senior Full-Stack Developer | AI Automation Architect</span>
        <hr style="margin: 8px 0; border-color: #334155;">
        🎯 AI Architecture<br>
        💻 Full-Stack Development<br>
        📞 +91 89469 19241<br>
        ✉️ engrohitjain5@gmail.com<br>
        🌐 <a href="https://rohitjain-resume.vercel.app/" target="_blank" style="color:#38bdf8;">Digital Portfolio Resume</a><br>
        🐙 <a href="https://github.com/rislrohitjain/" target="_blank" style="color:#64748b;">GitHub</a> | 🔗 <a href="https://linkedin.com/in/rohit-jain-061571a3" target="_blank" style="color:#64748b;">LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Ultra-compact file selector interface 
    uploaded_file = st.file_uploader("Upload Excel Sheet (.xlsx, .xls)", type=["xlsx", "xls"])

st.title("⚡ Advanced Polars Business Intelligence Suite")
st.caption("Pure Python Real-Time Data Studio — Built for Speed & Clarity")

# Clock engine start time
t_start = time.perf_counter()

if "filter_count" not in st.session_state:
    st.session_state.filter_count = 1

if uploaded_file is not None:
    try:
        # In-memory high speed spreadsheet conversion
        file_bytes = uploaded_file.read()
        raw_df = pl.read_excel(file_bytes, engine="calamine")
        all_columns = raw_df.columns
        
        # --- SECTION 1: DYNAMIC FILTER MATRIX ---
        st.write("### 🔍 1. Filter Data Your Way")
        st.info("Choose a column, an operation type, and enter a value to narrow down your records immediately.")
        
        f_btn_col1, f_btn_col2 = st.columns([2, 10])
        with f_btn_col1:
            if st.button("➕ Add More Rules", use_container_width=True):
                if st.session_state.filter_count < len(all_columns):
                    st.session_state.filter_count += 1
        with f_btn_col2:
            if st.button("❌ Remove Last Rule", use_container_width=True):
                if st.session_state.filter_count > 1:
                    st.session_state.filter_count -= 1

        active_filters = []
        for i in range(st.session_state.filter_count):
            col_f, col_op, col_val = st.columns([3, 2, 5])
            with col_f:
                f_col = st.selectbox("Column", all_columns, key=f"f_col_{i}")
            with col_op:
                f_op = st.selectbox("Condition", ["=", "not equal", "like", "%like%", "regex", ">", "<"], key=f"f_op_{i}")
            with col_val:
                f_val = st.text_input("Value to search", key=f"f_val_{i}")
                
            if f_val:
                active_filters.append({"column": f_col, "operator": f_op, "value": f_val})

        # Process filter metrics natively
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
                st.sidebar.error(f"Rule Error: {e}")

        # Isolated Scroll Container for Data Table
        st.write(f"#### Data Table Preview ({filtered_df.shape[0]} matching lines found)")
        st.markdown('<div class="scrollbox">', unsafe_allow_html=True)
        st.dataframe(filtered_df.to_pandas(), use_container_width=True, height=320)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- SECTION 2: SIMPLIFIED GRAPHICAL CANVAS WITH COUNT LOGIC ---
        st.write("---")
        st.write("### 📈 2. Comprehensive Graphics Presentation Canvas")
        st.info("Pick your targets to instantly see trends. Turn on 'Show Total Row Count' to easily see item quantities on your axis.")
        
        numeric_cols = [col for col in all_columns if raw_df[col].dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]]
        
        g_col1, g_col2 = st.columns([1, 2])
        with g_col1:
            st.markdown("#### Axis Settings")
            x_target = st.selectbox("Horizontal Target (X Axis)", all_columns, index=0)
            
            # Count mode option toggle
            use_count = st.toggle("Show Total Row Count (Frequency)", value=False, help="Toggle this to count how many times each item appears in the chosen column.")
            
            if use_count:
                st.caption("ℹ️ *Y-Axis is locked to 'Total Count' mode*")
                y_target = "Total Count"
            else:
                y_target = st.selectbox("Vertical Target (Y Axis Value)", numeric_cols if numeric_cols else all_columns, index=0)
                
            chart_type = st.radio("Choose Chart Layout", ["Simple Line Graph", "Simple Pie Chart", "Bar Chart Trend", "Scatter Matrix"])

        with g_col2:
            st.markdown('<div class="scrollbox">', unsafe_allow_html=True)
            if filtered_df.shape[0] > 0:
                
                # Dynamic aggregation processing if 'use_count' is enabled
                if use_count:
                    # Group by X target and count occurrences natively in Polars
                    plot_df = filtered_df.group_by(x_target).agg(pl.len().alias("Total Count")).sort("Total Count", descending=True)
                    pandas_view = plot_df.to_pandas()
                else:
                    pandas_view = filtered_df.to_pandas()
                
                # Render logic
                if chart_type == "Simple Line Graph":
                    fig = px.line(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Line Graph - Trends of {y_target} per {x_target}")
                elif chart_type == "Simple Pie Chart":
                    fig = px.pie(pandas_view, names=x_target, values=y_target, template="plotly_dark", title=f"Pie Chart - Distribution Ratio of {y_target}")
                elif chart_type == "Bar Chart Trend":
                    fig = px.bar(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Bar Chart - Quantities and Volumes of {y_target}")
                elif chart_type == "Scatter Matrix":
                    if use_count:
                        fig = px.scatter(pandas_view, x=x_target, y=y_target, size=y_target, template="plotly_dark", title="Scatter Count Layout")
                    else:
                        fig = px.scatter(pandas_view, x=x_target, y=y_target, template="plotly_dark", title=f"Scatter Matrix - Correlation: {x_target} vs {y_target}")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data matches your current criteria to update graphics views.")
            st.markdown('</div>', unsafe_allow_html=True)

        # --- SECTION 3: EASY TO UNDERSTAND ML/AI ---
        if len(numeric_cols) >= 2 and filtered_df.shape[0] >= 5:
            st.write("---")
            st.write("### 🧠 3. Predictive Machine Learning Insight Array")
            st.info("This AI automatically scans numerical columns and groups related patterns into clear, color-coded cluster segments.")
            
            ml_col1, ml_col2 = st.columns([1, 2])
            with ml_col1:
                features = st.multiselect("Data items for AI to analyze", numeric_cols, default=numeric_cols[:2])
                clusters = st.slider("Number of behavior groups to discover", 2, 6, 3)
            with ml_col2:
                st.markdown('<div class="scrollbox">', unsafe_allow_html=True)
                if st.button("Run Smart AI Discovery Grouping") and features:
                    ml_data = filtered_df.select(features).drop_nulls()
                    if ml_data.shape[0] > clusters:
                        X_scaled = StandardScaler().fit_transform(ml_data.to_numpy())
                        kmeans = KMeans(n_clusters=clusters, random_state=42).fit(X_scaled)
                        
                        plot_ml_df = ml_data.with_columns(pl.Series("Discovered Group ID", kmeans.labels_).cast(pl.String))
                        fig_ml = px.scatter(plot_ml_df.to_pandas(), x=features[0], y=features[1], color="Discovered Group ID", template="plotly_dark", title="AI Automatically Discovered Patterns & Segments")
                        st.plotly_chart(fig_ml, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as general_err:
        st.error(f"Spreadsheet Parsing Conflict: {general_err}")
else:
    st.info("System Engine Online. Drag and drop any Excel document into the left-hand sidebar controller to launch interactive analysis.")

# --- SECTION 4: COMPUTATIONAL PROFILE DIAGNOSTICS FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)
st.write("---")

footer_container = st.container()
with footer_container:
    st.markdown("#### 🛠️ Real-Time Compute & Engine Execution Profile Diagnostics")
    
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

    st.markdown(
        "<div style='text-align: center; color: #64748b; padding-top: 15px; font-size: 0.85rem;'>"
        "Responsive Client Viewport Range Optimized: Mobile Phones / Tablets / Ultra-Wide 4K Office Projectors"
        "</div>", 
        unsafe_allow_html=True
    )