import cv2
import RPi.GPIO as GPIO
import Adafruit_DHT

# Set up the GPIO pins for the LEDs
GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.OUT)  # Top-left quadrant
GPIO.setup(14, GPIO.OUT)  # Top-right quadrant
GPIO.setup(18, GPIO.OUT)  # Bottom-left quadrant
GPIO.setup(6, GPIO.OUT)  # Bottom-right quadrant

# Load the Haar cascade classifier for face detection
cascade = cv2.CascadeClassifier('/home/pi/Desktop/project/haarcascade_frontalface_default.xml')

# Open the webcam
cap = cv2.VideoCapture(0)

# Get the frame dimensions and calculate the quadrant dimensions
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
q_width = int(width / 2)
q_height = int(height / 2)

# Initialize variables to keep track of the number of people detected in each quadrant
num_people_q1 = 0  # Top-left quadrant
num_people_q2 = 0  # Top-right quadrant
num_people_q3 = 0  # Bottom-left quadrant
num_people_q4 = 0  # Bottom-right quadrant

# Set up the DHT11 sensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17

while True:
    # Read the temperature and humidity from the DHT11 sensor
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    # Read a frame from the webcam
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame using the Haar cascade
    faces = cascade.detectMultiScale(gray, 1.3, 5)
    
    # Reset the occupancy counts for each quadrant
    num_people_q1 = 0
    num_people_q2 = 0
    num_people_q3 = 0
    num_people_q4 = 0
    
    # Loop over each face and draw a bounding box around it
    for (x, y, w, h) in faces:
        # Calculate which quadrant the face belongs to
        if x < q_width and y < q_height:
            num_people_q1 += 1
            GPIO.output(3, GPIO.HIGH)  # Turn on the LED for the top-left quadrant
        elif x >= q_width and y < q_height:
            num_people_q2 += 1
            GPIO.output(14, GPIO.HIGH)  # Turn on the LED for the top-right quadrant
        elif x < q_width and y >= q_height:
            num_people_q3 += 1
            GPIO.output(18, GPIO.HIGH)  # Turn on the LED for the bottom-left quadrant
        else:
            num_people_q4 += 1
            GPIO.output(6, GPIO.HIGH)  # Turn on the LED for the bottom-right quadrant
        
        # Draw a bounding box around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Turn off the LEDs in quadrants where there are no people detected
    if num_people_q1 == 0:
        GPIO.output(3, GPIO.LOW)
    if num_people_q2 == 0:
        GPIO.output(14, GPIO.LOW)
    if num_people_q3 == 0:
        GPIO.output(18, GPIO.LOW)
    if num_people_q4 == 0:
        GPIO.output(6, GPIO.LOW)
    
    # Draw the lines separating the quadrants on the frame
    cv2.line(frame, (q_width, 0), (q_width, height), (0, 255, 0), 2)
    cv2.line(frame, (0, q_height), (width, q_height), (0, 255, 0), 2)

    # Draw the number of people detected in each quadrant on the frame
    cv2.putText(frame, "Q1: " + str(num_people_q1), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "Q2: " + str(num_people_q2),(10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "Q3: " + str(num_people_q3), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "Q4: " + str(num_people_q4), (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Turn on the LED if a person is detected in the corresponding quadrant, otherwise turn it off
    GPIO.output(3, GPIO.HIGH if num_people_q1 > 0 else GPIO.LOW)
    GPIO.output(14, GPIO.HIGH if num_people_q2 > 0 else GPIO.LOW)
    GPIO.output(18, GPIO.HIGH if num_people_q3 > 0 else GPIO.LOW)
    GPIO.output(6, GPIO.HIGH if num_people_q4 > 0 else GPIO.LOW)

    # Read the temperature and humidity from the DHT11 sensor
    import Adafruit_DHT
    dht_pin = 17  # BCM pin used to read the sensor data
    dht_sensor = Adafruit_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, dht_pin)

    # Draw the temperature and humidity on the frame
    if humidity is not None and temperature is not None:
        temp_text = f"Temp: {temperature:.1f}C"
        hum_text = f"Hum: {humidity}%"
        cv2.putText(frame, temp_text, (10, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, hum_text, (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show the current occupancy level
    occupancy = num_people_q1 + num_people_q2 + num_people_q3 + num_people_q4
    cv2.putText(frame, "Occupancy: " + str(occupancy), (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # Wait for 1 millisecond for a key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#Release the capture and clean up the GPIO pins
cap.release()
GPIO.cleanup()
cv2.destroyAllWindows()