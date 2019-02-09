import os
import random
import traceback

import pygame
from pygame import mixer

class music_controller(object):
    music_directory = '/home/magico13/Music'
    playlist = []
    regular_playlist = []
    shuffled_playlist = []
    shuffled = False
    playing = False
    current_index = 0
    volume = 0.1

    SONG_FINISHED = pygame.USEREVENT+1

    def __init__(self):
        mixer.init()
        mixer.music.set_endevent(self.SONG_FINISHED)
        if self.load_playlist_file() > 0:
            self.load_current_index_file()


    def update(self):
        '''Called when a song finishes playback.'''
        if (self.playing):
            self.skip_forward()

    def set_current_index(self, index, load = True):
        '''Sets the current index being played and loads the appropraite song if requested.
        Intended for internal use only.'''
        if len(self.playlist) > 0:
            index %= len(self.playlist)
        else:
            index = -1
        self.current_index = index
        if load and index >= 0:
            mixer.music.stop()
            mixer.music.load(self.playlist[index])
            mixer.music.set_volume(self.volume) # volume is lost after a load
        with open('data/music_index.txt', 'w') as f: f.write('{}\n'.format(index))
        return index

    def play(self, index=None):
        '''Plays the song at the index or unpauses the music.'''
        if len(self.playlist) == 0: self.load_playlist()
        if not index: index = self.current_index
        if (not self.playing and mixer.music.get_busy() and index == self.current_index): #paused
            mixer.music.unpause()
        else: #stopped or different song
            index = self.set_current_index(index)
            if index < 0: return False
            mixer.music.play()
        self.playing = True
        return True

    def stop(self):
        '''Stops music playback.'''
        mixer.music.stop()
        self.playing = False
    
    def pause(self):
        '''Pauses music playback.'''
        mixer.music.pause()
        self.playing = False

    def skip_forward(self):
        '''Skips to the next song in the playlist.'''
        self.play(self.current_index + 1)
    
    def skip_backward(self):
        '''Rewinds the song if it has played more than 5 seconds, otherwise skips to the previous song.'''
        if (self.playing and mixer.music.get_pos() > 5000):
            mixer.music.play()
        else:
            self.play(self.current_index - 1)
    
    def volume_up(self, amount=0.05):
        '''Turns up the volume by the specified amount (default 5%)'''
        self.volume += amount
        self.volume = min(self.volume, 1.0)
        mixer.music.set_volume(self.volume)

    def volume_down(self, amount=0.05):
        '''Turns down the volume by the specified amount (default 5%)'''
        self.volume -= amount
        self.volume = max(self.volume, 0)
        mixer.music.set_volume(self.volume)

    def shuffle_task(self):
        '''Shuffles or unshuffles the playlist depending on the current state.'''
        if (len(self.playlist) > 0):
            playing_name = self.playlist[self.current_index]
            if self.shuffled: #shuffle the playlist
                self.regular_playlist = self.playlist
                random.shuffle(self.playlist)
            else:
                self.playlist = self.regular_playlist
            index = self.get_song_index_by_name(playing_name)
            self.set_current_index(index, False)

    def load_playlist(self, directory=None):
        '''Loads the music contained in "directory" and any subfolders.'''
        if not directory: directory = self.music_directory

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
        #save the playlist to a file
        with open('data/playlist.txt', 'w') as f:
            f.write('\n'.join(self.regular_playlist))
            if (self.shuffled):
                f.write('shuffled\n')
                f.writelines('\n'.join(self.shuffled_playlist))

    def load_playlist_file(self, path='data/playlist.txt'):
        '''Loads the playlist from the provided file'''
        self.regular_playlist = []
        self.playlist = []
        self.shuffled_playlist = []
        loadingShuffled = False
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line == "shuffled":
                        loadingShuffled = True
                        continue
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

    def load_current_index_file(self, path='data/music_index.txt'):
        '''Loads the current index in the playlist from a file'''
        self.current_index = 0
        try:
            with open(path, 'r') as f:
                current = int(f.readline().strip())
            self.set_current_index(current)
        except:
            traceback.print_exc()
        return self.current_index


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
        pretty = os.path.basename(self.playlist[index][:-4])
        if '- ' in pretty:
            pretty = pretty.rsplit('- ', 1)[1].strip() #turn "02 - filename" into "filename"
        if len(pretty) > max_characters: pretty = pretty[:max_characters]+'...'
        return pretty
