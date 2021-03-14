from fettler.server import app
from fettler.server.schemas import Policy


@app.post("/policy", summary="add cache refresh policy")
async def add_policy(policy: Policy):
    pass
