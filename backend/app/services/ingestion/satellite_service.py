"""Satellite observations and remote sensing data ingestion service."""

import math
from typing import Any, Dict, List


class SatelliteService:
    """Simulates/interfaces with Copernicus Sentinel-1/2 SAR, NASA FIRMS, and MODIS."""

    @staticmethod
    def get_thermal_anomalies(lat: float, lon: float) -> List[Dict[str, Any]]:
        """Active wildfire hotspots (MODIS / VIIRS 375m)."""
        return [
            {
                "satellite": "VIIRS-SNPP",
                "latitude": lat + 0.04,
                "longitude": lon + 0.03,
                "brightness_temp_k": 365.4,
                "fire_radiative_power_mw": 84.2,
                "confidence": "high",
                "acquisition_time": "Recent (t - 45m)"
            }
        ]

    @staticmethod
    def get_sar_surface_water_mask(lat: float, lon: float) -> Dict[str, Any]:
        """Synthetic Sentinel-1 C-band SAR backscatter inundation detection."""
        return {
            "satellite": "Sentinel-1A SAR",
            "polarization": "VV/VH",
            "backscatter_threshold_db": -16.5,
            "detected_water_expansion_pct": 312.4,  # Water area increased by 312% vs baseline
            "cloud_penetration_verified": True
        }

    @staticmethod
    def deduplicate_alerts(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove repeated alerts from multiple sources or duplicated sensor messages."""
        seen = set()
        unique_alerts: List[Dict[str, Any]] = []
        for alert in alerts:
            identity = (
                str(alert.get("type") or "unknown"),
                str(alert.get("source") or "unknown"),
                round(float(alert.get("latitude", 0.0)), 5),
                round(float(alert.get("longitude", 0.0)), 5),
                str(alert.get("title") or alert.get("message") or ""),
            )
            if identity in seen:
                continue
            seen.add(identity)
            unique_alerts.append(alert)
        return unique_alerts

    @staticmethod
    def haversine_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
        """Distance in kilometers between two coordinates."""
        lat_a_rad = math.radians(lat_a)
        lon_a_rad = math.radians(lon_a)
        lat_b_rad = math.radians(lat_b)
        lon_b_rad = math.radians(lon_b)
        delta_lat = lat_b_rad - lat_a_rad
        delta_lon = lon_b_rad - lon_a_rad
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat_a_rad) * math.cos(lat_b_rad) * math.sin(delta_lon / 2) ** 2
        )
        return 2 * 6371.0 * math.asin(math.sqrt(min(1.0, a)))
