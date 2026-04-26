import cv2

def authenticate():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    cam = cv2.VideoCapture(0)

    print("Authenticating...")

    if not cam.isOpened():
        print("Camera not available")
        return False

    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            id_, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            if confidence < 60:
                print("Access Granted")
                cam.release()
                cv2.destroyAllWindows()
                return True
            else:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)

        cv2.imshow("Face Recognition Login", frame)

        if cv2.waitKey(1) == 27:
            break

    cam.release()
    return False