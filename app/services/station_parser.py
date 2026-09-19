import csv
import math
from pathlib import Path
from typing import List, Dict, Any

MU = 398600.4418
EARTH_RADIUS_KM = 6378.137

# Metadata registry for space stations and docked craft
STATION_METADATA: Dict[str, Dict[str, Any]] = {
    "ISS (ZARYA)": {
        "slug": "iss-zarya",
        "station_group": "ISS",
        "station_type": "coreModule",
        "name_fa": "ایستگاه بین‌المللی فضایی (زاریا)",
        "operator_en": "NASA / Roscosmos",
        "operator_fa": "ناسا / روسکاسموس",
        "badge_en": "Core Module",
        "badge_fa": "ماژول اصلی",
        "year": 1998,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/International_Space_Station_after_undocking_of_STS-132.jpg/640px-International_Space_Station_after_undocking_of_STS-132.jpg",
        "description_en": "First module of the International Space Station launched in 1998, providing electrical power, storage, and propulsion control.",
        "description_fa": "نخستین ماژول ایستگاه فضایی بین‌المللی پرتاب‌شده در ۱۹۹۸ که تأمین برق، انبارش و مانور مداری اولیه را عهده‌دار بود.",
        "abilities_en": ["Microgravity Science", "Continuous Human Presence", "Earth Observation", "Orbital Lab"],
        "abilities_fa": ["علوم ریزگرانش", "حضور مداوم انسان", "دیده‌بانی زمین", "آزمایشگاه مداری"],
    },
    "POISK": {
        "slug": "iss-poisk",
        "station_group": "ISS",
        "station_type": "labModule",
        "name_fa": "ماژول پوئیسک (ISS)",
        "operator_en": "Roscosmos",
        "operator_fa": "روسکاسموس",
        "badge_en": "Docking & Science",
        "badge_fa": "اتصال و پژوهش",
        "year": 2009,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Mini-Research_Module_2_%28Poisk%29.jpg/640px-Mini-Research_Module_2_%28Poisk%29.jpg",
        "description_en": "Russian Mini-Research Module 2 (MRM-2) functioning as an airlock for spacewalks and docking port for Soyuz and Progress.",
        "description_fa": "ماژول پژوهشی شماره ۲ روسیه که به عنوان هوابند راهپیمایی‌های فضایی و پورت اتصال سایوز و پروگرس عمل می‌کند.",
        "abilities_en": ["Spacewalk Airlock", "Soyuz Docking", "External Science Payload"],
        "abilities_fa": ["هوابند پیاده‌روی فضایی", "اتصال سایوز", "محموله‌های علمی بیرونی"],
    },
    "CSS (TIANHE)": {
        "slug": "css-tianhe",
        "station_group": "Tiangong",
        "station_type": "coreModule",
        "name_fa": "ایستگاه تیانگونگ (ماژول تیان‌هه)",
        "operator_en": "CMSA (China)",
        "operator_fa": "سازمان فضایی سرنشین‌دار چین",
        "badge_en": "Core Module",
        "badge_fa": "ماژول اصلی",
        "year": 2021,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Tiangong_Space_Station_in_November_2022.jpg/640px-Tiangong_Space_Station_in_November_2022.jpg",
        "description_en": "Core module of China's Tiangong space station, providing living quarters, life support, and orbital guidance.",
        "description_fa": "ماژول مرکزی ایستگاه فضایی تیانگونگ چین که محل سکونت فضانوردان، پشتیبانی حیات و هدایت ایستگاه است.",
        "abilities_en": ["3-Taikonaut Quarters", "Robotic Arm Control", "Ion Propulsion", "Station Control"],
        "abilities_fa": ["سکونتگاه ۳ فضانورد", "کنترل بازوی رباتیک", "پیش‌رانش یونی", "کنترل ایستگاه"],
    },
    "ISS (NAUKA)": {
        "slug": "iss-nauka",
        "station_group": "ISS",
        "station_type": "labModule",
        "name_fa": "آزمایشگاه ناوکا (ISS)",
        "operator_en": "Roscosmos / ESA",
        "operator_fa": "روسکاسموس / اسا",
        "badge_en": "Laboratory",
        "badge_fa": "آزمایشگاه مداری",
        "year": 2021,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Nauka_module_attached_to_the_ISS.jpg/640px-Nauka_module_attached_to_the_ISS.jpg",
        "description_en": "Multipurpose Laboratory Module (MLM) providing extensive research facilities and hosting the European Robotic Arm (ERA).",
        "description_fa": "ماژول آزمایشگاهی چندمنظوره روسیه با امکانات گسترده پژوهشی و بازوی رباتیک اروپایی (ERA).",
        "abilities_en": ["Materials Science", "Fluid Physics", "European Robotic Arm", "Crew Quarters"],
        "abilities_fa": ["علم مواد", "فیزیک سیالات", "بازوی رباتیک اروپا", "اتاق خواب خدمه"],
    },
    "CSS (WENTIAN)": {
        "slug": "css-wentian",
        "station_group": "Tiangong",
        "station_type": "labModule",
        "name_fa": "ماژول علمی ون‌تیان (تیانگونگ)",
        "operator_en": "CMSA (China)",
        "operator_fa": "سازمان فضایی سرنشین‌دار چین",
        "badge_en": "Science Lab",
        "badge_fa": "آزمایشگاه علمی",
        "year": 2022,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Tiangong_Space_Station_in_November_2022.jpg/640px-Tiangong_Space_Station_in_November_2022.jpg",
        "description_en": "First lab module of Tiangong space station equipped for life science research and extravehicular activity spacewalk airlock.",
        "description_fa": "نخستین ماژول آزمایشگاهی تیانگونگ مجهز به محفظه‌های علوم زیستی، بوم‌شناسی فضایی و هوابند جدید راهپیمایی.",
        "abilities_en": ["Biology Research", "EVA Airlock", "Secondary Robotic Arm", "Solar Arrays"],
        "abilities_fa": ["پژوهش زیست‌شناسی", "هوابند پیاده‌روی فضایی", "بازوی رباتیک کمکی", "آرایه‌های خورشیدی"],
    },
    "CSS (MENGTIAN)": {
        "slug": "css-mengtian",
        "station_group": "Tiangong",
        "station_type": "labModule",
        "name_fa": "ماژول علمی منگ‌تیان (تیانگونگ)",
        "operator_en": "CMSA (China)",
        "operator_fa": "سازمان فضایی سرنشین‌دار چین",
        "badge_en": "Physics Lab",
        "badge_fa": "آزمایشگاه فیزیک",
        "year": 2022,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Tiangong_Space_Station_in_November_2022.jpg/640px-Tiangong_Space_Station_in_November_2022.jpg",
        "description_en": "Second lab module of Tiangong dedicated to microgravity physics, aerospace technology, and payload deployment.",
        "description_fa": "دومین ماژول آزمایشگاهی تیانگونگ اختصاص‌یافته به فیزیک ریزگرانش، احتراق و پرتاب ریزماهواره‌ها از فضا.",
        "abilities_en": ["Cold Atom Physics", "CubeSat Deployer", "Fluid Dynamics", "High-Precision Clocks"],
        "abilities_fa": ["فیزیک اتم سرد", "پرتاب‌کننده کیوب‌ست", "دینامیک سیالات", "ساعت‌های اتمی دقیق"],
    },
    "CREW DRAGON 12": {
        "slug": "crew-dragon-12",
        "station_group": "ISS",
        "station_type": "crewCraft",
        "name_fa": "فضاپیمای سرنشین‌دار دراگون ۱۲",
        "operator_en": "SpaceX / NASA",
        "operator_fa": "اسپیس‌ایکس / ناسا",
        "badge_en": "Crew Spacecraft",
        "badge_fa": "فضاپیمای سرنشین‌دار",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Crew_Dragon_approaches_ISS.jpg/640px-Crew_Dragon_approaches_ISS.jpg",
        "description_en": "Autonomous reusable crew spacecraft transporting astronauts to and from the International Space Station.",
        "description_fa": "فضاپیمای سرنشین‌دار و قابل استفاده مجدد اسپیس‌ایکس جهت انتقال فضانوردان به ایستگاه فضایی بین‌المللی.",
        "abilities_en": ["Autonomous Docking", "4-Crew Capacity", "Emergency Evacuation", "SuperDraco Thrusters"],
        "abilities_fa": ["اتصال خودکار مداری", "ظرفیت ۴ سرنشین", "تخلیه اضطراری", "پیش‌رانه‌های سوپردراکو"],
    },
    "SOYUZ-MS 29": {
        "slug": "soyuz-ms-29",
        "station_group": "ISS",
        "station_type": "crewCraft",
        "name_fa": "فضاپیمای سایوز ام‌اس ۲۹",
        "operator_en": "Roscosmos",
        "operator_fa": "روسکاسموس",
        "badge_en": "Crew Spacecraft",
        "badge_fa": "فضاپیمای سرنشین‌دار",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Soyuz_MS-13_approaches_the_ISS.jpg/640px-Soyuz_MS-13_approaches_the_ISS.jpg",
        "description_en": "Russian crewed spacecraft providing astronaut transport and acting as a continuous lifeboat for the ISS expedition.",
        "description_fa": "فضاپیمای سرنشین‌دار روسی برای انتقال فضانوردان و ایفای نقش قایق نجات مداوم ایستگاه فضایی.",
        "abilities_en": ["3-Cosmonaut Transport", "Kurs Rendezvous Radar", "Lifeboat Function", "Parachute Landing"],
        "abilities_fa": ["انتقال ۳ کیهان‌نورد", "رادار ره‌گیری کورس", "قابلیت قایق نجات", "فرود با چتر نجات"],
    },
    "SHENZHOU-23 (SZ-23)": {
        "slug": "shenzhou-23",
        "station_group": "Tiangong",
        "station_type": "crewCraft",
        "name_fa": "فضاپیمای سرنشین‌دار شنژو ۲۳",
        "operator_en": "CMSA (China)",
        "operator_fa": "سازمان فضایی سرنشین‌دار چین",
        "badge_en": "Crew Spacecraft",
        "badge_fa": "فضاپیمای سرنشین‌دار",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Shenzhou_spacecraft_model.jpg/640px-Shenzhou_spacecraft_model.jpg",
        "description_en": "Chinese crew spacecraft delivering taikonauts to the Tiangong space station for long-duration orbital rotations.",
        "description_fa": "فضاپیمای سرنشین‌دار چین برای اعزام فضانوردان به ایستگاه تیانگونگ جهت شیفت‌های بلندمدت مداری.",
        "abilities_en": ["Orbital Module", "Reentry Capsule", "Precision Docking", "Taikonaut Transport"],
        "abilities_fa": ["ماژول مداری", "کپسول بازگشت", "اتصال دقیق خودکار", "انتقال فضانوردان"],
    },
    "CYGNUS NG-24": {
        "slug": "cygnus-ng-24",
        "station_group": "ISS",
        "station_type": "cargoCraft",
        "name_fa": "فضاپیمای باری سیگنوس ان‌جی ۲۴",
        "operator_en": "Northrop Grumman / NASA",
        "operator_fa": "نورثروپ گرومن / ناسا",
        "badge_en": "Cargo Resupply",
        "badge_fa": "ترابری باری",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Cygnus_PCM_attached_to_Node_2.jpg/640px-Cygnus_PCM_attached_to_Node_2.jpg",
        "description_en": "Automated cargo vessel supplying pressurized science experiments, food, and hardware to the ISS crew.",
        "description_fa": "فضاپیمای خودکار ترابری فضایی حامل محموله‌های تحت‌فشار، آزمایش‌های علمی و مایحتاج خدمه ایستگاه فضایی.",
        "abilities_en": ["Pressurized Cargo", "ISS Orbit Reboost", "Destructive Reentry Disposal"],
        "abilities_fa": ["بار تحت فشار", "تقویت و اصلاح مدار ایستگاه", "دفع ایمن پسماند"],
    },
    "TIANZHOU-10": {
        "slug": "tianzhou-10",
        "station_group": "Tiangong",
        "station_type": "cargoCraft",
        "name_fa": "فضاپیمای باری تیانژو ۱۰",
        "operator_en": "CMSA (China)",
        "operator_fa": "سازمان فضایی سرنشین‌دار چین",
        "badge_en": "Cargo Resupply",
        "badge_fa": "ترابری باری",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Tiangong_Space_Station_in_November_2022.jpg/640px-Tiangong_Space_Station_in_November_2022.jpg",
        "description_en": "Automated freight transport spacecraft delivering propellant, consumables, and scientific hardware to Tiangong.",
        "description_fa": "فضاپیمای باربری خودکار انتقال‌دهنده پیشرانه مایع، تجهیزات علمی و ملزومات ایستگاه تیانگونگ.",
        "abilities_en": ["In-Orbit Refueling", "6.5-Ton Payload", "Fast Autonomous Rendezvous"],
        "abilities_fa": ["سوخت‌گیری در مدار", "حمل ۶.۵ تن بار", "اتصال سریع خودکار"],
    },
    "PROGRESS-MS 34": {
        "slug": "progress-ms-34",
        "station_group": "ISS",
        "station_type": "cargoCraft",
        "name_fa": "فضاپیمای باری پروگرس ام‌اس ۳۴",
        "operator_en": "Roscosmos",
        "operator_fa": "روسکاسموس",
        "badge_en": "Cargo Resupply",
        "badge_fa": "ترابری باری",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Progress_MS-14_approaching_the_ISS.jpg/640px-Progress_MS-14_approaching_the_ISS.jpg",
        "description_en": "Russian robotic resupply spacecraft providing orbital station boosts, water, oxygen, and scientific gear.",
        "description_fa": "فضاپیمای خودکار روسی تأمین‌کننده اکسیژن، آب، سوخت مداری و مانورهای ارتفاعی ایستگاه بین‌المللی.",
        "abilities_en": ["Orbital Boost Engine", "Fuel Transfer", "Waste Disposal"],
        "abilities_fa": ["موتور ارتقای مدار", "انتقال سوخت", "دفع ایمن پسماند"],
    },
    "PROGRESS-MS 35": {
        "slug": "progress-ms-35",
        "station_group": "ISS",
        "station_type": "cargoCraft",
        "name_fa": "فضاپیمای باری پروگرس ام‌اس ۳۵",
        "operator_en": "Roscosmos",
        "operator_fa": "روسکاسموس",
        "badge_en": "Cargo Resupply",
        "badge_fa": "ترابری باری",
        "year": 2026,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Progress_MS-14_approaching_the_ISS.jpg/640px-Progress_MS-14_approaching_the_ISS.jpg",
        "description_en": "Russian cargo resupply spacecraft arriving with scientific experiments and food rations.",
        "description_fa": "فضاپیمای ترابری پروگرس حامل آزمایش‌های علمی تازه، آب و سوخت برای فضانوردان.",
        "abilities_en": ["Automated Docking", "Cargo Transfer", "ISS Reboost"],
        "abilities_fa": ["اتصال خودکار", "انتقال بار", "افزایش ارتفاع مداری"],
    },
}

