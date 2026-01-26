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

	def play(self, stream_url, title="Helwan Stream", format_string=None):
		player = self.find_available_player()
		if not player:
			return False, "No player found"

		real_url = os.path.expanduser(stream_url)

		try:
			if player == 'mpv':
				cmd = [
					player,
					"--vo=gpu",
					"--gpu-api=opengl",
					"--hwdec=auto"
				]

				if format_string:
					cmd.append(f"--ytdl-format={format_string}")

				cmd.append(real_url)
			else:
				cmd = [player, real_url]

			subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			return True, "Success"
		except Exception as e:
			return False, str(e)



