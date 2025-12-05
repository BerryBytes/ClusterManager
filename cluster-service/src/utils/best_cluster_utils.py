"""Utilities for selecting the best cluster based on CPU and memory usage."""
from src.utils.app_constant import CPU_THRESHOLD, RAM_THRESHOLD


def get_best_cluster(data):
    """Select the cluster with the lowest CPU and memory usage below thresholds."""
    best_data = {}
    best_cpu = float("inf")
    best_memory = float("inf")
    send_notification = True

    for filename, stats in data.items():
        cpu = stats["CPU"]
        memory = stats["MEMORY"]

        if cpu < CPU_THRESHOLD and memory < RAM_THRESHOLD:
            if cpu < best_cpu or (cpu == best_cpu and memory < best_memory):
                best_cpu = cpu
                best_memory = memory
                best_data = {filename: {"best_cpu": cpu, "best_memory": memory}}
                send_notification = False

        elif cpu < best_cpu and memory < best_memory:
            best_cpu = cpu
            best_memory = memory
            best_data = {filename: {"best_cpu": cpu, "best_memory": memory}}
            send_notification = True

    if send_notification:
        best_data = {}
        send_notification_to_admin()

    return best_data


def send_notification_to_admin():
    """Notify admin when CPU or memory usage exceeds defined thresholds."""
    print("Notification sent to admin: CPU or memory usage exceeds 80.")
