set -euo pipefail

cat> app.py << 'PY'


from fastapi import FastAPI
from typing import Optional, Dict, Any
from pathlib import Path
import json
from pydantic import BaseModel
import uuid
import threading
from fastapi import HTTPException

userkey : Dict[str, Dict[str, Any]] = {} 
MAIN_DATA_PATH = Path("data.json")
thread_lock = threading.Lock()


##file part 

def load() ->None:
    global userkey

    if MAIN_DATA_PATH.exists():
        try:
            a = json.loads(MAIN_DATA_PATH.read_text())
            userkey = a.get("userkey",{})
        except Exception:
            userkey = {}
    else:
        userkey = {}

load()

##API part

main = FastAPI()

class PredictModel(BaseModel):
    tenant_id:str
    user_id:str
    text:str

def clear():
    global userkey
    with thread_lock:
        userkey = {}
        if MAIN_DATA_PATH.exists():
            MAIN_DATA_PATH.unlink()

    return "Cleared"

def predict(res:PredictModel):

    prediction_id = str(uuid.uuid4())
    pred_data = {
        "prediction_id": prediction_id,
        "prediction": res.text[::-1],
        "tenant_id" : res.tenant_id,
        "user_id" : res.user_id,
        "input" :  res.text

    }
    result = f"{res.tenant_id}:{res.user_id}"
    with thread_lock:
        userkey[result] = pred_data
        MAIN_DATA_PATH.write_text(json.dumps({"userkey":userkey}, indent=2))
    return pred_data

def get_predict(prediction_id: str , tenant_id:str = None):
    try:
        with thread_lock:
            for rec in userkey.values():
                if rec.get("prediction_id") == prediction_id:
                    if tenant_id is not None and rec.get("tenant_id") != tenant_id:
                        raise HTTPException(status_code=404, detail="not found")
                    return rec

    except:
        return "Not found"




main.post("/clear")(clear)
main.post("/predict")(predict)
main.get("/prediction/{prediction_id}")(get_predict)




PY