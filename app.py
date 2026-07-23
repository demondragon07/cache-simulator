import streamlit as st
import pandas as pd
import plotly.express as px

from simulator import CacheSimulator
from utils import (
    read_trace,
    generate_random_trace,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Interactive Cache Simulator",
    page_icon="💾",
    layout="wide",
)

st.title("💾 Interactive Cache Simulator & Performance Analyzer")

st.markdown(
"""
Visualize how different cache replacement and write
policies affect system performance.

Supported Features

- LRU
- FIFO
- Write Through
- Write Back
- EMAT Calculation
- Interactive Step-by-Step Simulation
"""
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("⚙ Cache Configuration")

cache_size = st.sidebar.slider(
    "Cache Size (Lines)",
    min_value=2,
    max_value=16,
    value=4,
)

block_size = st.sidebar.selectbox(
    "Block Size (Bytes)",
    [1, 2, 4, 8, 16],
    index=2,
)

replacement_policy = st.sidebar.selectbox(
    "Replacement Policy",
    [
        "LRU",
        "FIFO",
    ],
)

write_policy = st.sidebar.selectbox(
    "Write Policy",
    [
        "Write Through",
        "Write Back",
    ],
)

hit_time = st.sidebar.number_input(
    "Cache Hit Time (ns)",
    min_value=1,
    value=1,
)

memory_time = st.sidebar.number_input(
    "Memory Access Time (ns)",
    min_value=10,
    value=100,
)

st.sidebar.markdown("---")

st.sidebar.info(
"""
Tip

Larger block sizes generally reduce compulsory misses but
may increase cache pollution.
"""
)

# --------------------------------------------------
# Memory Trace
# --------------------------------------------------

st.header("📂 Memory Access Trace")

left, right = st.columns(2)

trace = None

# Upload Trace File

with left:

    uploaded_file = st.file_uploader(
        "Upload Trace File",
        type=["txt"],
    )

    if uploaded_file is not None:

        trace = read_trace(uploaded_file)

        st.success(
            f"Loaded {len(trace)} memory accesses."
        )

# Random Trace

with right:

    random_length = st.slider(
        "Random Trace Length",
        min_value=10,
        max_value=100,
        value=20,
    )

    if st.button("🎲 Generate Random Trace"):

        trace = generate_random_trace(random_length)

        st.session_state["trace"] = trace

# Preserve generated trace

if trace is None:

    trace = st.session_state.get("trace")

# --------------------------------------------------
# Preview Trace
# --------------------------------------------------

if trace:

    trace_df = pd.DataFrame(
        trace,
        columns=[
            "Address",
            "Operation",
        ],
    )

    st.subheader("Trace Preview")

    st.dataframe(
        trace_df,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        f"Total Memory Accesses : {len(trace)}"
    )

    # ----------------------------------------------

    if st.button(
        "▶ Run Simulation",
        type="primary",
        use_container_width=True,
    ):

        simulator = CacheSimulator(
            cache_size=cache_size,
            block_size=block_size,
            replacement_policy=replacement_policy,
            write_policy=write_policy,
            hit_time=hit_time,
            memory_access_time=memory_time,
        )

        simulator.run(trace)

        summary = simulator.summary()

        history = simulator.history_dataframe()

        cache = simulator.cache_dataframe()

        config = simulator.get_configuration()

        st.session_state["simulator"] = simulator

        st.session_state["summary"] = summary

        st.session_state["history"] = history

        st.session_state["cache"] = cache

        st.session_state["config"] = config

else:

    st.warning(
        "Upload a trace file or generate a random trace."
    )

# --------------------------------------------------
# Display Simulation Results
# --------------------------------------------------

if "simulator" in st.session_state:

    simulator = st.session_state["simulator"]
    summary = st.session_state["summary"]
    history = st.session_state["history"]
    cache = st.session_state["cache"]

    st.markdown("---")

    st.header("📊 Performance Metrics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Cache Hits",
        summary["Hits"],
    )

    c2.metric(
        "Cache Misses",
        summary["Misses"],
    )

    c3.metric(
        "Hit Rate",
        f"{summary['Hit Rate']}%",
    )

    c4.metric(
        "Miss Rate",
        f"{summary['Miss Rate']}%",
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Memory Writes",
        summary["Memory Writes"],
    )

    c6.metric(
        "EMAT",
        f"{summary['EMAT']} ns",
    )

    c7.metric(
        "Cache Usage",
        summary["Cache Usage"],
    )

    c8.metric(
        "Occupancy",
        f"{summary['Occupancy (%)']}%",
    )

    st.markdown("---")

    # --------------------------------------------------
    # Charts
    # --------------------------------------------------

    left, right = st.columns([2, 1])

    with left:

        st.subheader("📦 Current Cache")

        def highlight_cache(row):

            if row["Dirty"]:

                return [
                    "background-color:#ffcccc"
                ] * len(row)

            if row["Valid"]:

                return [
                    "background-color:#d4edda"
                ] * len(row)

            return [""] * len(row)

        st.dataframe(
            cache.style.apply(
                highlight_cache,
                axis=1,
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "🟢 Valid Cache Line     🔴 Dirty Cache Line"
        )

    with right:

        st.subheader("📈 Hit vs Miss")

        fig = px.pie(
            values=[
                summary["Hits"],
                summary["Misses"],
            ],
            names=[
                "Hits",
                "Misses",
            ],
            hole=0.45,
        )

        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                t=40,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.markdown("---")

    # --------------------------------------------------
    # Step-by-Step Simulation
    # --------------------------------------------------

    st.header("📜 Step-by-Step Simulation")

    st.caption(
        "Expand any step to see exactly how the cache behaved."
    )

    history_records = simulator.get_history()

    def highlight_snapshot(row):

        if row["Dirty"]:

            return ["background-color:#ffcccc"] * len(row)

        if row["Valid"]:

            return ["background-color:#d4edda"] * len(row)

        return [""] * len(row)

    for step in history_records:

        title = (
            f"Step {step['Step']} | "
            f"{step['Operation']} | "
            f"Address {step['Address']}"
        )

        with st.expander(title):

            c1, c2 = st.columns(2)

            with c1:

                st.write(
                    f"**Memory Address:** {step['Address']}"
                )

                st.write(
                    f"**Block Number:** {step['Block']}"
                )

                st.write(
                    f"**Operation:** {step['Operation']}"
                )

            with c2:

                if step["Result"] == "Hit":

                    st.success("✅ Cache Hit")

                else:

                    st.error("❌ Cache Miss")

                st.write(
                    f"**Cache Line:** {step['Cache Line']}"
                )

                st.info(step["Action"])

            st.markdown("**Cache State After This Access**")

            snapshot = pd.DataFrame(
                step["Cache Snapshot"]
            )

            st.dataframe(
                snapshot.style.apply(
                    highlight_snapshot,
                    axis=1,
                ),
                use_container_width=True,
                hide_index=True,
            )

    # --------------------------------------------------
    # Complete Simulation History
    # --------------------------------------------------

    st.markdown("---")

    st.header("📑 Simulation History")

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # Download Reports
    # --------------------------------------------------

    st.markdown("---")

    st.header("📥 Export Reports")

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(
            label="📄 Download History (CSV)",
            data=simulator.export_history_csv(),
            file_name="simulation_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with c2:

        st.download_button(
            label="📊 Download Summary (CSV)",
            data=simulator.export_summary_csv(),
            file_name="simulation_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # --------------------------------------------------
    # Cache Configuration
    # --------------------------------------------------

    st.markdown("---")

    st.header("⚙ Cache Configuration")

    config_df = simulator.configuration_dataframe()

    st.dataframe(
        config_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # Memory Hierarchy
    # --------------------------------------------------

    st.markdown("---")

    st.header("🖥 Memory Hierarchy")

    st.graphviz_chart("""
    digraph G{

    rankdir=TB;

    node [shape=box style=filled fillcolor=lightblue];

    CPU;

    Cache;

    Memory;

    CPU->Cache;

    Cache->Memory;

    }
    """)

    # --------------------------------------------------
    # EMAT
    # --------------------------------------------------

    st.markdown("---")

    st.header("📘 Effective Memory Access Time")

    st.latex(
    r"EMAT = HitTime + MissRate \times MemoryAccessTime"
    )

    st.info(
    f"""
    Using current values

    Hit Time = **{summary['Hit Time']} ns**

    Miss Rate = **{summary['Miss Rate']} %**

    Memory Access Time = **{summary['Memory Access Time']} ns**

    Therefore,

    **EMAT = {summary['EMAT']} ns**
    """
    )

    # --------------------------------------------------
    # Footer
    # --------------------------------------------------

    st.markdown("---")

    st.markdown(
    """
    ### 💾 Interactive Cache Simulator & Performance Analyzer

    Built using

    - Python
    - Streamlit
    - Plotly
    - Pandas

    Features

    - LRU Replacement
    - FIFO Replacement
    - Write Through
    - Write Back
    - Block Mapping
    - Dirty Bit
    - EMAT
    - Step-by-Step Simulation
    """
    )
