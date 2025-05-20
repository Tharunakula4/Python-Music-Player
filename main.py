import os
import threading
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from mutagen.mp3 import MP3
from pygame import mixer

root = tk.Tk()

statusbar = ttk.Label(root, text="Welcome to Melody", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side=BOTTOM, fill=X)

menubar = Menu(root)
root.config(menu=menubar)

subMenu = Menu(menubar, tearoff=0)
playlist = []

def browse_file():
    global filename_path
    filename_path = filedialog.askopenfilename()
    if filename_path:
        add_to_playlist(filename_path)

def add_to_playlist(filepath):
    filename = os.path.basename(filepath)
    index = 0
    playlistbox.insert(index, filename)
    playlist.insert(index, filepath)

menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)

def about_us():
    tkinter.messagebox.showinfo('About Melody', 'This is a music player built using Python Tkinter by @attreyabhatt')

helpMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpMenu)
helpMenu.add_command(label="About Us", command=about_us)

mixer.init()

root.title("Melody")
try:
    root.iconbitmap(r'C:\Users\HP\images\melody.ico')
except:
    pass  # In case the .ico file path is wrong or missing

leftframe = Frame(root)
leftframe.pack(side=LEFT, padx=30, pady=30)

playlistbox = Listbox(leftframe)
playlistbox.pack()

addBtn = ttk.Button(leftframe, text="+ Add", command=browse_file)
addBtn.pack(side=LEFT)

def del_song():
    selected_song = playlistbox.curselection()
    if selected_song:
        index = int(selected_song[0])
        playlistbox.delete(index)
        playlist.pop(index)

delBtn = ttk.Button(leftframe, text="- Del", command=del_song)
delBtn.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(pady=30)

topframe = Frame(rightframe)
topframe.pack()

lengthlabel = ttk.Label(topframe, text='Total Length : --:--')
lengthlabel.pack(pady=5)

currenttimelabel = ttk.Label(topframe, text='Current Time : --:--', relief=GROOVE)
currenttimelabel.pack()

paused = False
current_time = 0
stop_thread = False

def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    mins, secs = divmod(total_length, 60)
    timeformat = '{:02d}:{:02d}'.format(round(mins), round(secs))
    lengthlabel['text'] = "Total Length - " + timeformat

    global stop_thread, current_time
    stop_thread = True
    time.sleep(0.3)
    stop_thread = False
    current_time = 0
    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()

def start_count(total_time):
    global paused, current_time, stop_thread
    while current_time <= total_time and not stop_thread:
        if not paused and mixer.music.get_busy():
            mins, secs = divmod(current_time, 60)
            timeformat = '{:02d}:{:02d}'.format(round(mins), round(secs))
            currenttimelabel['text'] = "Current Time - " + timeformat
            time.sleep(1)
            current_time += 1
        else:
            time.sleep(0.2)

def play_music():
    global paused
    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = False
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            selected_song = int(selected_song[0])
            play_it = playlist[selected_song]
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar['text'] = "Playing music - " + os.path.basename(play_it)
            show_details(play_it)
        except:
            tkinter.messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')

def stop_music():
    global stop_thread
    mixer.music.stop()
    stop_thread = True
    statusbar['text'] = "Music Stopped"
    currenttimelabel['text'] = "Current Time : --:--"

def pause_music():
    global paused
    paused = True
    mixer.music.pause()
    statusbar['text'] = "Music Paused"

def rewind_music():
    play_music()
    statusbar['text'] = "Music Rewinded"

def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)

muted = False

def mute_music():
    global muted
    if muted:
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=volumePhoto)
        scale.set(70)
        muted = False
    else:
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)
        muted = True

middleframe = Frame(rightframe)
middleframe.pack(pady=30, padx=30)

playPhoto = PhotoImage(file='images/play.png')
playBtn = ttk.Button(middleframe, image=playPhoto, command=play_music)
playBtn.grid(row=0, column=0, padx=10)

stopPhoto = PhotoImage(file='images/stop.png')
stopBtn = ttk.Button(middleframe, image=stopPhoto, command=stop_music)
stopBtn.grid(row=0, column=1, padx=10)

pausePhoto = PhotoImage(file='images/pause.png')
pauseBtn = ttk.Button(middleframe, image=pausePhoto, command=pause_music)
pauseBtn.grid(row=0, column=2, padx=10)

bottomframe = Frame(rightframe)
bottomframe.pack()

rewindPhoto = PhotoImage(file='images/rewind.png')
rewindBtn = ttk.Button(bottomframe, image=rewindPhoto, command=rewind_music)
rewindBtn.grid(row=0, column=0)

mutePhoto = PhotoImage(file='images/mute.png')
volumePhoto = PhotoImage(file='images/volume.png')
volumeBtn = ttk.Button(bottomframe, image=volumePhoto, command=mute_music)
volumeBtn.grid(row=0, column=1)

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)
mixer.music.set_volume(0.7)
scale.grid(row=0, column=2, pady=15, padx=30)

def on_closing():
    stop_music()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
