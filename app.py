import streamlit as st
import numpy as np
import math
import plotly.graph_objects as go
import joblib
import pandas as pd
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart AI Wireless Network Simulator",
    page_icon="📡",
    layout="wide"
)


# ============================================================
# LOAD AI MODEL
# ============================================================

MODEL_FILE = "models/wireless_model.pkl"

try:
    model = joblib.load(MODEL_FILE)
    model_loaded = True

except Exception:
    model = None
    model_loaded = False


# ============================================================
# SESSION STATE
# ============================================================

if "simulation_history" not in st.session_state:
    st.session_state.simulation_history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ============================================================
# WIRELESS CALCULATION FUNCTIONS
# ============================================================

def calculate_path_loss(distance_m, frequency_ghz):
    """
    Calculate Free Space Path Loss (FSPL).
    """

    distance_m = max(distance_m, 1)

    distance_km = distance_m / 1000

    frequency_mhz = frequency_ghz * 1000

    path_loss = (
        32.44
        + 20 * math.log10(distance_km)
        + 20 * math.log10(frequency_mhz)
    )

    return path_loss


def calculate_received_power(transmit_power, path_loss):
    """
    Calculate received signal power.
    """

    return transmit_power - path_loss


def calculate_interference(users, nodes):
    """
    Simplified educational interference model.
    """

    user_interference = users * 1.2

    node_interference = nodes * 0.5

    interference = (
        user_interference
        + node_interference
    )

    return min(interference, 100)


def calculate_snr(received_power, noise_power, interference):
    """
    Calculate Signal-to-Noise Ratio.
    """

    interference_penalty = (
        interference * 0.20
    )

    effective_noise = (
        noise_power
        + interference_penalty
    )

    snr = (
        received_power
        - effective_noise
    )

    return snr


def calculate_packet_loss(snr, users):
    """
    Calculate simplified packet loss.
    """

    if snr >= 25:

        base_loss = 1

    elif snr >= 15:

        base_loss = 5

    elif snr >= 8:

        base_loss = 12

    else:

        base_loss = 25

    congestion = max(
        0,
        (users - 10) * 0.3
    )

    packet_loss = (
        base_loss
        + congestion
    )

    return min(
        packet_loss,
        50
    )


def calculate_throughput(
    bandwidth_mhz,
    snr,
    users
):
    """
    Calculate simplified wireless throughput.
    """

    if snr >= 25:

        efficiency = 4.5

    elif snr >= 15:

        efficiency = 3.0

    elif snr >= 8:

        efficiency = 1.5

    else:

        efficiency = 0.5

    total_throughput = (
        bandwidth_mhz
        * efficiency
    )

    throughput = (
        total_throughput
        / max(users, 1)
    )

    return throughput


def calculate_latency(users, packet_loss):
    """
    Calculate simplified network latency.
    """

    return (
        10
        + users * 1.5
        + packet_loss * 2
    )


# ============================================================
# SIGNAL QUALITY
# ============================================================

def get_signal_quality(received_power):

    if received_power >= -50:

        return "Excellent", "🟢"

    elif received_power >= -65:

        return "Good", "🟢"

    elif received_power >= -75:

        return "Moderate", "🟡"

    else:

        return "Weak", "🔴"


# ============================================================
# NETWORK HEALTH SCORE
# ============================================================

def calculate_health_score(
    snr,
    packet_loss,
    throughput,
    latency
):

    snr_score = min(
        max((snr / 30) * 100, 0),
        100
    )

    loss_score = max(
        0,
        100 - packet_loss * 4
    )

    throughput_score = min(
        max((throughput / 10) * 100, 0),
        100
    )

    latency_score = max(
        0,
        100 - latency * 0.8
    )

    score = (
        snr_score * 0.35
        + loss_score * 0.25
        + throughput_score * 0.20
        + latency_score * 0.20
    )

    return round(
        max(0, min(score, 100)),
        1
    )


def health_label(score):

    if score >= 80:

        return "Excellent", "🟢"

    elif score >= 60:

        return "Good", "🟢"

    elif score >= 40:

        return "Moderate", "🟡"

    else:

        return "Poor", "🔴"


# ============================================================
# NETWORK TOPOLOGY
# ============================================================

