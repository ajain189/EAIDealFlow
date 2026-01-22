import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = None
MODEL = "gemini-2.0-flash-exp"

def init_client():
    """Initialize Gemini client."""
    global client
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            return True
        except:
            return False
    return False

def scrape_website_summary(url: str) -> str:
    """Use Gemini to summarize company from website URL."""
    if not client:
        if not init_client():
            return ""
    
    if not url or not url.strip():
        return ""
    
    prompt = f"""Analyze the website at {url} and extract:
1. Company description (2 sentences max)
2. Key services or products offered
3. Any hints about ownership, size, or employees

Return as brief bullet points. If you cannot access the site, return empty string."""
    
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text if response.text else ""
    except:
        return ""

def generate_emails(company_name: str, industry: str, revenue: float, 
                    median_multiple: float, website_summary: str, tone: str = 'formal') -> dict:
    """Generate 3-email drip campaign."""
    if not client:
        if not init_client():
            return {
                'hook': {'subject': 'Introduction', 'body': '[AI unavailable]'},
                'asset': {'subject': 'Valuation Report', 'body': '[AI unavailable]'},
                'close': {'subject': 'Follow-up', 'body': '[AI unavailable]'}
            }
    
    try:
        hook_prompt = f"""Write a professional cold outreach email for {company_name} ({industry}).
Revenue: ${revenue:,.0f}. Similar companies trade at {median_multiple:.1f}x.
Tone: {tone}. 3 sentences. No emojis.
Format: SUBJECT: [subject]
BODY: [body]"""
        
        hook_response = client.models.generate_content(model=MODEL, contents=hook_prompt)
        hook = _parse_email(hook_response.text if hook_response.text else "")
        
        asset_prompt = f"""Write a follow-up email offering a free valuation snapshot for {company_name}.
Tone: {tone}. 2-3 sentences.
Format: SUBJECT: [subject]
BODY: [body]"""
        
        asset_response = client.models.generate_content(model=MODEL, contents=asset_prompt)
        asset = _parse_email(asset_response.text if asset_response.text else "")
        
        close_prompt = f"""Write a brief final follow-up for {company_name} asking for 5 minutes.
Tone: {tone}. 2 sentences max.
Format: SUBJECT: [subject]
BODY: [body]"""
        
        close_response = client.models.generate_content(model=MODEL, contents=close_prompt)
        close = _parse_email(close_response.text if close_response.text else "")
        
        return {'hook': hook, 'asset': asset, 'close': close}
    except:
        return {
            'hook': {'subject': 'Introduction', 'body': '[Generation failed]'},
            'asset': {'subject': 'Valuation Report', 'body': '[Generation failed]'},
            'close': {'subject': 'Follow-up', 'body': '[Generation failed]'}
        }

def generate_upside_bullets(company_name: str, industry: str, target_margin: float,
                            peer_median_margin: float, website_summary: str) -> list:
    """Generate 3 operational upside bullet points."""
    if not client:
        if not init_client():
            return [
                "Operational efficiency improvements identified",
                "Scale benefits through platform resources",
                "Technology and process improvements"
            ]
    
    margin_gap = peer_median_margin - target_margin if peer_median_margin and target_margin else 0
    
    prompt = f"""Generate exactly 3 bullet points about operational upside for {company_name} ({industry}).
Margin gap vs peers: {margin_gap:.1f}%
Return only 3 bullets, one per line, starting with "•" """
    
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        if response.text:
            bullets = [line.strip().lstrip('•').strip() for line in response.text.strip().split('\n') if line.strip()]
            return bullets[:3] if len(bullets) >= 3 else bullets + ['Operational improvements identified'] * (3 - len(bullets))
    except:
        pass
    
    return [
        f"Margin improvement potential of {abs(margin_gap):.1f}% through operational optimization",
        "Scale benefits through platform resources",
        "Technology and process improvements"
    ]

def _parse_email(raw: str) -> dict:
    """Parse raw AI response into subject and body."""
    lines = raw.strip().split('\n')
    subject = ""
    body_lines = []
    in_body = False
    
    for line in lines:
        if line.upper().startswith('SUBJECT:'):
            subject = line.split(':', 1)[1].strip()
        elif line.upper().startswith('BODY:'):
            in_body = True
        elif in_body:
            body_lines.append(line)
    
    return {
        'subject': subject or "Follow-up from EAI Capital",
        'body': '\n'.join(body_lines).strip() or raw
    }
