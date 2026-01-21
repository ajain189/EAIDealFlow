"""
AI Service module for EAI DealFlow Terminal.
Handles Gemini API integration with parallel email generation, tone selector, and retry logic.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Global client - initialized lazily
_client = None
MODEL = "gemini-2.0-flash"


def _get_client():
    """Get or initialize the Gemini client."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                _client = genai.Client(api_key=api_key)
            except ImportError:
                print("Warning: google-genai not installed. AI features disabled.")
                return None
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                return None
    return _client


def _call_with_retry(prompt: str, max_retries: int = 3) -> Optional[str]:
    """
    Call Gemini with exponential backoff retry.

    Args:
        prompt: The prompt to send
        max_retries: Maximum retry attempts

    Returns:
        Response text or None on failure
    """
    client = _get_client()
    if not client:
        return None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1  # 1s, 3s, 5s
                print(f"Gemini API attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Gemini API failed after {max_retries} attempts: {e}")
                return None
    return None


def scrape_website_summary(url: str) -> str:
    """
    Use Gemini to summarize company from website URL.
    Returns empty string on failure (silent fallback).

    Args:
        url: Website URL to analyze

    Returns:
        Summary string or empty string on failure
    """
    if not url or not url.strip():
        return ""

    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    prompt = f"""Analyze the website at {url} and extract:
1. Company description (2 sentences max)
2. Key services or products offered
3. Any hints about ownership, company size, or employee count

Return as brief bullet points. Be concise. If you cannot access the site, return an empty response."""

    result = _call_with_retry(prompt)
    return result.strip() if result else ""


# Tone-specific prompt templates for high-quality email generation
TONE_TEMPLATES = {
    'formal': {
        'style': 'formal, professional, respectful, and measured',
        'greeting': 'Dear',
        'sign_off': 'Best regards',
        'characteristics': 'Use complete sentences, proper titles, respectful distance. No contractions.'
    },
    'friendly': {
        'style': 'warm, personable, conversational yet professional',
        'greeting': 'Hi',
        'sign_off': 'Best',
        'characteristics': 'Use a warm tone, contractions are okay, be approachable but still professional.'
    },
    'direct': {
        'style': 'concise, straightforward, action-oriented, no fluff',
        'greeting': 'Hello',
        'sign_off': 'Regards',
        'characteristics': 'Get to the point quickly, use short sentences, focus on value and next steps.'
    }
}


def _generate_hook_email(
    company: str,
    industry: str,
    revenue: float,
    multiple: float,
    tone: str,
    summary: str
) -> Dict[str, str]:
    """Generate Email 1: The Hook - Initial outreach establishing credibility."""
    t = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['formal'])

    prompt = f"""You are a professional M&A advisor writing a cold outreach email.

TARGET COMPANY: {company}
INDUSTRY: {industry}
REVENUE: ${revenue:,.0f}
MARKET MULTIPLE: {multiple:.1f}x (based on comparable transactions)
WEBSITE INFO: {summary if summary else 'Not available'}

TONE REQUIREMENTS:
- Style: {t['style']}
- {t['characteristics']}
- Start greeting with "{t['greeting']}"
- End with "{t['sign_off']}"

EMAIL REQUIREMENTS:
1. Subject line should be intriguing but professional (no clickbait)
2. Body should be 3-4 sentences maximum
3. Establish credibility by referencing data/analysis
4. Mention you see operational upside potential
5. Naturally reference the valuation multiple
6. NO emojis, NO hype words, NO exclamation marks
7. Include a soft call-to-action

Return EXACTLY in this format:
SUBJECT: [your subject line]
BODY:
[your email body]"""

    result = _call_with_retry(prompt)
    if result:
        return _parse_email(result)
    fallback_body = (
        f'{t["greeting"]} [Owner],\n\n'
        f'I am reaching out regarding {company}. Our team has been analyzing the '
        f'{industry} sector and identified your company as a potential fit for our '
        f'investment thesis.\n\n{t["sign_off"]},\n[Your Name]\nEAI Capital'
    )
    return {
        'subject': 'Introduction - EAI Capital',
        'body': fallback_body
    }


def _generate_asset_email(company: str, tone: str) -> Dict[str, str]:
    """Generate Email 2: The Asset - Offering value through the valuation snapshot."""
    t = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['formal'])

    prompt = f"""You are a professional M&A advisor writing a follow-up email offering a free valuation report.

TARGET COMPANY: {company}

TONE REQUIREMENTS:
- Style: {t['style']}
- {t['characteristics']}
- Start greeting with "{t['greeting']}"
- End with "{t['sign_off']}"

EMAIL REQUIREMENTS:
1. Reference your previous outreach
2. Offer a free one-page valuation snapshot
3. Mention it benchmarks against recent comparable sales
4. State the PDF is attached
5. 2-3 sentences maximum
6. NO emojis, NO hype

Return EXACTLY in this format:
SUBJECT: [your subject line]
BODY:
[your email body]"""

    result = _call_with_retry(prompt)
    if result:
        return _parse_email(result)
    fallback_body = (
        f'{t["greeting"]} [Owner],\n\n'
        f'Following up on my previous note. I have prepared a one-page valuation '
        f'snapshot for {company}, benchmarking your business against recent '
        f'comparable transactions in the market.\n\n'
        f'Please find it attached.\n\n{t["sign_off"]},\n[Your Name]'
    )
    return {
        'subject': f'Valuation Snapshot for {company}',
        'body': fallback_body
    }