def create_network_topology(
    num_nodes,
    distance,
    transmit_power,
    frequency_ghz
):

    # Access Point
    ap_x = 0
    ap_y = 0

    # Node positions
    angles = np.linspace(
        0,
        2 * np.pi,
        num_nodes,
        endpoint=False
    )

    radius = distance

    node_x = (
        radius
        * np.cos(angles)
    )

    node_y = (
        radius
        * np.sin(angles)
    )

    # Create figure
    fig = go.Figure()

    # --------------------------------------------------------
    # Coverage Circle
    # --------------------------------------------------------

    coverage_radius = (
        distance * 1.15
    )

    theta = np.linspace(
        0,
        2 * np.pi,
        200
    )

    circle_x = (
        coverage_radius
        * np.cos(theta)
    )

    circle_y = (
        coverage_radius
        * np.sin(theta)
    )

    fig.add_trace(
        go.Scatter(
            x=circle_x,
            y=circle_y,
            mode="lines",
            line=dict(
                width=2,
                dash="dash"
            ),
            name="Coverage Area",
            hoverinfo="skip"
        )
    )

    # --------------------------------------------------------
    # Signal Colors
    # --------------------------------------------------------

    signal_colors = []

    signal_labels = []

    for x, y in zip(
        node_x,
        node_y
    ):

        node_distance = math.sqrt(
            x ** 2
            + y ** 2
        )

        path_loss = calculate_path_loss(
            node_distance,
            frequency_ghz
        )

        received_power = (
            calculate_received_power(
                transmit_power,
                path_loss
            )
        )

        quality, icon = (
            get_signal_quality(
                received_power
            )
        )

        signal_labels.append(
            f"{icon} {quality}<br>"
            f"Power: "
            f"{received_power:.1f} dBm"
        )

        if quality == "Excellent":

            signal_colors.append("green")

        elif quality == "Good":

            signal_colors.append("lightgreen")

        elif quality == "Moderate":

            signal_colors.append("orange")

        else:

            signal_colors.append("red")

    # --------------------------------------------------------
    # Connection Lines
    # --------------------------------------------------------

    for x, y in zip(
        node_x,
        node_y
    ):

        fig.add_trace(
            go.Scatter(
                x=[ap_x, x],
                y=[ap_y, y],
                mode="lines",
                line=dict(
                    width=1,
                    dash="dot"
                ),
                hoverinfo="skip",
                showlegend=False
            )
        )

    # --------------------------------------------------------
    # Access Point
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=[ap_x],
            y=[ap_y],
            mode="markers+text",
            marker=dict(
                size=30,
                symbol="diamond"
            ),
            text=[
                "📡 Access Point"
            ],
            textposition="top center",
            name="Access Point"
        )
    )

    # --------------------------------------------------------
    # Wireless Nodes
    # --------------------------------------------------------

    labels = [
        f"Node {i + 1}"
        for i in range(num_nodes)
    ]

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(
                size=20,
                color=signal_colors
            ),
            text=labels,
            textposition="bottom center",
            customdata=signal_labels,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "%{customdata}"
                "<extra></extra>"
            ),
            name="Wireless Nodes"
        )
    )

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    margin = distance * 1.5

    fig.update_layout(

        title=(
            "📡 Wireless Network Topology "
            "& Signal Strength"
        ),

        xaxis_title="X Position (m)",

        yaxis_title="Y Position (m)",

        height=560,

        template="plotly_white",

        xaxis=dict(
            range=[
                -margin,
                margin
            ],
            scaleanchor="y",
            scaleratio=1
        ),

        yaxis=dict(
            range=[
                -margin,
                margin
            ]
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


# ============================================================
# PERFORMANCE GRAPH
# ============================================================

def create_performance_graph(
    throughput,
    packet_loss,
    latency,
    snr
):

    metrics = [
        "Throughput",
        "SNR",
        "Packet Loss",
        "Latency"
    ]

    values = [
        throughput,
        snr,
        packet_loss,
        latency
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=metrics,
            y=values,
            text=[
                f"{throughput:.2f}",
                f"{snr:.2f}",
                f"{packet_loss:.2f}",
                f"{latency:.2f}"
            ],
            textposition="auto"
        )
    )

    fig.update_layout(

        title="📊 Network Performance",

        yaxis_title="Value",

        height=400,

        template="plotly_white"
    )

    return fig


# ============================================================
# AI PREDICTION
# ============================================================

def predict_network_status(

    nodes,
    users,
    distance,
    frequency,
    bandwidth,
    path_loss,
    received_power,
    interference,
    snr,
    packet_loss,
    throughput,
    latency

):

    features = [

        nodes,
        users,
        distance,
        frequency,
        bandwidth,
        path_loss,
        received_power,
        interference,
        snr,
        packet_loss,
        throughput,
        latency

    ]

    feature_names = [

        "nodes",
        "users",
        "distance_m",
        "frequency_ghz",
        "bandwidth_mhz",
        "path_loss_db",
        "received_power_dbm",
        "interference",
        "snr_db",
        "packet_loss_percent",
        "throughput_mbps",
        "latency_ms"

    ]

    input_data = {

        name: [value]

        for name, value in zip(
            feature_names,
            features
        )

    }

    input_df = pd.DataFrame(
        input_data
    )

    prediction = model.predict(
        input_df
    )[0]

    probabilities = (
        model.predict_proba(
            input_df
        )[0]
    )

    classes = model.classes_

    probability_dict = {

        cls: prob

        for cls, prob in zip(
            classes,
            probabilities
        )

    }

    confidence = (
        max(probabilities)
        * 100
    )

    return (
        prediction,
        confidence,
        probability_dict
    )


# ============================================================
# AI OPTIMIZATION ENGINE
# ============================================================

def generate_ai_optimization(

    prediction,
    users,
    nodes,
    distance,
    bandwidth,
    frequency,
    snr,
    packet_loss,
    throughput,
    latency,
    interference

):

    # GOOD NETWORK
    if prediction == "GOOD":

        return {

            "issue":
                "No major network issue detected.",

            "recommendation":
                (
                    "The wireless network is operating "
                    "efficiently. No immediate "
                    "optimization is required."
                ),

            "action":
                "Maintain current configuration.",

            "priority":
                "LOW"
        }

    # HIGH USERS
    if users >= 60:

        next_bandwidth = min(
            bandwidth * 2,
            80
        )

        return {

            "issue":
                (
                    "High number of active users "
                    "is causing network congestion."
                ),

            "recommendation":
                (
                    f"Reduce active users or increase "
                    f"bandwidth from {bandwidth} MHz "
                    f"to {next_bandwidth} MHz."
                ),

            "action":
                "Increase bandwidth / reduce users",

            "priority":
                "HIGH"
        }

    # LARGE DISTANCE
    if distance >= 250:

        return {

            "issue":
                (
                    "Large distance between the "
                    "access point and wireless nodes."
                ),

            "recommendation":
                (
                    "Move devices closer to the "
                    "access point or deploy an "
                    "additional access point."
                ),

            "action":
                "Reduce distance / add AP",

            "priority":
                "HIGH"
        }

    # HIGH INTERFERENCE
    if interference >= 50:

        return {

            "issue":
                (
                    "High wireless interference is "
                    "reducing network performance."
                ),

            "recommendation":
                (
                    "Reduce channel contention, "
                    "decrease active users, or "
                    "consider changing the wireless channel."
                ),

            "action":
                "Reduce interference",

            "priority":
                "HIGH"
        }

    # LOW SNR
    if snr < 10:

        return {

            "issue":
                "Low Signal-to-Noise Ratio detected.",

            "recommendation":
                (
                    "Improve signal quality by reducing "
                    "distance, increasing signal strength, "
                    "or reducing interference."
                ),

            "action":
                "Improve signal quality",

            "priority":
                "HIGH"
        }

    # HIGH PACKET LOSS
    if packet_loss >= 15:

        return {

            "issue":
                (
                    "High packet loss is affecting "
                    "wireless communication reliability."
                ),

            "recommendation":
                (
                    "Reduce network load and improve "
                    "wireless signal quality."
                ),

            "action":
                "Reduce packet loss",

            "priority":
                "MEDIUM"
        }

    # HIGH LATENCY
    if latency >= 100:

        return {

            "issue":
                "High network latency detected.",

            "recommendation":
                (
                    "Reduce active users and network "
                    "congestion to improve response time."
                ),

            "action":
                "Reduce latency",

            "priority":
                "MEDIUM"
        }

    # LOW THROUGHPUT
    if throughput < 2:

        return {

            "issue":
                "Low network throughput detected.",

            "recommendation":
                (
                    "Increase available bandwidth or "
                    "reduce the number of active users."
                ),

            "action":
                "Improve throughput",

            "priority":
                "MEDIUM"
        }

    # DEFAULT
    return {

        "issue":
            "Moderate wireless network degradation.",

        "recommendation":
            (
                "Consider increasing bandwidth, "
                "reducing active users, or improving "
                "signal conditions."
            ),

        "action":
            "Optimize network configuration",

        "priority":
            "MEDIUM"
    }


# ============================================================
# AUTOMATIC AI OPTIMIZATION SIMULATION
# ============================================================

def simulate_ai_optimization(

    users,
    nodes,
    distance,
    bandwidth,
    frequency,
    prediction

):

    optimized_users = users

    optimized_nodes = nodes

    optimized_distance = distance

    optimized_bandwidth = bandwidth

    if prediction == "CONGESTED":

        optimized_users = max(
            1,
            int(users * 0.5)
        )

        optimized_bandwidth = min(
            bandwidth * 2,
            80
        )

        optimized_distance = max(
            10,
            int(distance * 0.8)
        )

    elif prediction == "MODERATE":

        optimized_users = max(
            1,
            int(users * 0.75)
        )

        optimized_bandwidth = min(
            bandwidth * 1.5,
            80
        )

        optimized_distance = max(
            10,
            int(distance * 0.9)
        )

    optimized_path_loss = (
        calculate_path_loss(
            optimized_distance,
            frequency
        )
    )

    optimized_received_power = (
        calculate_received_power(
            20,
            optimized_path_loss
        )
    )

    optimized_interference = (
        calculate_interference(
            optimized_users,
            optimized_nodes
        )
    )

    optimized_snr = calculate_snr(
        optimized_received_power,
        -90,
        optimized_interference
    )

    optimized_packet_loss = (
        calculate_packet_loss(
            optimized_snr,
            optimized_users
        )
    )

    optimized_throughput = (
        calculate_throughput(
            optimized_bandwidth,
            optimized_snr,
            optimized_users
        )
    )

    optimized_latency = (
        calculate_latency(
            optimized_users,
            optimized_packet_loss
        )
    )

    # Run optimized state through Random Forest
    optimized_prediction = None

    if model_loaded:

        optimized_prediction, _, _ = (
            predict_network_status(

                optimized_nodes,
                optimized_users,
                optimized_distance,
                frequency,
                optimized_bandwidth,
                optimized_path_loss,
                optimized_received_power,
                optimized_interference,
                optimized_snr,
                optimized_packet_loss,
                optimized_throughput,
                optimized_latency

            )
        )

    return {

        "users":
            optimized_users,

        "nodes":
            optimized_nodes,

        "distance":
            optimized_distance,

        "bandwidth":
            optimized_bandwidth,

        "snr":
            optimized_snr,

        "packet_loss":
            optimized_packet_loss,

        "throughput":
            optimized_throughput,

        "latency":
            optimized_latency,

        "status":
            optimized_prediction
            if optimized_prediction
            else "N/A"

    }


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title(
    "📡 Smart AI-Based Wireless Network Simulator"
)

st.caption(
    "AI-assisted wireless communication simulation, "
    "network analysis, performance monitoring and optimization."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "⚙️ Network Configuration"
)


num_nodes = st.sidebar.slider(

    "Number of Nodes",

    min_value=2,

    max_value=30,

    value=10

)


num_users = st.sidebar.slider(

    "Number of Users",

    min_value=1,

    max_value=100,

    value=10

)


distance = st.sidebar.slider(

    "Distance Between Nodes (meters)",

    min_value=10,

    max_value=500,

    value=50

)


bandwidth_option = st.sidebar.selectbox(

    "Bandwidth",

    [

        "5 MHz",

        "10 MHz",

        "20 MHz",

        "40 MHz",

        "80 MHz"

    ]

)


frequency_option = st.sidebar.selectbox(

    "Frequency",

    [

        "2.4 GHz",

        "5 GHz"

    ]

)


bandwidth_mhz = int(

    bandwidth_option.replace(
        " MHz",
        ""
    )

)


frequency_ghz = float(

    frequency_option.replace(
        " GHz",
        ""
    )

)


st.sidebar.divider()


simulate = st.sidebar.button(

    "🚀 Start Simulation",

    use_container_width=True

)


# ============================================================
# NETWORK CONFIGURATION
# ============================================================

st.subheader(
    "📊 Network Configuration"
)


col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "Nodes",
        num_nodes
    )


