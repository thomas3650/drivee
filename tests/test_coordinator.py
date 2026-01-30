# """Test the Drivee coordinator."""

# from __future__ import annotations

# from datetime import timedelta
# from unittest.mock import AsyncMock, MagicMock, patch

# import pytest
# from custom_components.drivee.const import (
#     UPDATE_INTERVAL_CHARGING_SECONDS,
# )
# from drivee_client.errors import AuthenticationError, DriveeError


# @pytest.mark.asyncio
# async def test_coordinator_update_success(
#     mock_charge_point,
#     mock_charging_history,
#     mock_price_periods,
# ) -> None:
#     """Test successful data update."""
#     with patch(
#         "custom_components.drivee.coordinator.DriveeClient"
#     ) as mock_client_class:
#         from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator

#         mock_client = MagicMock()
#         mock_client.get_charge_point = AsyncMock(return_value=mock_charge_point)
#         mock_client.get_charging_history = AsyncMock(return_value=mock_charging_history)
#         mock_client.get_price_periods = AsyncMock(return_value=mock_price_periods)
#         mock_client_class.return_value = mock_client

#         # Create mock hass
#         mock_hass = MagicMock()
#         mock_config_entry = MagicMock()

#         coordinator = DriveeDataUpdateCoordinator(
#             hass=mock_hass,
#             logger=MagicMock(),
#             name="Test",
#             update_interval=timedelta(minutes=10),
#             client=mock_client,
#             config_entry=mock_config_entry,
#         )

#         data = await coordinator._update_data()

#         assert data.charge_point == mock_charge_point
#         assert data.charging_history == mock_charging_history
#         assert data.price_periods == mock_price_periods
#         assert coordinator.last_update_success_time is not None


# @pytest.mark.asyncio
# async def test_coordinator_authentication_error() -> None:
#     """Test authentication error handling."""
#     with patch(
#         "custom_components.drivee.coordinator.DriveeClient"
#     ) as mock_client_class:
#         from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator
#         from homeassistant.exceptions import ConfigEntryAuthFailed

#         mock_client = MagicMock()
#         mock_client.get_charge_point = AsyncMock(
#             side_effect=AuthenticationError("Auth failed")
#         )
#         mock_client_class.return_value = mock_client

#         mock_hass = MagicMock()
#         mock_config_entry = MagicMock()

#         coordinator = DriveeDataUpdateCoordinator(
#             hass=mock_hass,
#             logger=MagicMock(),
#             name="Test",
#             update_interval=timedelta(minutes=10),
#             client=mock_client,
#             config_entry=mock_config_entry,
#         )

#         with pytest.raises(ConfigEntryAuthFailed):
#             await coordinator._update_data()


# @pytest.mark.asyncio
# async def test_coordinator_drivee_error() -> None:
#     """Test Drivee API error handling."""
#     with patch(
#         "custom_components.drivee.coordinator.DriveeClient"
#     ) as mock_client_class:
#         from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator
#         from homeassistant.helpers.update_coordinator import UpdateFailed

#         mock_client = MagicMock()
#         mock_client.get_charge_point = AsyncMock(side_effect=DriveeError("API error"))
#         mock_client_class.return_value = mock_client

#         mock_hass = MagicMock()
#         mock_config_entry = MagicMock()

#         coordinator = DriveeDataUpdateCoordinator(
#             hass=mock_hass,
#             logger=MagicMock(),
#             name="Test",
#             update_interval=timedelta(minutes=10),
#             client=mock_client,
#             config_entry=mock_config_entry,
#         )

#         with pytest.raises(UpdateFailed):
#             await coordinator._update_data()


# @pytest.mark.asyncio
# async def test_coordinator_interval_adjustment_charging(
#     mock_charge_point,
#     mock_charging_history,
#     mock_price_periods,
# ) -> None:
#     """Test update interval adjusts when charging starts."""
#     with patch(
#         "custom_components.drivee.coordinator.DriveeClient"
#     ) as mock_client_class:
#         from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator

#         # Set charging state
#         mock_charge_point.evse.is_charging = True

#         mock_client = MagicMock()
#         mock_client.get_charge_point = AsyncMock(return_value=mock_charge_point)
#         mock_client.get_charging_history = AsyncMock(return_value=mock_charging_history)
#         mock_client.get_price_periods = AsyncMock(return_value=mock_price_periods)
#         mock_client_class.return_value = mock_client

#         mock_hass = MagicMock()
#         mock_config_entry = MagicMock()

#         coordinator = DriveeDataUpdateCoordinator(
#             hass=mock_hass,
#             logger=MagicMock(),
#             name="Test",
#             update_interval=timedelta(minutes=10),
#             client=mock_client,
#             config_entry=mock_config_entry,
#         )

#         await coordinator._update_data()

#         assert coordinator.update_interval == timedelta(
#             seconds=UPDATE_INTERVAL_CHARGING_SECONDS
#         )


# @pytest.mark.asyncio
# async def test_coordinator_cache_behavior(
#     mock_charge_point,
#     mock_charging_history,
#     mock_price_periods,
# ) -> None:
#     """Test caching behavior for history and price periods."""
#     with patch(
#         "custom_components.drivee.coordinator.DriveeClient"
#     ) as mock_client_class:
#         from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator

#         mock_client = MagicMock()
#         mock_client.get_charge_point = AsyncMock(return_value=mock_charge_point)
#         mock_client.get_charging_history = AsyncMock(return_value=mock_charging_history)
#         mock_client.get_price_periods = AsyncMock(return_value=mock_price_periods)
#         mock_client_class.return_value = mock_client

#         mock_hass = MagicMock()
#         mock_config_entry = MagicMock()

#         coordinator = DriveeDataUpdateCoordinator(
#             hass=mock_hass,
#             logger=MagicMock(),
#             name="Test",
#             update_interval=timedelta(minutes=10),
#             client=mock_client,
#             config_entry=mock_config_entry,
#         )

#         # First update - should fetch from API
#         await coordinator._update_data()
#         assert mock_client.get_charging_history.call_count == 1
#         assert mock_client.get_price_periods.call_count == 1

#         # Second update immediately - should use cache
#         await coordinator._update_data()
#         assert mock_client.get_charging_history.call_count == 1  # Still 1
#         assert mock_client.get_price_periods.call_count == 1  # Still 1
