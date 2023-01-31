#python 3.7.6 must be used
import shutil
from imageai.Detection import ObjectDetection
import os
import sys
import csv
import math

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

from moviepy.video.io.VideoFileClip import VideoFileClip


#file explorer
root = tk.Tk()
root.withdraw()

input_file = file_path = filedialog.askopenfilename()

#frame progress bar
root = tk.Tk()
root.title('Qutum')
width = root.winfo_screenwidth()/2
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))

def update_progress_label():
    return f"Current Progress: {math.floor(pb['value']*10)/10}%"


def frame_progress():
    if (pb['value'] + float(100/len(times))) <= 99.9:
        pb['value'] += float(100/len(times))
        value_label['text'] = update_progress_label()
    else:
        value_label['text'] = "Now analysing each frame..."
        pb['value'] = 0

def analysis_progress():
    if (pb['value'] + float(100/len(times))) <= 99.9:
        pb['value'] += float(100/len(times))
        value_label['text'] = update_progress_label()
    else:
        value_label['text'] = "Your footage has been completely analysed and a .csv file has been made!"
        root.after(1000,finish)

def stop():
    root.destroy()
    shutil.rmtree(frames_path)
    sys.exit()

def finish():
    root.destroy()

# progressbar
pb = ttk.Progressbar(
    root,
    orient='horizontal',
    mode='determinate',
    length=350
)
# place the progressbar
pb.grid(column=0, row=0, columnspan=2, padx=219, pady=200)

# label
value_label = ttk.Label(root, text=update_progress_label())
value_label.grid(column=0, row=1, columnspan=2)

# start button
stop_button = ttk.Button(
    root,
    text='Stop',
    command=stop
)
stop_button.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)





#removes file extension but uses file name to make a dir
frames_path = input_file.rsplit("/", 2)[0] + "/" + (input_file.rpartition("/")[2]).rpartition(".")[0]
os.mkdir(frames_path)

#extract frames every 15 seconds
def extract_frames(footage, times, output):
    clip = VideoFileClip(footage)
    for t in times:
        framepath = os.path.join(output, '{}.png'.format(t))
        clip.save_frame(framepath, t)
        frame_progress()
        root.update()
        print("Frame %s has been cut" % (t))
    print("ended")


footage = input_file
times = [0]

duration = math.floor(VideoFileClip(footage).duration)
while times[-1] < duration and (times[-1]+15) < duration:
    times.append(times[-1]+15)

extract_frames(footage, times, frames_path)


#start running AI through the frames
data = [
    ['frame', 'detected']
]
input_path = frames_path
dir = os.listdir(input_path)

output_path = input_path + " processed"
os.mkdir(output_path)

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath(r"yolo.h5")
detector.loadModel()

custom = detector.CustomObjects(person=True)

for frames in dir:
    count = 0
    input = str(frames)
    output = input

    detections = detector.detectObjectsFromImage(
        custom_objects=custom,
        input_image=os.path.join(input_path, input), 
        output_image_path=os.path.join(output_path, output),
        minimum_percentage_probability=30,
    )

    print(input+" has been processed.")
    analysis_progress()
    root.update()

    for eachObject in detections:
        if eachObject['name'] == 'person':
            count += 1

    data.append([input, count])



with open(((input_file.rpartition("/")[2]).rpartition(".")[0]) + '.csv', 'w', newline='') as f:
    # create the csv writer
    writer = csv.writer(f)
    writer.writerows(data)
    sys.exit()


# from imageai.Detection import VideoObjectDetection
# import os

# vid_obj_detect = VideoObjectDetection()

# vid_obj_detect.setModelTypeAsYOLOv3()
# vid_obj_detect.setModelPath(r"yolo.h5")
# vid_obj_detect.loadModel()

# def forFrame(frame_number, output_array, output_count):
#     print("FOR FRAME " , frame_number)
#     print("Output count for unique objects : ", output_count)
#     print("------------END OF A FRAME --------------")

# detected_vid_obj = vid_obj_detect.detectObjectsFromVideo(
#     input_file_path=r"testclip10seconds.mp4",
#     output_file_path=r"example.mp4",
#     frames_per_second=30,
#     log_progress=True,
#     per_frame_function=forFrame,  
#     minimum_percentage_probability=40, 
# )

