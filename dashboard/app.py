import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import json
import os
from datetime import datetime

# ===============================
# Configuration & Styles
# ===============================
st.set_page_config(
    page_title="LLM Quality Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Industry Level" look
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Card-like metrics */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #f8fafc;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 5px;
        color: #cbd5e1;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #6366f1;
        color: white;
    }
    
    /* Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# Data Loading
# ===============================
@st.cache_data
def load_data():
    RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    
    # Load summaries
    summary_files = glob.glob(os.path.join(RESULTS_DIR, "*_summary.json"))
    history = []
    
    for f in summary_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                history.append(data)
        except Exception:
            pass
            
    if not history:
        return pd.DataFrame(), pd.DataFrame(), RESULTS_DIR
        
    history_df = pd.DataFrame(history).sort_values("timestamp", ascending=True)
    
    # Load all details for latest runs to enable drill-down without reloading everything
    # (In prod, you'd load this on demand)
    return history_df, RESULTS_DIR

history_df, RESULTS_DIR = load_data()

# ===============================
# Sidebar
# ===============================
with st.sidebar:
    st.title("🛡️ LLM Quality Monitor")
    st.markdown("---")
    
    if not history_df.empty:
        st.write(f"**Total Runs:** {len(history_df)}")
        st.write(f"**Last Run:** {pd.to_datetime(history_df['timestamp'].iloc[-1]).strftime('%Y-%m-%d %H:%M')}")
    else:
        st.warning("No data found.")
        
    st.markdown("### Settings")
    metric_cols = [c for c in history_df.columns if c not in ["run_id", "timestamp", "total_samples", "commit"] and not c.startswith("Unnamed")] if not history_df.empty else []
    
    selected_metrics = st.multiselect(
        "Trace Metrics",
        options=metric_cols,
        default=metric_cols[:4] if len(metric_cols) >= 4 else metric_cols
    )
    
    st.markdown("### 🛠️ Tools")
    if st.button("Generate Synthetic Data"):
        st.session_state['show_generator'] = True

# ===============================
# Main Dashboard
# ===============================

# Handle Generator UI
if st.session_state.get('show_generator', False):
    st.markdown("## 🧬 Synthetic Test Data Generator")
    st.info("Uses Ragas to generate Question-Answer pairs from your `fs11/` documents.")
    
    col_gen1, col_gen2 = st.columns(2)
    with col_gen1:
        test_size = st.slider("Number of samples:", min_value=1, max_value=50, value=5)
    with col_gen2:
        if st.button("🚀 Start Generation"):
            with st.spinner("Analyzing documents & hallucinating questions... (This may take a minute)"):
                try:
                    # Run the generation script as a subprocess or import logic
                    # Importing is cleaner but script is standalone without param inputs
                    # Let's run command for isolation
                    import subprocess
                    result = subprocess.run(
                        ["python", "testDataFeaxtory.py", str(test_size)], 
                        capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Generation Complete!")
                        st.balloons()
                        # Force reload of data
                        if os.path.exists(gen_file):
                             st.session_state['gen_data_timestamp'] = datetime.now()
                    else:
                        st.error("❌ Generation failed:")
                        st.code(result.stderr)
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state['show_generator'] = False
        st.rerun()
        
    # Show existing generated data if any
    if os.path.exists(gen_file):
        st.markdown("---")
        st.markdown("### 📄 Review Generated Test Cases")
        
        try:
            gen_df = pd.read_json(gen_file)
            
            # Metrics about the generated set
            m1, m2, m3 = st.columns(3)
            m1.metric("Generated Samples", len(gen_df))
            if "question_type" in gen_df.columns:
                 type_counts = gen_df["question_type"].value_counts().to_dict()
                 top_type = max(type_counts, key=type_counts.get) if type_counts else "N/A"
                 m2.metric("Dominant Type", top_type)
            
            # Interactive Editor/Viewer
            st.dataframe(
                gen_df, 
                use_container_width=True,
                height=400,
                column_config={
                    "question": st.column_config.TextColumn("Question", width="medium"),
                    "ground_truth": st.column_config.TextColumn("Ground Truth", width="medium"),
                    "evolution_type": st.column_config.TextColumn("Type", width="small"),
                    "episode_done": st.column_config.CheckboxColumn("Done", disabled=True),
                }
            )
            
            st.download_button(
                label="📥 Download JSON",
                data=gen_df.to_json(orient="records", indent=4),
                file_name="ragas_testset.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.warning(f"Could not read generated JSON file: {e}")
            
    st.stop() # Stop rendering the rest of the dashboard when in generator mode

if history_df.empty:
    st.info("👋 Welcome! Run `python evaluation/run_eval.py` to generate your first evaluation report.")
    st.stop()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Evaluation Overview")
    st.markdown("High-level performance metrics of your RAG pipeline.")
with col2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# 1. KPI Cards (Most recent run)
latest_run = history_df.iloc[-1]
prev_run = history_df.iloc[-2] if len(history_df) > 1 else None

st.markdown("### 📊 Latest Performance")
kpi_cols = st.columns(len(selected_metrics) + 1)

# Total Samples Card
kpi_cols[0].metric(
    "Test Coverage", 
    f"{int(latest_run.get('total_samples', 0))} Samples",
    delta=f"{int(latest_run.get('total_samples', 0) - prev_run.get('total_samples', 0))}" if prev_run is not None else None
)

# Metric Cards
for i, metric in enumerate(selected_metrics):
    val = latest_run.get(metric, 0)
    prev_val = prev_run.get(metric, 0) if prev_run is not None else 0
    delta = val - prev_val
    
    # Color logic: Green if goes up (usually good), unless you define 'bad' metrics like latency (TODO)
    kpi_cols[i+1].metric(
        label=metric.replace("_", " ").title(),
        value=f"{val:.4f}",
        delta=f"{delta:.4f}"
    )

st.markdown("---")

# 2. Main Tabs
tab1, tab2, tab3 = st.tabs(["📈 Trends & Analysis", "🔬 Deep Dive", "⚔️ Compare Comparisons"])

# --- TAB 1: Trends ---
with tab1:
    st.markdown("#### Historical Velocity")
    
    if selected_metrics:
        # Create a clean line chart
        fig = px.line(
            history_df, 
            x="run_id", 
            y=selected_metrics,
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1"),
            hovermode="x unified",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Recent Runs")
    display_df = history_df[["run_id", "timestamp"] + selected_metrics].sort_values("timestamp", ascending=False)
    
    # Styled dataframe with heatmap
    try:
        st.dataframe(
            display_df.style.background_gradient(cmap="RdYlGn", subset=selected_metrics, axis=None),
            use_container_width=True
        )
    except ImportError:
         st.warning("⚠️ Heatmap styling disabled (matplotlib missing). Running basic table.")
         st.dataframe(display_df, use_container_width=True)

# --- TAB 2: Deep Dive ---
with tab2:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        run_id_select = st.selectbox("Inspect Run:", history_df["run_id"].unique(), index=len(history_df)-1)
    
    details_path = os.path.join(RESULTS_DIR, f"{run_id_select}_details.csv")
    
    if os.path.exists(details_path):
        details_df = pd.read_csv(details_path)
        
        # Breakdown
        st.markdown(f"#### Run Details: `{run_id_select}`")
        
        # 1. Distribution of scores
        if selected_metrics:
            dist_fig = px.box(
                details_df, 
                y=selected_metrics,
                points="all", 
                color_discrete_sequence=["#6366f1"]
            )
            dist_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#cbd5e1"),
                xaxis_title="Metric",
                yaxis_title="Score"
            )
            st.plotly_chart(dist_fig, use_container_width=True)
            
        # 2. Lowest Performing Samples (The "Why?")
        st.markdown("#### 🚨 Failure Analysis (Lowest Scores)")
        
        sort_metric = st.selectbox("Find worst examples by:", options=selected_metrics)
        
        bad_examples = details_df.sort_values(sort_metric, ascending=True).head(5)
        
        for idx, row in bad_examples.iterrows():
            with st.expander(f"❌ {sort_metric} = {row[sort_metric]:.4f} | Input: {str(row['user_input'])[:50]}..."):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**User Input:**")
                    st.info(row['user_input'])
                    st.markdown("**Generated Response:**")
                    st.warning(row['response'])
                with c2:
                    st.markdown("**Reference (Ground Truth):**")
                    st.success(row['reference'])
                    st.markdown("**Retrieved Context:**")
                    st.code(str(row['retrieved_contexts'])[:500] + "...")
                    
        st.markdown("#### Full Dataset")
        st.dataframe(details_df, use_container_width=True)
            
    else:
        st.error("Detail CSV not found for this run.")

# --- TAB 3: Compare ---
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        base_run = st.selectbox("Base Run", history_df["run_id"], index=max(0, len(history_df)-2), key='base')
    with col2:
        comp_run = st.selectbox("Comparison Run", history_df["run_id"], index=len(history_df)-1, key='comp')
        
    # Get Data
    run_base_data = history_df[history_df["run_id"] == base_run].iloc[0]
    run_comp_data = history_df[history_df["run_id"] == comp_run].iloc[0]
    
    # Radar Chart Data
    categories = selected_metrics
    val_base = [run_base_data[m] for m in categories]
    val_comp = [run_comp_data[m] for m in categories]
    
    # 1. Radar Chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=val_base,
        theta=categories,
        fill='toself',
        name=f'Base: {base_run}'
    ))
    fig.add_trace(go.Scatterpolar(
        r=val_comp,
        theta=categories,
        fill='toself',
        name=f'Compare: {comp_run}'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Delta Table
    delta_data = []
    for m in categories:
        delta_data.append({
            "Metric": m,
            f"{base_run}": run_base_data[m],
            f"{comp_run}": run_comp_data[m],
            "Delta": run_comp_data[m] - run_base_data[m]
        })
    
    delta_df = pd.DataFrame(delta_data)
    
    def color_delta(val):
        color = '#4ade80' if val > 0 else '#f87171' if val < 0 else '#94a3b8'
        return f'color: {color}; font-weight: bold'
    
    st.table(delta_df.style.applymap(color_delta, subset=['Delta']))
