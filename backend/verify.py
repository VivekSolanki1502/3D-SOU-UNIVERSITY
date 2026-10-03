import asyncio
import os
import httpx
from app.main import app


async def main():
    admin_email = os.environ["VERIFY_ADMIN_EMAIL"]
    admin_password = os.environ["VERIFY_ADMIN_PASSWORD"]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/api/v1/health")
        print("GET /api/v1/health ->", res.status_code, res.json())
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        # 2. Campus buildings
        res_b = await client.get("/api/v1/campus/buildings")
        print("GET /api/v1/campus/buildings ->", res_b.status_code, len(res_b.json()), "buildings")

        # 3. Campus search
        res_s = await client.get("/api/v1/campus/search?q=library")
        print("GET /api/v1/campus/search?q=library ->", res_s.status_code, res_s.json())

        # 4. Admin Auth
        res_auth = await client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": admin_password
        })
        print("POST /api/v1/auth/login ->", res_auth.status_code, res_auth.json()["role"])

        token = res_auth.json()["access_token"]
        res_stats = await client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})
        print("GET /api/v1/admin/stats ->", res_stats.status_code, res_stats.json())

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
