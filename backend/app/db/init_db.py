import logging
from datetime import date, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import async_engine, AsyncSessionLocal
from app.db.models.user import User
from app.db.models.campus import Building, Floor, Room, Facility
from app.db.models.event import Event
from app.db.models.exam import Exam
from app.db.models.sos import SOSContact
from app.db.models.audit import AuditLog

logger = logging.getLogger(__name__)


async def init_database():
    """Create database tables if they do not exist."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created.")

    # Seed initial data
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)


async def seed_initial_data(session: AsyncSession):
    # 1. Seed Admin User
    admin_result = await session.execute(select(User).where(User.email == settings.SEED_ADMIN_EMAIL))
    admin_user = admin_result.scalar_one_or_none()
    if not admin_user:
        admin_user = User(
            email=settings.SEED_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.SEED_ADMIN_PASSWORD),
            display_name=settings.SEED_ADMIN_NAME,
            role="admin",
            department="Administration",
            is_active=True
        )
        session.add(admin_user)

        # Seed demo student & faculty
        student_user = User(
            email=settings.SEED_STUDENT_EMAIL,
            hashed_password=get_password_hash(settings.SEED_STUDENT_PASSWORD),
            display_name=settings.SEED_STUDENT_NAME,
            role="student",
            department="Computer Engineering",
            is_active=True
        )
        faculty_user = User(
            email=settings.SEED_FACULTY_EMAIL,
            hashed_password=get_password_hash(settings.SEED_FACULTY_PASSWORD),
            display_name=settings.SEED_FACULTY_NAME,
            role="faculty",
            department="Computer Science & Engineering",
            is_active=True
        )
        session.add(student_user)
        session.add(faculty_user)
        await session.flush()
        logger.info("Created default admin, faculty, and student user accounts.")

    # Check and insert audit log if none exist
    audit_check = await session.execute(select(AuditLog))
    if not audit_check.scalars().first():
        session.add(AuditLog(
            actor_id=admin_user.id if admin_user else "system",
            actor_email=admin_user.email if admin_user else "system@silveroakuni.ac.in",
            action="SYSTEM_INIT",
            entity_type="system",
            entity_id="init",
            details="System initialized with default seed accounts and campus dataset."
        ))

    # 2. Seed Campus Buildings
    b_result = await session.execute(select(Building))
    if not b_result.scalars().first():
        buildings = [
            Building(
                id="innovation-hub",
                name="Innovation Hub",
                short_code="IH",
                department="Computer Science & Engineering",
                faculty_lead="Dr. Meera Shah",
                floors_count=4,
                pos_x=-4.4,
                pos_z=1.2,
                dim_w=4.2,
                dim_d=3.1,
                dim_h=5.2,
                description="State-of-the-art research, computing labs, robotics, and innovation center.",
                aliases=["block b", "બ્લોક બી", "ब्लॉक बी", "ih", "cse block"],
                metadata_json={"zone": "A", "total_rooms": 24, "year_built": 2021},
                is_active=True
            ),
            Building(
                id="central-library",
                name="Central Library",
                short_code="LIB",
                department="Learning Commons",
                faculty_lead="Library Services",
                floors_count=3,
                pos_x=4.1,
                pos_z=-2.3,
                dim_w=3.8,
                dim_d=3.2,
                dim_h=3.4,
                description="3-floor comprehensive learning commons with digital archives and reading halls.",
                aliases=["library", "પુસ્તકાલય", "पुस्तकालय", "reading room", "lib"],
                metadata_json={"zone": "Central", "books_count": 45000},
                is_active=True
            ),
            Building(
                id="admin-block",
                name="Admin Block",
                short_code="AB",
                department="Administration",
                faculty_lead="Registrar Office",
                floors_count=2,
                pos_x=-5.1,
                pos_z=-4.2,
                dim_w=3.2,
                dim_d=2.8,
                dim_h=2.8,
                description="Main administrative block housing student section, accounts, and chancellor's office.",
                aliases=["reception", "વહીવટી બ્લોક", "प्रशासन ब्लॉक", "admin"],
                metadata_json={"zone": "C", "reception_desk": True},
                is_active=True
            ),
            Building(
                id="school-design",
                name="School of Design",
                short_code="SD",
                department="Design & Architecture",
                faculty_lead="Prof. Rohan Patel",
                floors_count=3,
                pos_x=3.6,
                pos_z=3.4,
                dim_w=4.4,
                dim_d=2.7,
                dim_h=4.1,
                description="Creative design studios, animation labs, and architecture workshops.",
                aliases=["design school", "ડિઝાઇન", "डिजाइन", "sd"],
                metadata_json={"zone": "D", "studios_count": 8},
                is_active=True
            )
        ]
        session.add_all(buildings)
        await session.flush()

        # Seed Rooms
        rooms = [
            Room(
                id="room-b204",
                building_id="innovation-hub",
                floor_number=2,
                room_number="B-204",
                name="Room B-204 (AI & ML Lab)",
                room_type="lab",
                department="Computer Science & Engineering",
                faculty_in_charge="Dr. Meera Shah",
                capacity=60,
                model_id="b204",
                coordinates_3d={"x": -4.4, "y": 2.5, "z": 1.2},
                aliases=["b204", "classroom 204", "રૂમ બી ૨૦૪", "कमरा बी 204", "ai lab"],
                is_accessible=True,
                is_active=True
            ),
            Room(
                id="lab-b108",
                building_id="innovation-hub",
                floor_number=1,
                room_number="B-108",
                name="Computer Lab 19 (High Performance Computing)",
                room_type="lab",
                department="Computer Science & Engineering",
                faculty_in_charge="Prof. Amit Sharma",
                capacity=80,
                model_id="b108",
                coordinates_3d={"x": -4.4, "y": 1.0, "z": 1.2},
                aliases=["computer lab", "લેબ", "कंप्यूटर लैब", "hpc lab"],
                is_accessible=True,
                is_active=True
            ),
            Room(
                id="meera-shah",
                building_id="innovation-hub",
                floor_number=3,
                room_number="B-312",
                name="Dr. Meera Shah (Head of Dept. Cabin)",
                room_type="faculty-office",
                department="Computer Science & Engineering",
                faculty_in_charge="Dr. Meera Shah",
                capacity=5,
                model_id="b312",
                coordinates_3d={"x": -4.4, "y": 3.8, "z": 1.2},
                aliases=["meera", "hod cse", "computer science faculty cabin"],
                is_accessible=True,
                is_active=True
            ),
            Room(
                id="seminar-hall-1",
                building_id="central-library",
                floor_number=1,
                room_number="LIB-101",
                name="Central Seminar Hall",
                room_type="hall",
                department="Learning Commons",
                capacity=200,
                model_id="lib101",
                coordinates_3d={"x": 4.1, "y": 1.0, "z": -2.3},
                aliases=["seminar hall", "conference hall"],
                is_accessible=True,
                is_active=True
            ),
            Room(
                id="placement-cell",
                building_id="admin-block",
                floor_number=1,
                room_number="AB-105",
                name="Training & Placement Cell (T&P)",
                room_type="cell",
                department="Placement & Corporate Relations",
                capacity=30,
                model_id="ab105",
                coordinates_3d={"x": -5.1, "y": 1.0, "z": -4.2},
                aliases=["placement", "job cell", "t&p"],
                is_accessible=True,
                is_active=True
            )
        ]
        session.add_all(rooms)

        # Seed Facilities
        facilities = [
            Facility(
                id="medical-room",
                name="Campus Medical Center & First Aid",
                facility_type="medical",
                building_id="admin-block",
                location_description="Admin Block · Ground floor · 24/7 Nurse Available",
                code_symbol="✚",
                aliases=["clinic", "doctor", "મેડિકલ રૂમ", "चिकित्सा कक्ष", "hospital"],
                is_accessible=True,
                metadata_json={"contact": "+91 79 6604 6300", "emergency": True},
                is_active=True
            ),
            Facility(
                id="canteen",
                name="Central Food Court & Canteen",
                facility_type="canteen",
                building_id=None,
                location_description="Central Campus · Ground level · 8:00 AM – 8:00 PM",
                code_symbol="◒",
                aliases=["food court", "cafeteria", "કેન્ટીન", "कैंटीन"],
                is_accessible=True,
                metadata_json={"timings": "8 AM - 8 PM", "seating": 400},
                is_active=True
            ),
            Facility(
                id="parking",
                name="East Vehicle Parking",
                facility_type="parking",
                building_id=None,
                location_description="East Gate · 180 two/four-wheeler spaces · Accessible bays",
                code_symbol="P",
                aliases=["car park", "bike parking", "પાર્કિંગ", "पार्किंग"],
                is_accessible=True,
                metadata_json={"capacity": 180},
                is_active=True
            ),
            Facility(
                id="main-gate",
                name="University Main Gate & Security",
                facility_type="gate",
                building_id=None,
                location_description="North entrance · Security check & Visitor pass desk",
                code_symbol="⌂",
                aliases=["entrance", "north gate", "મુખ્ય દરવાજો", "मुख्य द्वार"],
                is_accessible=True,
                metadata_json={"guard_post": True},
                is_active=True
            ),
            Facility(
                id="auditorium",
                name="Grand University Auditorium",
                facility_type="auditorium",
                building_id=None,
                location_description="Central Quad · 650 Air-conditioned seats · Barrier-free ramp",
                code_symbol="AU",
                aliases=["hall", "main auditorium", "ઓડિટોરિયમ", "सभागार"],
                is_accessible=True,
                metadata_json={"seats": 650},
                is_active=True
            ),
            Facility(
                id="assembly-area",
                name="Emergency Assembly Ground",
                facility_type="sports",
                building_id=None,
                location_description="Main Sports Ground · Primary designated emergency safe zone",
                code_symbol="⌖",
                aliases=["sports ground", "safe zone", "મિલન સ્થળ", "सभा क्षेत्र"],
                is_accessible=True,
                metadata_json={"safe_zone": True},
                is_active=True
            )
        ]
        session.add_all(facilities)
        await session.flush()
        logger.info("Seeded campus buildings, rooms, and facilities.")

    # Seed floor records independently so existing building databases can be upgraded.
    buildings_result = await session.execute(select(Building))
    for building in buildings_result.scalars().all():
        floors_result = await session.execute(
            select(Floor.floor_number).where(Floor.building_id == building.id)
        )
        existing_floor_numbers = set(floors_result.scalars().all())
        missing_floors = [
            Floor(
                id=f"{building.id}-floor-{floor_number}",
                building_id=building.id,
                floor_number=floor_number,
                floor_label="Ground Floor" if floor_number == 0 else f"Floor {floor_number}",
            )
            for floor_number in range(building.floors_count)
            if floor_number not in existing_floor_numbers
        ]
        session.add_all(missing_floors)
    await session.flush()

    # 3. Seed Events
    e_result = await session.execute(select(Event))
    if not e_result.scalars().first():
        events = [
            Event(
                title="SOU TechFest 2026: AI & Robotics Expo",
                description="Annual national tech festival featuring hackathons, autonomous robotics, and project displays.",
                category="tech-fest",
                event_date=date(2026, 10, 15),
                start_time=time(9, 30),
                end_time=time(17, 30),
                venue="Innovation Hub & Central Quad",
                building_id="innovation-hub",
                room_id="room-b204",
                organizer="Faculty of Technology & Computer Applications",
                is_published=True
            ),
            Event(
                title="Industry Connect & Campus Placement Drive",
                description="On-campus interview drive with leading MNCs and tech startups for final year students.",
                category="academic",
                event_date=date(2026, 10, 20),
                start_time=time(10, 0),
                end_time=time(16, 0),
                venue="Grand University Auditorium",
                building_id="admin-block",
                room_id="placement-cell",
                organizer="Training & Placement Cell",
                is_published=True
            ),
            Event(
                title="Blood Donation & Health Checkup Camp",
                description="Free health checkup, optical screening, and voluntary blood donation drive organized with Red Cross.",
                category="social",
                event_date=date(2026, 10, 8),
                start_time=time(9, 0),
                end_time=time(15, 0),
                venue="Medical Room, Admin Block",
                building_id="admin-block",
                organizer="NSS Unit & SOU Medical Centre",
                is_published=True
            )
        ]
        session.add_all(events)
        await session.flush()

    # 4. Seed Exams
    ex_result = await session.execute(select(Exam))
    if not ex_result.scalars().first():
        exams = [
            Exam(
                subject_name="Distributed Cloud Computing & Microservices",
                subject_code="CS-701",
                course="B.Tech Computer Engineering",
                department="Computer Science & Engineering",
                semester=7,
                exam_date=date(2026, 10, 28),
                start_time=time(10, 30),
                end_time=time(13, 0),
                venue="Innovation Hub · Floor 2",
                building_id="innovation-hub",
                room_id="room-b204",
                status="scheduled",
                description="Mid-Semester Exam. Please carry university ID card and scientific calculator."
            ),
            Exam(
                subject_name="Advanced Deep Learning & Neural Networks",
                subject_code="AI-503",
                course="B.Tech Artificial Intelligence",
                department="Computer Science & Engineering",
                semester=5,
                exam_date=date(2026, 10, 30),
                start_time=time(14, 0),
                end_time=time(16, 30),
                venue="Innovation Hub · Lab B-108",
                building_id="innovation-hub",
                room_id="lab-b108",
                status="scheduled",
                description="Practical and theory examination conducted on GPU cluster."
            ),
            Exam(
                subject_name="Design Thinking and UX Principles",
                subject_code="DS-302",
                course="B.Des User Experience Design",
                department="Design & Architecture",
                semester=3,
                exam_date=date(2026, 11, 2),
                start_time=time(10, 0),
                end_time=time(13, 0),
                venue="School of Design · Studio 3",
                building_id="school-design",
                status="scheduled",
                description="Portfolio review and design sprint jury."
            )
        ]
        session.add_all(exams)
        await session.flush()

    # 5. Seed SOS Emergency Contacts
    sos_result = await session.execute(select(SOSContact))
    if not sos_result.scalars().first():
        sos_contacts = [
            SOSContact(
                title="Campus Security Control Room",
                category="security",
                phone_number="+91 79 6604 6301",
                alternate_phone="+91 98250 00001",
                location_name="Main Gate & Admin Post",
                building_id="admin-block",
                coordinates_3d={"x": -5.1, "y": 0, "z": -4.2},
                available_hours="24/7",
                priority=1,
                description="Immediate campus physical security, patrol response, and visitor issues.",
                is_active=True
            ),
            SOSContact(
                title="University Medical Centre & Ambulance",
                category="medical",
                phone_number="+91 79 6604 6300",
                alternate_phone="108",
                location_name="Admin Block Ground Floor",
                building_id="admin-block",
                coordinates_3d={"x": -5.1, "y": 0, "z": -4.2},
                available_hours="24/7 On-call Doctor & Ambulance",
                priority=1,
                description="First aid, trauma response, emergency medical room, and patient transport.",
                is_active=True
            ),
            SOSContact(
                title="Women Helpline & Anti-Ragging Cell",
                category="women_safety",
                phone_number="+91 79 6604 6305",
                alternate_phone="181",
                location_name="Admin Block Room AB-102",
                building_id="admin-block",
                coordinates_3d={"x": -5.1, "y": 0, "z": -4.2},
                available_hours="24/7 Toll Free",
                priority=2,
                description="Strict zero-tolerance anti-ragging support and women safety squad.",
                is_active=True
            ),
            SOSContact(
                title="Fire Emergency & Safety Officer",
                category="fire",
                phone_number="+91 79 6604 6310",
                alternate_phone="101",
                location_name="Central Utility Building",
                coordinates_3d={"x": 0, "y": 0, "z": 0},
                available_hours="24/7",
                priority=2,
                description="Fire alarms, extinguishers, evacuation marshals, and smoke response.",
                is_active=True
            )
        ]
        session.add_all(sos_contacts)
        await session.flush()

    await session.commit()
    logger.info("Database seeding completed successfully.")