with col2:

    st.metric(
        "Users",
        num_users
    )


with col3:

    st.metric(
        "Distance",
        f"{distance} m"
    )


with col4:

    st.metric(
        "Bandwidth",
        bandwidth_option
    )


# ============================================================
# RUN SIMULATION
# ============================================================

if simulate:

    transmit_power = 20

    noise_power = -90


    # --------------------------------------------------------
    # PATH LOSS
    # --------------------------------------------------------

    path_loss = calculate_path_loss(

        distance,

        frequency_ghz

    )


    # --------------------------------------------------------
    # RECEIVED POWER
    # --------------------------------------------------------

    received_power = (
        calculate_received_power(

            transmit_power,

            path_loss

        )
    )


    # --------------------------------------------------------
    # INTERFERENCE
    # --------------------------------------------------------

    interference = (
        calculate_interference(

            num_users,

            num_nodes

        )
    )


    # --------------------------------------------------------
    # SNR
    # --------------------------------------------------------

    snr = calculate_snr(

        received_power,

        noise_power,

        interference

    )


    # --------------------------------------------------------
    # PACKET LOSS
    # --------------------------------------------------------

    packet_loss = calculate_packet_loss(

        snr,

        num_users

    )


    # --------------------------------------------------------
    # THROUGHPUT
    # --------------------------------------------------------

    throughput = calculate_throughput(

        bandwidth_mhz,

        snr,

        num_users

    )


    # --------------------------------------------------------
    # LATENCY
    # --------------------------------------------------------

    latency = calculate_latency(

        num_users,

        packet_loss

    )


    # --------------------------------------------------------
    # SIGNAL QUALITY
    # --------------------------------------------------------

    signal_quality, signal_icon = (
        get_signal_quality(
            received_power
        )
    )


    # --------------------------------------------------------
    # HEALTH SCORE
    # --------------------------------------------------------

    health_score = calculate_health_score(

        snr,

        packet_loss,

        throughput,

        latency

    )


    health_text, health_icon = (
        health_label(
            health_score
        )
    )


    # --------------------------------------------------------
    # AI PREDICTION
    # --------------------------------------------------------

    prediction = None

    confidence = 0

    probabilities = {}


    if model_loaded:

        (
            prediction,
            confidence,
            probabilities

        ) = predict_network_status(

            num_nodes,

            num_users,

            distance,

            frequency_ghz,

            bandwidth_mhz,

            path_loss,

            received_power,

            interference,

            snr,

            packet_loss,

            throughput,

            latency

        )


    # --------------------------------------------------------
    # AI OPTIMIZATION
    # --------------------------------------------------------

    optimization = None


    if prediction is not None:

        optimization = (
            generate_ai_optimization(

                prediction=prediction,

                users=num_users,

                nodes=num_nodes,

                distance=distance,

                bandwidth=bandwidth_mhz,

                frequency=frequency_ghz,

                snr=snr,

                packet_loss=packet_loss,

                throughput=throughput,

                latency=latency,

                interference=interference

            )
        )


    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    run_number = (
        len(
            st.session_state
            .simulation_history
        ) + 1
    )


    simulation_record = {

        "Run":
            run_number,

        "Date & Time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Nodes":
            num_nodes,

        "Users":
            num_users,

        "Distance (m)":
            distance,

        "Bandwidth (MHz)":
            bandwidth_mhz,

        "Frequency (GHz)":
            frequency_ghz,

        "SNR (dB)":
            round(snr, 2),

        "Throughput (Mbps)":
            round(throughput, 2),

        "Packet Loss (%)":
            round(packet_loss, 2),

        "Latency (ms)":
            round(latency, 2),

        "Interference":
            round(interference, 2),

        "AI Status":
            prediction
            if prediction
            else "N/A",

        "Health Score":
            health_score

    }


    st.session_state.simulation_history.append(
        simulation_record
    )


    # --------------------------------------------------------
    # SAVE LAST RESULT
    # --------------------------------------------------------

    st.session_state.last_result = {

        "transmit_power":
            transmit_power,

        "noise_power":
            noise_power,

        "path_loss":
            path_loss,

        "received_power":
            received_power,

        "interference":
            interference,

        "snr":
            snr,

        "packet_loss":
            packet_loss,

        "throughput":
            throughput,

        "latency":
            latency,

        "signal_quality":
            signal_quality,

        "signal_icon":
            signal_icon,

        "health_score":
            health_score,

        "health_text":
            health_text,

        "health_icon":
            health_icon,

        "prediction":
            prediction,

        "confidence":
            confidence,

        "probabilities":
            probabilities,

        "optimization":
            optimization,

        "nodes":
            num_nodes,

        "users":
            num_users,

        "distance":
            distance,

        "bandwidth":
            bandwidth_mhz,

        "frequency":
            frequency_ghz

    }


