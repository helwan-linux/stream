import subprocess
import shutil
import os

class PlayerManager:
    def __init__(self):
        self.supported_players = ['mpv', 'vlc', 'parole', 'mplayer']

    def find_available_player(self):
        for player in self.supported_players:
            if shutil.which(player):
                return player
        return None

    def play(self, stream_url, title="Helwan Stream"):
        player = self.find_available_player()
        if not player:
            return False, "No player found"

        # تحويل أي مسار فيه ~ لمسار حقيقي عشان الدونلود يشتغل
        real_url = os.path.expanduser(stream_url)

        try:
            # ده السطر اللي شغل لك الفيديو في الترمينال
            if player == 'mpv':
                cmd = [player, real_url, "--vo=gpu", "--gpu-api=opengl", "--hwdec=auto"]
            else:
                cmd = [player, real_url]
            
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Success"
        except Exception as e:
            return False, str(e)
