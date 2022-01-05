#Import necessary libraries
from flask import Flask, render_template, Response
import cv2
import mediapipe as mp

#Initialize the Flask app
app = Flask(__name__)


# camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture(0)
'''
for ip camera use - rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' 
for local webcam use cv2.VideoCapture(0)
'''
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

finger_tips =[8, 12, 16, 20]
thumb_tip= 4


def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
                     
            frame = cv2.flip(frame, 1)

            h,w,c = frame.shape

            print(frame.shape)

            results = hands.process(frame)
            print(results)

            if results.multi_hand_landmarks:

                for hand_landmark in results.multi_hand_landmarks:
                    #accessing the landmarks by their position
                    lm_list=[]
                    for id ,lm in enumerate(hand_landmark.landmark):
                        lm_list.append(lm)

                    #array to hold true or false if finger is folded    
                    finger_fold_status =[]
                    for tip in finger_tips:
                        #getting the landmark tip position and drawing blue circle
                        x,y = int(lm_list[tip].x*w), int(lm_list[tip].y*h)
                        cv2.circle(frame, (x,y), 15, (255, 0, 0), cv2.FILLED)

                        #writing condition to check if finger is folded i.e checking if finger tip starting value is smaller than finger starting position which is inner landmark. for index finger    
                        #if finger folded changing color to green
                        if lm_list[tip].x < lm_list[tip - 3].x:
                            cv2.circle(frame, (x,y), 15, (0, 255, 0), cv2.FILLED)
                            finger_fold_status.append(True)
                        else:
                            finger_fold_status.append(False)

                    print(finger_fold_status)

                    #checking if all fingers are folded
                    if all(finger_fold_status):
                        #checking if the thumb is up
                        if lm_list[thumb_tip].y < lm_list[thumb_tip-1].y < lm_list[thumb_tip-2].y:
                            print("LIKE")  
                            cv2.putText(frame ,"LIKE", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

                        #check if thumb is down
                        if lm_list[thumb_tip].y > lm_list[thumb_tip-1].y > lm_list[thumb_tip-2].y:
                            print("DISLIKE")   
                            cv2.putText(frame ,"DISLIKE", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)


                mp_draw.draw_landmarks(frame, hand_landmark,
                mp_hands.HAND_CONNECTIONS, mp_draw.DrawingSpec((0,0,255),2,2),
                mp_draw.DrawingSpec((0,255,0),4,2))
      
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)