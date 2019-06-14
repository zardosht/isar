import logging
import os

# import vlc

from isar.scene import sceneutil, scenemodel

logger = logging.getLogger("isar.scene.audioutil")


audio_players_dict = {}


class AudioPlayer:
    def __init__(self, filename):

        current_project = scenemodel.current_project
        if current_project is None:
            logger.warning("Current Project is None!")

        self.filename = filename
        self.playing = False

        file_path = str(os.path.join(current_project.base_path, self.filename))
        # self.vlc_instance = vlc.Instance()

        self.mediaList = self.vlc_instance.media_list_new()
        media = self.vlc_instance.media_new(file_path)
        self.mediaList.add_media(media)

        self.player = self.vlc_instance.media_list_player_new()
        self.player.set_media_list(self.mediaList)

    def play(self):
        self.player.play()

    def stop(self):
        self.player.stop()

    # def set_loop(self, loop):
    #     if loop:
    #         # self.player.set_playback_mode(vlc.PlaybackMode.repeat)
    #         self.player.set_playback_mode(vlc.PlaybackMode.loop)
    #     else:
    #         self.player.set_playback_mode(vlc.PlaybackMode.default)


def play(audio_file, loop=False):
    if audio_file in audio_players_dict:
        audio_player = audio_players_dict[audio_file]
        audio_player.set_loop(loop)
        audio_player.play()
    else:
        audio_player = AudioPlayer(audio_file)
        audio_player.set_loop(loop)
        audio_players_dict[audio_file] = audio_player
        audio_player.play()


def stop(audio_file):
    if audio_file in audio_players_dict:
        audio_players_dict[audio_file].stop()
    else:
        audio_player = AudioPlayer(audio_file)
        audio_players_dict[audio_file] = audio_player
        audio_player.stop()


