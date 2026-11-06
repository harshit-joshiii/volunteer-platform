# 🌱 VolunteerConnect – AI-Powered Volunteer Matching Platform

> Connecting passionate volunteers with NGOs through intelligent, AI-powered recommendations.

## 📌 About the Project

VolunteerConnect is a platform designed to bridge the gap between volunteers and Non-Governmental Organizations (NGOs).

Finding the right volunteering opportunity can be difficult. Similarly, NGOs often struggle to find volunteers whose skills, interests and availability align with their requirements.

Our platform addresses this challenge through an AI-powered matching system that connects volunteers with suitable NGOs based on their profiles, skills, interests, location and availability.

## ✨ Key Features

### 👤 Volunteer Portal
- Register and create a volunteer profile.
- Add skills, interests, location and availability.
- Receive personalized NGO recommendations.
- View match scores and explanations for recommended opportunities.

### 🏢 NGO Portal
- Register an NGO and provide its mission and requirements.
- Specify required skills, focus areas and available volunteering slots.
- Access an NGO dashboard.
- Discover and rank potential volunteers based on compatibility.

### 🤖 AI-Powered Matching
- Uses Google Gemini AI to identify suitable volunteer–NGO matches.
- Generates match scores and personalized explanations.
- Uses a rule-based matching algorithm as a fallback when the Gemini API is unavailable.

### 🔐 Additional Features
- User authentication and session management.
- Password hashing.
- NGO browsing.
- Volunteer profiles.
- Testimonials.
- Impact and scheduling pages.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| AI Integration | Google Gemini API |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | JSON |
| Authentication | Werkzeug Security |
| Templating | Jinja2 |

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9 or later
- pip (Python package manager)
- Google Gemini API key (optional, for AI-powered matching)

### 1. Clone the repository

```bash
git clone https://github.com/harshit-joshiii/volunteer-platform.git
```

### 2. Navigate to the project directory

```bash
cd volunteer-platform
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install Flask google-generativeai
```

### 5. Configure Gemini API (Optional)

Get an API key from Google AI Studio:

https://aistudio.google.com/apikey

Set the environment variable:

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your_api_key"
```

**macOS / Linux:**
```bash
export GEMINI_API_KEY="your_api_key"
```

The platform can also use its rule-based matching system without a Gemini API key.

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

http://127.0.0.1:5000/

## 🧠 How the Matching System Works

The platform considers multiple compatibility factors:

1. **Skills:** Compares volunteer skills with the skills required by NGOs.
2. **Interests:** Checks whether the volunteer's interests align with the NGO's focus area.
3. **Location:** Considers geographical compatibility.
4. **Availability:** Compares volunteer availability with the NGO's schedule.

The platform uses Google Gemini to generate intelligent recommendations and explanations. If the AI service is unavailable, a rule-based scoring mechanism provides alternative recommendations.

## 📂 Project Structure

```text
volunteer-platform/
│
├── app.py                  # Main Flask application
├── gemini_helper.py        # AI matching and scoring logic
│
├── static/                 # Static frontend assets
│
├── templates/              # HTML templates
│
└── .gitignore
```

The application creates and uses JSON data files inside a `data/` directory at runtime.

## 🚀 Future Scope

- Real-time communication between volunteers and NGOs.
- Advanced geographical matching.
- Volunteer activity tracking and verified impact reports.
- NGO verification and trust mechanisms.
- Improved dashboards and analytics.
- Deployment with a production database.

## 👥 Team Members

Add your hackathon team members and their respective contributions here.

## 🏆 Built For

Developed as a hackathon project with the aim of making volunteering more accessible, efficient and impactful.

---

**Together, let's connect people with causes that matter. 🌍**
