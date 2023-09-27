import cv2
import numpy as np
        

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel')

cap = cv2.VideoCapture(0)
blink_counter = 0
blink_threshold = 5
eyes_open = True

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Adjust the parameters for face detection
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,    # Decreased scaleFactor
        minNeighbors=8,     # Increased minNeighbors
        minSize=(50, 50)    # Increased minSize
    )

    eye_count = 0
    face_count = len(faces)

    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104, 117, 123))
    net.setInput(blob)
    detections = net.forward()

    num_faces = 0  # Initialize a counter for detected faces

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # Adjust confidence threshold as needed
            num_faces += 1  # Increment the counter for each detected face
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            (x, y, x2, y2) = box.astype(int)
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)
            eye_count += 1

        aspect_ratio = float(ew) / eh #aspect ratio to determine if the eyes are closed based on their width and height.

        if aspect_ratio < 0.2:
            blink_counter += 1
            if blink_counter >= blink_threshold:
                eyes_open = False
        else:
            blink_counter = 0
            eyes_open = True

    if num_faces > 1:
        message = "Multiple people detected!"
    elif not eyes_open:
        message = "Blinking"
    elif eye_count == 0:
        message = "No eyes detected (looking away?)"
    else:
        message = "Eyes detected (looking at screen)"

    cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Eye Movement Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# code for providing warning
""" import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel')

cap = cv2.VideoCapture(0)
blink_counter = 0
blink_threshold = 5
eyes_open = True
message_count=0
warning_count=0
message=""
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=8,
        minSize=(50, 50)
    )

    eye_count = 0

    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104, 117, 123))
    net.setInput(blob)
    detections = net.forward()

    num_faces = 0

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            num_faces += 1
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            (x, y, x2, y2) = box.astype(int)
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            eye_count += 1


    pre_message=message

    if num_faces > 1:
        message = "Multiple people detected!"
    
    elif eye_count == 0:
        message = "No eyes detected (looking away?)"
    else:
        message = "Eyes detected (looking at screen)"

    

    # Print the message to the console
    if pre_message==message :
        message_count+=1
        if message=="No eyes detected (looking away?)" or message=="Multiple people detected!" :
            if message_count>300:
                print("You are disqualified from the exam")
                break

        
    else :
        if message_count>18:
            if message=="No eyes detected (looking away?)" or message=="Multiple people detected!" :
                print(message)
                warning_count+=1
                print("Warning "+str(warning_count))
        message_count=0
        
    
    if warning_count>=5 :
        print("You are disqualified from the exam")
        break

cap.release()
cv2.destroyAllWindows() """