def _generate_close_email(company: str, tone: str) -> Dict[str, str]:
    """Generate Email 3: The Close - Professional nudge for a brief conversation."""
    t = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['formal'])

    prompt = f"""You are a professional M&A advisor writing a final follow-up email.

TARGET COMPANY: {company}

TONE REQUIREMENTS:
- Style: {t['style']}
- {t['characteristics']}
- Start greeting with "{t['greeting']}"
- End with "{t['sign_off']}"

EMAIL REQUIREMENTS:
1. Reference the valuation report you sent
2. Ask for just 5 minutes to discuss
3. Be LOW PRESSURE - respect their time
4. 2 sentences MAXIMUM
5. NO emojis, NO desperation

Return EXACTLY in this format:
SUBJECT: [your subject line]
BODY:
[your email body]"""

    result = _call_with_retry(prompt)
    if result:
        return _parse_email(result)
    fallback_body = (
        f'{t["greeting"]} [Owner],\n\n'
        f'Wanted to check if you had a chance to review the valuation snapshot. '
        f'Happy to walk through the data in a brief 5-minute call at your '
        f'convenience.\n\n{t["sign_off"]},\n[Your Name]'
    )
    return {
        'subject': f'Quick follow-up - {company}',
        'body': fallback_body
    }


def _parse_email(raw: str) -> Dict[str, str]:
    """Parse raw AI response into subject and body."""
    lines = raw.strip().split('\n')
    subject = ""
    body_lines = []
    in_body = False

    for line in lines:
        line_upper = line.upper().strip()
        if line_upper.startswith('SUBJECT:'):
            subject = line.split(':', 1)[1].strip()
        elif line_upper.startswith('BODY:'):
            in_body = True
        elif in_body:
            body_lines.append(line)

    body = '\n'.join(body_lines).strip()

    # If parsing failed, use the raw response as body
    if not subject and not body:
        return {
            'subject': 'Follow-up from EAI Capital',
            'body': raw.strip()
        }

    return {
        'subject': subject or 'Follow-up from EAI Capital',
        'body': body or raw.strip()
    }


def generate_emails(
    company_name: str,
    industry: str,
    revenue: float,
    median_multiple: float,
    website_summary: str,
    tone: str = 'formal'
) -> Dict[str, Dict[str, str]]:
    """
    Generate 3-email drip campaign in parallel.

    Args:
        company_name: Target company name
        industry: Industry category
        revenue: Target revenue
        median_multiple: Median valuation multiple from peers
        website_summary: Summary from website scraping
        tone: Email tone ('formal', 'friendly', or 'direct')

    Returns:
        Dict with 'hook', 'asset', 'close' keys, each containing 'subject' and 'body'
    """
    tone = tone.lower()
    if tone not in TONE_TEMPLATES:
        tone = 'formal'

    # Run all 3 email generations in parallel
    results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        hook_future = executor.submit(
            _generate_hook_email, company_name, industry, revenue,
            median_multiple, tone, website_summary
        )
        asset_future = executor.submit(_generate_asset_email, company_name, tone)
        close_future = executor.submit(_generate_close_email, company_name, tone)
        futures = {
            hook_future: 'hook',
            asset_future: 'asset',
            close_future: 'close'
        }

        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                print(f"Error generating {key} email: {e}")
                results[key] = {
                    'subject': f'Follow-up - {company_name}',
                    'body': '[Email generation failed. Please write manually.]'
                }

    return results


def generate_upside_bullets(
    company_name: str,
    industry: str,
    target_margin: float,
    peer_median_margin: float,
    website_summary: str
) -> List[str]:
    """
    Generate 3 operational upside bullet points using template + AI.

    Args:
        company_name: Target company name
        industry: Industry category
        target_margin: Target's estimated EBITDA margin
        peer_median_margin: Median margin of peer group
        website_summary: Summary from website scraping

    Returns:
        List of 3 bullet point strings
    """
    margin_gap = (peer_median_margin - target_margin) if (peer_median_margin and target_margin) else 0

    prompt = f"""Generate exactly 3 bullet points about operational upside potential for an M&A target.

COMPANY: {company_name}
INDUSTRY: {industry}
MARGIN GAP VS PEERS: {margin_gap:.1f}% potential improvement opportunity
COMPANY INFO: {website_summary if website_summary else 'Limited information available'}

REQUIREMENTS:
- Each bullet should be exactly 1 sentence
- Focus on REALISTIC, SPECIFIC operational improvements
- Reference concrete areas: pricing, efficiency, synergies, tech upgrades, vendor consolidation
- Professional tone, data-driven language
- NO generic statements, NO hype

Return ONLY the 3 bullets, one per line, starting with "•"."""

    result = _call_with_retry(prompt)

    if result:
        # Parse bullets from response
        bullets = []
        for line in result.strip().split('\n'):
            line = line.strip()
            if line:
                # Remove bullet character if present
                cleaned = line.lstrip('•-*').strip()
                if cleaned:
                    bullets.append(cleaned)

        if len(bullets) >= 3:
            return bullets[:3]
        elif bullets:
            # Pad with template bullets if not enough
            while len(bullets) < 3:
                bullets.append('Additional operational efficiencies identified through platform integration')
            return bullets

    # Fallback template bullets
    margin_bullet = (
        f"Margin improvement potential of {abs(margin_gap):.1f}% through "
        "operational optimization and best practice implementation"
    )
    return [
        margin_bullet,
        "Scale synergies through EAI's platform resources and shared services",
        "Technology modernization to drive efficiency and improve retention"
    ]


def check_api_status() -> bool:
    """Check if Gemini API is available and configured."""
    client = _get_client()
    if not client:
        return False

    try:
        # Simple test call
        response = client.models.generate_content(
            model=MODEL,
            contents="Reply with just the word 'OK'"
        )
        return bool(response.text)
    except Exception:
        return False
