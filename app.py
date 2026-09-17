from fastapi import FastAPI
from typing import Optional, Dict, Any
from pathlib import Path
import json
from pydantic import BaseModel
import uuid

userkey : Dict[str, Dict[str, Any]] = {} 
finalPrediction : Optional[Dict[str, Any]] = None  #global prediction final and none at first 
MAIN_DATA_PATH = Path("data.json")


##file part 

def load() ->None:
    global finalPrediction,userkey

    if MAIN_DATA_PATH.exists():
        try:
            a = json.loads(MAIN_DATA_PATH.read_text())
            finalPrediction = a.get("finalPrediction")
            userkey = a.get("userkey",{})
        except Exception:
            finalPrediction = None
            userkey = {}
    else:
        finalPrediction = None
        userkey = {}

load()

##API part

main = FastAPI()

class PredictModel(BaseModel):
    tenant_id:str
    user_id:str
    text:str

def clear():
    global finalPrediction, userkey
    finalPrediction = None
    userkey = {}
    if MAIN_DATA_PATH.exists():
        MAIN_DATA_PATH.unlink()

    return "Cleared"

def predict(res:PredictModel):

    global finalPrediction
    prediction_id = str(uuid.uuid4())
    pred_data = {
        "prediction_id": prediction_id,
        "prediction": res.text[::-1],
        "tenant_id" : res.tenant_id,
        "user_id" : res.user_id,
        "input" :  res.text

    }
    userkey[res.user_id] = pred_data
    finalPrediction = pred_data
    MAIN_DATA_PATH.write_text(json.dumps({"finalPrediction": finalPrediction, "userkey": userkey}, indent=2))
    return pred_data




main.post("/clear")(clear)
main.post("/predict")(predict)

