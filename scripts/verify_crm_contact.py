#!/usr/bin/env python3
"""
Verify that a specific contact exists in BoldTrail CRM
"""
import asyncio
import sys
from src.integrations.boldtrail import BoldTrailClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Check if contact 21780 exists and show its details"""
    
    print("=" * 60)
    print("BoldTrail CRM Contact Verification")
    print("=" * 60)
    print()
    
    # Initialize BoldTrail client
    crm_client = BoldTrailClient()
    
    # Contact ID from your SMS notification
    contact_id = "21780"
    
    print(f"🔍 Checking for contact ID: {contact_id}")
    print()
    
    try:
        # Get contact details
        contact = await crm_client.get_contact(contact_id)
        
        if contact:
            print("✅ CONTACT FOUND IN CRM!")
            print()
            print(f"📧 Email: {contact.get('email', 'N/A')}")
            print(f"👤 Name: {contact.get('firstName', '')} {contact.get('lastName', '')}")
            print(f"📱 Phone: {contact.get('cellPhone1', 'N/A')}")
            print(f"🏷️  Type: {contact.get('dealType', 'N/A')}")
            print(f"📍 Source: {contact.get('source', 'N/A')}")
            print(f"📅 Created: {contact.get('createdAt', 'N/A')}")
            print(f"🆔 Contact ID: {contact.get('id', 'N/A')}")
            print()
            print("=" * 60)
            print("✅ IMPLEMENTATION IS WORKING!")
            print("=" * 60)
            return 0
        else:
            print("❌ Contact not found")
            return 1
            
    except Exception as e:
        print(f"❌ Error checking contact: {str(e)}")
        logger.exception("Error in verification")
        return 1
    
    print()
    print("Now checking by email...")
    print()
    
    try:
        # Also search by email
        contacts = await crm_client.search_contacts(email="hamsimirza1@gmail.com")
        
        if contacts:
            print(f"✅ Found {len(contacts)} contact(s) with this email:")
            for contact in contacts:
                print(f"  - ID: {contact.get('id')}, Name: {contact.get('firstName')} {contact.get('lastName')}")
        else:
            print("No contacts found with this email")
            
    except Exception as e:
        print(f"Error searching by email: {str(e)}")
    
    print()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

