"""
AI-powered guest recommendations using Google Gemini.
Generates vacation-appropriate privacy advice for AirBnB/VRBO guests.
"""

'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''

import os
import json
import re
import logging
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = 'gemini-3-flash-preview'
GENERATION_CONFIG = types.GenerateContentConfig(
    temperature=0.7,
    top_p=0.95,
    max_output_tokens=2048,  # Increased to ensure complete responses
    response_mime_type='application/json'
)

# In-memory cache for recommendations
_recommendation_cache = {}

# Retry configuration
MAX_RETRIES = 2  # Will try up to 3 times total (initial + 2 retries)

# Lazy-initialized Gemini client
_client = None


def _get_client():
    """
    Lazy-load the Gemini client.
    Only initializes when first needed, allowing .env to load first.
    """
    global _client
    if _client is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment")
            raise ValueError("GEMINI_API_KEY environment variable is required")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_bulk_recommendations(vulnerabilities):
    """
    Generate AI recommendations for multiple vulnerabilities.
    
    Args:
        vulnerabilities: List of dicts with keys: cve_id, description, cvss_severity, 
                        device_vendor, device_model, device_ip
    
    Returns:
        Dict mapping CVE IDs to recommendation objects (or None if generation failed)
    """
    if not vulnerabilities:
        return {}
    
    results = {}
    logger.info(f"[AI] Generating recommendations for {len(vulnerabilities)} vulnerabilities")
    
    for vuln in vulnerabilities:
        cve_id = vuln.get('cve_id', 'UNKNOWN')
        try:
            recommendation = _generate_single_recommendation(vuln)
            results[cve_id] = recommendation
            
            if recommendation:
                logger.info(f"[AI] ✓ {cve_id}: Successfully generated recommendation")
            else:
                logger.warning(f"[AI] ✗ {cve_id}: Failed to generate recommendation after retries")
                
        except Exception as e:
            logger.error(f"[AI] Error generating recommendation for {cve_id}: {e}")
            results[cve_id] = None
    
    return results


def _generate_single_recommendation(vulnerability):
    """
    Generate a single recommendation with retry logic.
    Returns None if all attempts fail.
    """
    cve_id = vulnerability.get('cve_id', 'UNKNOWN')
    severity = vulnerability.get('cvss_severity', 'UNKNOWN')
    vendor = vulnerability.get('device_vendor', 'Unknown')
    
    # Check cache first
    cache_key = f"{cve_id}_{severity}_{vendor}"
    if cache_key in _recommendation_cache:
        logger.info(f"[AI] Cache hit for {cve_id}")
        return _recommendation_cache[cache_key]
    
    # Try up to MAX_RETRIES + 1 times
    for attempt in range(MAX_RETRIES + 1):
        try:
            if attempt > 0:
                logger.info(f"[AI] Retry {attempt}/{MAX_RETRIES} for {cve_id}")
            
            recommendation = _call_gemini_api(vulnerability)
            
            if recommendation:
                # Cache successful result
                _recommendation_cache[cache_key] = recommendation
                return recommendation
            else:
                logger.warning(f"[AI] Attempt {attempt + 1} failed validation for {cve_id}")
                
        except Exception as e:
            logger.error(f"[AI] Attempt {attempt + 1} error for {cve_id}: {e}")
            if attempt == MAX_RETRIES:
                return None
    
    # All retries exhausted
    return None


def _call_gemini_api(vulnerability):
    """
    Make API call to Gemini and parse response.
    Returns validated recommendation dict or None.
    """
    cve_id = vulnerability.get('cve_id', 'UNKNOWN')
    description = vulnerability.get('description', 'No description available')
    severity = vulnerability.get('cvss_severity', 'UNKNOWN')
    vendor = vulnerability.get('device_vendor', 'Unknown')
    model = vulnerability.get('device_model', 'Unknown')
    device_ip = vulnerability.get('device_ip', 'Unknown')
    
    # Build concise, focused prompt
    prompt = _build_prompt(cve_id, description, severity, vendor, model, device_ip)
    
    try:
        # Call Gemini API
        client = _get_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=GENERATION_CONFIG
        )
        
        # Extract response text
        if not response or not response.text:
            logger.error(f"[AI] Empty response from Gemini for {cve_id}")
            return None
        
        response_text = response.text.strip()
        
        # Parse and validate JSON response
        recommendation = _parse_and_validate_response(response_text, cve_id)
        return recommendation
        
    except Exception as e:
        logger.error(f"[AI] Gemini API error for {cve_id}: {e}")
        return None


