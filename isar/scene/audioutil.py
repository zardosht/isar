import logging
import os

import vlc

from isar.scene import sceneutil, scenemodel

logger = logging.getLogger("isar.scene.audioutil")


audio_players_dict = {}


class AudioPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.playing = False
        current_project = scenemodel.current_project
        if current_project is None:
            logger.warning("Current Project is None!")

        file_path = str(os.path.join(current_project.base_path, self.filename))
        self.player = vlc.MediaPlayer(file_path)

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
    if audio_file in audio_players_dict:
        audio_players_dict[audio_file].play()
    else:
        audio_player = AudioPlayer(audio_file)
        audio_players_dict[audio_file] = audio_player
        audio_player.play()


def stop(audio_file):
    if audio_file in audio_players_dict:
        audio_players_dict[audio_file].stop()
    else:
        audio_player = AudioPlayer(audio_file)
        audio_players_dict[audio_file] = audio_player
        audio_player.stop()


