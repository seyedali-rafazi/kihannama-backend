import asyncio
import logging
from sqlalchemy import select, func
from ..config import settings
from ..database import AsyncSessionLocal, async_engine, Base, mongo_db, init_mongo
from ..models.satellite import Satellite
from ..models.station import SpaceStation, GroundStation
from ..models.launcher import Launcher
from .tle_parser import parse_tle_file
from .station_parser import parse_station_ops_csv
from .launcher_data import LAUNCHERS_SEED_DATA
from .ground_station_data import GROUND_STATIONS_SEED_DATA

logger = logging.getLogger("kihannama.seeder")


async def seed_stations(session):
    try:
        count_res = await session.execute(select(func.count(SpaceStation.id)))
        count = count_res.scalar() or 0
        if count > 0:
            logger.info(f"Space stations already populated ({count} records). Skipping.")
            return

        logger.info("Parsing and seeding space stations from station-ops.csv...")
        stations = parse_station_ops_csv(str(settings.RESOLVED_STATION_OPS_PATH))
        
        db_stations = [SpaceStation(**s) for s in stations]
        session.add_all(db_stations)
        await session.commit()
        logger.info(f"Successfully seeded {len(stations)} space station records.")

        # Also populate MongoDB if connected
        if mongo_db is not None:
            try:
                col = mongo_db["space_stations"]
                await col.delete_many({})
                await col.insert_many(stations)
                logger.info("Synchronized space stations to MongoDB collection.")
            except Exception as me:
                logger.warning(f"MongoDB space stations sync error: {me}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error seeding space stations: {e}")

async def seed_satellites(session, max_count: int = 5000):
    try:
        count_res = await session.execute(select(func.count(Satellite.id)))
        count = count_res.scalar() or 0
        if count > 0:
            logger.info(f"Satellites already populated ({count} records). Skipping.")
            return

        logger.info(f"Parsing and seeding up to {max_count} active satellites from active-satellite.txt...")
        batch = []
        total_inserted = 0
        
        for sat_data in parse_tle_file(str(settings.RESOLVED_ACTIVE_SATELLITE_PATH)):
            batch.append(Satellite(**sat_data))
            if len(batch) >= 1000:
                session.add_all(batch)
                await session.commit()
                total_inserted += len(batch)
                logger.info(f"Inserted {total_inserted} satellites...")
                batch = []
                if total_inserted >= max_count:
                    break

        if batch and total_inserted < max_count:
            session.add_all(batch)
            await session.commit()
            total_inserted += len(batch)

        logger.info(f"Successfully seeded {total_inserted} satellites into PostgreSQL.")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error seeding satellites: {e}")

async def seed_launchers(session):
    try:
        count_res = await session.execute(select(func.count(Launcher.id)))
        count = count_res.scalar() or 0
        if count > 0:
            logger.info(f"Launchers already populated ({count} records). Skipping.")
            return

        logger.info("Seeding launchers catalog...")
        db_launchers = [Launcher(**item) for item in LAUNCHERS_SEED_DATA]
        session.add_all(db_launchers)
        await session.commit()
        logger.info(f"Successfully seeded {len(db_launchers)} launcher records.")

        if mongo_db is not None:
            try:
                col = mongo_db["launchers"]
                await col.delete_many({})
                await col.insert_many(LAUNCHERS_SEED_DATA)
                logger.info("Synchronized launchers to MongoDB collection.")
            except Exception as me:
                logger.warning(f"MongoDB launchers sync error: {me}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error seeding launchers: {e}")

async def seed_ground_stations(session):
    try:
        count_res = await session.execute(select(func.count(GroundStation.id)))
        count = count_res.scalar() or 0
        if count > 0:
            logger.info(f"Ground stations already populated ({count} records). Skipping.")
            return

        logger.info("Seeding ground stations catalog...")
        db_stations = [GroundStation(**item) for item in GROUND_STATIONS_SEED_DATA]
        session.add_all(db_stations)
        await session.commit()
        logger.info(f"Successfully seeded {len(db_stations)} ground station records.")

        if mongo_db is not None:
            try:
                col = mongo_db["ground_stations"]
                await col.delete_many({})
                await col.insert_many(GROUND_STATIONS_SEED_DATA)
                logger.info("Synchronized ground stations to MongoDB collection.")
            except Exception as me:
                logger.warning(f"MongoDB ground stations sync error: {me}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error seeding ground stations: {e}")

async def run_seed():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await init_mongo()

    async with AsyncSessionLocal() as session:
        await seed_stations(session)
        await seed_ground_stations(session)
        await seed_launchers(session)
        await seed_satellites(session)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())

