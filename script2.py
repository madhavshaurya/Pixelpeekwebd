import cv2
import numpy as np
import dlib
from imutils import face_utils
from scipy.spatial import distance as dist

# Define a function to compute the eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Define the threshold for drowsiness detection
EAR_THRESHOLD = 0.25

# Load the face and eye detectors from the dlib library
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# Start the video capture device (webcam)
cap = cv2.VideoCapture(0)

# Initialize variables for head nodding detection
nod_counter = 0
nod_threshold = 8
nod_time = 0

while True:
    # Capture a frame from the video
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = detector(gray)

    # Loop over each face
    for face in faces:
        # Get the facial landmarks for the face region
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        # Extract the eye regions from the face landmarks
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]

        # Compute the eye aspect ratio for each eye
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # Detect head nodding
        (x, y, w, h) = face_utils.rect_to_bb(face)
        roi = gray[y:y+h, x:x+w]
        rows,cols = roi.shape
        sobel_y = cv2.Sobel(roi, cv2.CV_64F, 0, 1, ksize=5)
        _, sobel_y = cv2.threshold(sobel_y, 60, 255, cv2.THRESH_BINARY)
        edge_count = np.count_nonzero(sobel_y == 255)
        if edge_count > 20 and nod_time == 0:
            nod_counter += 1
            nod_time = 10
        elif nod_time > 0:
            nod_time -= 1
        else:
            nod_counter = 0

        # Label the user as drowsy or active based on the eye aspect ratio and head nodding behavior
        if ear < EAR_THRESHOLD and nod_counter >= nod_threshold:
            label = 'Drowsy'
        else:
            label = 'Active'

        # Draw the label on the frame
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Display the resulting frame
    cv2.imshow('Drowsiness Detection', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and close the window
cap.release()
cv2.destroyAllWindows()