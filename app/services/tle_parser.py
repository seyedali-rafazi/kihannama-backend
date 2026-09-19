import math
from pathlib import Path
from typing import List, Dict, Any, Generator

MU = 398600.4418  # Earth gravitational parameter in km^3/s^2
EARTH_RADIUS_KM = 6378.137

def classify_orbit(altitude_km: float, inclination_deg: float) -> str:
    if altitude_km < 2000:
        return "LEO"
    elif 2000 <= altitude_km < 35000:
        return "MEO"
    elif 35000 <= altitude_km <= 36500 and inclination_deg < 25.0:
        return "GEO"
    else:
        return "HEO"

def classify_category(name: str) -> str:
    upper = name.upper()
    if "STARLINK" in upper:
        return "Starlink"
    if "ONEWEB" in upper:
        return "OneWeb"
    if any(k in upper for k in ["GPS", "NAVSTAR", "GLONASS", "BEIDOU", "GALILEO"]):
        return "Navigation"
    if any(k in upper for k in ["ISS", "TIANGONG", "CSS", "SHENZHOU", "CREW DRAGON", "SOYUZ"]):
        return "Space Station"
    if any(k in upper for k in ["GOES", "NOAA", "METEOSAT", "FENGYUN", "SENTINEL", "LANDSAT"]):
        return "Earth Observation"
    if any(k in upper for k in ["HUBBLE", "TELESCOPE", "CHANDRA", "SWIFT", "TESS", "SPEKTR"]):
        return "Scientific"
    return "Communication" if any(k in upper for k in ["SAT", "COM", "TEL"]) else "Other"

def parse_tle_file(file_path: str) -> Generator[Dict[str, Any], None, None]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"TLE file not found at: {file_path}")

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = [line.strip() for line in f if line.strip()]

    for i in range(0, len(lines), 3):
        if i + 2 >= len(lines):
            break

        name_line = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]

        if not (line1.startswith("1 ") and line2.startswith("2 ")):
            continue

        try:
            norad_id = line1[2:7].strip()
            intl_desig = line1[9:17].strip()
            epoch = line1[18:32].strip()

            inclination = float(line2[8:16])
            raan = float(line2[17:25])
            ecc_raw = line2[26:33].strip()
            eccentricity = float("0." + ecc_raw) if ecc_raw else 0.0
            arg_perigee = float(line2[34:42])
            mean_anomaly = float(line2[43:51])
            mean_motion = float(line2[52:63])

            if mean_motion <= 0:
                continue

            # Compute orbital characteristics
            period_minutes = 1440.0 / mean_motion
            period_seconds = 86400.0 / mean_motion
            n_rad_s = (mean_motion * 2.0 * math.pi) / 86400.0
            
            # Semi-major axis: a = (mu / n^2)^(1/3)
            semi_major_axis_km = math.pow(MU / (n_rad_s * n_rad_s), 1.0 / 3.0)
            mean_altitude_km = semi_major_axis_km - EARTH_RADIUS_KM
            perigee_altitude_km = semi_major_axis_km * (1.0 - eccentricity) - EARTH_RADIUS_KM
            apogee_altitude_km = semi_major_axis_km * (1.0 + eccentricity) - EARTH_RADIUS_KM

            orbit_class = classify_orbit(mean_altitude_km, inclination)
            category = classify_category(name_line)

            yield {
                "norad_id": norad_id,
                "name": name_line,
                "intl_desig": intl_desig,
                "epoch": epoch,
                "inclination": round(inclination, 4),
                "raan": round(raan, 4),
                "eccentricity": round(eccentricity, 7),
                "arg_perigee": round(arg_perigee, 4),
                "mean_anomaly": round(mean_anomaly, 4),
                "mean_motion": round(mean_motion, 8),
                "semi_major_axis": round(semi_major_axis_km, 2),
                "altitude": round(mean_altitude_km, 2),
                "perigee_altitude": round(perigee_altitude_km, 2),
                "apogee_altitude": round(apogee_altitude_km, 2),
                "period": round(period_minutes, 2),
                "orbit_class": orbit_class,
                "category": category,
                "tle_line1": line1,
                "tle_line2": line2,
            }
        except Exception:
            continue
