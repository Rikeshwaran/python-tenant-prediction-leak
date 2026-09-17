import sys,json
from pathlib import Path

MAIN_DATA_FILE = Path("data.json")

def eval():

    #check if file exist
    if not MAIN_DATA_FILE.exists():
        return 1

    #check file data
    try:
        filedata = json.loads(MAIN_DATA_FILE.read_text())
    except:
        return 1

    rawdata = filedata.get("userkey") or filedata.get("rawdata") or {}

    a = list(rawdata.values())
    if not a:
        return 1

    for rec in a:
        for fields in ("prediction_id", "prediction", "tenant_id", "user_id", "input"):
            if fields not in rec or rec.get(fields) is None:
                return 1
            
    
    #key check
    for key in rawdata.keys():
        if ":" not in str(key):
            return 1

    #global leak check 
    b = filedata.get("finalPrediction")
    if b is None:
        b = filedata.get("last_prediction")
    if b is not None:
        return 1

    #key match check
    for key, rec in rawdata.items():
        parts = str(key).split(":",1)
        if len(parts)!=2:
            return 1

        c,d = parts
        if rec.get("tenant_id")!=c:
            return 1
        if rec.get("user_id")!=d:
            return 1

    users={}
    for rec in a:
        uid,tid = rec.get("user_id"), rec.get("tenant_id")

        if uid is None or tid is None:
            continue

        users.setdefault(uid, set()).add(tid)

    for uid , tenants in users.items():
        if len(tenants)<2:
            continue

        count = sum(1 for rec in a if rec.get("user_id") == uid)
        if count<len(tenants):
            return 1

    return 0

result = eval()

print(result)
sys.exit(result)
    

    
    

    