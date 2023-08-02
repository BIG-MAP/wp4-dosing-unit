import logging
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse

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


@app.get("/dosimats")
async def list_dosimats() -> APIResponse:
    """
    Returns a list of dosing units.
    """
    dosimat_ids = app.state.dosimat_manager.get_ids()
    return APIResponse(data={"dosimat_ids": dosimat_ids})


@app.get("/dosimats/{id}/status")
async def get_status(id: int):
    """
    Returns the status of the dosing unit.
    """
    dosimat = app.state.dosimat_manager.get_unit(id)
    if dosimat is None:
        return JSONResponse(
            status_code=404,
            content=APIResponse(error=f"Could not find dosimat with id {id}"),
        )

    is_ready = dosimat.is_ready()
    return APIResponse(data={"is_ready": is_ready})


@app.post("/dosimats/{id}/dispense", status_code=202)
async def dispense(id: int, ml: float, background_tasks: BackgroundTasks):
    """
    Dispenses the given volume of liquid.
    """
    # We need to convert the ml to an integer if it is a whole number, because Dosimat method names
    # don't expect decimals for whole numbers. It depends, however, on how the Dosimat is configured.
    if ml.is_integer():
        ml = int(ml)

    dosimat = app.state.dosimat_manager.get_unit(id)
    if dosimat is None:
        return JSONResponse(
            status_code=404,
            content=APIResponse(error=f"Could not find dosimat with id {id}"),
        )

    is_ready = dosimat.is_ready()
    if not is_ready:
        return JSONResponse(
            status_code=400,
            content=APIResponse(error=f"Dosimat with id {id} is not ready"),
        )

    try:
        background_tasks.add_task(app.state.dosimat_manager.dispense, id, ml)
        return APIResponse(message="Dispensing successful")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse(error=f"Could not dispense: {e}"),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
