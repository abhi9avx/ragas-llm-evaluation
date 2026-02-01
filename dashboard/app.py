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
    page_title="Ragas LLM Studio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Ultra Wow" look
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }

    /* Card Containers */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }

    /* Text Styling */
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(to right, #ffffff, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Positive/Negative Colors */
    .delta-pos { color: #4ade80; }
    .delta-neg { color: #f87171; }
    .delta-neu { color: #94a3b8; }

    /* Custom Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        border-radius: 8px 8px 0 0;
        color: #94a3b8;
        font-weight: 600;
        padding: 0 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #818cf8;
        border-bottom: 2px solid #818cf8;
    }
    
    /* Streamlit Components overrides */
    div[data-testid="stDataFrame"] {
        background-color: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
    }
    
    .stButton button {
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: None;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255,255,255,0.02);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# Data Logic
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
    return history_df, RESULTS_DIR

history_df, RESULTS_DIR = load_data()

# ===============================
# Helper Functions
# ===============================
def render_metric_card(label, value, delta=None, delta_text=None):
    delta_html = ""
    if delta is not None:
        color_class = "delta-pos" if delta > 0 else "delta-neg" if delta < 0 else "delta-neu"
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "─"
        display_delta = abs(delta)
        delta_html = f'<div class="metric-delta {color_class}">{arrow} {display_delta:.4f} {delta_text if delta_text else ""}</div>'
        
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# ===============================
# Sidebar & Navigation
# ===============================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem;">🧬</div>
            <h1 style="font-size: 1.5rem; background: linear-gradient(to right, #818cf8, #c7d2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Ragas Studio</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if not history_df.empty:
        st.caption("🔍 DASHBOARD STATUS")
        st.markdown(f"**Run Count:** `{len(history_df)}`")
        st.markdown(f"**Latest:** `{pd.to_datetime(history_df['timestamp'].iloc[-1]).strftime('%d %b %H:%M')}`")
    
    st.markdown("---")
    st.caption("⚙️ CONFIGURATION")
    
    metric_cols = [c for c in history_df.columns if c not in ["run_id", "timestamp", "total_samples", "commit"] and not c.startswith("Unnamed")] if not history_df.empty else []
    
    selected_metrics = st.multiselect(
        "Active Metrics",
        options=metric_cols,
        default=metric_cols[:4] if len(metric_cols) >= 4 else metric_cols,
        help="Select which Ragas metrics to visualize across the dashboard."
    )
    
    st.markdown("---")
    st.caption("🛠️ UTILITIES")
    
    col_tools1, col_tools2 = st.columns(2)
    with col_tools1:
         if st.button("🧪 Gen Data", use_container_width=True):
            st.session_state['show_generator'] = True
    with col_tools2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# ===============================
# Synthetic Data Generator View
# ===============================
if st.session_state.get('show_generator', False):
    st.markdown("## 🧬 Synthetic Test Data Factory")
    st.markdown("Generate high-quality Q&A test sets directly from your `fs11/` documents using Ragas + GPT-4o.")
    
    gen_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "testdata", "generated_testset.json")
    
    # Generator Controls
    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            test_size = st.slider("Samples to Generate", 1, 50, 5, help="More samples = longer generation time")
        with c2:
            st.write("") # Spacer
            st.write("") 
            if st.button("🚀 Start Engine", type="primary", use_container_width=True):
                with st.status("🏭 Constructing Dataset...", expanded=True) as status:
                    try:
                        st.write("Reading documents...")
                        import subprocess
                        result = subprocess.run(
                            ["python", "testDataFeaxtory.py", str(test_size)], 
                            capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        )
                        if result.returncode == 0:
                            status.update(label="✅ Generation Successful!", state="complete", expanded=False)
                            st.balloons()
                            if os.path.exists(gen_file):
                                st.session_state['gen_data_timestamp'] = datetime.now()
                        else:
                            status.update(label="❌ Generation Failed", state="error")
                            st.error(result.stderr)
                    except Exception as e:
                        st.error(f"Error: {e}")
        with c3:
            st.write("")
            st.write("")
            if st.button("✖️ Close Tool", use_container_width=True):
                st.session_state['show_generator'] = False
                st.rerun()

    # Review Section
    if os.path.exists(gen_file):
        st.markdown("### 🔍 Dataset Preview")
        try:
            gen_df = pd.read_json(gen_file)
            
            # Stats
            nm1, nm2, nm3 = st.columns(3)
            nm1.metric("Total Questions", len(gen_df))
            if "evolution_type" in gen_df.columns:
                 top_type = gen_df["evolution_type"].mode()[0] if not gen_df.empty else "N/A"
                 nm2.metric("Dominant Evolution", top_type)
            
            st.dataframe(
                gen_df,
                use_container_width=True,
                height=300,
                column_config={
                    "question": st.column_config.TextColumn("Question", width="large"),
                    "ground_truth": "Ground Truth",
                    "evolution_type": st.column_config.TextColumn("Type", width="small"),
                }
            )
            
            # Download
            st.download_button(
                "📥 Download JSON Dataset",
                data=gen_df.to_json(orient="records", indent=4),
                file_name="ragas_synthetic_data.json",
                mime="application/json"
            )
        except Exception as e:
            st.warning(f"Could not load data: {e}")
            
    st.stop()


# ===============================
# Main Dashboard View
# ===============================
if history_df.empty:
    st.info("👋 Welcome! Run `python evaluation/run_eval.py` to generate your first evaluation report.")
    st.stop()

# 1. Header Section
st.markdown("### 📊 Performance Overview")

latest_run = history_df.iloc[-1]
prev_run = history_df.iloc[-2] if len(history_df) > 1 else None

# 2. KPI Cards Row
col_kpi = st.columns(len(selected_metrics) + 1)
with col_kpi[0]:
    val = int(latest_run.get('total_samples', 0))
    delta = val - int(prev_run.get('total_samples', 0)) if prev_run is not None else 0
    render_metric_card("Total Samples", f"{val}", delta=delta)

for i, metric in enumerate(selected_metrics):
    with col_kpi[i+1]:
        val = latest_run.get(metric, 0)
        prev_val = prev_run.get(metric, 0) if prev_run is not None else 0
        delta = val - prev_val
        render_metric_card(metric.replace("_", " "), f"{val:.3f}", delta=delta)

st.markdown("<br>", unsafe_allow_html=True)

# 3. Main Content
tab_main, tab_dive, tab_comp = st.tabs(["📈 Velocity & Trends", "🔬 Failure Analysis", "⚔️ Model Comparison"])

with tab_main:
    st.markdown("#### Evaluation Velocity")
    
    if selected_metrics:
        # High-end Area Chart
        fig = go.Figure()
        
        colors = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b']
        
        for idx, metric in enumerate(selected_metrics):
            color = colors[idx % len(colors)]
            fig.add_trace(go.Scatter(
                x=history_df['timestamp'],
                y=history_df[metric],
                mode='lines+markers',
                name=metric.replace("_", " ").title(),
                line=dict(color=color, width=3, shape='spline'),
                fill='tozeroy',
                fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
                hovertemplate='<b>%{y:.4f}</b>'
            ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=0),
            height=350,
            hovermode="x unified",
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zeroline=False),
            legend=dict(orientation="h", y=1.1, x=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("#### Recent Runs History")
        display_df = history_df[["run_id", "timestamp"] + selected_metrics].sort_values("timestamp", ascending=False)
        st.dataframe(
            display_df.style.background_gradient(cmap="RdYlGn", subset=selected_metrics, axis=None, vmin=0, vmax=1),
            use_container_width=True,
            height=300
        )
    with c2:
        st.markdown("#### Aggregated Score Distribution")
        if selected_metrics:
            # Radar chart of latest run vs average
            avg_scores = history_df[selected_metrics].mean()
            latest_scores = history_df.iloc[-1][selected_metrics]
            
            fig_rad = go.Figure()
            fig_rad.add_trace(go.Scatterpolar(
                r=avg_scores.values,
                theta=[m.replace("_", " ").title() for m in selected_metrics],
                fill='toself',
                name='Average',
                line_color='#94a3b8'
            ))
            fig_rad.add_trace(go.Scatterpolar(
                r=latest_scores.values,
                theta=[m.replace("_", " ").title() for m in selected_metrics],
                fill='toself',
                name='Latest',
                line_color='#6366f1'
            ))
            fig_rad.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                polar=dict(radialaxis=dict(visible=True, range=[0, 1]))
            )
            st.plotly_chart(fig_rad, use_container_width=True)

with tab_dive:
    st.markdown("#### 🕵️ Deep Dive Inspection")
    
    col_sel, _ = st.columns([1, 2])
    with col_sel:
        run_id_select = st.selectbox("Select Run ID", history_df["run_id"].unique(), index=len(history_df)-1)
    
    details_path = os.path.join(RESULTS_DIR, f"{run_id_select}_details.csv")
    
    if os.path.exists(details_path):
        details_df = pd.read_csv(details_path)
        
        # Breakdown
        col_dist, col_worst = st.columns([1, 2])
        
        with col_dist:
             st.markdown("**Score Distribution**")
             if selected_metrics:
                dist_fig = px.box(
                    details_df, 
                    y=selected_metrics,
                    color_discrete_sequence=["#8b5cf6"]
                )
                dist_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=300,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                st.plotly_chart(dist_fig, use_container_width=True)

        with col_worst:
            st.markdown("**🚨 Critical Failures (Top 3)**")
            if selected_metrics:
                sort_metric = st.selectbox("Sort failures by:", options=selected_metrics, key="failure_sort")
                bad_examples = details_df.sort_values(sort_metric, ascending=True).head(3)
                
                for i, row in bad_examples.iterrows():
                     with st.expander(f"🔴 Score: {row[sort_metric]:.2f} | Q: {str(row['user_input'])[:60]}..."):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.caption("Prompt / Query")
                            st.info(row['user_input'])
                            st.caption("Model Response")
                            st.warning(row['response'])
                        with c2:
                            st.caption("Reference Truth")
                            st.success(row['reference'])
                            st.caption("Retrieved Context")
                            st.text_area("Context", value=str(row['retrieved_contexts'])[:400] + "...", height=100, disabled=True)

        st.markdown("---")
        st.markdown("**Full Trace Data**")
        st.dataframe(details_df, use_container_width=True)
    else:
        st.warning("No detailed trace logs available for this run.")

with tab_comp:
    st.markdown("#### ⚔️ A/B Comparison")
    
    c1, c2 = st.columns(2)
    with c1:
        base_run = st.selectbox("Base Baseline", history_df["run_id"], index=max(0, len(history_df)-2), key='base_sl')
    with c2:
        comp_run = st.selectbox("Challenger Model", history_df["run_id"], index=len(history_df)-1, key='comp_sl')
        
    run_base_data = history_df[history_df["run_id"] == base_run].iloc[0]
    run_comp_data = history_df[history_df["run_id"] == comp_run].iloc[0]
    
    # 1. Delta Cards
    st.markdown("<br>", unsafe_allow_html=True)
    d_cols = st.columns(len(selected_metrics))
    for i, m in enumerate(selected_metrics):
        base_val = run_base_data.get(m, 0)
        comp_val = run_comp_data.get(m, 0)
        diff = comp_val - base_val
        with d_cols[i]:
            render_metric_card(m.replace("_", " "), f"{comp_val:.3f}", delta=diff, delta_text="vs Base")

    # 2. Side by Side Chart
    st.markdown("<br>", unsafe_allow_html=True)
    categories = selected_metrics
    val_base = [run_base_data[m] for m in categories]
    val_comp = [run_comp_data[m] for m in categories]
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=categories,
        y=val_base,
        name=f"Base ({base_run})",
        marker_color='#cbd5e1'
    ))
    fig_comp.add_trace(go.Bar(
        x=categories,
        y=val_comp,
        name=f"Challenger ({comp_run})",
        marker_color='#6366f1'
    ))
    
    fig_comp.update_layout(
         template="plotly_dark",
         paper_bgcolor="rgba(0,0,0,0)",
         plot_bgcolor="rgba(0,0,0,0)",
         barmode='group',
         height=400
    )
    st.plotly_chart(fig_comp, use_container_width=True)
