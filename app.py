# app.py - Main Flask app (Volunteer Matching Platform)
from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from gemini_helper import get_gemini_match, calculate_match_score, generate_insights

app = Flask(__name__)
app.secret_key = "connectvol-hackathon-2026"

VOLUNTEERS_FILE = 'data/volunteers.json'
NGOS_FILE = 'data/ngos.json'
TESTIMONIALS_FILE = 'data/testimonials.json'

# Sample testimonials only (for seeding)
SAMPLE_TESTIMONIALS = [
    {"volunteer_name": "Priya Sharma", "ngo_name": "Green Earth Vadodara", 
     "quote": "AI matched me perfectly! Planted 200 trees last weekend.", "rating": 5},
    {"volunteer_name": "Rahul Patel", "ngo_name": "Tech for Good India", 
     "quote": "Taught coding to 30 kids. Best decision ever.", "rating": 5}
]

def load_json(file_path, default):
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        save_json(file_path, default)
        return default
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return default

def save_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_volunteers():
    # No seeding – return empty list if file is empty or missing
    return load_json(VOLUNTEERS_FILE, [])

def save_volunteers(data):
    save_json(VOLUNTEERS_FILE, data)

def load_ngos():
    # No seeding – return empty list if file is empty or missing
    return load_json(NGOS_FILE, [])

def save_ngos(data):
    save_json(NGOS_FILE, data)

def load_testimonials():
    # Seed testimonials if file is empty
    data = load_json(TESTIMONIALS_FILE, [])
    if not data:
        data = SAMPLE_TESTIMONIALS
        save_json(TESTIMONIALS_FILE, data)
    return data

def save_testimonials(data):
    save_json(TESTIMONIALS_FILE, data)

def find_user_by_email(email):
    # Check volunteers
    volunteers = load_volunteers()
    for vol in volunteers:
        if vol.get('email') == email:
            user_data = {k: v for k, v in vol.items() if k != 'password'}
            return {'type': 'volunteer', 'data': user_data, 'password_hash': vol.get('password')}
    # Check NGOs
    ngos = load_ngos()
    for ngo in ngos:
        if ngo.get('contact_email') == email:
            user_data = {k: v for k, v in ngo.items() if k != 'password'}
            return {'type': 'ngo', 'data': user_data, 'password_hash': ngo.get('password')}
    return None

@app.route('/')
def index():
    stats = {
    "volunteers": len(load_volunteers()),
    "ngos": len(load_ngos()),
    "hours": len(load_volunteers()) * 12   # average 12 hours per volunteer
    }
    return render_template('index.html', stats=stats, testimonials=load_testimonials()[:4])

@app.route('/volunteer/register', methods=['GET', 'POST'])
def volunteer_register():
    if request.method == 'POST':
        volunteer = {
            'name': request.form['name'],
            'email': request.form['email'],
            'password': generate_password_hash(request.form['password']),
            'skills': request.form.getlist('skills'),
            'interests': request.form.getlist('interests'),
            'availability': request.form.getlist('availability'),
            'location': request.form['location'],
            'bio': request.form['bio']
        }
        volunteers = load_volunteers()
        volunteers.append(volunteer)
        save_volunteers(volunteers)

        session['user_type'] = 'volunteer'
        session['user_data'] = {k: v for k, v in volunteer.items() if k != 'password'}
        return redirect(url_for('match'))

    skills_options = ["Teaching","Medical","Tech","Legal","Art","Construction","Fundraising","Logistics","Counseling","Environmental"]
    interests_options = ["Children","Elderly","Environment","Animals","Disaster Relief","Education","Health","Community Development"]
    return render_template('volunteer_register.html', skills_options=skills_options, interests_options=interests_options)

@app.route('/ngo/register', methods=['GET', 'POST'])
def ngo_register():
    if request.method == 'POST':
        ngo = {
            'ngo_name': request.form['ngo_name'],
            'mission': request.form['mission'],
            'required_skills': request.form.getlist('required_skills'),
            'focus_area': request.form['focus_area'],
            'location': request.form['location'],
            'open_slots': int(request.form['open_slots']),
            'schedule': request.form['schedule'],
            'contact_email': request.form['contact_email'],
            'password': generate_password_hash(request.form['password'])
        }
        ngos = load_ngos()
        ngos.append(ngo)
        save_ngos(ngos)

        session['user_type'] = 'ngo'
        session['user_data'] = {k: v for k, v in ngo.items() if k != 'password'}
        return redirect(url_for('ngo_dashboard'))

    skills_options = ["Teaching","Medical","Tech","Legal","Art","Construction","Fundraising","Logistics","Counseling","Environmental"]
    return render_template('ngo_register.html', skills_options=skills_options)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = find_user_by_email(email)
        if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
            session['user_type'] = user['type']
            session['user_data'] = user['data']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_data' not in session:
        return redirect(url_for('login'))
    if session['user_type'] == 'volunteer':
        return redirect(url_for('match'))
    else:
        return redirect(url_for('ngo_dashboard'))

@app.route('/match')
def match():
    if 'user_data' not in session or session.get('user_type') != 'volunteer':
        return redirect(url_for('login'))
    volunteer = session['user_data']
    ngos = load_ngos()
    matches = get_gemini_match(volunteer, ngos)
    return render_template('match.html', matches=matches, volunteer_name=volunteer['name'])

@app.route('/ngo/dashboard')
def ngo_dashboard():
    if 'user_data' not in session or session.get('user_type') != 'ngo':
        return redirect(url_for('login'))
    ngo = session['user_data']
    volunteers = load_volunteers()
    matches = []
    for vol in volunteers:
        score = calculate_match_score(vol, ngo)
        insights = generate_insights(vol, ngo, score)
        matches.append({
            'volunteer_name': vol['name'],
            'match_score': score,
            'skills': ', '.join(vol.get('skills', [])),
            'availability': ', '.join(vol.get('availability', [])),
            'location': vol.get('location', ''),
            'bio': vol.get('bio', ''),
            'insights': insights,
            'email': vol.get('email')
        })
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return render_template('ngo_dashboard.html', matches=matches[:10], ngo=ngo)

@app.route('/browse')
def browse():
    ngos = load_ngos()
    return render_template('browse.html', ngos=ngos)

@app.route('/profile')
def profile():
    if 'user_data' not in session:
        return redirect(url_for('index'))
    return render_template('profile.html', user=session['user_data'], user_type=session['user_type'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/schedule')
def schedule():
    commitments = [
        {"ngo": "Green Earth Vadodara", "date": "Apr 5, 2026", "activity": "Tree Planting Drive", "time": "9:00 AM"},
        {"ngo": "Tech for Good India", "date": "Apr 12, 2026", "activity": "Coding Workshop", "time": "2:00 PM"}
    ]
    return render_template('schedule.html', commitments=commitments)

@app.route('/impact')
def impact():
    data = {"hours": 87, "ngos_supported": 3, "top_skills": ["Teaching", "Environmental"]}
    return render_template('impact.html', impact_data=data)

@app.route('/testimonials', methods=['GET', 'POST'])
def testimonials():
    if request.method == 'POST':
        new_t = {
            'volunteer_name': request.form['volunteer_name'],
            'ngo_name': request.form['ngo_name'],
            'quote': request.form['quote'],
            'rating': int(request.form['rating'])
        }
        testimonials = load_testimonials()
        testimonials.append(new_t)
        save_testimonials(testimonials)
        return redirect(url_for('testimonials'))
    return render_template('testimonials.html', testimonials=load_testimonials())

if __name__ == '__main__':
    app.run(debug=True)