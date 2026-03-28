# gemini_helper.py - AI-powered matching with Gemini
import json
import os
import google.generativeai as genai

# Configure Gemini if API key is present
API_KEY = os.environ.get('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)

def calculate_match_score(volunteer, ngo):
    """Rule-based scoring (fallback)"""
    score = 0
    vol_skills = set(volunteer.get('skills', []))
    ngo_skills = set(ngo.get('required_skills', []))
    if vol_skills and ngo_skills:
        common_skills = len(vol_skills.intersection(ngo_skills))
        score += (common_skills / max(len(vol_skills), len(ngo_skills))) * 40
    
    vol_interests = set(volunteer.get('interests', []))
    if ngo.get('focus_area') in vol_interests:
        score += 30
    elif any(i in vol_interests for i in [ngo.get('focus_area', '')]):
        score += 20
    
    if volunteer.get('location', '').lower() == ngo.get('location', '').lower():
        score += 15
    elif "vadodara" in volunteer.get('location', '').lower():
        score += 10
    
    vol_avail = set(volunteer.get('availability', []))
    ngo_schedule = ngo.get('schedule', '').lower()
    if any(day.lower() in ngo_schedule for day in vol_avail):
        score += 15
    
    return min(95, int(score))

def generate_insights(volunteer, ngo, score):
    """Generate a list of insight strings for the match"""
    insights = []
    vol_skills = set(volunteer.get('skills', []))
    ngo_skills = set(ngo.get('required_skills', []))
    common = vol_skills.intersection(ngo_skills)
    if common:
        insights.append(f"✓ Your skills in {', '.join(common)} are exactly what they need.")
    
    if volunteer.get('interests') and ngo.get('focus_area') in volunteer.get('interests', []):
        insights.append(f"✓ Your interest in {ngo.get('focus_area')} aligns perfectly with their focus area.")
    
    if volunteer.get('location') == ngo.get('location'):
        insights.append("✓ You're in the same city – easy to coordinate and commute.")
    elif "vadodara" in volunteer.get('location', '').lower():
        insights.append("✓ You're in the same region – great for community impact.")
    
    vol_avail = set(volunteer.get('availability', []))
    ngo_schedule = ngo.get('schedule', '').lower()
    if any(day.lower() in ngo_schedule for day in vol_avail):
        insights.append(f"✓ Your availability ({', '.join(vol_avail)}) fits their schedule.")
    
    if ngo.get('open_slots', 0) > 0:
        insights.append(f"✓ They have {ngo['open_slots']} open slots – they're actively looking for volunteers.")
    
    if not insights:
        insights.append("✓ This could be a great opportunity to explore!")
    
    return insights

def generate_reason(volunteer, ngo, score, insights):
    """Generate a friendly reason based on insights"""
    if score >= 80:
        return f"This is an excellent match! {insights[0] if insights else 'Your profile fits their needs perfectly.'}"
    elif score >= 60:
        return f"Good potential here. {insights[0] if insights else 'You have some overlapping interests.'}"
    else:
        return f"Worth considering. {insights[0] if insights else 'Your skills could still be valuable.'}"

def get_gemini_match(volunteer, ngos):
    """Try Gemini first, fall back to rule-based"""
    if not ngos:
        return []
    
    if API_KEY:
        try:
            return get_gemini_match_ai(volunteer, ngos)
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to rule-based matching.")
    
    scored_ngos = []
    for ngo in ngos:
        score = calculate_match_score(volunteer, ngo)
        insights = generate_insights(volunteer, ngo, score)
        reason = generate_reason(volunteer, ngo, score, insights)
        scored_ngos.append({
            "ngo_name": ngo.get("ngo_name"),
            "match_score": score,
            "reason": reason,
            "insights": insights,
            "contact_email": ngo.get("contact_email")
        })
    scored_ngos.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_ngos[:3]

def get_gemini_match_ai(volunteer, ngos):
    """Call Gemini API to get matches with rich insights"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    volunteer_str = json.dumps(volunteer, indent=2)
    ngos_str = json.dumps(ngos, indent=2)
    
    prompt = f"""
You are an AI volunteer matching expert. Given a volunteer profile and a list of NGOs, return the top 3 best matching NGOs.
For each match, provide:
- ngo_name (string)
- match_score (integer 0-100)
- reason (a short, friendly explanation of why this is a good match)
- insights (a list of specific reasons, e.g., skill match, location, availability, mission alignment)

Format the response as a JSON array. Example:
[
  {{
    "ngo_name": "Green Earth Vadodara",
    "match_score": 95,
    "reason": "This is an excellent match! Your environmental passion and weekend availability align perfectly.",
    "insights": [
      "✓ Your skills in Environmental and Construction match their needs.",
      "✓ You're both located in Vadodara.",
      "✓ Your weekend availability fits their schedule."
    ]
  }}
]

Volunteer: {volunteer_str}

NGOs: {ngos_str}

Return ONLY the JSON array, no extra text.
"""
    response = model.generate_content(prompt)
    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        matches = json.loads(text)
        for match in matches:
            for ngo in ngos:
                if ngo.get('ngo_name') == match.get('ngo_name'):
                    match['contact_email'] = ngo.get('contact_email')
                    break
        return matches[:3]
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        raise Exception("Invalid Gemini response")