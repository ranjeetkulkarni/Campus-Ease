from flask import Flask, render_template, request, redirect, url_for, flash
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import torch
import librosa
import soundfile as sf
import requests
import os
import PyPDF2

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/seproject'
app.secret_key = '4325534543544354455'
db = PyMongo(app).db
logged_in = False
bcrypt = Bcrypt(app)
email = ""
username = ""
password = ""
balance = 0
income = 0
expenses = 0
history = []

# Set device: Use GPU if available, else use CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pre-trained Wav2Vec 2.0 processor and model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h").to(device)

# Your actual API key
api_key = "AIzaSyApvZXWXyl48mnoza945A8CPdh95I4gwg4"  # Replace with your actual API key

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/topic-listing', methods=['GET', 'POST'])
def topic_listing():
    return  render_template('topics-listing.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return  render_template('contact.html')

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    return  render_template('authenticate.html')

@app.route('/topics-detail', methods=['GET', 'POST'])
def topics_detail():
    return  render_template('topics-detail.html')

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    return  render_template('tracker.html')

@app.route('/user_portal', methods=['GET', 'POST'])
def user_portal():
    return  render_template('user_portal.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global logged_in
    if logged_in:
        flash("Successfully logged out")
    logged_in = False
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in, email
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        info = db.authentication.find_one({'email': email})
        print(email, password)
        if (info is None):
            return redirect('/sign-up')
        else:
            hashed_passwd = info['password']
            if bcrypt.check_password_hash(hashed_passwd, password):
                logged_in = True
                print("Login Successful")
                return redirect('/')
            else:
                message = 'incorrect password'
                print("login unsuccessful")
    print(logged_in)
    return render_template('login.html', message=message)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    global username, email, password
    message = 'Sign up successful'
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(username, email, password)

        if email == db.accounts.find_one({'email': email}):
            message = 'user already exists'
        if len(username) < 3:
            message = 'username too short'
        elif len(password) < 7:
            message = 'password too short'
        elif password != confirm_password:
            message = 'passwords do not match'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            db.authentication.insert_one(
                    {
                        "email": email,
                        "username": username,
                        "password": hashed_password,
                        "balance": 0,
                        "income": 0,
                        "expenses": 0,
                        "history": [],
                    }
                )
            return redirect('/login')
        print(message)
        

    return render_template('signup.html', message=message)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return  render_template('forgot_password.html')

@app.route('/delete_history', methods=['POST'])
def delete_history():
    global email
    if not logged_in:
        return redirect('/login')

    # Remove transaction history from the database
    db.authentication.update_one(
        {'email': email},
        {"$set": {
            "history": [],  # Clear the history
            "balance": 0,   # Reset balance
            "income": 0,    # Reset income
            "expenses": 0   # Reset expenses
        }}
    )

    # Redirect to the application page after deletion
    return redirect('/Application')

@app.route('/api/save-changes', methods=['POST'])
def save_changes():
    global email, balance, income, expenses, history
    # if not logged_in:                                                       #this does changes to the database and shows the changes in the application page
    #     return redirect('/login')
    
    data = request.form
    description = data.get('description')
    amount = float(data.get('amount'))
    if logged_in:
        db.authentication.update_one(
            {'email': email},
            {"$push": {"history": {"description": description, "amount": amount}}}
        )
        user_data = db.authentication.find_one({'email': email})
        history = user_data.get('history', [])
        income = sum(item['amount'] for item in history if item['amount'] > 0)
        expenses = sum(item['amount'] for item in history if item['amount'] < 0)
        balance = income + expenses

        db.authentication.update_one(
            {'email': email},
            {"$set": {
                "balance": balance,
                "income": income,
                "expenses": expenses
            }}
        )
    else:
        history.append({"description": description, "amount": amount})
        if (amount > 0):
            income += amount
        else:
            expenses += amount
        balance = income + expenses


    return redirect('/Application')


@app.route('/Application', methods=['GET', 'POST'])
def Application():
    global email, balance, income, expenses, history
    user_data = db.authentication.find_one({'email': email})                      # this shows intial calculations present in the database
    if user_data:
        # Perform calculations
        history = user_data.get('history', [])
        income = sum(item['amount'] for item in history if item['amount'] > 0)
        expenses = sum(item['amount'] for item in history if item['amount'] < 0)
        balance = income + expenses
    # Update user data in the database
        db.authentication.update_one(
            {'email': email},
            {"$set": {
                "balance": balance,
                "income": income,
                "expenses": expenses
            }}
        )

    return render_template(
        'Application.html',
        balance=balance,
        income=income,
        expenses=abs(expenses),  # Ensure expenses are positive for display
        history=history,
        abs=abs  # Make the abs() function available to the template
    )


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    return  render_template('admin_login.html')

@app.route('/admin_portal', methods=['GET', 'POST'])
def admin_portal():
    return  render_template('admin_portal.html')

@app.route('/about' , methods=['GET', 'POST'])
def about():
    return  render_template('about.html')

@app.route('/404' , methods=['GET', 'POST'])
def _404():
    return  render_template('404.html')

@app.route('/audio-summarizer', methods=['GET', 'POST'])
def audio_summarizer():
    if logged_in == False :
        return redirect('/login')
    transcription = ""
    summary = ""
    def extract_text_from_pdf(pdf_path):
        text = ""
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()  # Extract text from each page
        return text


    if request.method == 'POST':
        # Check if file is in request
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if a file was uploaded
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            # Ensure the 'static/uploads' directory exists
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # Save the uploaded file
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)

            # Convert MP3 to WAV if necessary
            _, ext = os.path.splitext(filepath)
            if ext.lower() != '.pdf':
                if ext.lower() == '.mp3':
                    try:
                        # Load the MP3 file
                        audio, sr = librosa.load(filepath, sr=16000)
                    
                        # Define the new WAV file path
                        wav_filepath = os.path.splitext(filepath)[0] + '.wav'
                    
                        # Save the audio in WAV format
                        sf.write(wav_filepath, audio, sr)
                    
                        # Remove the original MP3 file
                        os.remove(filepath)
                    
                        # Update filepath to the new WAV file
                        filepath = wav_filepath
                    
                        print(f"Converted MP3 to WAV: {wav_filepath}")
                    except Exception as e:
                        print("Error converting MP3 to WAV:", e)
                        return "Error converting audio file"

                # Load and process the audio file
                try:
                    speech_array, sampling_rate = sf.read(filepath)

                    # Resample if necessary
                    if sampling_rate != 16000:
                        speech_array = librosa.resample(speech_array, orig_sr=sampling_rate, target_sr=16000)
                        sampling_rate = 16000

                    # Prepare input values for the model
                    input_values = processor(speech_array, sampling_rate=sampling_rate, return_tensors="pt").input_values.to(device)

                    # Perform inference to get transcription
                    with torch.no_grad():
                        logits = model(input_values).logits

                    # Decode the predicted token IDs to get the transcription
                    predicted_ids = torch.argmax(logits, dim=-1)
                    transcription = processor.batch_decode(predicted_ids, clean_up_tokenization_spaces=True)[0]
                    print("Transcription:", transcription)
                
                except Exception as e:
                    print("Error processing audio file:", e)
                    return "Error processing audio file"
            else:
                transcription = extract_text_from_pdf(filepath)
                    
            
            # Capture summary type from the form
            summary_type = request.form.get('summary_type', 'short')
            summary_prompt = f"Summarize the following text in a {summary_type} way:\n{transcription}"

            # Prepare summarization request
            try:
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

                # Define the payload for the summarization request
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": summary_prompt
                                }
                            ]
                        }
                    ]
                }

                # Define headers for the API request
                headers = {
                    "Content-Type": "application/json"
                }

                # Make a POST request to the Gemini API for summarization
                response = requests.post(api_url, json=payload, headers=headers)

                # Process API response
                if response.status_code == 200:
                    summary = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Error Generating Summary")
                else:
                    print("API Error:", response.status_code, response.text)
                    summary = "Error Generating Summary"
                
                print("Summary:", summary)

            except Exception as e:
                print("Error in summarization:", e)
                summary = "Error Generating Summary"
                
    return render_template('Audio.html', transcription=transcription, summary=summary)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
