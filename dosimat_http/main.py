import logging
import os

from fastapi import FastAPI

from driver.driver import Dosimat876

serial_port = os.environ.get("SERIAL_PORT", "/dev/ttyUSB0")
dosimat = Dosimat876(serial_port)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lifespan(app: FastAPI):
    yield
    app.state.logger.info("Shutting down the dosing unit")
    app.state.dosimat.close()


app = FastAPI(lifespan=lifespan)
app.state.dosimat = dosimat
app.state.logger = logger


@app.get("/start")
def start():
    return {"response": app.state.dosimat.send_command("$G")}


@app.get("/stop")
def stop():
    return {"response": app.state.dosimat.send_command("$S")}


@app.get("/hold")
def hold():
    return {"response": app.state.dosimat.send_command("$H")}


@app.get("/status")
def status():
    return {"response": app.state.dosimat.send_command("$D")}


@app.get("/confirm/{action}")
def confirm(action: str):
    return {"response": app.state.dosimat.send_command(f"$A({action.upper()})")}


@app.get("/load/{method}")
def load(method: str):
    return {"response": app.state.dosimat.send_command(f"$L({method})")}


@app.get("/request/{variable}")
def request(variable: str):
    return {"response": app.state.dosimat.send_command(f"$Q({variable.upper()})")}


@app.post("/dispense/{ml}")
def dispense(ml: float):
    method_name = f"{ml}ml-XDOS"
    app.state.dosimat.send_command(f"$L({method_name})")
    app.state.dosimat.send_command("$G")
    return {"response": "Dispensing started"}


@app.on_event("shutdown")
def shutdown_event():
    app.state.dosimat.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