# ============================================================
# DISPLAY LAST RESULT
# ============================================================

if st.session_state.last_result:

    r = (
        st.session_state
        .last_result
    )


    # ========================================================
    # RESULTS
    # ========================================================

    st.divider()

    st.subheader(
        "📡 Wireless Simulation Results"
    )


    # ========================================================
    # MAIN KPI CARDS
    # ========================================================

    k1, k2, k3, k4, k5 = (
        st.columns(5)
    )


    with k1:

        st.metric(

            "SNR",

            f"{r['snr']:.2f} dB"

        )


    with k2:

        st.metric(

            "Throughput",

            f"{r['throughput']:.2f} Mbps"

        )


    with k3:

        st.metric(

            "Packet Loss",

            f"{r['packet_loss']:.2f}%"

        )


    with k4:

        st.metric(

            "Latency",

            f"{r['latency']:.2f} ms"

        )


    with k5:

        st.metric(

            "Network Health",

            f"{r['health_score']:.1f}/100"

        )


    # ========================================================
    # HEALTH STATUS
    # ========================================================

    if r["health_score"] >= 80:

        st.success(

            f"{r['health_icon']} "
            f"Network Health: "
            f"{r['health_text']} — "
            f"Score {r['health_score']}/100"

        )

    elif r["health_score"] >= 40:

        st.warning(

            f"{r['health_icon']} "
            f"Network Health: "
            f"{r['health_text']} — "
            f"Score {r['health_score']}/100"

        )

    else:

        st.error(

            f"{r['health_icon']} "
            f"Network Health: "
            f"{r['health_text']} — "
            f"Score {r['health_score']}/100"

        )


    # ========================================================
    # ADDITIONAL RF PARAMETERS
    # ========================================================

    p1, p2, p3, p4 = (
        st.columns(4)
    )


    with p1:

        st.metric(

            "Received Power",

            f"{r['received_power']:.2f} dBm"

        )


    with p2:

        st.metric(

            "Path Loss",

            f"{r['path_loss']:.2f} dB"

        )


    with p3:

        st.metric(

            "Interference",

            f"{r['interference']:.1f}"

        )


    with p4:

        st.metric(

            "Signal Quality",

            f"{r['signal_icon']} "
            f"{r['signal_quality']}"

        )


    # ========================================================
    # AI NETWORK PREDICTION
    # ========================================================

    st.divider()

    st.subheader(
        "🤖 AI Network Prediction"
    )


    if model_loaded and r["prediction"]:

        prediction = r["prediction"]


        if prediction == "GOOD":

            st.success(
                "🟢 AI Prediction: GOOD"
            )

        elif prediction == "MODERATE":

            st.warning(
                "🟡 AI Prediction: MODERATE"
            )

        else:

            st.error(
                "🔴 AI Prediction: CONGESTED"
            )


        st.metric(

            "AI Confidence",

            f"{r['confidence']:.2f}%"

        )


        probability_col1, probability_col2, probability_col3 = (
            st.columns(3)
        )


        with probability_col1:

            st.metric(

                "GOOD",

                f"{r['probabilities'].get('GOOD', 0) * 100:.2f}%"

            )


        with probability_col2:

            st.metric(

                "MODERATE",

                f"{r['probabilities'].get('MODERATE', 0) * 100:.2f}%"

            )


        with probability_col3:

            st.metric(

                "CONGESTED",

                f"{r['probabilities'].get('CONGESTED', 0) * 100:.2f}%"

            )


    else:

        st.error(
            "AI model could not be loaded."
        )

        st.info(

            "Make sure "
            "`models/wireless_model.pkl` "
            "exists and run "
            "`train_model.py`."

        )


    # ========================================================
    # AI OPTIMIZATION
    # ========================================================

    if r["optimization"]:

        opt = r["optimization"]


        st.divider()

        st.subheader(
            "💡 AI Network Optimization"
        )


        opt_col1, opt_col2, opt_col3 = (
            st.columns(3)
        )


        with opt_col1:

            st.metric(

                "Priority",

                opt["priority"]

            )


        with opt_col2:

            st.metric(

                "Action",

                opt["action"]

            )


        with opt_col3:

            st.metric(

                "AI Status",

                r["prediction"]

            )


        if opt["priority"] == "HIGH":

            st.error(

                f"🔍 Main Issue: "
                f"{opt['issue']}"

            )

        elif opt["priority"] == "MEDIUM":

            st.warning(

                f"🔍 Main Issue: "
                f"{opt['issue']}"

            )

        else:

            st.success(

                f"🔍 Main Issue: "
                f"{opt['issue']}"

            )


        st.info(

            f"💡 Recommendation: "
            f"{opt['recommendation']}"

        )


    # ========================================================
    # AUTOMATIC AI OPTIMIZATION
    # ========================================================

    if r["prediction"]:

        st.divider()

        st.subheader(
            "⚡ Automatic AI Optimization Simulation"
        )


        st.caption(

            "Educational simulation only — "
            "this does not modify real "
            "wireless hardware or network settings."

        )


        optimized = (
            simulate_ai_optimization(

                r["users"],

                r["nodes"],

                r["distance"],

                r["bandwidth"],

                r["frequency"],

                r["prediction"]

            )
        )


        comparison_table = pd.DataFrame({

            "Metric": [

                "Users",

                "Bandwidth (MHz)",

                "Distance (m)",

                "SNR (dB)",

                "Throughput (Mbps)",

                "Packet Loss (%)",

                "Latency (ms)"

            ],

            "Before": [

                r["users"],

                r["bandwidth"],

                r["distance"],

                round(r["snr"], 2),

                round(r["throughput"], 2),

                round(r["packet_loss"], 2),

                round(r["latency"], 2)

            ],

            "After": [

                optimized["users"],

                optimized["bandwidth"],

                optimized["distance"],

                round(
                    optimized["snr"],
                    2
                ),

                round(
                    optimized["throughput"],
                    2
                ),

                round(
                    optimized["packet_loss"],
                    2
                ),

                round(
                    optimized["latency"],
                    2
                )

            ]

        })


        st.dataframe(

            comparison_table,

            use_container_width=True,

            hide_index=True

        )


        # ----------------------------------------------------
        # HEALTH BEFORE / AFTER
        # ----------------------------------------------------

        before_score = (
            r["health_score"]
        )


        after_score = (
            calculate_health_score(

                optimized["snr"],

                optimized["packet_loss"],

                optimized["throughput"],

                optimized["latency"]

            )
        )


        ac1, ac2, ac3 = (
            st.columns(3)
        )


        with ac1:

            st.metric(

                "Before Health",

                f"{before_score}/100"

            )


        with ac2:

            st.metric(

                "After Health",

                f"{after_score}/100",

                delta=(
                    f"{after_score - before_score:.1f}"
                )

            )


        with ac3:

            st.metric(

                "Optimized AI Status",

                optimized["status"]

            )


        # ----------------------------------------------------
        # OPTIMIZATION GRAPH
        # ----------------------------------------------------

        chart_metrics = [

            "SNR",

            "Throughput",

            "Packet Loss",

            "Latency"

        ]


        before_values = [

            r["snr"],

            r["throughput"],

            r["packet_loss"],

            r["latency"]

        ]


        after_values = [

            optimized["snr"],

            optimized["throughput"],

            optimized["packet_loss"],

            optimized["latency"]

        ]


        fig_opt = go.Figure()


        fig_opt.add_trace(

            go.Bar(

                name="Before",

                x=chart_metrics,

                y=before_values

            )

        )


        fig_opt.add_trace(

            go.Bar(

                name="After",

                x=chart_metrics,

                y=after_values

            )

        )


        fig_opt.update_layout(

            title=(
                "Before vs After "
                "AI Optimization"
            ),

            barmode="group",

            height=430,

            template="plotly_white"

        )


        st.plotly_chart(

            fig_opt,

            use_container_width=True

        )


    # ========================================================
    # WIRELESS PARAMETERS
    # ========================================================

    st.divider()

    st.subheader(
        "📐 Wireless Parameters"
    )


    detail1, detail2, detail3, detail4 = (
        st.columns(4)
    )


    with detail1:

        st.metric(

            "Transmit Power",

            f"{r['transmit_power']} dBm"

        )


    with detail2:

        st.metric(

            "Noise Power",

            f"{r['noise_power']} dBm"

        )


    with detail3:

        st.metric(

            "Frequency",

            f"{r['frequency']} GHz"

        )


    with detail4:

        st.metric(

            "Bandwidth",

            f"{r['bandwidth']} MHz"

        )


    # ========================================================
    # NETWORK TOPOLOGY
    # ========================================================

    st.divider()

    st.subheader(
        "🌐 Wireless Network Topology"
    )


    topology = (
        create_network_topology(

            r["nodes"],

            r["distance"],

            r["transmit_power"],

            r["frequency"]

        )
    )


    st.plotly_chart(

        topology,

        use_container_width=True

    )


    st.markdown(

        """
### 📶 Signal Strength

🟢 **Excellent / Good** — Strong wireless signal

🟡 **Moderate** — Signal degradation possible

🔴 **Weak** — Poor wireless connection

⭕ **Dashed Circle** — Approximate wireless coverage area
"""

    )


    # ========================================================
    # PERFORMANCE ANALYSIS
    # ========================================================

    st.divider()

    st.subheader(
        "📈 Performance Analysis"
    )


    performance_graph = (
        create_performance_graph(

            r["throughput"],

            r["packet_loss"],

            r["latency"],

            r["snr"]

        )
    )


    st.plotly_chart(

        performance_graph,

        use_container_width=True

    )


