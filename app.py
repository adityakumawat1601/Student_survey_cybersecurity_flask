from flask import Flask, render_template, request, redirect
import sqlite3
import bcrypt
import qrcode
import socket
import webbrowser

def generate_flask_qr_code(port=5000, box_size=10, border=4):
    # Get the local IP address dynamically
    local_ip = socket.gethostbyname(socket.gethostname())

    # Set the Flask app URL
    flask_url = f"http://{local_ip}:{port}"

    # Generate a QR code for the Flask app URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(flask_url)
    qr.make(fit=True)
    # Create an image from the QR code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    # Save the QR code image
    qr_img.save("qr_code.png")
    print(f"Flask App URL: {flask_url}")
    # Open the saved QR code image
    webbrowser.open("qr_code.png")

# Call the function with the desired parameters
generate_flask_qr_code(port=5000, box_size=10, border=4)


app = Flask(__name__)

# Function to create a connection to the SQLite database
def create_connection():
    return sqlite3.connect('users.db')

# Function to create the user table if it doesn't exist
def create_user_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            dob TEXT NOT NULL,
            password TEXT NOT NULL
        
        )
    ''')
    connection.commit()
    connection.close()

# Create the user table when the application starts
create_user_table()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user_entry', methods=['POST'])
def user_entry():
    global student_id
    name = request.form['name']
    student_id = request.form['studentID']
    dob = request.form['dob']
    password = request.form['password']

    # Check if the user with the given student ID already exists
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE student_id = ?', (student_id,))
    existing_user = cursor.fetchone()
    connection.close()

    if existing_user:
        # User already exists, provide a message and a link to redirect to the index page
        return render_template("user_exists.html")

    # User doesn't exist, proceed to store the user information in the database
    connection = create_connection()
    cursor = connection.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('''
        INSERT INTO users (name, student_id, dob, password)
        VALUES (?, ?, ?, ?)
    ''', (name, student_id, dob, hashed_password))
    connection.commit()
    connection.close()


    # Generate and save QR code
    return render_template("questions.html")


@app.route('/leaflets',methods=['GET','POST'])
def leaflet():
    global total_doughnuts
    if request.method=="GET":
        return redirect('/')
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')
    q4 = request.form.get('q4')
    q5 = request.form.get('q5')
    total_doughnuts = sum(2 for q in [q1, q2, q3, q4, q5] if q == 'yes')

    return render_template('leaflets.html')

@app.route('/doughnuts', methods=['GET','POST'])
def doughnut():
    if request.method =="GET":
        return redirect('/')

    return render_template('doughnuts.html', totalDoughnuts=total_doughnuts)



if __name__ == "__main__":
   app.run(host='0.0.0.0', debug=True)

    




