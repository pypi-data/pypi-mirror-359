import json
import time
from collections.abc import Callable
from datetime import datetime

from evalassist.model import LogRecord
from fastapi import Request, Response
from fastapi.routing import APIRoute
from sqlmodel import Session
from starlette.background import BackgroundTask

from .const import STORAGE_ENABLED
from .database import engine  # Assumes you have engine/session setup

ignored_endpoints = [
    "/health",
    "/evaluators/",
    "/criterias/",
    # "/test_case/",
    "/user/",
    "/default-credentials/",
    "/benchmarks/",
    "/domains-and-personas/",
    "/feature-flags/",
]


def log_info(method, path, req_body, res_body, headers, runtime):
    if not STORAGE_ENABLED:
        return
    record = {
        "path": path,
        "method": method,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "runtime": runtime,
    }

    if path in ignored_endpoints:
        return

    if req_body:
        req = json.loads(req_body.decode())
        if "llm_provider_credentials" in req:
            req["llm_provider_credentials"] = ""
        record["request"] = req

    if res_body:
        res = json.loads(res_body.decode())
        record["response"] = res

    if "user_id" in headers:
        record["user_id"] = int(headers.get("user_id"))

    log_record = LogRecord(data=json.dumps(record), user_id=headers.get("user_id"))
    with Session(engine) as session:
        session.add(log_record)
        session.commit()


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()
            start_timestamp = time.time()
            response = await original_route_handler(request)
            end_timestamp = time.time()
            runtime = round(end_timestamp - start_timestamp, 2)
            tasks = response.background
            task = BackgroundTask(
                log_info,
                request.method,
                request.url.path,
                req_body,
                response.body if hasattr(response, "body") else None,
                request.headers,
                runtime,
            )

            # check if the original response had background tasks already attached to it
            if tasks:
                tasks.add_task(task)  # add the new task to the tasks list
                response.background = tasks
            else:
                response.background = task

            return response

        return custom_route_handler
