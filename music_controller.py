import os
import random
import traceback
from datetime import datetime

import vlc

class music_controller(object):
    music_directory = '~/Music'
    playlist = []
    regular_playlist = []
    shuffled_playlist = []
    shuffled = False
    playing = False
    current_index = 0
    volume = 10

    instance = None
    player = None

    current_file = 'data/music_current.txt'
    playlist_file = 'data/music_playlist.txt'
    volume_file = 'data/volume.txt'

    last_update = None

    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        if self.load_playlist_file() > 0:
            self.load_current_music_file()
        self.load_volume_file()
        self.last_update = datetime.utcnow()

    def update(self):
        '''Called when a song finishes playback.'''
        if (self.playing and not self.player.is_playing()):
            if (datetime.utcnow() - self.last_update).total_seconds() > 1:
                self.skip_forward()
                return True
        return False

    def set_current_index(self, index, load = True):
        '''Sets the current index being played and loads the appropraite song if requested.
        Intended for internal use only.'''
        if len(self.playlist) > 0:
            index %= len(self.playlist)
        else:
            index = -1
        self.current_index = index
        if load and index >= 0:
            media = self.instance.media_new(self.playlist[index])
            self.player.set_media(media)
            self.player.audio_set_volume(self.volume)
        if index >= 0: 
            with open(self.current_file, 'w') as f: 
                f.write('{}\n'.format(self.playlist[index]))
        return index

    def play(self, index=None):
        '''Plays the song at the index or unpauses the music.'''
        if len(self.playlist) == 0: self.load_library()
        if index == None: index = self.current_index
        if (not self.playing and index == self.current_index and self.player.get_state() == vlc.State.Paused): #paused
            self.player.set_pause(0)
        else: #stopped or different song
            index = self.set_current_index(index)
            if index < 0: return False
            self.player.play()
        self.playing = True
        self.last_update = datetime.utcnow()
        return True

    def stop(self):
        '''Stops music playback.'''
        self.player.stop()
        self.playing = False
    
    def pause(self):
        '''Pauses music playback.'''
        self.player.pause()
        self.playing = False

    def skip_forward(self):
        '''Skips to the next song in the playlist.'''
        self.play(self.current_index + 1)
    
    def skip_backward(self):
        '''Rewinds the song if it has played more than 5 seconds, otherwise skips to the previous song.'''
        if (self.playing and self.player.get_time() > 5000):
             self.player.set_time(0)
        else:
            self.play(self.current_index - 1)
    
    def volume_up(self, amount=5):
        '''Turns up the volume by the specified amount (default 5%)'''
        self.volume += amount
        self.volume = min(self.volume, 100)
        if self.player: self.player.audio_set_volume(self.volume)
        with open(self.volume_file, 'w') as f: f.write(str(self.volume))

    def volume_down(self, amount=5):
        '''Turns down the volume by the specified amount (default 5%)'''
        self.volume -= amount
        self.volume = max(self.volume, 0)
        if self.player: self.player.audio_set_volume(self.volume)
        with open(self.volume_file, 'w') as f: f.write(str(self.volume))

    def toggle_shuffle(self):
        self.shuffled = not self.shuffled
        self.shuffle_task()

    def shuffle_task(self):
        '''Shuffles or unshuffles the playlist depending on the current state.'''
        if (len(self.playlist) > 0):
            playing_name = self.playlist[self.current_index]
            if self.shuffled: #shuffle the playlist
                self.regular_playlist = list(self.playlist)
                random.shuffle(self.playlist)
                self.shuffled_playlist = list(self.playlist)
            else:
                self.playlist = list(self.regular_playlist)
            index = self.get_song_index_by_name(playing_name)
            self.set_current_index(index, False)
            self.save_playlist()

    def load_library(self, directory=None):
        '''Loads the music contained in "directory" and any subfolders.'''
        if not directory: directory = self.music_directory
        self.music_directory = directory

        print('Loading music from '+directory)
        self.playlist = []
        for rootName, dirNames, fileNames in os.walk(directory):
            print('Checking ' +  rootName)
            dirNames.sort()
            fileNames.sort()
            found = 0
            for f in fileNames:
                if f.endswith('.mp3'):
                    self.playlist.append(os.path.join(rootName, f))
                    found += 1
            print('Found {0} mp3 files.'.format(found))
        print('Found a total of {0} mp3 files.'.format(len(self.playlist)))
        if (len(self.playlist) > 0):
            #self.set_current_index(max(0, self.current_index))
            self.regular_playlist = self.playlist
            if (self.shuffled): self.shuffle_task()
        self.save_playlist()
        self.stop()
        self.play(0)

    def save_playlist(self):
        '''Save the playlist to a file'''
        with open(self.playlist_file, 'w') as f:
            f.write('\n'.join(self.regular_playlist))
            if (self.shuffled):
                f.write('\nshuffled\n')
                f.write('\n'.join(self.shuffled_playlist))

    def load_playlist_file(self, path=None):
        '''Loads the playlist from the provided file'''
        self.regular_playlist = []
        self.playlist = []
        self.shuffled_playlist = []
        loadingShuffled = False
        if not path: path = self.playlist_file
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line == "shuffled":
                        loadingShuffled = True
                        self.shuffled = True
                        continue
                    #verify that the file is accessible
                    if not os.path.exists(line): continue
                    if not loadingShuffled:
                        self.regular_playlist.append(line)
                    else:
                        self.shuffled_playlist.append(line)
            if self.shuffled:
               self.playlist = list(self.shuffled_playlist)
            else:
                self.playlist = list(self.regular_playlist)
            print('Loaded playlist of {} items'.format(len(self.playlist)))
        except:
            traceback.print_exc()
        return len(self.playlist)

    def load_current_music_file(self, path=None):
        '''Loads the current index in the playlist from a file'''
        self.current_index = 0
        if not path: path = self.current_file
        try:
            with open(path, 'r') as f:
                current = f.readline().strip()
            current = self.get_song_index_by_name(current)
            self.set_current_index(current)
        except:
            traceback.print_exc()
        return self.current_index

    def load_volume_file(self, path=None):
        self.volume = 10
        if not path: path = self.volume_file
        try:
            with open(path, 'r') as f:
                self.volume = int(f.readline().strip())
        except:
            traceback.print_exc()

    def get_song_index_by_name(self, name):
        '''Finds the index for a particular song'''
        if len(self.playlist) > 0:
            for i in range(len(self.playlist)):
                if (self.playlist[i] == name):
                    return i
        return -1

    def get_pretty_name(self, index=None, max_characters=20):
        '''Returns a "pretty" name for an mp3, stripping off extra characters when possible.'''
        if not index: index = self.current_index
        if (index >= len(self.playlist) or index < 0): return 'N/A'
        pretty = None
        if index == self.current_index:
            #should have this loaded, can get the name from vlc
            media = self.player.get_media()
            if media:
                media.parse()
                pretty = media.get_meta(0)
        if not pretty: #either not the current song or couldn't parse it
            pretty = os.path.basename(self.playlist[index][:-4])
            if '- ' in pretty:
                pretty = pretty.rsplit('- ', 1)[1].strip() #turn "02 - filename" into "filename"
        if len(pretty) > max_characters: pretty = pretty[:max_characters]+'...'
        return pretty
