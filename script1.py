import cv2
import dlib

# Load face detection and landmark detection models
face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# Initialize video capture object
cap = cv2.VideoCapture(0)

# Set up variables for counting students and bad posture
num_students = 0
num_bad_posture_students = 0
yawn_count_threshold = 20
yawn_count = 0

while True:
    # Capture frame from camera
    ret, frame = cap.read()

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_detector(gray)

    # Update the number of students present
    num_students = len(faces)
    num_bad_posture_students = 0

    # Loop over each detected face
    for face in faces:
        # Detect landmarks for the face
        landmarks = landmark_detector(gray, face)

        # Get the upper and lower lip coordinates
        upper_lip = (landmarks.part(51).x, landmarks.part(51).y)
        lower_lip = (landmarks.part(57).x, landmarks.part(57).y)

        # Calculate the distance between the upper and lower lips
        lip_distance = abs(upper_lip[1] - lower_lip[1])

        # Check if the student has bad posture (yawning)
        if lip_distance > yawn_count_threshold:
            num_bad_posture_students += 1
            yawn_count += 1
        else:
            yawn_count = 0

        # Draw a rectangle around the face and display the student's ID
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
        cv2.putText(frame, f"Student {num_students}", (face.left(), face.top() - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Calculate the percentage of students with bad posture
    if num_students > 0:
        bad_posture_percentage = round((num_bad_posture_students / num_students) * 100, 2)
    else:
        bad_posture_percentage = 0

    # Display the number of students and the percentage of students with bad posture
    cv2.putText(frame, f"Number of Students: {num_students}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Bad Posture: {bad_posture_percentage}%", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the output
    cv2.imshow("Smart Classroom", frame)

    # Exit the loop if 'q' is pressed
    if cv2.getWindowProperty("Smart Classroom", cv2.WND_PROP_VISIBLE) < 1:
        break


# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()