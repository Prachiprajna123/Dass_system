from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash, send_from_directory
from bson import SON, Binary, ObjectId

# Your code here

import os
from dotenv import load_dotenv

load_dotenv()
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from pymongo import MongoClient
import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, send_file, render_template
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['dass_system']  # Main database
db = client['dass_system']
  # Main database

# Collections
users_collection = db['users']
admins_collection = db['admins']
survey_pdfs_collection = db['survey_pdfs']



# Secret key for session management
app.secret_key = os.urandom(24)

# File upload configurations
STATIC_FOLDER = 'static'
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Define subdirectories within the static directory
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
ADMIN_UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'admin_uploads')
ADMIN_LOGIN_UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'admin_login_uploads')
REGISTRATION_UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'registration_uploads')

# Ensure the static and subdirectories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ADMIN_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ADMIN_LOGIN_UPLOAD_FOLDER, exist_ok=True)

os.makedirs(REGISTRATION_UPLOAD_FOLDER, exist_ok=True)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD =os.getenv('EMAIL_PASSWORD')
def send_email_with_pdf(to_email, subject, body, pdf_path):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body of the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_path)}')
            msg.attach(part)

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
def is_logged_in():
    return 'username' in session

def is_admin_logged_in():
    return 'admin' in session
@app.route('/start_assessment')
def start_assessment():
    return render_template("Assessment.html")

class CustomPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Survey Results Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Collect form data (including name, gender, contact, and email)
        data = {}
        for i in range(1, 43):
            response = request.form.get(f'q{i}')
            if response is None or response.strip() == '':
                return jsonify({"success": False, "error": f"Missing response for question {i}"}), 400
            try:
                data[f'q{i}'] = int(response)
            except ValueError:
                return jsonify({"success": False, "error": f"Invalid response for question {i}"}), 400

        # Collect additional form fields
        name = request.form.get('name', '')
        gender = request.form.get('gender', '')
        contact = request.form.get('contact', '')
        email = request.form.get('email', '')

        # Create DataFrame
        df = pd.DataFrame(data, index=[0])

        # Check for missing or invalid data
        if df.isnull().values.any():
            raise ValueError("Some data are missing or invalid.")

        # Check for all-zero responses
        if df.sum().sum() == 0:
            raise ValueError("All responses are zero. Cannot generate plots.")

        # List of questions
        questions = [
            "I found myself getting upset by quite trivial things",
            "I was aware of dryness of my mouth",
            "I couldn't seem to experience any positive feeling at all",
            "I experienced breathing difficulty (e.g., excessively rapid breathing, breathlessness in the absence of physical exertion)",
            "I just couldn't seem to get going",
            "I tended to over-react to situations",
            "I had a feeling of shakiness (e.g., legs going to give way)",
            "I found it difficult to relax",
            "I found myself in situations that made me so anxious I was most relieved when they ended",
            "I felt that I had nothing to look forward to",
            "I found myself getting upset rather easily",
            "I felt that I was using a lot of nervous energy",
            "I felt sad and depressed",
            "I found myself getting impatient when I was delayed in any way (e.g., lifts, traffic lights, being kept waiting)",
            "I had a feeling of faintness",
            "I felt that I had lost interest in just about everything",
            "I felt I wasn't worth much as a person",
            "I felt that I was rather touchy",
            "I perspired noticeably (e.g., hands sweaty) in the absence of high temperatures or physical exertion",
            "I felt scared without any good reason",
            "I felt that life wasn't worthwhile",
            "I found it hard to wind down",
            "I had difficulty in swallowing",
            "I couldn't seem to get any enjoyment out of the things I did",
            "I was aware of the action of my heart in the absence of physical exertion (e.g., sense of heart rate increase, heart missing a beat)",
            "I felt down-hearted and blue",
            "I found that I was very irritable",
            "I felt I was close to panic",
            "I found it hard to calm down after something upset me",
            "I feared that I would be 'thrown' by some trivial but unfamiliar task",
            "I was unable to become enthusiastic about anything",
            "I found it difficult to tolerate interruptions to what I was doing",
            "I was in a state of nervous tension",
            "I felt I was pretty worthless",
            "I was intolerant of anything that kept me from getting on with what I was doing",
            "I felt terrified",
            "I could see nothing in the future to be hopeful about",
            "I felt that life was meaningless",
            "I found myself getting agitated",
            "I was worried about situations in which I might panic and make a fool of myself",
            "I experienced trembling (e.g., in the hands)",
            "I found it difficult to work up the initiative to do things"
        ]

        # Map questions to answers in a readable format
        responses_readable = {}
        for i, question in enumerate(questions, start=1):
            responses_readable[question] = data.get(f'q{i}', 0)

        # Store survey data in MongoDB
        

        # Insert into the survey_responses collection
        users_collection.update_one({"Ename":name},{"$set":{"responses": responses_readable,"timestamp": datetime.now()}})

        # Plot the survey results (same as before)
        temp_image_paths = []

        # Bar chart
        plt.figure(figsize=(10, 6))
        df.T.plot(kind='bar', legend=False)
        plt.title('Survey Results - Bar Chart', fontsize=14, fontweight='bold')
        plt.xlabel('Questions', fontsize=12)
        plt.ylabel('Responses', fontsize=12)
        temp_image_path = 'temp_bar_chart.png'
        plt.savefig(temp_image_path)
        plt.close()
        temp_image_paths.append(temp_image_path)

        # Pie chart
        plt.figure(figsize=(8, 8))
        df.T.plot(kind='pie', subplots=True, legend=False)
        plt.title('Survey Results - Pie Chart', fontsize=14, fontweight='bold')
        temp_image_path = 'temp_pie_chart.png'
        plt.savefig(temp_image_path)
        plt.close()
        temp_image_paths.append(temp_image_path)

        # Line chart
        plt.figure(figsize=(10, 6))
        df.T.plot(kind='line', legend=False)
        plt.title('Survey Results - Line Chart', fontsize=14, fontweight='bold')
        plt.xlabel('Questions', fontsize=12)
        plt.ylabel('Responses', fontsize=12)
        temp_image_path = 'temp_line_chart.png'
        plt.savefig(temp_image_path)
        plt.close()
        temp_image_paths.append(temp_image_path)

        # Generate the PDF (same as before)
        pdf = CustomPDF()
        pdf.add_page()

        # Add user details to PDF
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Client Information', ln=True, align='C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Name: {name}', ln=True)
        pdf.cell(0, 10, f'Gender: {gender}', ln=True)
        pdf.cell(0, 10, f'Contact: {contact}', ln=True)
        pdf.cell(0, 10, f'Email: {email}', ln=True)
        pdf.ln(10)

        # Add scoring and interpretation information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Scoring and Interpretation', ln=True, align='C')
        pdf.set_font('Arial', '', 12)
        scoring_info = """Scoring and Interpretation Information:
Compared to the general population, the y-axis for this plot may be truncated to enhance the ability of the practitioner to observe changes. 
Small changes in symptoms over time may be significant."""
        pdf.multi_cell(0, 10, scoring_info)
        pdf.ln(10)

        # Add Client Responses header
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Client Responses', 0, 1, 'C')
        pdf.ln(5)

        # Table header with bold text
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(10, 10, '#', border=1, align='C', fill=True)
        pdf.cell(90, 10, 'Question', border=1, align='C', fill=True)
        pdf.cell(20, 10, 'Never', border=1, align='C', fill=True)
        pdf.cell(25, 10, 'Sometimes', border=1, align='C', fill=True)
        pdf.cell(20, 10, 'Often', border=1, align='C', fill=True)
        pdf.cell(25, 10, 'Almost Always', border=1, align='C', fill=True)
        pdf.ln()

        # Populate the table with proper styling and bold responses
        pdf.set_font('Arial', '', 10)
        for i, question in enumerate(questions, start=1):
            response = data.get(f'q{i}', 0)  # Get the response value (0-3)

            # Add row with question and response options
            pdf.cell(10, 10, str(i), border=1, align='C')
            pdf.cell(90, 10, question, border=1)
            pdf.cell(20, 10, '0' if response == 0 else '', border=1, align='C')
            pdf.cell(25, 10, '1' if response == 1 else '', border=1, align='C')
            pdf.cell(20, 10, '2' if response == 2 else '', border=1, align='C')
            pdf.cell(25, 10, '3' if response == 3 else '', border=1, align='C')
            pdf.ln()

        # Add graphs to PDF
        for temp_image_path in temp_image_paths:
            pdf.add_page()
            pdf.image(temp_image_path, x=10, y=10, w=190)

        # Save PDF
        temp_pdf_path = 'survey_results.pdf'
        pdf.output(temp_pdf_path)

        # Read the PDF as a response
        with open(temp_pdf_path, 'rb') as f:
            pdf_binary = Binary(f.read())

        pdf_data = {
            "user_name": name,
            "user_email": email,
            "pdf_file": pdf_binary,
            "timestamp": datetime.now()
        }
        users_collection.update_one({ "Ename": name},{"$push": {"pdf_data":pdf_data}})

        
        response_buf = BytesIO()
        with open(temp_pdf_path, 'rb') as f:
            response_buf.write(f.read())
        response_buf.seek(0)

        # Clean up temporary files
        for temp_image_path in temp_image_paths:
            os.remove(temp_image_path)
        os.remove(temp_pdf_path)
        flash("response  sent successfully", "success")
        return redirect("/success")

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500


        
@app.route("/")
def index():
    return render_template("index.html")

