#!/usr/bin/python
import threading
import sys
import subprocess
import time
import ctypes

OUTPUT_FILE = "spotify.txt"
WATCH_INTERVAL = 1

class SpotifyWatcher(threading.Thread):
    def __init__(self):
        current_os = sys.platform
        self.valid_os = True
        self._stop = False
        
        if "darwin" in current_os:
            self.scraper = AppleSpotifyScraper()
        elif "win32" in current_os:
            self.scraper = WindowsSpotifyScraper()
        else:
            self.valid_os = False

    def watch(self):
        if not self.valid_os:
            return

        user_update = self.scraper.scrape()
        write_to_file(user_update)      

class AppleSpotifyScraper:
    def __init__(self):
        print("Apple Spotify scraper created")

    def scrape(self):
       script = """
           tell application "Spotify"
                set theTrack to current track
                set theArtist to artist of theTrack
                set theName to name of theTrack
                    if player state is playing then
                    set playStatus to "playing"
                else
                    set playStatus to "notPlaying"
                end if
            end tell
            set theValue to theName & "\n" & theArtist & "\n" & playStatus
            return theValue
       """.encode('UTF-8')
       osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
       result = osa.communicate(script)[0].decode("UTF-8").split("\n");
       return User(result[0], result[1], result[2]=="playing")

class WindowsSpotifyScraper:
    def __init__(self):
        print("Windows Spotify scraper created")
        self.spotify_pids = []
        self.__get_spotify_pids()

    def __get_spotify_pids(self):
        tasklist = subprocess.Popen("tasklist.exe /FI \"IMAGENAME eq spotify.exe\"", shell=True, stdout=subprocess.PIPE).communicate()[0].decode("UTF-8")
        tasks = tasklist.split("\r\n")[3:]
        for entry in tasks:
            split = entry.split()
            if len(split) > 1:
                self.spotify_pids.append(int(split[1]))

    def scrape(self):
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
        titles = []
        
        def foreach_window(hwnd, lParam):
            if not IsWindowVisible(hwnd):
                return True
            pidbuff = ctypes.POINTER(ctypes.c_ulong)(ctypes.c_ulong(1))
            GetWindowThreadProcessId(hwnd, pidbuff)
            pid = pidbuff.contents.value
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)

            if buff.value == "":
                return True
            if not pid in self.spotify_pids:
                return True 

            titles.append(buff.value)
            return True
        
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        result = titles[0]
        if result == "Spotify":
            return User("", "", False)
        else:
            spl = result.split("-")
            print(spl)
            return User(spl[0].strip(), spl[1].strip(), True)

class User:
    def __init__(self, song, artist, playing):
        self.song = song
        self.artist = artist
        self.playing = playing
    
    def get_song_info(self):
        return "{} - {}".format(self.song, self.artist)


def write_to_file(user):
    f = open(OUTPUT_FILE, 'w')
    f.truncate()
    f.write(user.get_song_info())
    f.close()

if __name__ == "__main__":
    watcher = SpotifyWatcher()
    
    if not watcher.valid_os:
        print("Invalid OS (You [probable] linux user, you)!  Cannot function :(");
        sys.exit(1)

    while True:
        watcher.watch()
        time.sleep(WATCH_INTERVAL)
