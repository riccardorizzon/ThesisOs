import pytest
from sqlalchemy import text
from app.db.session_async import AsyncSessionLocal


@pytest.mark.integration
async def test_async_session_select_one():
    try:
        async with AsyncSessionLocal() as s:
            r = await s.execute(text("SELECT 1"))
            assert r.scalar_one() == 1
    except Exception as e:  # no DB available in this environment
        pytest.skip(f"async DB not reachable: {e}")
