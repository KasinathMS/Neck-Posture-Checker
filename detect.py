import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose()

video = cv2.VideoCapture("video.mp4")  

while True:
    success, img = video.read()
    
    if not success:
        break
    
    img = cv2.resize(img, (800, 600))
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = pose.process(img_rgb)

    h, w, _ = img.shape

    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark

        # Get required landmarks
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

        # Convert normalized coordinates to pixel values
        ls = (int(left_shoulder.x * w), int(left_shoulder.y * h))
        le = (int(left_ear.x * w), int(left_ear.y * h))
        lh = (int(left_hip.x * w), int(left_hip.y * h))

        # Calculate horizontal distance between ear and shoulder
        ear_shoulder_distance = abs(le[0] - ls[0])
        
        # Calculate shoulder-hip distance for normalization
        shoulder_hip_distance = math.sqrt((ls[0] - lh[0])**2 + (ls[1] - lh[1])**2)
        
        # Normalize the distance (as ratio)
        if shoulder_hip_distance > 0:
            distance_ratio = ear_shoulder_distance / shoulder_hip_distance
        else:
            distance_ratio = 0

        # Draw lines
        cv2.line(img, le, ls, (0, 255, 0), 3)
        cv2.line(img, ls, lh, (0, 255, 0), 3)
        
        # Draw vertical reference line from shoulder
        cv2.line(img, ls, (ls[0], le[1]), (255, 0, 0), 2)

        # Posture logic
        if distance_ratio > 0.15:
            posture = "BAD POSTURE"
            color = (0, 0, 255)
        else:
            posture = "GOOD POSTURE"
            color = (0, 255, 0)

        # Display distance ratio
        cv2.putText(img, f"Distance Ratio: {distance_ratio:.2f}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (255, 255, 255), 2)

        # Display posture status
        cv2.putText(img, posture,
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, color, 3)

        # Draw pose landmarks
        mp_drawing.draw_landmarks(
            img,
            result.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    cv2.imshow("Neck Posture Checker", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):   
        break

video.release()
cv2.destroyAllWindows()