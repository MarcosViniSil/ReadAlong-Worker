import psutil
from fastapi import FastAPI
import uvicorn

app = FastAPI()


def get_cpu_temperature():
    try:
        temperatures = psutil.sensors_temperatures()

        for entries in temperatures.values():
            for entry in entries:
                if entry.current is not None:
                    return entry.current

    except Exception:
        pass

    return None


@app.get("/metrics")
async def metrics():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu": psutil.cpu_percent(interval=None),
        "memory": memory.percent,
        "disk": disk.percent,
        "temperature": get_cpu_temperature(),
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


async def run_metrics_server():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="warning",
    )

    server = uvicorn.Server(config)

    await server.serve()
