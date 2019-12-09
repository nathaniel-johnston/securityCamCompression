import cv2
import math

videoFile = "C:/Users/user/pictures/Camera Roll/test 3.mp4"
background = "C:/Users/user/pictures/Camera Roll/test 1.mp4"
vid2 = "C:/Users/user/pictures/Camera Roll/test 2.mp4"

avg = None

def weightedAvg(num1, num2, weight):
    return math.floor(num1 * weight + (1 - weight) * num2)


def getLength(cap):
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    return frames / fps

def findLongest(cap):
    longest = 0

    for i in range (1, len(cap)):
        if getLength(cap[i]) > getLength(cap[longest]):
            longest = i

    return longest

def write(videos, compression):
    length = len(videos)
    cap = []
    ret = [{} for i in range (length)]
    frame = [{} for i in range (length)]
    avg = [None for i in range (length)]
    xAvg = [None for i in range (length)]
    yAvg = [None for i in range (length)]
    wAvg = [None for i in range (length)]
    hAvg = [None for i in range (length)]
    count = 0

    compression = int(compression)

    if(compression < 1):
        print("Error: compression must be a whole number greater than or equal to 1. Using default compression of 1.")
        compression = 1
    elif(compression > 10):
        print("Error: compression too high. The video will likely be too fast. Using a compression of 10 instead.")
        compression = 10

    for i in range (length):
        cap.append(cv2.VideoCapture(videos[i]))
        ret[i], frame[i] = cap[i].read()

    longest = findLongest(cap)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    height, width = frame[0].shape[:2]
    writer = cv2.VideoWriter("final.avi", fourcc, cap[longest].get(cv2.CAP_PROP_FPS), (width, height))

    while ret[longest]:
        for vid in range (length):
            (x, y, w, h) = (0, 0, 0, 0)
            max = 0;

            if (ret[vid] and vid != longest):
                (frame[longest], avg[vid], xAvg[vid], yAvg[vid], wAvg[vid], hAvg[vid]) = \
                    detect(frame[vid], frame[longest], avg[vid], xAvg[vid], yAvg[vid], wAvg[vid], hAvg[vid])

        count += 1

        writer.write(frame[longest])

        for i in range(length):
            if(compression > 1):
                cap[i].set(1, compression*count)
            ret[i], frame[i] = cap[i].read()

    for i in range (length):
        cap[i].release()

    writer.release()

def detect(frame, longestFrame, avg, xAvg, yAvg, wAvg, hAvg):
    (x, y, w, h) = (0, 0, 0, 0)
    max = 0

    #Grey out the video and then blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (15, 15), 0)

    if avg is None:
        avg = gray.astype("float")
        return (longestFrame, avg, xAvg, yAvg, wAvg, hAvg)

    #subtract the current frame from a weighted average of the previous frames
    cv2.accumulateWeighted(gray, avg, .7)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    #find a black and white outline of the calculated difference in the frames
    thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=15)

    #find the areas that are outlined (the ares with motion
    (thresh, contour, hierarchy) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Find the largest contour area
    for i in contour:
        if cv2.contourArea(i) > max:
            max = cv2.contourArea(i)
            (x, y, w, h) = cv2.boundingRect(i)

    #compute a weighted average of the previous contour areas to smooth out the motion
    if yAvg is None or xAvg is None or wAvg is None or hAvg is None:
        yAvg = y
        xAvg = x
        wAvg = w
        hAvg = h
    else:
        yAvg = weightedAvg(yAvg, y, 0.7)
        xAvg = weightedAvg(xAvg, x, 0.7)
        wAvg = weightedAvg(wAvg, w, 0.7)
        hAvg = weightedAvg(hAvg, h, 0.7)

    #stitch the motion onto a background
    if wAvg * hAvg > 10000:
        longestFrame = stitch(frame, longestFrame, xAvg, yAvg, wAvg, hAvg)

    return (longestFrame, avg, xAvg, yAvg, wAvg, hAvg)


def stitch(image, background, x, y, w, h):
    alpha = 0.5
    background[y:y + h, x:x + w] = cv2.addWeighted(background[y:y + h, x:x + w], alpha, image[y:y + h, x:x + w],1 - alpha, 0)

    return background

def main():
    write((videoFile, vid2, background), 9)


if __name__ == "__main__":
    main()
