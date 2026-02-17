"""
Seed script – populates the database with predefined Hyderabad areas.
Run this after the database tables are created.
"""

import logging
from sqlalchemy.orm import Session
from app.models.area import Area

logger = logging.getLogger(__name__)

# ─── Predefined Hyderabad areas with real coordinates ───
SEED_AREAS = [
    {
        "name": "Gachibowli",
        "center_lat": 17.4401,
        "center_lon": 78.3489,
        "boundary_type": "circle",
        "radius_meters": 2500,
    },
    {
        "name": "Madhapur",
        "center_lat": 17.4483,
        "center_lon": 78.3915,
        "boundary_type": "circle",
        "radius_meters": 2000,
    },
    {
        "name": "Hitech City",
        "center_lat": 17.4435,
        "center_lon": 78.3772,
        "boundary_type": "circle",
        "radius_meters": 2000,
    },
    {
        "name": "Kukatpally",
        "center_lat": 17.4849,
        "center_lon": 78.3942,
        "boundary_type": "circle",
        "radius_meters": 3000,
    },
    {
        "name": "Kondapur",
        "center_lat": 17.4600,
        "center_lon": 78.3548,
        "boundary_type": "circle",
        "radius_meters": 2200,
    },
    {
        "name": "LB Nagar",
        "center_lat": 17.3457,
        "center_lon": 78.5522,
        "boundary_type": "circle",
        "radius_meters": 2500,
    },
]


def seed_areas(db: Session) -> None:
    """
    Insert predefined areas into the database if they don't already exist.
    Uses upsert-like logic: skip if area name already exists.
    """
    for area_data in SEED_AREAS:
        existing = db.query(Area).filter(Area.name == area_data["name"]).first()
        if existing:
            logger.info(f"Area '{area_data['name']}' already exists, skipping.")
            continue

        area = Area(**area_data)
        db.add(area)
        logger.info(f"Seeded area: {area_data['name']}")

    db.commit()
    logger.info("Area seeding complete.")
