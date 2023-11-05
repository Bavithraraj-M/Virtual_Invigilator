from flask import  Flask,render_template,request,url_for,redirect
from flask_mysqldb import  MySQL
import cv2
import numpy as np
import threading

app =Flask(__name__)

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="Mithun@2003"

app.config["MYSQL_DB"]="crud"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql=MySQL(app)

user_name=""
user_mail=""
ismalprac=False;
@app.route("/signup",methods=['GET','POST'])

def signup():
    if request.method=='POST':
        global user_name,user_mail
        name=request.form['name']
        email=request.form['email']
        user_name=name
        user_mail=email
        password=request.form['password']
        print(email,password)
        con = mysql.connection.cursor()
        sql="insert into users (Name,email,password) value (%s,%s,%s)"
        con.execute(sql,[name,email,password])
        mysql.connection.commit()
        con.close()
        return redirect(url_for("home"))
    return render_template('signup.html')


@app.route("/",methods=['GET','POST'])

def login():
    if request.method=="POST":
         global user_name, user_mail
         uemail=request.form["email"]
         upassword=request.form["password"]
         try:
            cur=mysql.connection.cursor()
            cur.execute("select * from users where email=%s and password=%s", [uemail,upassword])
            res=cur.fetchone()

            if res:

                user_name = res["name"]
                user_mail = uemail
                cur.close()
                return redirect(url_for("home"))

            else:
                cur.close()
                print("<h3> Sign Up to continue . . .<h3>")
                return render_template('signup.html')
         except Exception as e:
            print(e)
         finally:
            mysql.connection.commit()
         cur.close()
    return render_template('index.html')



@app.route("/admin",methods=['GET','POST'])
def alogin():
    if request.method=="POST":
         uemail=request.form["email"]
         upassword=request.form["password"]
         try:
            cur=mysql.connection.cursor()
            cur.execute("select * from admin where email=%s and password=%s", [uemail,upassword])
            res=cur.fetchone()
            if res:
                return redirect(url_for("result"))
            else:
                return render_template('signup.html')
            cur.close()
         except Exception as e:
            print(e)
         finally:
            mysql.connection.commit()
         cur.close()
    return render_template('admin.html')

#--------------------------------------------------------------------------------------------------
@app.route("/result",methods=["POST","GET"])
def result():
    cur=mysql.connection.cursor()
    sql="select * from marks"
    cur.execute(sql)
    res=cur.fetchall()
    cur.close()
    return render_template("result.html",res=res)

@app.route("/instruct",methods=["POST","GET"])
def instruct():
    return render_template("instruct.html")


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Load the face detection model
net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel')

# Initialize the video capture (use a webcam with index 0)
cap = None  # This will be initialized later

# Initialize other variables
blink_counter = 0
blink_threshold = 5
eyes_open = True
message_count = 0
warning_count = 0
message = ""

# Create a flag to control the video capture loop
capture_active = False

