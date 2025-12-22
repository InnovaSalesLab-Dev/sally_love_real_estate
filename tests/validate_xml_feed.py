#!/usr/bin/env python3
"""
Quick XML Feed Validator
========================
Test if we're fetching all MLS listings from BoldTrail XML feed
"""

import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import xml.etree.ElementTree as ET
from src.integrations.boldtrail import BoldTrailClient
from src.config.settings import settings

def normalize_address(address: str) -> str:
    """Normalize address for comparison"""
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

async def main():
    print("=" * 80)
    print("🔍 BOLDTRAIL XML FEED VALIDATOR")
    print("=" * 80)
    print()
    
    # Check config
    print("📋 Configuration:")
    print(f"   Zapier Key: {settings.BOLDTRAIL_ZAPIER_KEY[:20]}..." if settings.BOLDTRAIL_ZAPIER_KEY else "   ❌ Not configured")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print()
    
    if not settings.BOLDTRAIL_ZAPIER_KEY:
        print("❌ ERROR: BOLDTRAIL_ZAPIER_KEY not configured in .env file")
        return
    
    # Initialize client
    client = BoldTrailClient()
    
    # Fetch listings
    print("📡 Fetching listings from XML feed...")
    print(f"   URL: https://api.kvcore.com/export/listings/{settings.BOLDTRAIL_ZAPIER_KEY[:20]}.../10")
    print()
    
    try:
        listings = await client.search_listings_from_xml()
        
        print("=" * 80)
        print("✅ SUCCESS - FEED STATISTICS")
        print("=" * 80)
        print(f"📊 Total listings fetched: {len(listings)}")
        print()
        
        if len(listings) == 0:
            print("⚠️  WARNING: No listings found!")
            print("   This could mean:")
            print("   - No properties are in your BoldTrail CRM")
            print("   - The Zapier key is incorrect")
            print("   - The XML feed is not configured")
            return
        
        # Count by status
        active = sum(1 for l in listings if l.get('status', '').lower() == 'active')
        pending = sum(1 for l in listings if l.get('status', '').lower() in ['pending', 'under contract'])
        sold = sum(1 for l in listings if l.get('status', '').lower() == 'sold')
        
        print("📈 Listings by Status:")
        print(f"   Active: {active}")
        print(f"   Pending: {pending}")
        print(f"   Sold: {sold}")
        print()
        
        # Show sample listings
        print("=" * 80)
        print("📋 SAMPLE LISTINGS (First 5)")
        print("=" * 80)
        for i, listing in enumerate(listings[:5], 1):
            print(f"\n{i}. {listing.get('address', 'N/A')}, {listing.get('city', 'N/A')}")
            print(f"   Price: ${listing.get('price', 0):,.0f}")
            print(f"   Beds/Baths: {listing.get('bedrooms', 0)}/{listing.get('bathrooms', 0)}")
            print(f"   Status: {listing.get('status', 'N/A')}")
            print(f"   Agent: {listing.get('agentName', 'N/A')}")
        
        print()
        print("=" * 80)
        print("🔍 INTERACTIVE SEARCH")
        print("=" * 80)
        print("Enter an address to search (or press Enter to skip):")
        print("Examples:")
        print("  - 17300 SE 91st Lee Avenue")
        print("  - 1738 Augustine Drive")
        print("  - 368 Grand Vista Trail")
        print()
        
        while True:
            search_term = input("🏠 Search address (or 'q' to quit): ").strip()
            
            if not search_term or search_term.lower() == 'q':
                break
            
            # Search for property
            normalized_search = normalize_address(search_term)
            found_listings = []
            
            for listing in listings:
                address = listing.get('address', '')
                city = listing.get('city', '')
                full_address = f"{address}, {city}"
                
                if normalized_search in normalize_address(full_address) or \
                   normalized_search in normalize_address(address):
                    found_listings.append(listing)
            
            print()
            if found_listings:
                print(f"✅ Found {len(found_listings)} matching listing(s):")
                print()
                for i, listing in enumerate(found_listings, 1):
                    print(f"{i}. {listing.get('address', 'N/A')}, {listing.get('city', 'N/A')}, {listing.get('state', 'FL')} {listing.get('zip', '')}")
                    print(f"   MLS #: {listing.get('mlsNumber', 'N/A')}")
                    print(f"   Price: ${listing.get('price', 0):,.0f}")
                    print(f"   Beds/Baths: {listing.get('bedrooms', 0)}/{listing.get('bathrooms', 0)}")
                    print(f"   Property Type: {listing.get('propertyType', 'N/A')}")
                    print(f"   Status: {listing.get('status', 'N/A')}")
                    print(f"   Agent: {listing.get('agentName', 'N/A')} ({listing.get('agentPhone', 'N/A')})")
                    if listing.get('listDate'):
                        print(f"   Listed: {listing.get('listDate', 'N/A')}")
                    if listing.get('status', '').lower() == 'sold' and listing.get('soldDate'):
                        print(f"   Sold: {listing.get('soldDate', 'N/A')}")
                    print()
            else:
                print(f"❌ No listings found for: {search_term}")
                print()
                print("   Try searching by:")
                print("   - Street number and name (e.g., '17300 SE 91st Lee')")
                print("   - Just street name (e.g., 'Augustine Drive')")
                print("   - City name (e.g., 'The Villages')")
                print()
        
        print()
        print("=" * 80)
        print("✅ VALIDATION COMPLETE")
        print("=" * 80)
        print(f"✅ XML Feed is working correctly")
        print(f"✅ Fetched {len(listings)} total listings")
        print(f"✅ Active listings: {active}")
        print()
        print("🎉 Your BoldTrail XML feed integration is working!")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