def _build_prompt(cve_id, description, severity, vendor, model, device_ip):
    """
    Build a concise, token-efficient prompt for Gemini.
    """
    # Truncate description to save tokens
    desc_short = description[:200] if len(description) > 200 else description
    
    prompt = f"""You are a cybersecurity advisor for vacation rental guests (AirBnB/VRBO).

CONTEXT:
- Guest is staying temporarily at vacation rental
- Guest CANNOT modify/fix devices (not their property)
- Guest needs BEHAVIOR advice for privacy protection
- Audience: Non-technical vacationers, not IT professionals

VULNERABILITY:
CVE: {cve_id}
Severity: {severity}
Device: {vendor} {model} ({device_ip})
Issue: {desc_short}

TASK:
Provide vacation-appropriate privacy advice in JSON format.

RULES:
- DO: Advise on activities to avoid (banking, work emails, etc)
- DO: Suggest privacy protections (VPN, cellular data, HTTPS)
- DO: Explain real risks in simple terms
- DON'T: Tell guests to update/patch devices
- DON'T: Tell guests to contact administrators
- DON'T: Give technical device management tasks

REQUIRED OUTPUT FORMAT (valid JSON only):
{{
  "summary": "One sentence explaining the privacy risk for a guest",
  "immediate_actions": [
    "Action 1 - specific behavior to adopt",
    "Action 2 - specific behavior to adopt",
    "Action 3 - specific behavior to adopt"
  ],
  "best_practices": [
    "Practice 1 - ongoing privacy habit",
    "Practice 2 - ongoing privacy habit"
  ],
  "risk_explanation": "2-3 sentences explaining what could happen and why it matters to a vacationer"
}}

Generate complete JSON response with ALL fields filled:"""
    
    return prompt


def _parse_and_validate_response(response_text, cve_id):
    """
    Parse JSON response and validate all required fields are present.
    Returns validated dict or None if validation fails.
    """
    try:
        # Remove markdown code block formatting if present
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```'):
            # Extract content between ```json and ```
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
            if match:
                cleaned_text = match.group(1)
            else:
                # Try removing just the backticks
                cleaned_text = re.sub(r'```(?:json)?', '', cleaned_text).strip()
        
        # Attempt to parse JSON
        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            # Try auto-completion for truncated JSON
            logger.warning(f"[AI] JSON parse error for {cve_id}, attempting auto-complete: {e}")
            completed_text = _autocomplete_json(cleaned_text)
            data = json.loads(completed_text)
        
        # Validate required fields
        required_fields = ['summary', 'immediate_actions', 'best_practices', 'risk_explanation']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.error(f"[AI] {cve_id} missing required fields: {missing_fields}")
            _save_debug_output(cve_id, response_text, "missing_fields")
            return None
        
        # Validate field types and content
        if not isinstance(data.get('summary'), str) or not data['summary'].strip():
            logger.error(f"[AI] {cve_id} has invalid summary field")
            return None
        
        if not isinstance(data.get('immediate_actions'), list) or len(data['immediate_actions']) == 0:
            logger.error(f"[AI] {cve_id} has invalid or empty immediate_actions")
            return None
        
        if not isinstance(data.get('best_practices'), list) or len(data['best_practices']) == 0:
            logger.error(f"[AI] {cve_id} has invalid or empty best_practices")
            return None
        
        if not isinstance(data.get('risk_explanation'), str) or not data['risk_explanation'].strip():
            logger.error(f"[AI] {cve_id} has invalid risk_explanation field")
            return None
        
        # All validation passed
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"[AI] Could not parse JSON for {cve_id}: {e}")
        _save_debug_output(cve_id, response_text, "json_error")
        return None
    except Exception as e:
        logger.error(f"[AI] Validation error for {cve_id}: {e}")
        return None


def _autocomplete_json(incomplete_json):
    """
    Attempt to auto-complete truncated JSON by adding missing closing characters.
    """
    text = incomplete_json.strip()
    
    # Count open/close characters
    open_braces = text.count('{')
    close_braces = text.count('}')
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    
    # Add missing closing brackets
    while open_brackets > close_brackets:
        # Check if we're in a string context
        if text.rstrip()[-1] not in [']', '}', '"']:
            text += '"'
        text += ']'
        close_brackets += 1
    
    # Add missing closing braces
    while open_braces > close_braces:
        text += '}'
        close_braces += 1
    
    return text


def _save_debug_output(cve_id, response_text, error_type):
    """
    Save problematic responses for debugging.
    """
    try:
        debug_file = f"/tmp/gemini_response_{cve_id}_{error_type}.txt"
        with open(debug_file, 'w') as f:
            f.write(response_text)
        logger.info(f"[AI] Debug output saved to {debug_file}")
    except Exception as e:
        logger.error(f"[AI] Could not save debug output: {e}")


def clear_cache():
    """Clear the recommendation cache."""
    global _recommendation_cache
    _recommendation_cache = {}
    logger.info("[AI] Cache cleared")
