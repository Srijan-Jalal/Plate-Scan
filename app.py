from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

Model = "PTM.xml"  
cap = cv2.VideoCapture(0)  
cap.set(3, 640)  
cap.set(4, 480)  

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

min_area = 500
count = 0
save_snippet = False

@app.route('/')
def index():
    return render_template('Index.html')

def gen():
    global save_snippet, count
    while True:
        success, img = cap.read()

        if not success:
            print("Error: Failed to capture frame")
            break

        plate_cascade = cv2.CascadeClassifier(Model)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

        for (x, y, w, h) in plates:
            area = w * h

            if area > min_area:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

                img_roi = img[y: y + h, x:x + w]

                if save_snippet:
                    cv2.imwrite("saved_plates/scaned_img_" + str(count) + ".jpg", img_roi)
                    count += 1
                    save_snippet = False

                cv2.imshow("ROI", img_roi)

        _, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_snippet', methods=['POST'])
def save_snippet():
    global save_snippet
    save_snippet = True
    return 'Success'

if __name__ == '__main__':
    app.run()

    