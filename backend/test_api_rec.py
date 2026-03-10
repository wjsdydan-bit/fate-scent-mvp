import asyncio
from main import get_recommendations, RecommendRequest

async def test_recommend():
    req = RecommendRequest(
        user_name="test",
        gender="여성",
        saju_data={
            "weakest": "Fire",
            "strongest": "Water",
            "saju_name": "갑자 을축 병인",
        },
        pref_tags=["꽃향기(플로럴)"],
        dislike_tags=[],
        gender_filter="전체",
        brand_filter_mode="유명 브랜드 위주",
        interests=["연애운"]
    )
    try:
        res = await get_recommendations(req)
        print("Success:", len(res.top3), "perfumes returned.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error:", e)

asyncio.run(test_recommend())
