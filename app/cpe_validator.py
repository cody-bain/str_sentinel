import requests
import logging
import os
import time
from rapidfuzz import fuzz, process
from dotenv import load_dotenv

# Some code snippets developed with assistance from generative AI tools. All AI-generated content was reviewed, revised, and adapted to meet STR Sentinel requirements.
'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''
# Load environment variables from .env file
load_dotenv('/app/.env')

# NVD API Configuration
NVD_API_KEY = os.getenv('NVD_API_KEY')
NVD_CPE_API = "https://services.nvd.nist.gov/rest/json/cpes/2.0"

# Local CPE database (loaded from file)
LOCAL_CPE_DB = None
LOCAL_CPE_FILE = "/app/shared/cpe_dictionary.json"

# In-memory cache to avoid repeated API calls for the same vendor
cpe_cache = {}


def load_local_cpe_database():
    """
    Load local CPE database from file into memory.
    Only loads once - subsequent calls return cached version.
    
    Returns:
        List of CPE dictionaries, or None if file doesn't exist
    """
    global LOCAL_CPE_DB
    
    if LOCAL_CPE_DB is not None:
        return LOCAL_CPE_DB
    
    if not os.path.exists(LOCAL_CPE_FILE):
        logging.error(f"[CPE Database] Local CPE database not found at {LOCAL_CPE_FILE}")
        logging.error(f"[CPE Database] The cpe_dictionary.json file is required for operation")
        return None
    
    try:
        import json
        logging.info(f"[CPE Database] Loading local CPE database from {LOCAL_CPE_FILE}...")
        with open(LOCAL_CPE_FILE, 'r') as f:
            data = json.load(f)
        
        LOCAL_CPE_DB = data.get('cpes', [])
        download_date = data.get('download_date', 'unknown')
        
        logging.info(f"[CPE Database] Loaded {len(LOCAL_CPE_DB):,} CPEs (downloaded: {download_date})")
        return LOCAL_CPE_DB
        
    except Exception as e:
        logging.error(f"[CPE Database] Error loading local database: {e}")
        return None


def search_local_cpe_database(vendor, product=None):
    """
    Search local CPE database for vendor/product matches.
    Much faster than API calls - searches in-memory.
    
    Args:
        vendor: Vendor name (e.g., "apple", "hikvision")
        product: Optional product name for filtering
    
    Returns:
        List of CPE dictionaries matching the vendor/product
    """
    db = load_local_cpe_database()
    if db is None:
        return None
    
    vendor_lower = vendor.lower()
    product_lower = product.lower() if product else None
    
    # Normalize underscores/hyphens for flexible matching
    if product_lower:
        product_normalized = product_lower.replace('_', '-')
    
    logging.debug(f"[CPE Database] Searching for vendor='{vendor_lower}', product='{product_lower}'")
    
    matches = []
    checked = 0
    for cpe_entry in db:
        cpe_name = cpe_entry.get('cpeName', '')
        checked += 1
        
        # Parse CPE string: cpe:2.3:type:vendor:product:version:...
        parts = cpe_name.split(':')
        if len(parts) < 5:
            continue
        
        cpe_vendor = parts[3].lower()
        cpe_product = parts[4].lower()
        
        # Match vendor
        if vendor_lower in cpe_vendor or cpe_vendor in vendor_lower:
            # If product specified, filter by product too (normalize for comparison)
            if product_lower:
                cpe_product_normalized = cpe_product.replace('_', '-')
                if product_normalized in cpe_product_normalized or cpe_product_normalized in product_normalized:
                    matches.append(cpe_entry)
            else:
                matches.append(cpe_entry)
    
    logging.info(f"[CPE Database] Checked {checked} CPEs, found {len(matches)} matches")
    return matches


