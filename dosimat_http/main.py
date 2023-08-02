import logging
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import BackgroundTasks, FastAPI

from dosimat_http.dosimat_manager import DosimatManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lifespan(app: FastAPI):
    yield
    app.state.logger.info("Shutting down the dosing manager units")
    app.state.dosimat_manager.close()


app = FastAPI(lifespan=lifespan)
app.state.dosimat_manager = DosimatManager()
app.state.logger = logger


@dataclass
class APIResponse:
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None


@app.get("/dosimats/{id}/status")
async def get_status(id: int) -> APIResponse:
    """
    Returns the status of the dosing unit.
    """
    is_ready = app.state.dosimat_manager.get_unit(id).is_ready()
    return APIResponse(data={"is_ready": is_ready})


@app.post("/dosimats/{id}/dispense", status_code=202)
async def dispense(
    id: int, ml: float, background_tasks: BackgroundTasks
) -> APIResponse:
    """
    Dispenses the given volume of liquid.
    """
    try:
        background_tasks.add_task(app.state.dosimat_manager.dispense, id, ml)
        return APIResponse(message="Dispensing successful")
    except Exception as e:
        return APIResponse(error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
