"""Diagnostics support for Drivee."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Get coordinator data safely
    charge_point_data = {}
    if coordinator.data and coordinator.data.charge_point:
        cp = coordinator.data.charge_point
        charge_point_data = {
            "id": cp.id,
            "name": cp.name,
            "evse": {
                "is_charging": cp.evse.is_charging,
                "is_charging_session_active": cp.evse.is_charging_session_active,
                "session_id": getattr(cp.evse.session, "id", None),
            },
        }

    # Session tracking
    session_tracking = {
        "last_session_id": coordinator._last_session_id,
        "current_session_id": getattr(
            coordinator.data.charge_point.evse.session if coordinator.data else None,
            "id",
            None,
        ),
    }

    # Cache statistics (using cachetools)
    cache_stats = {
        "history_cache_size": len(coordinator._history_cache),
        "history_cache_maxsize": coordinator._history_cache.maxsize,
        "history_cache_ttl": coordinator._history_cache.ttl,
        "has_cached_history": "data" in coordinator._history_cache,
        "price_cache_size": len(coordinator._price_cache),
        "price_cache_maxsize": coordinator._price_cache.maxsize,
        "price_cache_ttl": coordinator._price_cache.ttl,
        "has_cached_prices": "data" in coordinator._price_cache,
    }

    # Update interval info
    update_info = {
        "current_update_interval_seconds": coordinator.update_interval.total_seconds(),
        "last_update_success": (
            coordinator.last_update_success_time.isoformat()
            if coordinator.last_update_success_time
            else None
        ),
        "last_update_status": (
            "success" if coordinator.last_update_success else "failed"
        ),
    }

    return {
        "entry": {
            "title": entry.title,
            "unique_id": entry.unique_id,
        },
        "charge_point": charge_point_data,
        "session_tracking": session_tracking,
        "cache_statistics": cache_stats,
        "update_information": update_info,
        "coordinator_state": {
            "available": coordinator.last_update_success,
        },
    }
