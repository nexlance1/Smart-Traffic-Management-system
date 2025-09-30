from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock Traffic Signal API")

class SignalCommand(BaseModel):
    junction_id: str
    action: str
    duration: int = 0

@app.post("/send_command/")
def send_command(cmd: SignalCommand):
    return {"status":"ok","received":cmd.dict()}
