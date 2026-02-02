"""Tests for Drivee button entities."""

from __future__ import annotations

import pytest
from homeassistant.helpers.entity import EntityCategory

from custom_components.drivee.button import DriveeForceRefreshButton


class TestDriveeForceRefreshButton:
    """Test DriveeForceRefreshButton class."""

    async def test_force_refresh_button_press(self, mock_coordinator):
        """Test pressing button triggers coordinator refresh."""
        # Arrange
        button = DriveeForceRefreshButton(mock_coordinator)

        # Act
        await button.async_press()

        # Assert
        mock_coordinator.async_request_refresh.assert_called_once()

    def test_button_properties(self, mock_coordinator):
        """Test button has correct properties."""
        # Arrange & Act
        button = DriveeForceRefreshButton(mock_coordinator)

        # Assert
        assert button._attr_translation_key == "force_refresh"
        assert button._attr_icon == "mdi:refresh"
        assert button._attr_entity_category == EntityCategory.DIAGNOSTIC
        assert button._attr_has_entity_name is True

    def test_button_unique_id(self, mock_coordinator):
        """Test button generates correct unique ID."""
        # Arrange & Act
        button = DriveeForceRefreshButton(mock_coordinator)

        # Assert
        # Unique ID is generated from translation_key by base class
        assert button.unique_id == "force_refresh"
