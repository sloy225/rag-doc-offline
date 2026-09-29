import psutil


def get_system_info() -> dict[str, float | int | None]:
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:/")

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "cpu_physical": psutil.cpu_count(logical=False),
        "cpu_logical": psutil.cpu_count(logical=True),
        "ram_percent": ram.percent,
        "ram_total_gb": ram.total / (1024 ** 3),
        "ram_used_gb": ram.used / (1024 ** 3),
        "ram_available_gb": ram.available / (1024 ** 3),
        "disk_percent": disk.percent,
        "disk_free_gb": disk.free / (1024 ** 3),
    }