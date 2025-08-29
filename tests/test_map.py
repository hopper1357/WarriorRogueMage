import sys
import os
import pytest
import pygame

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tilemap import Map, HazardTile

@pytest.fixture
def temp_map_file(tmp_path):
    """Create a temporary map file for testing."""
    map_content = """\
#F#
.#.
F.F
"""
    map_file = tmp_path / "test_map.txt"
    map_file.write_text(map_content)
    return str(map_file) # Return the path as a string

def test_map_loading_and_tile_counts(temp_map_file):
    """Tests that the map loads correctly and counts walls and hazards."""
    game_map = Map(temp_map_file)

    # There are 3 '#' characters in the map
    assert len(game_map.walls) == 3
    # There are 3 'F' characters in the map
    assert len(game_map.hazards) == 3

def test_hazard_tile_properties(temp_map_file):
    """Tests that the properties of a loaded hazard tile are correct."""
    game_map = Map(temp_map_file)

    # Get one of the hazard tiles to inspect it
    # Note: The order is not guaranteed, so we find one at a known location.
    # The first 'F' is at col 1, row 0.
    hazard_tile = None
    for tile in game_map.hazards:
        if tile.rect.x == 1 * 32 and tile.rect.y == 0 * 32:
            hazard_tile = tile
            break

    assert hazard_tile is not None, "Hazard tile at (1, 0) not found"
    assert isinstance(hazard_tile, HazardTile)
    assert hazard_tile.damage == "1d6"
    assert hazard_tile.damage_type == "fire"
