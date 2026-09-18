## Task: Fix multi-tenant isolation in a broken FastAPI prediction API.

The given FastAPI app stores prediction results for multiple tenants, but isolation is broken. When two tenants use the same user_id, one tenant’s prediction overwrites the other, a global final prediction can leak across tenants, and retrieving a prediction by id does not check ownership. Fix the isolation so each tenant only ever receives its own predictions.

## Working Environment:
1. The project root is the working directory. All required files are in this folder.
2. Work on app.py. It contains the broken FastAPI prediction API.
3. A file named data.json should be created in the same directory because no database will be used.
4. All prediction details should be stored only in data.json.

## Expected schema:
After feeding predictions, data.json must contain a JSON object with a "userkey" field.
Each entry in "userkey" must be keyed by tenant_id:user_id (not by user_id alone).
There must be no "finalPrediction" or "last_prediction" field.

Schema of each stored record:
    {
    "prediction_id": "",
    "prediction": "",
    "tenant_id": "",
    "user_id": "",
    "input": ""
    }

Where:
    "prediction_id" is a unique id for the prediction.
    "prediction" is the model output (the input text reversed).
    "tenant_id" is the tenant that made the request.
    "user_id" is the user under that tenant.
    "input" is the original text that was sent.

## Required behavior:
The app.py must provide the endpoints below. Each endpoint must use file handling for non-existent, empty, or existing data in data.json.

# POST: /clear
1. Clear all stored predictions.
2. If data.json exists, remove it or empty the userkey.
3. Return a cleared status.

# POST: /predict
Input: tenant_id (str), user_id (str), text (str).
1. Create a prediction record using the schema above.
2. The prediction value must be the input text reversed.
3. Store the record under the key tenant_id:user_id so the same user_id under different tenants does not collide.
4. Write the full userkey to data.json (no finalPrediction field).
5. If data.json is missing, create it. If it already contains data, update it.
6. Return the full prediction record.
7. Concurrent requests must not mix results; protect shared state appropriately.

# GET: /prediction/{prediction_id}
Optional query: tenant_id.
1. Look up the prediction by prediction_id.
2. If tenant_id is provided, only return the record when it belongs to that tenant.
3. If not found or tenant does not match, return 404.
4. Do not fall back to any global final prediction.

## Feed sequence (use these exact values):
1. POST /clear
2. POST /predict with tenant_id=tenantA, user_id=user1, text=hello-A
3. POST /predict with tenant_id=tenantB, user_id=user1, text=hello-B
4. POST /predict with tenant_id=tenantC, user_id=userC, text=only-C

After this sequence, data.json must keep both tenantA and tenantB records even though they share user_id=user1.

## Expected Output:
After the feed sequence above, data.json must contain both predictions for user1 under different tenants.

Example of a correct data.json structure:
{
  "userkey": {
    "tenantA:user1": {
      "prediction_id": "<some-uuid>",
      "prediction": "A-olleh",
      "tenant_id": "tenantA",
      "user_id": "user1",
      "input": "hello-A"
    },
    "tenantB:user1": {
      "prediction_id": "<some-uuid>",
      "prediction": "B-olleh",
      "tenant_id": "tenantB",
      "user_id": "user1",
      "input": "hello-B"
    },
    "tenantC:userC": {
      "prediction_id": "<some-uuid>",
      "prediction": "C-ylno",
      "tenant_id": "tenantC",
      "user_id": "userC",
      "input": "only-C"
    }
  }
}

Keys must be in the form tenant_id:user_id.
There must be no finalPrediction or last_prediction field.
Both hello-A and hello-B must be present.
Looking up a prediction with the wrong tenant_id must not return another tenant’s data.

## Constraints:
1. Use only the Python standard library + FastAPI which is already available.
2. data.json must be created if it does not exist and updated in the current working directory.
3. Do not use any database or external storage; use data.json to store prediction data.
4. Storage must be keyed by tenant_id:user_id so the same user_id under different tenants stays isolated.
5. Do not keep a global finalPrediction that can leak across tenants.
6. Retrieval by prediction_id must enforce tenant ownership when tenant_id is supplied.
7. Concurrent requests must not mix results across tenants.
8. Empty, missing, or incorrectly keyed data are considered failures.
9. The solution must keep tenant data fully isolated.