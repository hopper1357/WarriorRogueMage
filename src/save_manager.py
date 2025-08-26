import pickle
import os

def save_game(player, filename="savegame.dat"):
    """Saves the player object to a file."""
    try:
        with open(filename, "wb") as f:
            pickle.dump(player, f)
        print(f"Game saved to {filename}")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game(filename="savegame.dat"):
    """Loads the player object from a file."""
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, "rb") as f:
            player = pickle.load(f)
        print(f"Game loaded from {filename}")
        return player
    except Exception as e:
        print(f"Error loading game: {e}")
        return None

def save_file_exists(filename="savegame.dat"):
    """Checks if a save file exists."""
    return os.path.exists(filename)