def opencv_thread(connection):
    global cap, capture_active,warning_count,message_count,message,blink_threshold,blink_counter
    cap = cv2.VideoCapture(0)  # Initialize video capture here
    capture_active = True
    while capture_active:
        global ismalprac;
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
                box = detections[0, 0, i, 3:7] * np.array(
                    [frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                (x, y, x2, y2) = box.astype(int)
                cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                eye_count += 1

        pre_message = message

        if num_faces > 1:
            message = "Multiple people detected!"
        elif eye_count == 0:
            message = "No eyes detected (looking away?)"
        else:
            message = "Eyes detected (looking at screen)"

        # Print the message to the console
        print(message,message_count)
        if pre_message == message:
            message_count += 1
            if message == "No eyes detected (looking away?)" or message == "Multiple people detected!":
                if message_count > 200:
                    ismalprac=True;
                    """"" print("You are disqualified from the exam")
                    #con = mysql.connection.cursor()
                    try:
                        con = connection.cursor()
                    except:
                        con = connection.cursor()

                    #sql = "insert into marks (name,email,mark,ismalprac) value (%s,%s,%s,%s)"
                    sql = "insert into marks (name,email,mark,ismalprac) value (%s,%s,%s,%s)"
                    "" con.execute(sql, [user_name, user_mail, str(count), "tabswitch"])
                    mysql.connection.commit()
                    con.close()
                    con.execute(sql, [user_name, user_mail, '0', "look away from screen"])
                    mysql.connection.commit()
                    con.close()"""
                    capture_active=False
                    break
        else:
            if message_count > 18:
                if message == "No eyes detected (looking away?)" or message == "Multiple people detected!":
                    print(message)
                    warning_count += 1
                    print("Warning " + str(warning_count))
            message_count = 0

        if warning_count >= 5:
            """ con = mysql.connection.cursor()
            sql = "insert into marks (name,email,mark,ismalprac) value (%s,%s,%s,%s)"
            con.execute(sql, [user_name, user_mail, '0', "mal-practice[eye/face]"])
            mysql.connection.commit()
            con.close()"""
            ismalprac=True;
            capture_active=False;
            print("You are disqualified from the exam")
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route("/start_capture", methods=["POST"])
def start_capture():
    global cap
    if cap is None:
        con = mysql.connection
        capture_thread = threading.Thread(target=opencv_thread,args=(con,))

        capture_thread.start()
    return redirect(url_for("instruct"))

#-------------------------------------------------------------------------------------

class Question:
    id=-1
    question=""
    option1=""
    option2 =""
    option3 =""
    option4 =""
    correct_opt=-1

    def __init__(self,q_id,question,option1,option2,option3,option4,correct_opt):
        self.id=q_id
        self.question=question
        self.option1=option1
        self.option2=option2
        self.option3=option3
        self.option4=option4
        self.correct_opt=correct_opt

    def get_correct_option(self):
        if self.correct_opt==1:
            return self.option1
        elif self.correct_opt==2:
            return self.option2
        elif self.correct_opt==3:
            return self.option3
        else:
            return  self.option4

q1= Question(1,"What does HTML stand for?", "HyperText Markup Language", "Hypertext Transfer Protocol", "Hyper Transfer Markup Language", "High Tech Machine Learning", 1)
q2= Question(2,"Which programming language is used for web styling?", "Python", "CSS", "JavaScript", "HTML", 2)
q3= Question(3,"What does CSS stand for?", "Cascading Style Sheet", "Computer Style Sheet", "Creative Style Sheet", "Colorful Style Sheet", 1)
q4= Question(4,"Which of the following is not a data structure?", "Array", "Tree", "Graph", "Loop", 4)
q5= Question(5,"What does XML stand for?", "eXtensible Markup Language", "Extra Modern Language", "Extensive Main Loop", "External Machine Learning", 1)
q6= Question(6,"Which data structure uses the Last-In-First-Out (LIFO) principle?", "Queue", "Stack", "Array", "List", 2)
q7= Question(7,"In Python, how do you define a function?", "function myFunction()", "def myFunction()", "func myFunction()", "define myFunction()", 2)
q8= Question(8,"What is the time complexity of binary search in a sorted list?", "O(log n)", "O(n)", "O(1)", "O(n^2)", 1)
q9= Question(9,"Which programming language is often used for server-side web development?", "HTML", "JavaScript", "CSS", "PHP", 4)
q10=Question(10,"Which of the following is a front-end JavaScript framework?", "React", "Node.js", "Django", "Ruby on Rails", 1)
ques=[q1,q2,q3,q4,q5,q6,q7,q8,q9,q10]
@app.route("/quiz",methods=["POST","GET"])
def quiz():
    return render_template("quiz.html",ques=ques)

@app.route("/submitquiz",methods=["POST","GET"])
def submitquiz():
    global capture_active,ismalprac
    capture_active = False
    count = 0

    if ismalprac:
        con = mysql.connection.cursor()
        sql = "insert into marks (name,email,mark,ismalprac) value (%s,%s,%s,%s)"
        con.execute(sql, [user_name, user_mail, 0, "look away from screen"])
        mysql.connection.commit()
        con.close()


    else:

        mal_prac=False
        ismalprac=True

        for q in ques:
            q_id=str(q.id)
            try:
                selected_opt=request.form[q_id]       # ... checking no of question crtly solved by user
                if mal_prac :
                    ismalprac=False;



            except:
                mal_prac=True

                continue
            crt_opt=q.get_correct_option()
            if crt_opt==selected_opt:
                count+=1

        con = mysql.connection.cursor()
        sql = "insert into marks (name,email,mark,ismalprac) value (%s,%s,%s,%s)"
        if not mal_prac or (mal_prac and not ismalprac) :

            con.execute(sql, [user_name, user_mail, str(count), "no malpractice"])
            mysql.connection.commit()
            con.close()
        else:
            con.execute(sql, [user_name, user_mail, str(count), "tabswitch"])
            mysql.connection.commit()
            con.close()
    return str(count);
#---------------------------------------------------------------------



@app.route("/home",methods=["POST","GET"])
def home():
    return render_template("home.html")


if __name__=='__main__':
    app.run(debug=True, threaded=True)
