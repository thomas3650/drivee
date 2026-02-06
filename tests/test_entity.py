"""Tests for DriveeBaseEntity."""

from __future__ import annotations

import pytest

from custom_components.drivee.entity import DriveeBaseEntity


class TestDriveeBaseEntity:
    """Test DriveeBaseEntity class."""

    def test_get_data(self, mock_coordinator, mock_coordinator_data):
        """Test _get_data returns coordinator data."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._get_data()

        # Assert
        assert result == mock_coordinator_data

    def test_get_charge_point(self, mock_coordinator, mock_charge_point):
        """Test _get_charge_point extracts charge point."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._get_charge_point()

        # Assert
        assert result == mock_charge_point

    def test_get_current_session_when_present(self, mock_coordinator):
        """Test _get_current_session returns session when present."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._get_current_session()

        # Assert
        assert result is not None
        assert result.session_id == "test-session-123"

    def test_get_current_session_when_missing(self, mock_coordinator):
        """Test _get_current_session returns None when no session."""
        # Arrange
        mock_coordinator.data.charge_point.evse.session = None

        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._get_current_session()

        # Assert
        assert result is None

    def test_get_history(self, mock_coordinator, mock_charging_history):
        """Test _get_history returns charging history."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._get_history()

        # Assert
        assert result == mock_charging_history

    def test_get_price_periods(self, mock_coordinator, mock_price_periods):
        """Test _get_price_periods returns price periods."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._get_price_periods()

        # Assert
        assert result == mock_price_periods

    def test_make_unique_id(self, mock_coordinator):
        """Test _make_unique_id builds correct format."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_entity"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity._make_unique_id("charging_status")

        # Assert
        assert result == "Drivee_charging_status"

    def test_init_sets_unique_id(self, mock_coordinator):
        """Test __init__ sets unique_id from translation key."""

        # Arrange & Act
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_sensor"

        entity = TestEntity(mock_coordinator)

        # Assert
        assert entity._attr_unique_id == "Drivee_test_sensor"

    def test_init_raises_without_translation_key(self, mock_coordinator):
        """Test __init__ raises ValueError if translation_key not set."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Translation key must be set"):
            DriveeBaseEntity(mock_coordinator)

    def test_device_info(self, mock_coordinator):
        """Test device_info returns correct structure."""

        # Arrange
        class TestEntity(DriveeBaseEntity):
            _attr_translation_key = "test_sensor"

        entity = TestEntity(mock_coordinator)

        # Act
        result = entity.device_info

        # Assert
        assert result["name"] == "Drivee Charger"
        assert ("drivee", "DRIVEE") in result["identifiers"]
