#!/usr/bin/env python3
"""
BoldTrail XML Listings Feed - Property Lookup
==============================================
This script fetches all MLS listings from BoldTrail's kvCORE syndication feed
and provides property lookup by address.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get this from: BoldTrail → Lead Engine → Lead Dropbox → Copy "Zapier Key"
BOLDTRAIL_ZAPIER_KEY = "YOUR_ZAPIER_KEY_HERE"

# XML Feed URL (replace {ZAPIER_KEY} with your actual key)
XML_FEED_URL = f"https://api.kvcore.com/export/listings/OTg3NjlhMWU0M2M0MDgzZTIzYmE5YzU0MDYxMjZlNzM6by0y/10"

# Alternative URL formats (try these if above doesn't work):
# OPTION 1: Without the /10 suffix
# XML_FEED_URL = f"https://api.kvcore.com/export/listings/OTg3NjlhMWU0M2M0MDgzZTIzYmE5YzU0MDYxMjZlNzM6by0y"
#
# OPTION 2: With different retention period (7 days)
# XML_FEED_URL = f"https://api.kvcore.com/export/listings/OTg3NjlhMWU0M2M0MDgzZTIzYmE5YzU0MDYxMjZlNzM6by0y/7"

# =============================================================================
# STEP 1: FETCH THE XML FEED
# =============================================================================

def fetch_listings_feed() -> str:
    """
    Fetch the XML listings feed from BoldTrail/kvCORE
    
    Returns:
        str: Raw XML content
    """
    print(f"📡 Fetching listings from BoldTrail XML feed...")
    print(f"🔗 URL: {XML_FEED_URL}")
    
    try:
        response = requests.get(XML_FEED_URL, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched feed")
        print(f"📊 Response size: {len(response.content)} bytes")
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching feed: {e}")
        raise

# =============================================================================
# STEP 2: PARSE THE XML FEED
# =============================================================================

def parse_listings_xml(xml_content: str) -> List[Dict]:
    """
    Parse the XML feed and extract all listings
    
    Args:
        xml_content: Raw XML string
        
    Returns:
        List of listing dictionaries
    """
    print(f"🔍 Parsing XML feed...")
    
    try:
        root = ET.fromstring(xml_content)
        listings = []
        
        # Find all listing elements (adjust tag name based on actual XML structure)
        # Common tag names: <listing>, <property>, <item>, <result>
        for listing_elem in root.findall('.//listing'):
            listing = extract_listing_data(listing_elem)
            if listing:
                listings.append(listing)
        
        print(f"✅ Parsed {len(listings)} listings")
        return listings
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        print("📄 First 500 characters of XML:")
        print(xml_content[:500])
        raise

# =============================================================================
# STEP 3: EXTRACT LISTING DATA
# =============================================================================

def extract_listing_data(listing_elem: ET.Element) -> Optional[Dict]:
    """
    Extract property data from a single listing XML element
    
    Args:
        listing_elem: XML element for one listing
        
    Returns:
        Dictionary with property details
    """
    
    def get_text(tag: str, default: str = "") -> str:
        """Helper to safely get text from XML element"""
        elem = listing_elem.find(tag)
        return elem.text if elem is not None and elem.text else default
    
    def get_number(tag: str, default: float = 0) -> float:
        """Helper to safely get number from XML element"""
        try:
            return float(get_text(tag, "0"))
        except (ValueError, TypeError):
            return default
    
    # Build listing dictionary
    # Adjust field names based on actual XML structure
    listing = {
        # Basic Info
        "address": get_text("address") or get_text("street_address"),
        "city": get_text("city"),
        "state": get_text("state"),
        "zip": get_text("zip") or get_text("postal_code"),
        "full_address": None,  # Will construct below
        
        # Property Details
        "mls_number": get_text("mls_number") or get_text("mls_id") or get_text("listing_id"),
        "price": get_number("price") or get_number("list_price"),
        "bedrooms": get_number("bedrooms") or get_number("beds"),
        "bathrooms": get_number("bathrooms") or get_number("baths"),
        "sqft": get_number("square_feet") or get_number("sqft") or get_number("living_area"),
        "lot_size": get_text("lot_size"),
        "year_built": get_text("year_built"),
        
        # Status
        "status": get_text("status") or get_text("listing_status"),
        "list_date": get_text("list_date") or get_text("listing_date"),
        "sold_date": get_text("sold_date"),
        
        # Property Type
        "property_type": get_text("property_type") or get_text("type"),
        "property_subtype": get_text("property_subtype"),
        
        # Description
        "description": get_text("description") or get_text("remarks"),
        "public_remarks": get_text("public_remarks"),
        
        # Listing Agent
        "agent_id": get_text("agent_id") or get_text("listing_agent_id"),
        "agent_name": get_text("agent_name") or get_text("listing_agent"),
        "agent_email": get_text("agent_email"),
        "agent_phone": get_text("agent_phone") or get_text("agent_direct_phone"),
        "agent_office": get_text("agent_office"),
        
        # Co-Listing Agent (if exists)
        "co_agent_name": get_text("co_agent_name") or get_text("co_listing_agent"),
        "co_agent_phone": get_text("co_agent_phone"),
        
        # Photos
        "photos": [],
        
        # Virtual Tour
        "virtual_tour_url": get_text("virtual_tour") or get_text("virtual_tour_url"),
        
        # Additional
        "listing_office": get_text("listing_office"),
        "mls_area": get_text("mls_area") or get_text("area"),
        "subdivision": get_text("subdivision"),
    }
    
    # Construct full address
    address_parts = [
        listing["address"],
        listing["city"],
        listing["state"],
        listing["zip"]
    ]
    listing["full_address"] = ", ".join([p for p in address_parts if p])
    
    # Extract photos
    photos_elem = listing_elem.find("photos") or listing_elem.find("images")
    if photos_elem:
        for photo in photos_elem.findall("photo") or photos_elem.findall("image"):
            if photo.text:
                listing["photos"].append(photo.text.strip())
    
    # Only return if we have at least an address and price
    if listing["address"] and listing["price"] > 0:
        return listing
    
    return None

# =============================================================================
# STEP 4: SEARCH LISTINGS BY ADDRESS
# =============================================================================

def normalize_address(address: str) -> str:
    """
    Normalize address for comparison
    
    Args:
        address: Raw address string
        
    Returns:
        Normalized address (lowercase, no punctuation)
    """
    return (address.lower()
            .replace(",", "")
            .replace(".", "")
            .replace("street", "st")
            .replace("avenue", "ave")
            .replace("boulevard", "blvd")
            .replace("road", "rd")
            .replace("drive", "dr")
            .replace("lane", "ln")
            .replace("court", "ct")
            .strip())

def search_property_by_address(listings: List[Dict], search_address: str) -> Optional[Dict]:
    """
    Search for a property by address
    
    Args:
        listings: List of all listings
        search_address: Address to search for
        
    Returns:
        Matching listing or None
    """
    normalized_search = normalize_address(search_address)
    
    for listing in listings:
        # Check against full address
        if normalized_search in normalize_address(listing["full_address"]):
            return listing
        
        # Check against street address only
        if normalized_search in normalize_address(listing["address"]):
            return listing
    
    return None

# =============================================================================
# STEP 5: FORMAT FOR VAPI RESPONSE
# =============================================================================

def format_for_vapi(listing: Optional[Dict]) -> Dict:
    """
    Format listing data for Vapi function response
    
    Args:
        listing: Listing dictionary or None
        
    Returns:
        Vapi-compatible response
    """
    if not listing:
        return {
            "found": False,
            "message": "Property not found in current listings"
        }
    
    return {
        "found": True,
        "property": {
            "address": listing["full_address"],
            "street_address": listing["address"],
            "city": listing["city"],
            "state": listing["state"],
            "zip": listing["zip"],
            "mls_number": listing["mls_number"],
            "price": listing["price"],
            "bedrooms": listing["bedrooms"],
            "bathrooms": listing["bathrooms"],
            "sqft": listing["sqft"],
            "status": listing["status"],
            "property_type": listing["property_type"],
            "description": listing["description"][:500] if listing["description"] else "",  # Truncate for AI
            "photos": listing["photos"][:5],  # First 5 photos
            "virtual_tour": listing["virtual_tour_url"]
        },
        "listing_agent": {
            "id": listing["agent_id"],
            "name": listing["agent_name"],
            "phone": listing["agent_phone"],
            "email": listing["agent_email"],
            "office": listing["agent_office"]
        },
        "co_listing_agent": {
            "name": listing["co_agent_name"],
            "phone": listing["co_agent_phone"]
        } if listing["co_agent_name"] else None
    }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BOLDTRAIL XML LISTINGS FEED - PROPERTY LOOKUP")
    print("=" * 70)
    print()
    
    # Check if Zapier key is configured
    if BOLDTRAIL_ZAPIER_KEY == "YOUR_ZAPIER_KEY_HERE":
        print("❌ ERROR: Please configure your BOLDTRAIL_ZAPIER_KEY")
        print()
        print("📋 Instructions:")
        print("1. Log into BoldTrail")
        print("2. Go to: Lead Engine → Lead Dropbox")
        print("3. Copy the 'Zapier Key'")
        print("4. Replace 'YOUR_ZAPIER_KEY_HERE' in this script")
        print()
        exit(1)
    
    try:
        # Fetch and parse listings
        xml_content = fetch_listings_feed()
        listings = parse_listings_xml(xml_content)
        
        print()
        print("=" * 70)
        print("LISTINGS SUMMARY")
        print("=" * 70)
        print(f"Total listings found: {len(listings)}")
        
        if len(listings) > 0:
            # Show sample listings
            print()
            print("📋 Sample listings:")
            for i, listing in enumerate(listings[:5], 1):
                print(f"\n{i}. {listing['full_address']}")
                print(f"   Price: ${listing['price']:,.0f}")
                print(f"   Beds/Baths: {listing['bedrooms']}/{listing['bathrooms']}")
                print(f"   Status: {listing['status']}")
                print(f"   Agent: {listing['agent_name']}")
            
            # Test search
            print()
            print("=" * 70)
            print("TEST SEARCH")
            print("=" * 70)
            
            test_address = listings[0]["address"]
            print(f"🔍 Searching for: {test_address}")
            
            result = search_property_by_address(listings, test_address)
            vapi_response = format_for_vapi(result)
            
            print()
            print("✅ Vapi Response Format:")
            print(json.dumps(vapi_response, indent=2))
            
            # Save to file for reference
            with open("boldtrail_listings.json", "w") as f:
                json.dump(listings, f, indent=2)
            print()
            print("💾 All listings saved to: boldtrail_listings.json")
        
        else:
            print()
            print("⚠️  No listings found!")
            print()
            print("Possible reasons:")
            print("1. No listings are currently synced to this BoldTrail account")
            print("2. The XML feed URL format is incorrect")
            print("3. The Zapier key is invalid")
            print()
            print("📄 Raw XML response (first 1000 chars):")
            print(xml_content[:1000])
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)