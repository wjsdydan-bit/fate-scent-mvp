import asyncio
from main import get_compatibility, CompatRequest

async def test():
    print("Testing compatibility...")
    req = CompatRequest(
        user_name="test",
        gender="여성",
        year=1995,
        month=1,
        day=1,
        know_time=True,
        perf_brand="Jo Malone",
        perf_name="Wood Sage"
    )
    try:
        res = await get_compatibility(req)
        print("Success:", res.compatibility_score)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