def parse_station_ops_csv(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"station-ops.csv not found at: {file_path}")

    stations: List[Dict[str, Any]] = []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = row["OBJECT_NAME"].strip()
            norad_cat_id = row["NORAD_CAT_ID"].strip()
            object_id = row.get("OBJECT_ID", "").strip()
            epoch = row.get("EPOCH", "").strip()

            mean_motion = float(row["MEAN_MOTION"])
            eccentricity = float(row["ECCENTRICITY"])
            inclination = float(row["INCLINATION"])
            ra_of_asc_node = float(row["RA_OF_ASC_NODE"])
            arg_of_pericenter = float(row["ARG_OF_PERICENTER"])
            mean_anomaly = float(row["MEAN_ANOMALY"])

            # Compute orbital period, altitude, velocity
            period_min = 1440.0 / mean_motion
            n_rad_s = (mean_motion * 2.0 * math.pi) / 86400.0
            semi_major_km = math.pow(MU / (n_rad_s * n_rad_s), 1.0 / 3.0)
            altitude_km = semi_major_km - EARTH_RADIUS_KM
            # Circular velocity approx: v = sqrt(mu / r)
            velocity_km_s = math.sqrt(MU / semi_major_km)

            # Retrieve rich metadata or synthesize default
            meta = STATION_METADATA.get(raw_name)
            if not meta:
                # Secondary payload or debris in station group
                is_deb = "DEB" in raw_name or "R/B" in raw_name
                group = "Debris" if is_deb else "Station Payload"
                stype = "debris" if is_deb else "microsat"
                slug = raw_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-")
                meta = {
                    "slug": slug,
                    "station_group": group,
                    "station_type": stype,
                    "name_fa": raw_name,
                    "operator_en": "International",
                    "operator_fa": "بین‌المللی",
                    "badge_en": "Orbital Object" if not is_deb else "Station Debris",
                    "badge_fa": "شیء مداری" if not is_deb else "ضایعات ایستگاه",
                    "year": 2026,
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Crew_Dragon_approaches_ISS.jpg/640px-Crew_Dragon_approaches_ISS.jpg",
                    "description_en": f"Operational object associated with space station orbital activities: {raw_name}.",
                    "description_fa": f"شیء مداری مرتبط با عملیات‌های ایستگاه‌های فضایی: {raw_name}.",
                    "abilities_en": ["Orbital Tracking", "Telemetry Monitoring"],
                    "abilities_fa": ["ردیابی مداری", "پایش تله‌متری"],
                }

            # Infographic sections
            infographic_left = [
                {
                    "titleEn": "Orbital Altitude",
                    "titleFa": "ارتفاع مداری",
                    "descriptionEn": f"{round(altitude_km, 1)} km above sea level in Low Earth Orbit.",
                    "descriptionFa": f"{round(altitude_km, 1)} کیلومتر بالاتر از سطح دریا در مدار پایینی زمین.",
                },
                {
                    "titleEn": "Orbital Velocity",
                    "titleFa": "سرعت مداری",
                    "descriptionEn": f"{round(velocity_km_s, 2)} km/s (~{round(velocity_km_s * 3600):,} km/h).",
                    "descriptionFa": f"{round(velocity_km_s, 2)} کیلومتر بر ثانیه (~{round(velocity_km_s * 3600):,} کیلومتر بر ساعت).",
                },
                {
                    "titleEn": "Inclination",
                    "titleFa": "زاویه انحراف مداری",
                    "descriptionEn": f"{round(inclination, 2)}° orbital tilt relative to Earth equator.",
                    "descriptionFa": f"{round(inclination, 2)} درجه زاویه مداری نسبت به خط استوا.",
                },
            ]

            infographic_right = [
                {
                    "titleEn": "Orbital Period",
                    "titleFa": "دوره تناوب مداری",
                    "descriptionEn": f"{round(period_min, 1)} minutes per Earth revolution.",
                    "descriptionFa": f"{round(period_min, 1)} دقیقه برای هر دور چرخش دور زمین.",
                },
                {
                    "titleEn": "Daily Revolutions",
                    "titleFa": "دورهای روزانه",
                    "descriptionEn": f"{round(mean_motion, 2)} orbits per 24 hours.",
                    "descriptionFa": f"{round(mean_motion, 2)} بار چرخش کامل در ۲۴ ساعت.",
                },
                {
                    "titleEn": "NORAD Catalog ID",
                    "titleFa": "شناسه رهگیری نوراد",
                    "descriptionEn": f"Catalog ID: {norad_cat_id} · COSPAR: {object_id}",
                    "descriptionFa": f"شناسه نوراد: {norad_cat_id} · شناسه بین‌المللی: {object_id}",
                },
            ]

            stations.append({
                "slug": meta["slug"],
                "object_name": raw_name,
                "norad_cat_id": norad_cat_id,
                "object_id": object_id,
                "epoch": epoch,
                "mean_motion": round(mean_motion, 8),
                "eccentricity": round(eccentricity, 7),
                "inclination": round(inclination, 4),
                "ra_of_asc_node": round(ra_of_asc_node, 4),
                "arg_of_pericenter": round(arg_of_pericenter, 4),
                "mean_anomaly": round(mean_anomaly, 4),
                "altitude": round(altitude_km, 2),
                "velocity": round(velocity_km_s, 2),
                "period": round(period_min, 2),
                "station_group": meta["station_group"],
                "station_type": meta["station_type"],
                "status": "operational",
                "year": meta["year"],
                "name_fa": meta.get("name_fa", raw_name),
                "operator_en": meta["operator_en"],
                "operator_fa": meta["operator_fa"],
                "badge_en": meta.get("badge_en", "Space Station"),
                "badge_fa": meta.get("badge_fa", "ایستگاه فضایی"),
                "image_url": meta["image_url"],
                "description_en": meta.get("description_en", ""),
                "description_fa": meta.get("description_fa", ""),
                "abilities_en": meta.get("abilities_en", []),
                "abilities_fa": meta.get("abilities_fa", []),
                "infographic_left": infographic_left,
                "infographic_right": infographic_right,
            })

    return stations
