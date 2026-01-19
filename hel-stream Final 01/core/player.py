import subprocess
import shutil

class PlayerManager:
    def __init__(self):
        # Priority list of players
        self.supported_players = ['mpv', 'vlc', 'parole', 'mplayer']

    def find_available_player(self):
        """
        Check the system for any installed media player from the list.
        """
        for player in self.supported_players:
            if shutil.which(player):
                return player
        return None

    def play(self, stream_url, title="Helwan Stream"):
        """
        Launch the stream in the first available player found.
        """
        player = self.find_available_player()
        
        if not player:
            return False, "No supported media player found on your system."

        try:
            # Different arguments for different players if needed
            cmd = [player, stream_url]
            
            # Example: adding title for MPV
            if player == 'mpv':
                cmd.append(f"--force-media-title={title}")
            
            # Run the player as a detached process
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Playing with {player}"
            
        except Exception as e:
            return False, str(e)
