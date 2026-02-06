"""Tests for Drivee sensor entities."""

from __future__ import annotations

import datetime
from unittest.mock import Mock, patch

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import State
from homeassistant.util import dt as dt_util

from custom_components.drivee.coordinator import DriveeData
from custom_components.drivee.sensor import DriveeTotalEnergySensor


def create_mock_session(
    session_id: str,
    started_at: datetime.datetime,
    stopped_at: datetime.datetime | None,
    energy: float,
) -> Mock:
    """Create a mock ChargingSession."""
    session = Mock()
    session.session_id = session_id
    session.started_at = started_at
    session.stopped_at = stopped_at
    session.energy = energy
    return session


class TestDriveeTotalEnergySensor:
    """Test DriveeTotalEnergySensor class."""

    def test_sensor_properties(self, mock_coordinator):
        """Test sensor has correct properties."""
        # Arrange & Act
        sensor = DriveeTotalEnergySensor(mock_coordinator)

        # Assert
        assert sensor._attr_translation_key == "total_energy"
        assert sensor._attr_icon == "mdi:counter"
        assert sensor._attr_device_class == SensorDeviceClass.ENERGY
        assert sensor._attr_native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
        assert sensor._attr_state_class == SensorStateClass.TOTAL_INCREASING
        assert sensor._attr_suggested_display_precision == 1
        assert sensor._attr_has_entity_name is True

    def test_sensor_unique_id(self, mock_coordinator):
        """Test sensor generates correct unique ID."""
        # Arrange & Act
        sensor = DriveeTotalEnergySensor(mock_coordinator)

        # Assert
        assert sensor.unique_id == "Drivee_total_energy"

    def test_initial_state(self, mock_coordinator):
        """Test sensor initial state is zero."""
        # Arrange & Act
        sensor = DriveeTotalEnergySensor(mock_coordinator)

        # Assert
        assert sensor._total_wh == 0.0
        assert sensor._last_finished_session_end is None

    async def test_first_initialization_marks_historical_sessions_without_adding_energy(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test Bug Fix #3: First initialization marks sessions as processed but doesn't add energy.

        This prevents huge energy spikes when the integration is first installed.
        Historical sessions should be marked as processed WITHOUT adding their energy.
        """
        # Arrange: Create historical sessions (before integration was installed)
        now = dt_util.now()
        historical_sessions = [
            create_mock_session(
                "session-1",
                now - datetime.timedelta(days=3),
                now - datetime.timedelta(days=3, hours=-1),
                50000.0,  # 50 kWh
            ),
            create_mock_session(
                "session-2",
                now - datetime.timedelta(days=2),
                now - datetime.timedelta(days=2, hours=-1),
                75000.0,  # 75 kWh
            ),
            create_mock_session(
                "session-3",
                now - datetime.timedelta(days=1),
                now - datetime.timedelta(days=1, hours=-1),
                100000.0,  # 100 kWh
            ),
        ]
        mock_charging_history.sessions = historical_sessions
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"

        # Mock async_get_last_state to return None (first initialization)
        with patch.object(sensor, "async_get_last_state", return_value=None):
            # Act: Initialize sensor
            await sensor.async_added_to_hass()

        # Assert: Total should still be 0 (historical energy NOT added)
        assert sensor._total_wh == 0.0

        # Assert: Last finished session should be marked (session-3 is the most recent)
        assert sensor._last_finished_session_end == historical_sessions[2].stopped_at

        # Assert: Native value should be 0.0 kWh
        assert sensor.native_value == 0.0

    async def test_active_session_does_not_reset_tracking_marker(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test Bug Fix #1: Active sessions don't reset the tracking marker to None.

        Previously, if an active session (stopped_at=None) was processed, it would
        reset _last_finished_session_end to None, causing all historical sessions
        to be re-added on the next update cycle.
        """
        # Arrange: Create finished sessions + one active session
        now = dt_util.now()
        sessions = [
            create_mock_session(
                "session-1",
                now - datetime.timedelta(hours=3),
                now - datetime.timedelta(hours=2),
                50000.0,  # 50 kWh - finished
            ),
            create_mock_session(
                "session-2",
                now - datetime.timedelta(hours=1),
                None,  # Active session (not finished)
                25000.0,  # 25 kWh - in progress
            ),
        ]
        mock_charging_history.sessions = sessions
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"

        # Mock async_get_last_state to return None (first initialization)
        with patch.object(sensor, "async_get_last_state", return_value=None):
            # Act: Initialize sensor
            await sensor.async_added_to_hass()

        # Assert: Tracking marker should point to session-1 (the only FINISHED session)
        assert sensor._last_finished_session_end == sessions[0].stopped_at

        # Assert: Tracking marker should NOT be None (bug would reset it to None)
        assert sensor._last_finished_session_end is not None

        # Simulate coordinator update (would trigger re-processing if marker was None)
        sensor._process_update()

        # Assert: Total should still be 0 (no double-counting)
        assert sensor._total_wh == 0.0

    async def test_state_restoration_preserves_total_on_parse_failure(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test Bug Fix #2: State restoration failure preserves accumulated energy.

        Previously, if datetime parsing failed, both _total_wh and _last_finished_session_end
        were reset to 0/None, losing all accumulated energy data.
        Now only the tracking marker is reset, preserving the total.
        """
        # Arrange
        mock_charging_history.sessions = []
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"

        # Create a mock state with invalid datetime format
        mock_state = Mock(spec=State)
        mock_state.attributes = {
            "_total_wh": 123456.0,  # 123.456 kWh accumulated
            "last_finished_session_end": "invalid-datetime-format",  # Will fail to parse
        }

        # Mock async_get_last_state to return corrupted state
        with patch.object(sensor, "async_get_last_state", return_value=mock_state):
            # Act: Initialize sensor with corrupted state
            await sensor.async_added_to_hass()

        # Assert: Total should be preserved even though datetime parsing failed
        assert sensor._total_wh == 123456.0

        # Assert: Tracking marker should be reset (will be rebuilt on next update)
        assert sensor._last_finished_session_end is None

    async def test_successful_state_restoration(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test that state restoration works correctly with valid state."""
        # Arrange
        now = dt_util.now()
        last_session_end = now - datetime.timedelta(hours=2)
        mock_charging_history.sessions = []
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"

        # Create a mock state with valid data
        mock_state = Mock(spec=State)
        mock_state.attributes = {
            "_total_wh": 50000.0,  # 50 kWh
            "last_finished_session_end": last_session_end.isoformat(),
        }

        # Mock async_get_last_state to return valid state
        with patch.object(sensor, "async_get_last_state", return_value=mock_state):
            # Act: Initialize sensor
            await sensor.async_added_to_hass()

        # Assert: Total should be restored
        assert sensor._total_wh == 50000.0

        # Assert: Tracking marker should be restored
        # Compare timestamps (may have microsecond differences)
        assert sensor._last_finished_session_end is not None
        assert (
            abs((sensor._last_finished_session_end - last_session_end).total_seconds())
            < 1
        )

    async def test_add_new_finished_sessions(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test that new finished sessions are correctly added to the total."""
        # Arrange: Sensor already has some accumulated energy
        now = dt_util.now()
        last_processed_session_end = now - datetime.timedelta(hours=3)

        # Create sessions: one old (already processed) + one new
        sessions = [
            create_mock_session(
                "session-old",
                now - datetime.timedelta(hours=4),
                last_processed_session_end,
                50000.0,  # 50 kWh - already counted
            ),
            create_mock_session(
                "session-new",
                now - datetime.timedelta(hours=1),
                now - datetime.timedelta(minutes=30),
                25000.0,  # 25 kWh - should be added
            ),
        ]
        mock_charging_history.sessions = sessions
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"

        # Set up sensor with existing state
        sensor._total_wh = 50000.0  # Already counted session-old
        sensor._last_finished_session_end = last_processed_session_end

        # Mock async_get_last_state
        mock_state = Mock(spec=State)
        mock_state.attributes = {
            "_total_wh": 50000.0,
            "last_finished_session_end": last_processed_session_end.isoformat(),
        }

        with patch.object(sensor, "async_get_last_state", return_value=mock_state):
            # Act: Initialize and process update
            await sensor.async_added_to_hass()

        # Assert: Total should now include the new session
        assert sensor._total_wh == 75000.0  # 50 kWh + 25 kWh

        # Assert: Tracking marker should point to the new session
        assert sensor._last_finished_session_end == sessions[1].stopped_at

        # Assert: Native value should be in kWh
        assert sensor.native_value == 75.0

    async def test_native_value_includes_current_session(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test that native_value includes energy from the current active session."""
        # Arrange
        now = dt_util.now()

        # Create one finished session + one active session
        finished_session = create_mock_session(
            "session-finished",
            now - datetime.timedelta(hours=2),
            now - datetime.timedelta(hours=1),
            50000.0,  # 50 kWh
        )
        active_session = create_mock_session(
            "session-active",
            now - datetime.timedelta(minutes=30),
            None,  # Active
            15000.0,  # 15 kWh in progress
        )

        mock_charging_history.sessions = [finished_session]

        # Set up charge point with active session
        mock_coordinator.data.charge_point.evse.session = active_session
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"

        # Manually set the accumulated total (simulating finished sessions were not added on init)
        sensor._total_wh = 0.0
        sensor._last_finished_session_end = finished_session.stopped_at

        # Act
        native_value = sensor.native_value

        # Assert: Should include active session energy (0 + 15 kWh)
        assert native_value == 15.0

    async def test_native_value_without_current_session(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test native_value when there's no active session."""
        # Arrange
        mock_charging_history.sessions = []
        mock_coordinator.data.charge_point.evse.session = None
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor._total_wh = 50000.0

        # Act
        native_value = sensor.native_value

        # Assert: Should only return accumulated total
        assert native_value == 50.0

    def test_extra_state_attributes(self, mock_coordinator):
        """Test that extra_state_attributes includes tracking data."""
        # Arrange
        now = dt_util.now()
        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor._total_wh = 123456.0
        sensor._last_finished_session_end = now

        # Act
        attributes = sensor.extra_state_attributes

        # Assert
        assert "_total_wh" in attributes
        assert attributes["_total_wh"] == 123456.0
        assert "last_finished_session_end" in attributes
        assert attributes["last_finished_session_end"] == now.isoformat()

    def test_extra_state_attributes_with_none_marker(self, mock_coordinator):
        """Test extra_state_attributes when tracking marker is None."""
        # Arrange
        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor._total_wh = 0.0
        sensor._last_finished_session_end = None

        # Act
        attributes = sensor.extra_state_attributes

        # Assert
        assert attributes["_total_wh"] == 0.0
        assert attributes["last_finished_session_end"] is None

    async def test_multiple_new_sessions_added_in_order(
        self, hass: HomeAssistant, mock_coordinator, mock_charging_history
    ):
        """Test that multiple new sessions are processed in chronological order."""
        # Arrange
        now = dt_util.now()
        last_processed = now - datetime.timedelta(hours=5)

        sessions = [
            create_mock_session(
                "session-1",
                now - datetime.timedelta(hours=4),
                now - datetime.timedelta(hours=3, minutes=30),
                10000.0,  # 10 kWh
            ),
            create_mock_session(
                "session-2",
                now - datetime.timedelta(hours=3),
                now - datetime.timedelta(hours=2, minutes=30),
                20000.0,  # 20 kWh
            ),
            create_mock_session(
                "session-3",
                now - datetime.timedelta(hours=2),
                now - datetime.timedelta(hours=1, minutes=30),
                30000.0,  # 30 kWh
            ),
        ]

        mock_charging_history.sessions = sessions
        mock_coordinator.data = DriveeData(
            charge_point=mock_coordinator.data.charge_point,
            charging_history=mock_charging_history,
            price_periods=mock_coordinator.data.price_periods,
        )

        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"
        sensor._total_wh = 0.0
        sensor._last_finished_session_end = last_processed

        # Mock state
        mock_state = Mock(spec=State)
        mock_state.attributes = {
            "_total_wh": 0.0,
            "last_finished_session_end": last_processed.isoformat(),
        }

        with patch.object(sensor, "async_get_last_state", return_value=mock_state):
            # Act
            await sensor.async_added_to_hass()

        # Assert: All three sessions should be added
        assert sensor._total_wh == 60000.0  # 10 + 20 + 30 kWh

        # Assert: Tracking marker should point to the last session
        assert sensor._last_finished_session_end == sessions[2].stopped_at

    async def test_no_data_from_coordinator(
        self, hass: HomeAssistant, mock_coordinator
    ):
        """Test sensor handles None data from coordinator gracefully."""
        # Arrange
        mock_coordinator.data = None
        sensor = DriveeTotalEnergySensor(mock_coordinator)
        sensor.hass = hass
        sensor.entity_id = "sensor.drivee_total_energy"
        sensor._total_wh = 50000.0

        with patch.object(sensor, "async_get_last_state", return_value=None):
            await sensor.async_added_to_hass()

        # Act: Process update with None data
        sensor._process_update()

        # Assert: Total should remain unchanged
        assert sensor._total_wh == 50000.0