# User registration
@app.route("/user_register", methods=['GET'])
def user_register():
    return render_template('register.html')
@app.route("/admin_register", methods=['GET'])
def admin_register_page():
    return render_template("admin_register.html")

@app.route("/admin_login", methods=['GET'])
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/register", methods=['POST'])
def register():
    name = request.form.get("name")
    age = request.form.get("age")
    email = request.form.get("email")
    gender = request.form.get("gender")
    contact = request.form.get("contact")
    photo = request.files['photo']
    password = request.form.get("password")

    if not password:
        return jsonify({"success": False, "error": "Password is required."}), 400

    try:
        filename = secure_filename(name + ".jpg")
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(photo_path)
        photo_url = f'/static/uploads/{filename}'
    except Exception as e:
        return jsonify({"success": False, "error": f"Photo upload failed: {e}"}), 500


    hashed_password = generate_password_hash(password)

    user_data = {
        "Ename": name,
        "age": age,
        "email": email,
        "gender": gender,
        "contact": contact,
        "photo_url": photo_url,
        "role": "user",
        "password": hashed_password,
        "responses": {},
        "timestamp": datetime.now()  # Store questions and answers in a readable format
    }

    try:
        users_collection.insert_one(user_data)
        response = {"success": True, 'name': name}
    except Exception as e:
        response = {"success": False, "error": f"Database insertion failed: {e}"}

    return jsonify(response)
@app.route("/admin")
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login_page'))
    users = list(users_collection.find())
    return render_template("admin.html", users=users)

# User login
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    user = users_collection.find_one({"Ename": username})

    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    if not check_password_hash(user['password'], password):
        return jsonify({"success": False, "error": "Incorrect password"}), 401

    session['username'] = user['Ename']
    session['user_id'] = str(user['_id'])

    response = {
        "success": True,
        "message": "Login successful",
    }
    return jsonify(response)

# User logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Admin registration


@app.route("/admin_register", methods=['POST'])
def admin_register():
    name = request.form.get("name")
    photo = request.files['photo']
    password = request.form.get("password")

    if not name or not password or not photo:
        return jsonify({"success": False, "error": "Invalid data"}), 400

    filename = secure_filename(photo.filename)
    photo_path = os.path.join(UPLOAD_FOLDER, filename)
    photo.save(photo_path)

    hashed_password = generate_password_hash(password)
    admin_data = {
        "name": name,
        "photo_url": photo_path,
        "password": hashed_password,
        "role": "admin"
    }

    try:
        admins_collection.insert_one(admin_data)
    except Exception as e:
        return jsonify({"success": False, "error": f"Database insertion failed: {e}"})

    response = {"success": True, 'name': name}
    return jsonify(response)

# Admin login
@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    name = request.form.get("name")
    password = request.form.get("password")

    if not name or not password:
        return jsonify({"success": False, "error": "Invalid data"}), 400

    admin = admins_collection.find_one({"name": name})
    if not admin:
        return jsonify({"success": False, "error": "No matching admin found"}), 404

    if check_password_hash(admin['password'], password):
        session['admin'] = admin['name']
        return jsonify({"success": True, "name": admin['name']})
    else:
        return jsonify({"success": False, "error": "Incorrect password"}), 401

# Admin logout
@app.route("/admin_logout")
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))
@app.route("/delete_user/<user_id>", methods=['POST'])
def delete_user(user_id):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    return redirect(url_for('admin'))

