import math
import random
import os

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

import joblib


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_SAMPLES = 1200

DATA_FOLDER = "data"
MODEL_FOLDER = "models"

DATA_FILE = os.path.join(
    DATA_FOLDER,
    "wireless_network_dataset.csv"
)

MODEL_FILE = os.path.join(
    MODEL_FOLDER,
    "wireless_model.pkl"
)


os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)


# ============================================================
# WIRELESS CALCULATIONS
# ============================================================

def calculate_path_loss(distance_m, frequency_ghz):

    distance_m = max(distance_m, 1)

    distance_km = distance_m / 1000
    frequency_mhz = frequency_ghz * 1000

    return (
        32.44
        + 20 * math.log10(distance_km)
        + 20 * math.log10(frequency_mhz)
    )


def calculate_received_power(
    transmit_power,
    path_loss
):

    return transmit_power - path_loss


def calculate_interference(users, nodes):

    user_interference = users * 1.2
    node_interference = nodes * 0.5

    return min(
        user_interference + node_interference,
        100
    )


def calculate_snr(
    received_power,
    noise_power,
    interference
):

    interference_penalty = interference * 0.20

    effective_noise = (
        noise_power +
        interference_penalty
    )

    return received_power - effective_noise


def calculate_packet_loss(snr, users):

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

    return min(
        base_loss + congestion,
        50
    )


def calculate_throughput(
    bandwidth,
    snr,
    users
):

    if snr >= 25:
        efficiency = 4.5

    elif snr >= 15:
        efficiency = 3.0

    elif snr >= 8:
        efficiency = 1.5

    else:
        efficiency = 0.5

    total_throughput = (
        bandwidth * efficiency
    )

    return total_throughput / max(users, 1)


def calculate_latency(
    users,
    packet_loss
):

    return (
        10
        + users * 1.5
        + packet_loss * 2
    )


# ============================================================
# NETWORK CLASSIFICATION
# ============================================================

def get_network_status(
    snr,
    packet_loss,
    latency
):

    if (
        snr >= 20
        and packet_loss < 5
        and latency < 50
    ):

        return "GOOD"

    elif (
        snr >= 10
        and packet_loss < 15
        and latency < 100
    ):

        return "MODERATE"

    else:

        return "CONGESTED"


# ============================================================
# GENERATE TARGETED DATA
# ============================================================

def generate_sample():

    while True:

        nodes = random.randint(2, 30)

        users = random.randint(1, 100)

        distance = random.randint(
            10,
            500
        )

        frequency = random.choice(
            [2.4, 5.0]
        )

        bandwidth = random.choice(
            [5, 10, 20, 40, 80]
        )

        transmit_power = 20
        noise_power = -90

        path_loss = calculate_path_loss(
            distance,
            frequency
        )

        received_power = calculate_received_power(
            transmit_power,
            path_loss
        )

        interference = calculate_interference(
            users,
            nodes
        )

        snr = calculate_snr(
            received_power,
            noise_power,
            interference
        )

        packet_loss = calculate_packet_loss(
            snr,
            users
        )

        throughput = calculate_throughput(
            bandwidth,
            snr,
            users
        )

        latency = calculate_latency(
            users,
            packet_loss
        )

        status = get_network_status(
            snr,
            packet_loss,
            latency
        )

        row = {
            "nodes": nodes,
            "users": users,
            "distance_m": distance,
            "frequency_ghz": frequency,
            "bandwidth_mhz": bandwidth,
            "path_loss_db": round(path_loss, 2),
            "received_power_dbm": round(
                received_power,
                2
            ),
            "interference": round(
                interference,
                2
            ),
            "snr_db": round(
                snr,
                2
            ),
            "packet_loss_percent": round(
                packet_loss,
                2
            ),
            "throughput_mbps": round(
                throughput,
                2
            ),
            "latency_ms": round(
                latency,
                2
            ),
            "status": status
        }

        return row


# ============================================================
# BALANCED DATASET GENERATION
# ============================================================

def generate_dataset():

    print()
    print("=" * 60)
    print("SMART AI WIRELESS NETWORK SIMULATOR")
    print("BALANCED DATASET GENERATION")
    print("=" * 60)
    print()

    target_per_class = NUMBER_OF_SAMPLES // 3

    data = []

    class_counts = {
        "GOOD": 0,
        "MODERATE": 0,
        "CONGESTED": 0
    }

    while min(class_counts.values()) < target_per_class:

        row = generate_sample()

        status = row["status"]

        if class_counts[status] < target_per_class:

            data.append(row)

            class_counts[status] += 1

    df = pd.DataFrame(data)

    df = df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    df.to_csv(
        DATA_FILE,
        index=False
    )

    print(
        f"Dataset generated: {DATA_FILE}"
    )

    print(
        f"Total samples: {len(df)}"
    )

    print()

    print("Class distribution:")

    print(
        df["status"].value_counts()
    )

    print()

    return df


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(df):

    print("=" * 60)
    print("TRAINING RANDOM FOREST MODEL")
    print("=" * 60)
    print()

    features = [
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

    X = df[features]

    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    print()

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"Model Accuracy: {accuracy * 100:.2f}%"
    )

    print()

    print("Classification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print(
        f"Model saved: {MODEL_FILE}"
    )

    print()

    return model


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    train_model(dataset)

    print("=" * 60)
    print("AI MODEL TRAINING COMPLETED")
    print("=" * 60)