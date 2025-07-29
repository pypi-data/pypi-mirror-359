import uvicorn

from arpakitlib.ar_base_worker_util import safe_run_worker_in_background, SafeRunInBackgroundModes
from project.core.settings import get_cached_settings
from project.core.util import setup_logging
from project.operation_execution.scheduled_operation_creator_worker import create_scheduled_operation_creator_worker


def __command():
    setup_logging()
    if get_cached_settings().api_start_scheduled_operation_creator_worker:
        _ = safe_run_worker_in_background(
            worker=create_scheduled_operation_creator_worker(),
            mode=SafeRunInBackgroundModes.thread
        )
    uvicorn.run(
        "project.api.asgi:app",
        port=get_cached_settings().api_port,
        host="localhost",
        workers=1,
        reload=False
    )


if __name__ == '__main__':
    __command()
