"""IoT environmental sensor and river gauge telemetry ingestion service."""

import random
from typing import List, Dict, Any


class IoTSensorService:
    """Manages real-time readings from river gauges, soil moisture, and rainfall sensors."""

    @staticmethod
    def get_river_gauges(region_lat: float, region_lon: float) -> List[Dict[str, Any]]:
        """Returns hydrological station telemetry for active river monitoring."""
        return [
            {
                "station_id": "RIV-GAUGE-KLR-01",
                "river_name": "Periyar River - Upper Basin",
                "latitude": region_lat + 0.08,
                "longitude": region_lon - 0.04,
                "water_level_meters": 14.85,
                "danger_level_meters": 12.50,
                "discharge_m3_s": 1420.0,
                "rate_of_rise_m_h": 0.45,
                "is_overflowing": True
            },
            {
                "station_id": "RIV-GAUGE-KLR-02",
                "river_name": "Chalakudy River",
                "latitude": region_lat - 0.05,
                "longitude": region_lon + 0.06,
                "water_level_meters": 8.70,
                "danger_level_meters": 9.00,
                "discharge_m3_s": 890.0,
                "rate_of_rise_m_h": 0.28,
                "is_overflowing": False
            },
            {
                "station_id": "RIV-GAUGE-KLR-03",
                "river_name": "Muvattupuzha Tributary",
                "latitude": region_lat - 0.12,
                "longitude": region_lon - 0.02,
                "water_level_meters": 7.40,
                "danger_level_meters": 7.00,
                "discharge_m3_s": 620.0,
                "rate_of_rise_m_h": 0.35,
                "is_overflowing": True
            }
        ]

    @staticmethod
    def get_soil_moisture_sensors(region_lat: float, region_lon: float) -> List[Dict[str, Any]]:
        """Returns in-situ soil moisture capacitive probes."""
        return [
            {
                "sensor_id": "SOIL-SAT-01",
                "latitude": region_lat + 0.05,
                "longitude": region_lon - 0.02,
                "volumetric_water_content_pct": 94.2,  # >85% is critical saturation
                "saturation_status": "SUPER_SATURATED"
            },
            {
                "sensor_id": "SOIL-SAT-02",
                "latitude": region_lat - 0.08,
                "longitude": region_lon + 0.04,
                "volumetric_water_content_pct": 87.6,
                "saturation_status": "SATURATED"
            },
            {
                "sensor_id": "SOIL-SAT-03",
                "latitude": region_lat + 0.10,
                "longitude": region_lon + 0.05,
                "volumetric_water_content_pct": 72.1,
                "saturation_status": "MODERATE"
            }
        ]
