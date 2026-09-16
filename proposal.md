Proposal

Task: The Agent needs to fix a FastAPI prediction API so that it correctly isolates predictions across multiple tenants. Retrieving a prediction by its ID must only succeed for the owning tenant, concurrent requests must not mix results, and no shared global state may leak one tenant’s prediction to another. The same user_id may exist under different tenants and must be treated as separate identities.

For this task, we propose fixing the multi-tenant request isolation in a FastAPI inference API so that each tenant only ever receives its own predictions, even under concurrent load.

Difficulty: This task requires the agent to correctly identify and eliminate interacting isolation failures in a multi-tenant prediction service. The agent needs to manage the relationship between tenant_id and user_id, ensure that prediction records are keyed and retrieved with proper ownership, remove any global mutable state that can leak results, and make concurrent requests safe so that one request never receives another request’s prediction.

Solution (Intended Approach): The agent should first change how predictions are stored so each one is keyed under a combined identity that includes both tenant_id and user_id. Next, it needs to make sure the owning tenant_id is saved inside every prediction record. After that, every time a prediction is retrieved, the code must check that the tenant making the request actually owns it before returning anything. The global “last prediction” variable has to be removed completely. Any remaining shared state should then be properly locked or isolated so concurrent requests can’t step on each other. Once all of that is done, the same user_id under two different tenants stays fully separate, looking up another tenant’s prediction gets blocked, and parallel calls from different tenants don’t interfere with each other.

Verification:
1. Run the original broken app and confirm predictions from one tenant can be seen by another.
2. After the fixes, check that the same user_id under two different tenants stays completely separate.
3. Try looking up a prediction using the wrong tenant_id and make sure it gets rejected.
4. Send concurrent requests from different tenants and verify the results never mix.
5. Confirm no leftover global state (like a last-prediction variable) returns another tenant’s data.

Category: Software engineering - Multi-tenant isolation 
w