def query_nvd_cpe_api(vendor, product=None):
    """
    Query NVD CPE API to get all official CPE strings for a vendor/product.
    Returns list of CPE dictionaries with cpeName, titles, etc.
    
    Args:
        vendor: Vendor name (e.g., "hikvision", "openbsd")
        product: Optional product name for more specific search
    
    Returns:
        List of CPE dictionaries from NVD API
    """
    # Check cache first
    cache_key = f"{vendor}:{product}" if product else vendor
    if cache_key in cpe_cache:
        logging.debug(f"[CPE Cache] Using cached results for {cache_key}")
        return cpe_cache[cache_key]
    
    # Try local database first (much faster)
    local_results = search_local_cpe_database(vendor, product)
    if local_results is not None:
        logging.info(f"[CPE Database] Found {len(local_results)} CPE entries for {vendor} in local database")
        cpe_cache[cache_key] = local_results
        return local_results
    
    # Fall back to API if local database not available
    logging.info(f"[NVD API] Falling back to API query for: {vendor}")
    
    # Build search query - start with just vendor for broader results
    keyword = vendor  # Don't include product in keyword search to get all vendor CPEs
    
    headers = {}
    if NVD_API_KEY:
        headers['apiKey'] = NVD_API_KEY
    
    params = {
        'keywordSearch': keyword,
        'resultsPerPage': 100,  # Max per page
        'startIndex': 0
    }
    
    try:
        logging.info(f"[NVD API] Querying CPE database for: {keyword}")
        
        all_cpe_list = []
        start_index = 0
        
        while True:
            params['startIndex'] = start_index
            response = requests.get(NVD_CPE_API, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                total_results = data.get('totalResults', 0)
                
                # Extract CPE information from this page
                for item in products:
                    cpe_data = item.get('cpe', {})
                    all_cpe_list.append({
                        'cpeName': cpe_data.get('cpeName'),
                        'cpeNameId': cpe_data.get('cpeNameId'),
                        'titles': cpe_data.get('titles', []),
                        'refs': cpe_data.get('refs', []),
                        'deprecated': cpe_data.get('deprecated', False)
                    })
                
                # Log progress
                if start_index == 0:
                    logging.info(f"[NVD API] Found {total_results} total CPE entries for {keyword}, fetching in pages of 100...")
                else:
                    logging.debug(f"[NVD API] Fetched {len(all_cpe_list)}/{total_results} CPEs...")
                
                # Check if we've fetched all results
                if len(all_cpe_list) >= total_results or len(products) == 0:
                    break
                
                # Move to next page
                start_index += 100
                
                # Respect rate limits (without key: 5 requests per 30 seconds, with key: 50 per 30 seconds)
                if not NVD_API_KEY:
                    time.sleep(6)  # Conservative rate limiting
                else:
                    time.sleep(0.6)  # Small delay even with API key
            else:
                logging.error(f"[NVD API] Query failed with status {response.status_code}")
                break
        
        # Cache results
        cpe_cache[cache_key] = all_cpe_list
        logging.info(f"[NVD API] Retrieved {len(all_cpe_list)} total CPE entries for {keyword}")
        
        return all_cpe_list
            
    except Exception as e:
        logging.error(f"[NVD API] Query failed: {e}")
        return []


def fuzzy_match_cpe(detected_cpe, official_cpe_list):
    """
    Fuzzy match a detected CPE against official NVD CPE strings.
    
    Args:
        detected_cpe: The CPE string we generated (e.g., "cpe:2.3:h:hikvision:ds_2cd2042wd_i:*...")
        official_cpe_list: List of official CPE dictionaries from NVD API
    
    Returns:
        Best matching official CPE string, or None if no good match found
    """
    if not official_cpe_list:
        return None
    
    # Extract just the CPE names for matching (include deprecated - they can still have CVEs)
    official_cpe_names = [cpe['cpeName'] for cpe in official_cpe_list]
    
    if not official_cpe_names:
        return None
    
    # Parse detected CPE components (vendor:product:version)
    try:
        parts = detected_cpe.split(':')
        detected_vendor = parts[3]
        detected_product = parts[4]
        detected_version = parts[5]  # Version is single field now (e.g., "7.6p1")
    except IndexError:
        logging.error(f"[CPE Validator] Malformed CPE string: {detected_cpe}")
        return None
    
    # First pass: exact vendor + fuzzy product match
    vendor_matches = [
        cpe for cpe in official_cpe_names 
        if f":{detected_vendor}:" in cpe.lower()
    ]
    
    if not vendor_matches:
        # Try fuzzy vendor matching
        logging.debug(f"[CPE Validator] No exact vendor match for '{detected_vendor}', trying fuzzy match")
        vendor_matches = official_cpe_names
    
    # Second pass: match product name with fuzzy matching
    product_scores = []
    for cpe in vendor_matches:
        try:
            cpe_parts = cpe.split(':')
            cpe_vendor = cpe_parts[3]
            cpe_product = cpe_parts[4]
            cpe_version = cpe_parts[5]
            
            # Normalize underscores to hyphens for comparison
            detected_product_normalized = detected_product.replace('_', '-')
            cpe_product_normalized = cpe_product.replace('_', '-')
            
            # Calculate product similarity
            product_similarity = fuzz.ratio(detected_product_normalized.lower(), cpe_product_normalized.lower())
            
            # Bonus points for version match
            version_bonus = 0
            if detected_version != '*' and cpe_version not in ['*', '-']:
                # Check if versions match (handle p1 suffix directly, no colon conversion needed)
                detected_ver_clean = detected_version.lower()
                cpe_ver_clean = cpe_version.lower()
                
                if detected_ver_clean == cpe_ver_clean:
                    version_bonus = 40  # Big bonus for exact version match
                elif detected_ver_clean.split('p')[0] == cpe_ver_clean.split('p')[0]:
                    version_bonus = 20  # Smaller bonus for matching major.minor
            
            total_score = product_similarity + version_bonus
            product_scores.append((cpe, total_score, cpe_version))
            
        except IndexError:
            continue
    
    if not product_scores:
        return None
    
    # Sort by score (highest first)
    product_scores.sort(key=lambda x: x[1], reverse=True)
    best_match = product_scores[0]
    
    # If we have a version, strongly prioritize actual version matches
    if detected_version != '*':
        # Find CPEs where the version actually matched (got version bonus)
        detected_ver_clean = detected_version.lower()
        version_matches = []
        
        for cpe, score, cpe_version in product_scores:
            if cpe_version not in ['*', '-'] and score >= 65:
                cpe_ver_clean = cpe_version.lower()
                # Check if this CPE actually matches our version
                if detected_ver_clean == cpe_ver_clean or detected_ver_clean.split('p')[0] == cpe_ver_clean.split('p')[0]:
                    version_matches.append((cpe, score, cpe_version))
        
        if version_matches:
            # Sort version matches by score
            version_matches.sort(key=lambda x: x[1], reverse=True)
            best_match = version_matches[0]
            logging.info(f"[CPE Validator] Version-matched CPE (score: {best_match[1]}): {best_match[0]}")
            return best_match[0]
        else:
            # No version match found - likely NVD pagination issue
            # Find best product match and modify to include our detected version
            if best_match[1] >= 65:
                try:
                    parts = best_match[0].split(':')
                    # Replace version field (index 5) with detected version
                    # Also need to remove any trailing fields after version and rebuild
                    constructed_parts = parts[:5] + [detected_version] + parts[6:]
                    # Ensure we have exactly 13 parts (CPE 2.3 format)
                    while len(constructed_parts) < 13:
                        constructed_parts.append('*')
                    constructed_cpe = ':'.join(constructed_parts[:13])
                    logging.info(f"[CPE Validator] No exact version in NVD, constructing CPE with detected version: {constructed_cpe}")
                    return constructed_cpe
                except IndexError:
                    pass
    
    # Return best match if above threshold
    if best_match[1] >= 65:  # Lowered threshold from 70 to 65
        logging.info(f"[CPE Validator] Best match found (score: {best_match[1]}): {best_match[0]}")
        return best_match[0]
    
    logging.warning(f"[CPE Validator] No good match found for {detected_cpe} (best score: {best_match[1]})")
    return None


def validate_cpe(detected_cpe):
    """
    Main validation function: queries NVD API and fuzzy matches against official CPEs.
    
    Args:
        detected_cpe: CPE string generated by our fingerprinting
    
    Returns:
        Tuple of (cpe_string, validation_status) where validation_status is:
        - 'validated': Found exact or fuzzy match in NVD
        - 'unvalidated': Could not validate against NVD
    """
    try:
        # Parse vendor and product from detected CPE
        parts = detected_cpe.split(':')
        vendor = parts[3]
        product = parts[4]
    except IndexError:
        logging.error(f"[CPE Validator] Cannot parse CPE: {detected_cpe}")
        return detected_cpe, 'unvalidated'
    
    # Query NVD API for this vendor
    official_cpes = query_nvd_cpe_api(vendor, product)
    
    if not official_cpes:
        logging.warning(f"[CPE Validator] No official CPEs found for {vendor}")
        return detected_cpe, 'unvalidated'
    
    # Fuzzy match against official CPEs
    logging.info(f"[CPE Validator] Fuzzy matching {detected_cpe} against {len(official_cpes)} official CPEs")
    validated_cpe = fuzzy_match_cpe(detected_cpe, official_cpes)
    
    if validated_cpe:
        logging.info(f"[CPE Validator] Fuzzy match successful: {validated_cpe}")
        return validated_cpe, 'validated'
    else:
        logging.warning(f"[CPE Validator] Fuzzy match failed, returning original CPE")
        return detected_cpe, 'unvalidated'
