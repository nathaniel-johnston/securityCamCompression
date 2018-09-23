# securityCamCompression
This project helps to shorten the viewing time of security footage by overlapping the motion of videos from a security camera into a single video. By using this program, someone watching some security camera footage would be able to see all the videos at once in a fraction of the time. In fact, they would only need to watch for the length of the longest video that is being merged.
An example of the program's output can be seen in here:
![](motion2.gif)

## How it works
1. The program has to detect the motion of one of the videos
  ```Python
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
 ```
2. Cut out the area with the motion and stitch it onto a background
 ```Python
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
 ```
 The stitch method is shown here:
 ```Python
 def stitch(image, background, x, y, w, h):
    #Using addWeighted for a ghosting effect on the stiched images
    alpha = 0.5
    background[y:y + h, x:x + w] = cv2.addWeighted(background[y:y + h, x:x + w], alpha, image[y:y + h, x:x + w],1 - alpha, 0)

    return background
 ```
3. Write the stitched video to a file

This basic algorithm was then expanded to support many video files at once. There is also an added functionality of compressing the video, in a sense, to watch it even faster. This is done by using only every nth frame.

## Limitation and Improvements

1. The program can be slow, especially with a small compression factor (other than 1)

I have found that skipping to the nth frame of video is very slow. Also, using OpenCv's VideoCapture to read videos is not the fastest either. In the future, I would like to look into other methods of reading video files and skipping frames in an effort to optimize the speed of this program.

2. There is no way to know when a certain movement occurred

All the motion is occurring at once, meaning information about the time of the motion is lost. I plan on writing a small timestamp over the moving parts in order to show when the motion is happening.

3. Cannot cut out useless portions of videos

If there is a portion of a video that has no motion for an extended period of time, it is probably better to just remove it in order to save the user's time. I plan on implementing this with the use of ffmpeg
