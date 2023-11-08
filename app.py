from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from distutils.log import debug
from fileinput import filename
from flask import *
import os
import datetime
from FindSkills.FindSkill import get_Skills
from FindSkills.top_skills import findTopSkills
from PdfConvertion.PdfProcessing import extract_text_from_pdf
from webscraping.jobSearch import runJob

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'skillmatcher'

mysql = MySQL(app)
topskills = []

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/fileupload', methods=['POST'])
def fileUpload():
    if request.method == 'POST':
        f = request.files['file']
        # Check if the file is a PDF
        if f.filename.split('.')[-1].lower() != 'pdf':
            return "Only PDF files are allowed."

        # Check if the file size is less than or equal to 2.5MB
        if len(f.read()) > 2.5 * 1024 * 1024:
            return "File size exceeds 2.5MB."

        # Reset the file pointer after reading for size check
        f.seek(0)
        # Assuming 'username' is sent as a parameter in the request
        username = session.get('username')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if the same file has been uploaded before by checking original filename
        cursor.execute('SELECT * FROM files WHERE username = %s', (username,))
        existing_file = cursor.fetchone()
        print(existing_file)
        if existing_file:
            # User has already uploaded a file, save with increment value
            file_number = existing_file['file_number'] + 1
            file_name = f'{username}_cv_{file_number}.pdf'
        else:
            # User is uploading for the first time
            file_number = 1
            file_name = f'{username}_cv.pdf'
        # Create a 'cv' directory if it doesn't exist
        cv_dir = os.path.join(os.getcwd(), 'cv')
        os.makedirs(cv_dir, exist_ok=True)

        # Save the file as 'username_cv.pdf'

        file_path = os.path.join(cv_dir, file_name)
        f.save(file_path)

        # Save the original filename
        original_filename = f.filename
        upload_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Add entry to the 'files' table
        cursor.execute(
            "INSERT INTO files (username, file_name, file_number, upload_date, filename_real) VALUES (%s, %s, %s, %s, %s)",
            (username, file_name, file_number if existing_file else 1, upload_date, original_filename))
        mysql.connection.commit()
        pdf_text = extract_text_from_pdf(file_path)
        cleaned_text = pdf_text.encode('ascii', 'ignore').decode('ascii')
        data  = [{"Information": cleaned_text }]
        with open('information.json', 'w') as json_file:
            json.dump(data, json_file)
        return render_template("Acknowledgement.html", name=file_name, pdf_text=pdf_text)

@app.route('/findskills', methods=['POST'])
def find_skills():
    skills = get_Skills()
    print (skills)
    topskills = findTopSkills()
    print (topskills)
    return render_template("skills.html",skills=skills)

@app.route('/findJobs')
def find_jobs():
    skill = findTopSkills()
    job_list = runJob(skill)
# enable to runn from websrcaping
   # with open('jobs_data.json', 'r') as json_file:
      #  job_list = json.load(json_file)
    return render_template('job.html', jobs=job_list)
@app.route('/saveJobs', methods=['POST'])
def save_job():
    job_title = request.form.get('job_title')
    company_name = request.form.get('company_name')
    job_link = request.form.get('job_link')
    username = session.get('username')
    upload_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO jobs VALUES (NULL, % s, % s, % s, % s, % s)', (username, job_title, company_name,job_link,upload_date,))
    mysql.connection.commit()

    return "Job saved successfully!"

@app.route('/oldCV', methods=['GET'])
def showUploadedFiles():
    username = session.get('username')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM files WHERE username = %s', (username,))
    uploaded_files = cursor.fetchall()
    return render_template("oldCV.html", uploaded_files=uploaded_files)

@app.route('/use_cv', methods=['POST'])
def use_cv_for_job_search():
    selected_file = request.form['file_name']
    print (selected_file)
    cv_dir = os.path.join(os.getcwd(), 'cv')
    os.makedirs(cv_dir, exist_ok=True)
    file_path = os.path.join(cv_dir, selected_file)
    pdf_text = extract_text_from_pdf(file_path)
    cleaned_text = pdf_text.encode('ascii', 'ignore').decode('ascii')
    data = [{"Information": cleaned_text}]
    with open('information.json', 'w') as json_file:
        json.dump(data, json_file)
    return render_template("Acknowledgement.html", name="file", pdf_text=pdf_text)


@app.route('/savedJobs', methods=['GET'])
def showSavedJobs():
    username = session.get('username')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM jobs WHERE username = %s', (username,))
    savedJobs = cursor.fetchall()

    return render_template("savedJobs.html", savedJobs = savedJobs)

@app.route('/deleteJob', methods=['POST'])
def delete_job():
    job_id = request.form.get('job_id')
    print (job_id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM jobs WHERE id = %s', (job_id,))
    mysql.connection.commit()
    return "Job deleted successfully!"


if __name__ == '__main__':
    app.run(debug=True)