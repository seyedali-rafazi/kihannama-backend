import math
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone

EPOCH_DEFAULT = "2026-09-19T00:00:00Z"
END_DEFAULT = "2026-09-20T00:00:00Z"
CLOCK_DURATION_SEC = 86400  # 24 hours

# Categorical color schemes [R, G, B, A]
PALETTES = {
    "LEO": [0, 229, 255, 210],         # Bright Cyan
    "MEO": [255, 179, 0, 210],         # Amber
    "GEO": [186, 104, 200, 210],       # Purple / Magenta
    "HEO": [255, 82, 82, 210],         # Coral / Red
    "Space Station": [0, 230, 118, 240], # Neon Emerald
    "Starlink": [64, 196, 255, 180],    # Sky Blue
    "Navigation": [255, 215, 64, 220],  # Gold
}

def get_satellite_color(sat: Any) -> List[int]:
    cat = getattr(sat, "category", "") or (sat.get("category") if isinstance(sat, dict) else "")
    orbit = getattr(sat, "orbit_class", "") or (sat.get("orbit_class") if isinstance(sat, dict) else "")
    
    if cat in PALETTES:
        return PALETTES[cat]
    if orbit in PALETTES:
        return PALETTES[orbit]
    return [0, 229, 255, 210]

def compute_position(
    altitude_m: float,
    inclination_deg: float,
    raan_deg: float,
    mean_anomaly_deg: float,
    period_sec: float,
    t: float
) -> Tuple[float, float, float]:
    r = 6378137.0 + altitude_m
    inc = math.radians(inclination_deg)
    raan = math.radians(raan_deg)
    phase = math.radians(mean_anomaly_deg)
    nu = ((2.0 * math.pi) / period_sec) * t + phase

    x_orb = r * math.cos(nu)
    y_orb = r * math.sin(nu)

    x = x_orb * math.cos(raan) - y_orb * math.cos(inc) * math.sin(raan)
    y = x_orb * math.sin(raan) + y_orb * math.cos(inc) * math.cos(raan)
    z = y_orb * math.sin(inc)

    lon = math.degrees(math.atan2(y, x))
    lat = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))

    return round(lon, 4), round(lat, 4), round(altitude_m, 1)

def generate_position_samples(
    altitude_m: float,
    inclination_deg: float,
    raan_deg: float,
    mean_anomaly_deg: float,
    period_sec: float
) -> List[float]:
    samples_per_orbit = 120 if altitude_m >= 2_000_000 else 60
    step = max(30.0, period_sec / samples_per_orbit)
    samples: List[float] = []

    t = 0.0
    while t <= CLOCK_DURATION_SEC:
        lon, lat, alt = compute_position(
            altitude_m, inclination_deg, raan_deg, mean_anomaly_deg, period_sec, t % period_sec
        )
        samples.extend([round(t, 1), lon, lat, alt])
        t += step

    return samples

def generate_full_orbit_polyline(
    altitude_m: float,
    inclination_deg: float,
    raan_deg: float,
    mean_anomaly_deg: float,
    period_sec: float,
    samples_count: int = 180
) -> List[float]:
    positions: List[float] = []
    for i in range(samples_count + 1):
        t = (period_sec / samples_count) * i
        lon, lat, alt = compute_position(
            altitude_m, inclination_deg, raan_deg, mean_anomaly_deg, period_sec, t
        )
        positions.extend([lon, lat, alt])
    return positions

def create_czml_document(
    name: str = "KihanNama Satellites CZML",
    epoch: str = EPOCH_DEFAULT,
    end: str = END_DEFAULT,
    multiplier: float = 60.0
) -> Dict[str, Any]:
    return {
        "id": "document",
        "name": name,
        "version": "1.0",
        "clock": {
            "interval": f"{epoch}/{end}",
            "currentTime": epoch,
            "multiplier": multiplier,
            "range": "LOOP",
            "step": "SYSTEM_CLOCK_MULTIPLIER",
        },
    }

def satellite_to_czml_packets(
    sat: Any,
    epoch: str = EPOCH_DEFAULT,
    end: str = END_DEFAULT,
    show_orbit: bool = True,
    show_label: bool = True,
    path_width: float = 1.5
) -> List[Dict[str, Any]]:
    # Extract properties whether ORM model or dict
    if isinstance(sat, dict):
        norad_id = str(sat["norad_id"])
        name = str(sat["name"])
        altitude_km = float(sat["altitude"])
        inclination = float(sat["inclination"])
        raan = float(sat["raan"])
        mean_anomaly = float(sat["mean_anomaly"])
        period_min = float(sat["period"])
    else:
        norad_id = str(sat.norad_id)
        name = str(sat.name)
        altitude_km = float(sat.altitude)
        inclination = float(sat.inclination)
        raan = float(sat.raan)
        mean_anomaly = float(sat.mean_anomaly)
        period_min = float(sat.period)

    altitude_m = altitude_km * 1000.0
    period_sec = max(60.0, period_min * 60.0)
    color_rgba = get_satellite_color(sat)

    orbit_packet = {
        "id": f"{norad_id}-orbit",
        "name": f"{name} Orbit",
        "availability": f"{epoch}/{end}",
        "polyline": {
            "show": show_orbit,
            "positions": {
                "cartographicDegrees": generate_full_orbit_polyline(
                    altitude_m, inclination, raan, mean_anomaly, period_sec
                )
            },
            "width": path_width,
            "arcType": "NONE",
            "disableDepthTestDistance": 0,
            "material": {
                "solidColor": {
                    "color": {"rgba": color_rgba}
                }
            },
        },
    }

    sat_packet = {
        "id": norad_id,
        "name": name,
        "availability": f"{epoch}/{end}",
        "position": {
            "epoch": epoch,
            "interpolationAlgorithm": "LAGRANGE",
            "interpolationDegree": 5,
            "referenceFrame": "FIXED",
            "cartographicDegrees": generate_position_samples(
                altitude_m, inclination, raan, mean_anomaly, period_sec
            ),
        },
        "billboard": {
            "show": True,
            "width": 24,
            "height": 24,
            "scale": 1,
            "verticalOrigin": "CENTER",
            "horizontalOrigin": "CENTER",
            "disableDepthTestDistance": 0,
        },
        "label": {
            "show": show_label,
            "text": name,
            "font": "11pt Inter, Vazirmatn, sans-serif",
            "fillColor": {"rgba": [241, 245, 249, 255]},
            "outlineColor": {"rgba": [0, 0, 0, 255]},
            "outlineWidth": 2,
            "style": "FILL_AND_OUTLINE",
            "verticalOrigin": "TOP",
            "pixelOffset": {"cartesian2": [0, 24]},
            "scale": 0.85,
            "disableDepthTestDistance": 0,
        },
    }

    return [orbit_packet, sat_packet]

def generate_czml_dataset(
    satellites: List[Any],
    name: str = "KihanNama Satellites CZML",
    epoch: str = EPOCH_DEFAULT,
    end: str = END_DEFAULT,
    multiplier: float = 60.0,
    show_orbit: bool = True,
    show_label: bool = True
) -> List[Dict[str, Any]]:
    packets = [create_czml_document(name=name, epoch=epoch, end=end, multiplier=multiplier)]
    for sat in satellites:
        packets.extend(satellite_to_czml_packets(
            sat, epoch=epoch, end=end, show_orbit=show_orbit, show_label=show_label
        ))
    return packets
