from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from pydantic import ValidationError
from app.main import app
from app.core.config import Settings, settings
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "SOU 3D Disha"
    assert data["version"] == "1.0.0"
    assert data["database"] == "connected"
    assert data["redis"] == "disabled"


@pytest.mark.asyncio
async def test_only_public_frontend_files_are_served():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        assert (await ac.get("/")).status_code == 200
        assert (await ac.get("/app.js")).status_code == 200
        assert (await ac.get("/static/backend/app/core/config.py")).status_code == 404
        assert (await ac.get("/backend/.env.example")).status_code == 404


@pytest.mark.asyncio
async def test_authentication_flow_and_invalid_logins():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Invalid login
        bad_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "WrongPassword123"
        })
        assert bad_res.status_code == 401

        # 2. Valid Admin login
        admin_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "Admin@SOU2026"
        })
        assert admin_res.status_code == 200
        admin_data = admin_res.json()
        assert admin_data["role"] == "admin"
        admin_token = admin_data["access_token"]

        # 3. Valid Student login
        student_res = await ac.post("/api/v1/auth/login", json={
            "email": "student@silveroakuni.ac.in",
            "password": "Student@SOU2026"
        })
        assert student_res.status_code == 200
        assert student_res.json()["role"] == "student"

        # 4. Valid Faculty login
        faculty_res = await ac.post("/api/v1/auth/login", json={
            "email": "faculty@silveroakuni.ac.in",
            "password": "Faculty@SOU2026"
        })
        assert faculty_res.status_code == 200
        assert faculty_res.json()["role"] == "faculty"

        # 5. Profile Check with JWT
        me_res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "admin@silveroakuni.ac.in"