else:

    st.info(

        "Configure the wireless network "
        "parameters from the sidebar and "
        "click **🚀 Start Simulation**."

    )


# ============================================================
# SIMULATION HISTORY
# ============================================================

st.divider()

st.subheader(
    "📜 Simulation History"
)


if st.session_state.simulation_history:

    history_df = pd.DataFrame(

        st.session_state
        .simulation_history

    )


    st.dataframe(

        history_df,

        use_container_width=True,

        hide_index=True

    )


    # --------------------------------------------------------
    # HISTORY SUMMARY
    # --------------------------------------------------------

    h1, h2, h3 = (
        st.columns(3)
    )


    with h1:

        st.metric(

            "Total Simulations",

            len(history_df)

        )


    with h2:

        good_count = int(

            (
                history_df["AI Status"]
                == "GOOD"
            ).sum()

        )

        st.metric(

            "GOOD Runs",

            good_count

        )


    with h3:

        avg_score = (
            history_df["Health Score"]
            .mean()
        )

        st.metric(

            "Average Health",

            f"{avg_score:.1f}/100"

        )


    # ========================================================
    # SIMULATION COMPARISON
    # ========================================================

    if len(history_df) >= 2:

        st.subheader(
            "📊 Simulation Comparison"
        )


        selected_runs = st.multiselect(

            "Select runs to compare",

            options=(
                history_df["Run"]
                .tolist()
            ),

            default=(
                history_df["Run"]
                .tolist()[
                    -min(
                        3,
                        len(history_df)
                    ):
                ]
            )

        )


        if selected_runs:

            comparison_df = (
                history_df[
                    history_df["Run"]
                    .isin(selected_runs)
                ]
                .copy()
            )


            st.dataframe(

                comparison_df,

                use_container_width=True,

                hide_index=True

            )


            cc1, cc2 = (
                st.columns(2)
            )


            # ------------------------------------------------
            # SNR
            # ------------------------------------------------

            with cc1:

                fig_snr = go.Figure()

                fig_snr.add_trace(

                    go.Bar(

                        x=(
                            comparison_df[
                                "Run"
                            ]
                            .astype(str)
                        ),

                        y=(
                            comparison_df[
                                "SNR (dB)"
                            ]
                        ),

                        text=(
                            comparison_df[
                                "SNR (dB)"
                            ]
                        ),

                        textposition="auto"

                    )

                )


                fig_snr.update_layout(

                    title="SNR Comparison",

                    xaxis_title="Run",

                    yaxis_title="SNR (dB)",

                    template="plotly_white"

                )


                st.plotly_chart(

                    fig_snr,

                    use_container_width=True

                )


            # ------------------------------------------------
            # THROUGHPUT
            # ------------------------------------------------

            with cc2:

                fig_tp = go.Figure()

                fig_tp.add_trace(

                    go.Bar(

                        x=(
                            comparison_df[
                                "Run"
                            ]
                            .astype(str)
                        ),

                        y=(
                            comparison_df[
                                "Throughput (Mbps)"
                            ]
                        ),

                        text=(
                            comparison_df[
                                "Throughput (Mbps)"
                            ]
                        ),

                        textposition="auto"

                    )

                )


                fig_tp.update_layout(

                    title="Throughput Comparison",

                    xaxis_title="Run",

                    yaxis_title="Mbps",

                    template="plotly_white"

                )


                st.plotly_chart(

                    fig_tp,

                    use_container_width=True

                )


            cc3, cc4 = (
                st.columns(2)
            )


            # ------------------------------------------------
            # PACKET LOSS
            # ------------------------------------------------

            with cc3:

                fig_loss = go.Figure()

                fig_loss.add_trace(

                    go.Bar(

                        x=(
                            comparison_df[
                                "Run"
                            ]
                            .astype(str)
                        ),

                        y=(
                            comparison_df[
                                "Packet Loss (%)"
                            ]
                        ),

                        text=(
                            comparison_df[
                                "Packet Loss (%)"
                            ]
                        ),

                        textposition="auto"

                    )

                )


                fig_loss.update_layout(

                    title="Packet Loss Comparison",

                    xaxis_title="Run",

                    yaxis_title="%",

                    template="plotly_white"

                )


                st.plotly_chart(

                    fig_loss,

                    use_container_width=True

                )


            # ------------------------------------------------
            # HEALTH SCORE
            # ------------------------------------------------

            with cc4:

                fig_health = go.Figure()

                fig_health.add_trace(

                    go.Bar(

                        x=(
                            comparison_df[
                                "Run"
                            ]
                            .astype(str)
                        ),

                        y=(
                            comparison_df[
                                "Health Score"
                            ]
                        ),

                        text=(
                            comparison_df[
                                "Health Score"
                            ]
                        ),

                        textposition="auto"

                    )

                )


                fig_health.update_layout(

                    title=(
                        "Network Health Comparison"
                    ),

                    xaxis_title="Run",

                    yaxis_title="Score / 100",

                    template="plotly_white"

                )


                st.plotly_chart(

                    fig_health,

                    use_container_width=True

                )


    # ========================================================
    # EXPORT CSV
    # ========================================================

    st.subheader(
        "⬇️ Export Simulation Results"
    )


    csv_data = (
        history_df
        .to_csv(
            index=False
        )
        .encode("utf-8")
    )


    st.download_button(

        label=(
            "📥 Download "
            "Simulation History CSV"
        ),

        data=csv_data,

        file_name=(
            "wireless_simulation_history.csv"
        ),

        mime="text/csv",

        use_container_width=True

    )


    # ========================================================
    # CLEAR HISTORY
    # ========================================================

    if st.button(

        "🗑️ Clear Simulation History",

        use_container_width=True

    ):

        st.session_state.simulation_history = []

        st.session_state.last_result = None

        st.rerun()


else:

    st.info(

        "No simulation history available. "
        "Run a simulation to create history."

    )


# ============================================================
# PROJECT INFORMATION
# ============================================================

st.divider()

st.subheader(
    "🎓 Project Information"
)


info1, info2, info3 = (
    st.columns(3)
)


with info1:

    st.markdown(

        """
### 📡 Wireless Communication

• Free Space Path Loss  
• Received Power  
• SNR  
• Interference  
• Packet Loss  
• Throughput  
• Latency
"""

    )


with info2:

    st.markdown(

        """
### 🤖 Artificial Intelligence

• Random Forest  
• GOOD / MODERATE / CONGESTED  
• Confidence Score  
• Class Probabilities  
• AI Recommendations  
• AI Optimization
"""

    )


with info3:

    st.markdown(

        """
### 📊 Dashboard

• Interactive Topology  
• Network Health Score  
• Performance Charts  
• Simulation History  
• Run Comparison  
• CSV Export
"""

    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(

    "Smart AI-Based Wireless Network Simulator | "
    "Introduction to Wireless Communication | "
    "Educational simulation using Python, Streamlit, "
    "Plotly and Random Forest"

)