import logging
import vlc


logger = logging.getLogger("isar.scene.audioutil")


audio_players_dict = {}


class AudioPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.playing = False
        self.player = vlc.MediaPlayer(self.filename)

    def play(self):
        if not self.playing:
            self.playing = True
            self.player.play()

    def stop(self):
        if self.playing:
            self.player.stop()
            self.playing = False

    def toggle_play_stop(self):
        if self.playing:
            self.stop()
        else:
            self.play()


def play(audio_file):
    pass


def stop(audio_file):
    pass