@pytest.mark.asyncio
async def test_rbac_access_matrix():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login tokens
        stu_token = (await ac.post("/api/v1/auth/login", json={"email": "student@silveroakuni.ac.in", "password": "Student@SOU2026"})).json()["access_token"]
        fac_token = (await ac.post("/api/v1/auth/login", json={"email": "faculty@silveroakuni.ac.in", "password": "Faculty@SOU2026"})).json()["access_token"]
        adm_token = (await ac.post("/api/v1/auth/login", json={"email": "admin@silveroakuni.ac.in", "password": "Admin@SOU2026"})).json()["access_token"]

        # 1. Unauthenticated / Visitor checks
        # Public campus read
        assert (await ac.get("/api/v1/campus/buildings")).status_code == 200
        # Public events read
        assert (await ac.get("/api/v1/events")).status_code == 200
        # Public SOS read
        assert (await ac.get("/api/v1/sos")).status_code == 200
        # Protected Admin stats -> 401 Unauthorized
        assert (await ac.get("/api/v1/admin/stats")).status_code == 401
        # Protected Exam view -> 401 Unauthorized without student/faculty/admin token
        assert (await ac.get("/api/v1/exams")).status_code == 401

        # 2. Student Role
        # Can view exams
        assert (await ac.get("/api/v1/exams", headers={"Authorization": f"Bearer {stu_token}"})).status_code == 200
        # Cannot create events -> 403 Forbidden
        assert (await ac.post("/api/v1/events", json={"title": "Hack", "event_date": "2026-11-01", "venue": "Quad"}, headers={"Authorization": f"Bearer {stu_token}"})).status_code == 403
        # Cannot access admin users -> 403 Forbidden
        assert (await ac.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {stu_token}"})).status_code == 403

        # 3. Faculty Role
        # Can view exams
        assert (await ac.get("/api/v1/exams", headers={"Authorization": f"Bearer {fac_token}"})).status_code == 200
        # Can create exam schedule
        create_exam_res = await ac.post("/api/v1/exams", json={
            "subject_name": "Compiler Design",
            "subject_code": "CS-601",
            "course": "B.Tech CSE",
            "department": "Computer Science & Engineering",
            "semester": 6,
            "exam_date": "2026-11-15",
            "start_time": "10:00:00",
            "end_time": "12:30:00",
            "venue": "Innovation Hub Floor 2",
            "building_id": "innovation-hub"
        }, headers={"Authorization": f"Bearer {fac_token}"})
        assert create_exam_res.status_code == 201
        created_exam_id = create_exam_res.json()["id"]

        # Faculty can update exam venue
        update_exam_res = await ac.patch(f"/api/v1/exams/{created_exam_id}", json={
            "venue": "Innovation Hub Hall B-201"
        }, headers={"Authorization": f"Bearer {fac_token}"})
        assert update_exam_res.status_code == 200
        assert update_exam_res.json()["venue"] == "Innovation Hub Hall B-201"

        # Faculty cannot delete buildings -> 403 Forbidden
        assert (await ac.delete("/api/v1/campus/buildings/innovation-hub", headers={"Authorization": f"Bearer {fac_token}"})).status_code == 403
        # Faculty cannot access audit logs -> 403 Forbidden
        assert (await ac.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {fac_token}"})).status_code == 403

        # 4. Admin Role
        # Admin can delete created exam
        del_res = await ac.delete(f"/api/v1/exams/{created_exam_id}", headers={"Authorization": f"Bearer {adm_token}"})
        assert del_res.status_code == 204

        # Admin can view audit logs
        audit_res = await ac.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {adm_token}"})
        assert audit_res.status_code == 200
        assert len(audit_res.json()) >= 1


@pytest.mark.asyncio
async def test_campus_entities_and_search():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Buildings
        b_res = await ac.get("/api/v1/campus/buildings")
        assert b_res.status_code == 200
        buildings = b_res.json()
        assert len(buildings) >= 4
        assert any(b["id"] == "innovation-hub" for b in buildings)
        # Check 3D coordinates presence
        b0 = buildings[0]
        assert "pos_x" in b0 and "pos_z" in b0 and "dim_w" in b0

        floors_res = await ac.get("/api/v1/campus/buildings/innovation-hub/floors")
        assert floors_res.status_code == 200
        assert len(floors_res.json()) == 4
        assert [floor["floor_number"] for floor in floors_res.json()] == [0, 1, 2, 3]
        assert (await ac.get("/api/v1/campus/buildings/unknown/floors")).status_code == 404

        # Rooms
        r_res = await ac.get("/api/v1/campus/rooms")
        assert r_res.status_code == 200
        rooms = r_res.json()
        assert len(rooms) >= 3

        # Labs
        labs_res = await ac.get("/api/v1/campus/labs")
        assert labs_res.status_code == 200
        assert len(labs_res.json()) >= 1

        # Search Query
        s_res = await ac.get("/api/v1/campus/search?q=library")
        assert s_res.status_code == 200
        results = s_res.json()
        assert len(results) >= 1
        assert results[0]["id"] == "central-library"


@pytest.mark.asyncio
async def test_admin_dashboard_and_stats():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        adm_token = (await ac.post("/api/v1/auth/login", json={"email": "admin@silveroakuni.ac.in", "password": "Admin@SOU2026"})).json()["access_token"]
        stats_res = await ac.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {adm_token}"})
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["buildings"] >= 4
        assert stats["rooms"] >= 3
        assert stats["facilities"] >= 5
        assert stats["events"] >= 3
        assert stats["exams"] >= 3
        assert stats["users"] >= 3


@pytest.mark.asyncio
async def test_not_found_handling():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        adm_token = (await ac.post("/api/v1/auth/login", json={"email": "admin@silveroakuni.ac.in", "password": "Admin@SOU2026"})).json()["access_token"]
        # Nonexistent building
        b_res = await ac.get("/api/v1/campus/buildings/non-existent-block-xyz")
        assert b_res.status_code == 404

        # Nonexistent event
        e_res = await ac.get("/api/v1/events/non-existent-event-xyz")
        assert e_res.status_code == 404

        # Nonexistent exam
        ex_res = await ac.get("/api/v1/exams/non-existent-exam-xyz", headers={"Authorization": f"Bearer {adm_token}"})
        assert ex_res.status_code == 404


@pytest.mark.asyncio
async def test_public_registration_cannot_assign_privileged_role():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        weak_password = await ac.post("/api/v1/auth/register", json={
            "email": "weak-password@silveroakuni.ac.in",
            "display_name": "Weak Password",
            "password": "short",
        })
        assert weak_password.status_code == 422

        response = await ac.post("/api/v1/auth/register", json={
            "email": "new-student@silveroakuni.ac.in",
            "display_name": "New Student",
            "password": "StudentPassword123",
            "role": "admin",
            "is_active": True,
        })

        assert response.status_code == 201
        user = response.json()
        assert user["role"] == "student"
        assert user["is_active"] is True

        login = await ac.post("/api/v1/auth/login", json={
            "email": "new-student@silveroakuni.ac.in",
            "password": "StudentPassword123",
        })
        token = login.json()["access_token"]
        assert (await ac.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})).status_code == 403

        admin_login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "Admin@SOU2026",
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        updated = await ac.patch(
            f"/api/v1/admin/users/{user['id']}",
            headers=admin_headers,
            json={"password": "UpdatedStudentPassword123"},
        )
        assert updated.status_code == 200
        assert (await ac.post("/api/v1/auth/login", json={
            "email": "new-student@silveroakuni.ac.in",
            "password": "StudentPassword123",
        })).status_code == 401
        updated_login = await ac.post("/api/v1/auth/login", json={
            "email": "new-student@silveroakuni.ac.in",
            "password": "UpdatedStudentPassword123",
        })
        assert updated_login.status_code == 200
        await ac.patch(
            f"/api/v1/admin/users/{user['id']}",
            headers=admin_headers,
            json={"is_active": False},
        )
        disabled_token = updated_login.json()["access_token"]
        assert (await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {disabled_token}"})).status_code == 401

        self_disable = await ac.patch(
            "/api/v1/admin/users/" + admin_login.json()["user_id"],
            headers=admin_headers,
            json={"is_active": False},
        )
        assert self_disable.status_code == 400
        self_demote = await ac.patch(
            "/api/v1/admin/users/" + admin_login.json()["user_id"],
            headers=admin_headers,
            json={"role": "student"},
        )
        assert self_demote.status_code == 400


@pytest.mark.asyncio
async def test_invalid_expired_and_incomplete_jwts_return_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "Admin@SOU2026",
        })
        user_id = login.json()["user_id"]
        tokens = [
            "not-a-jwt",
            create_access_token(user_id, "admin", expires_delta=timedelta(seconds=-1)),
            jwt.encode({"sub": user_id, "role": "admin"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM),
            create_access_token("missing-user-id", "admin"),
        ]

        for token in tokens:
            response = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_campus_crud_and_direct_role_enforcement():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        admin_login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "Admin@SOU2026",
        })
        student_login = await ac.post("/api/v1/auth/login", json={
            "email": "student@silveroakuni.ac.in",
            "password": "Student@SOU2026",
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        student_headers = {"Authorization": f"Bearer {student_login.json()['access_token']}"}
        building_data = {"id": "verification-building", "name": "Verification Building", "short_code": "VB"}

        assert (await ac.post("/api/v1/campus/buildings", json=building_data)).status_code == 401
        assert (await ac.post("/api/v1/campus/buildings", headers=student_headers, json=building_data)).status_code == 403
        created_building = await ac.post("/api/v1/campus/buildings", headers=admin_headers, json=building_data)
        assert created_building.status_code == 201
        changed_building = await ac.patch(
            "/api/v1/campus/buildings/verification-building",
            headers=admin_headers,
            json={"name": "Updated Verification Building"},
        )
        assert changed_building.status_code == 200
        assert changed_building.json()["name"] == "Updated Verification Building"
        assert (await ac.delete("/api/v1/campus/buildings/verification-building", headers=admin_headers)).status_code == 204

        room = await ac.post("/api/v1/campus/rooms", headers=admin_headers, json={
            "id": "verification-room",
            "building_id": "innovation-hub",
            "room_number": "IH-VERIFY",
            "name": "Verification Workshop",
            "room_type": "workshop",
        })
        assert room.status_code == 201
        assert (await ac.patch(
            "/api/v1/campus/rooms/verification-room",
            headers=admin_headers,
            json={"name": "Updated Verification Workshop"},
        )).status_code == 200
        assert (await ac.delete("/api/v1/campus/rooms/verification-room", headers=admin_headers)).status_code == 204

        facility = await ac.post("/api/v1/campus/facilities", headers=admin_headers, json={
            "id": "verification-facility",
            "name": "Verification Facility",
            "facility_type": "support",
            "location_description": "Verification area",
        })
        assert facility.status_code == 201
        assert (await ac.patch(
            "/api/v1/campus/facilities/verification-facility",
            headers=admin_headers,
            json={"is_active": False},
        )).status_code == 200
        assert (await ac.delete("/api/v1/campus/facilities/verification-facility", headers=admin_headers)).status_code == 204


@pytest.mark.asyncio
async def test_api_query_limits_and_cors_configuration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        assert (await ac.get("/api/v1/events?limit=101")).status_code == 422
        assert (await ac.get("/api/v1/events?skip=-1")).status_code == 422
        assert (await ac.get("/api/v1/campus/search?q=" + ("x" * 101))).status_code == 422

    base_settings = {
        "SECRET_KEY": "s" * 40,
        "POSTGRES_PASSWORD": "test-postgres-password",
        "SEED_ADMIN_EMAIL": "admin@example.edu",
        "SEED_ADMIN_PASSWORD": "test-admin-password",
        "SEED_ADMIN_NAME": "Test Admin",
        "SEED_FACULTY_EMAIL": "faculty@example.edu",
        "SEED_FACULTY_PASSWORD": "test-faculty-password",
        "SEED_FACULTY_NAME": "Test Faculty",
        "SEED_STUDENT_EMAIL": "student@example.edu",
        "SEED_STUDENT_PASSWORD": "test-student-password",
        "SEED_STUDENT_NAME": "Test Student",
    }
    with pytest.raises(ValidationError):
        Settings(**base_settings, BACKEND_CORS_ORIGINS=["*"])
    assert Settings(**base_settings, BACKEND_CORS_ORIGINS=["https://campus.example.edu/"]).BACKEND_CORS_ORIGINS == ["https://campus.example.edu"]


@pytest.mark.asyncio
async def test_inactive_campus_records_are_hidden_from_public_reads():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "Admin@SOU2026",
        })
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        building = await ac.post("/api/v1/campus/buildings", headers=admin_headers, json={
            "id": "hidden-building",
            "name": "Hidden Building",
            "short_code": "HB",
        })
        assert building.status_code == 201
        room = await ac.post("/api/v1/campus/rooms", headers=admin_headers, json={
            "id": "hidden-room",
            "building_id": "hidden-building",
            "room_number": "HB-1",
            "name": "Hidden Room",
            "room_type": "classroom",
        })
        assert room.status_code == 201

        assert (await ac.patch(
            "/api/v1/campus/rooms/hidden-room",
            headers=admin_headers,
            json={"is_active": False},
        )).status_code == 200
        rooms = await ac.get("/api/v1/campus/rooms", params={"building_id": "hidden-building"})
        assert "hidden-room" not in {item["id"] for item in rooms.json()}
        results = await ac.get("/api/v1/campus/search", params={"q": "Hidden Room"})
        assert "hidden-room" not in {item["id"] for item in results.json()}
        assert (await ac.patch(
            "/api/v1/campus/rooms/hidden-room",
            headers=admin_headers,
            json={"is_active": True},
        )).status_code == 200

        assert (await ac.patch(
            "/api/v1/campus/buildings/hidden-building",
            headers=admin_headers,
            json={"is_active": False},
        )).status_code == 200
        assert (await ac.get("/api/v1/campus/buildings/hidden-building")).status_code == 404
        assert (await ac.get("/api/v1/campus/buildings/hidden-building/floors")).status_code == 404
        buildings = await ac.get("/api/v1/campus/buildings")
        assert "hidden-building" not in {item["id"] for item in buildings.json()}
        rooms = await ac.get("/api/v1/campus/rooms", params={"building_id": "hidden-building"})
        assert "hidden-room" not in {item["id"] for item in rooms.json()}
        results = await ac.get("/api/v1/campus/search", params={"q": "Hidden Room"})
        assert "hidden-room" not in {item["id"] for item in results.json()}


