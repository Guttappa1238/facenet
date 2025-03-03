# coding=utf-8
"""Performs face detection in realtime.
Based on code from https://github.com/shanren7/real_time_face_recognition
"""
# MIT License
#
# Copyright (c) 2017 François Gervais
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import sys
import time
from PIL import Image

import cv2

import face


def store_single_disk(image, label):
    """
    @author : Guttappa Sajjan
    Stores a single image as a .png file on disk.
        Parameters:
        ---------------
        image       image array, (32, 32, 3) to be stored
        label       image label
    """
    ts = time.time()
    st = datetime.fromtimestamp(ts).strftime("%d-%m-%Y_%H-%M-%S")
    Image.fromarray(image).save(f"{label}_{st}.png")

def mark_attendance(csvData):
    with open('attendance.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
        rows = open('attendance.csv').read().split('\n')                                               
        newrows = []
        for row in rows:
            if row not in newrows:
                newrows.append(row)

        csvFile = open('FinalAttendance.csv', 'w')
        csvFile.write('\n'.join(newrows))
        #csvFile.to_excel ('FinalAttendance.xlsx', index = None, header=True)
        # df = pd.read_csv('FinalAttendance.csv')
        # df.to_excel('FinalAttendance.xlsx', sheet_name='gkz', index=True)  # index=True to write row index
        csvFile.close()
        
def add_overlays(frame, faces, frame_rate):
    if faces is not None:
        for face in faces:
            face_bb = face.bounding_box.astype(int)

            (startX, startY, endX, endY) = face.bounding_box.astype(int)
            x, y, w, h = [v for v in face_bb]
            sub_face = frame[startY:endY, startX:endX]
            store_single_disk(sub_face, face.name)
            cv2.rectangle(
                frame,
                (face_bb[0], face_bb[1]),
                (face_bb[2], face_bb[3]),
                (0, 255, 0),
                2,
            )
            if face.name is not None:
                cv2.putText(
                    frame,
                    face.name,
                    (face_bb[0], face_bb[3]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    thickness=2,
                    lineType=2,
                )
              

    cv2.putText(
        frame,
        str(frame_rate) + " fps",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        thickness=2,
        lineType=2,
    )


def main(args):
    frame_interval = 3  # Number of frames after which to run face detection
    fps_display_interval = 5  # seconds
    frame_rate = 0
    frame_count = 0

    video_capture = cv2.VideoCapture(0)
    face_recognition = face.Recognition()
    start_time = time.time()

    if args.debug:
        print("Debug enabled")
        face.debug = True

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        # resizing the frame by percent
        scale_percent = 60  # percent of original size
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

        if (frame_count % frame_interval) == 0:
            faces = face_recognition.identify(frame)

            # Check our current fps
            end_time = time.time()
            if (end_time - start_time) > fps_display_interval:
                frame_rate = int(frame_count / (end_time - start_time))
                start_time = time.time()
                frame_count = 0

        add_overlays(frame, faces, frame_rate)

        frame_count += 1
        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--debug", action="store_true", help="Enable some debug outputs."
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    main(parse_arguments(sys.argv[1:]))

