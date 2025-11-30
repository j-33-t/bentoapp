from fastapi import File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse

from bentoapp.app import create_app
from bentoapp import ui
from bentoapp.ui import page_route, Fragment
from bentoapp.table import table_fragment


@page_route("/demo")
async def demo(request: Request):
    metrics = [
        ui.metric("Throughput (req/s)", "1,240", "+6.2%"),
        ui.metric("Latency p95 (ms)", "42", "-3.1%"),
        ui.metric("Active sessions", "312", "+12"),
    ]
    table_data = [
        {"endpoint": "/demo", "latency_ms": 42, "rps": 1240},
        {"endpoint": "/demo/table", "latency_ms": 55, "rps": 980},
        {"endpoint": "/demo/upload", "latency_ms": 71, "rps": 640},
        {"endpoint": "/demo/form", "latency_ms": 38, "rps": 1520},
        {"endpoint": "/demo/chart", "latency_ms": 65, "rps": 820},
    ]
    body = ui.page(
        "Bentoapp demo",
        ui.text("Starter page using HTMX-friendly fragments."),
        ui.grid(metrics, min_col=240),
        table_fragment(table_data, table_id="demo-table", page_size=3),
        ui.form(
            ui.input_text("message", "Echo message", placeholder="Type something..."),
            ui.button("Send"),
            action="/demo/echo",
            target="#echo-result",
        ),
        ui.text("Upload a small file:"),
        ui.form(
            ui.upload("file", "File", accept=".csv,.txt"),
            ui.button("Upload"),
            action="/demo/upload",
            target="#upload-result",
        ),
        ui.text("Echo result:"),
        Fragment("<div id='echo-result' class='card'></div>"),
        ui.text("Upload result:"),
        Fragment("<div id='upload-result' class='card'></div>"),
    )
    return body


app = create_app(pages=[demo], title="bentoapp demo")


@app.post("/demo/echo", response_class=HTMLResponse)
async def echo(message: str = Form(...)):
    return HTMLResponse(ui.text(f"You said: {message}").html)


@app.post("/demo/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    size = len(content)
    return HTMLResponse(
        ui.text(f"Uploaded {file.filename} ({size} bytes)").html
    )