@pytest.mark.asyncio
async def test_public_detail_routes_hide_unpublished_and_inactive_records():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@silveroakuni.ac.in",
            "password": "Admin@SOU2026",
        })
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        event = await ac.post("/api/v1/events", headers=admin_headers, json={
            "title": "Unpublished test event",
            "event_date": "2026-11-20",
            "venue": "Test Hall",
            "is_published": False,
        })
        assert event.status_code == 201
        event_id = event.json()["id"]
        listed_events = await ac.get("/api/v1/events")
        assert event_id not in {item["id"] for item in listed_events.json()}
        assert (await ac.get(f"/api/v1/events/{event_id}")).status_code == 404
        admin_events = await ac.get("/api/v1/events", headers=admin_headers)
        assert event_id in {item["id"] for item in admin_events.json()}
        assert (await ac.get(f"/api/v1/events/{event_id}", headers=admin_headers)).status_code == 200

        contact = await ac.post("/api/v1/sos", headers=admin_headers, json={
            "title": "Inactive test contact",
            "category": "security",
            "phone_number": "100",
            "location_name": "Test Desk",
            "is_active": False,
        })
        assert contact.status_code == 201
        contact_id = contact.json()["id"]
        listed_contacts = await ac.get("/api/v1/sos")
        assert contact_id not in {item["id"] for item in listed_contacts.json()}
        assert (await ac.get(f"/api/v1/sos/{contact_id}")).status_code == 404
        admin_contacts = await ac.get("/api/v1/sos", headers=admin_headers)
        assert contact_id in {item["id"] for item in admin_contacts.json()}
        assert (await ac.get(f"/api/v1/sos/{contact_id}", headers=admin_headers)).status_code == 200

        published = await ac.patch(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
            json={"is_published": True},
        )
        assert published.status_code == 200
        assert (await ac.get(f"/api/v1/events/{event_id}")).status_code == 200

        unpublished = await ac.patch(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
            json={"is_published": False},
        )
        assert unpublished.status_code == 200
        assert (await ac.get(f"/api/v1/events/{event_id}")).status_code == 404
        assert (await ac.delete(f"/api/v1/events/{event_id}", headers=admin_headers)).status_code == 204

        activated = await ac.patch(
            f"/api/v1/sos/{contact_id}",
            headers=admin_headers,
            json={"is_active": True},
        )
        assert activated.status_code == 200
        assert (await ac.get(f"/api/v1/sos/{contact_id}")).status_code == 200

        deactivated = await ac.patch(
            f"/api/v1/sos/{contact_id}",
            headers=admin_headers,
            json={"is_active": False},
        )
        assert deactivated.status_code == 200
        assert (await ac.get(f"/api/v1/sos/{contact_id}")).status_code == 404
        assert (await ac.delete(f"/api/v1/sos/{contact_id}", headers=admin_headers)).status_code == 204