@app.route('/user_login')
def user_login():
    return render_template('login.html')
@app.route('/success')
def success():
    username = session['username']
    user = users_collection.find_one({"Ename": username})
    return render_template("success.html", user=user)

@app.route('/admin_success/<user_id>')
def admin_success(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    return render_template("success.html", user=user)

@app.route("/edit_user/<user_id>", methods=['GET', 'POST'])
def edit_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    if request.method == 'POST':
        name = request.form.get("name")
        age = request.form.get("age")
        email = request.form.get("email")
        gender = request.form.get("gender")
        contact = request.form.get("contact")
        photo = request.files['photo']



        if photo:
            filename = secure_filename(name + "update.jpg")
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(photo_path)
            photo_url = f'/static/uploads/{filename}'
        else:
            photo_url = user['photo_url']

        update_result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "Ename": name,
                "age": age,
                "email": email,
                "gender": gender,
                "contact": contact,
                "photo_url": photo_url
            }}
        )

        if update_result.modified_count > 0:
            return jsonify({"success": True, "message": "User updated successfully"})
        else:
            return jsonify({"success": False, "error": "No changes made"}), 400

    return render_template('edit.html', user=user)
@app.route("/view_response")
def view_response():
    user_name = session.get("username")
    print("user_name")
    user = users_collection.find_one({"Ename": user_name})  # Use find_one to get a single document

    if user is None:
        return "User not found. Please check your session or database.", 404

    return render_template("view_response.html", user=user)
@app.route('/send_mail/<user_id>', methods=['POST'])
def send_email(user_id):
    if 'admin' not in session:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    try:
        # Fetch the user document
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            flash("User not found", "error")
            return redirect(url_for('admin'))

        # Check if the user has any PDF data
        if "pdf_data" not in user or not user["pdf_data"]:
            flash("No PDF data found for this user", "error")
            return redirect(url_for('admin'))

        # Get the latest PDF data
        latest_pdf = user["pdf_data"][-1]  # Get the most recent PDF
        pdf_binary = latest_pdf["pdf_file"]

        # Save the binary data to a temporary file
        temp_pdf_path = 'temp_survey_results.pdf'
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_binary)

        # Send the email with the PDF
        email_sent = send_email_with_pdf(
            to_email=user["email"],
            subject='Your Survey Results',
            body='Please find your survey results attached.',
            pdf_path=temp_pdf_path
        )

        # Clean up the temporary file
        os.remove(temp_pdf_path)

        if not email_sent:
            flash("Failed to send email", "error")
            return redirect(url_for('admin'))

        flash("Email sent successfully", "success")
        return redirect(url_for('admin'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('admin'))

@app.route('/download_pdf/<user_id>', methods=['GET'])
def download_pdf(user_id):
    if 'admin' not in session:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    try:
        # Fetch the user document
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Check if the user has any PDF data
        if "pdf_data" not in user or not user["pdf_data"]:
            return jsonify({"success": False, "error": "No PDF data found for this user"}), 404

        # Get the latest PDF data
        latest_pdf = user["pdf_data"][-1]  # Get the most recent PDF
        pdf_binary = latest_pdf["pdf_file"]

        # Return the PDF as a downloadable file
        response_buf = BytesIO(pdf_binary)
        response_buf.seek(0)

        return send_file(response_buf, as_attachment=True, download_name='survey_results.pdf')

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500

google_api_key = os.getenv("GOOGLE_API_KEY")
import google.generativeai as genai
genai.configure(api_key=google_api_key)

# List all available models (for debugging)
models = genai.list_models()


# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-pro')  # Use the correct model name

# Chatbot route
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot_interaction():
    if request.method == "POST":
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

            try:
               response = model.generate_content(f"You are a helpful assistant that provides information about job applications, resumes, and career advice. If the question is unrelated to these topics, politely inform the user. User: {user_input}")
               chatbot_response = response.text

               if "unrelated" in chatbot_response.lower() or "not sure" in chatbot_response.lower():
                    chatbot_response = "I'm here to help with job applications, resumes, and career advice. If you have questions outside these topics, please contact support or visit our help center."

            except Exception as e:
                print(f"Error calling Google Gemini API: {e}")
                chatbot_response = "Sorry, I'm unable to process your request at the moment. Please try again later."

        return jsonify({"response": chatbot_response})

    return render_template("chatbot.html")

if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG",False)=="True")
