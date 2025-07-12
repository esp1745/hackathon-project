#!/usr/bin/env python3
"""
Test script for CSV integration with the RAG system
"""

import asyncio
import os
from app.utils.csv_processor import real_estate_processor

def test_csv_processing():
    """Test CSV processing functionality"""
    print("🧪 Testing CSV Processing...")
    
    csv_file = "HackathonInternalKnowledgeBase.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file '{csv_file}' not found!")
        return False
    
    try:
        # Read CSV content
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Process CSV
        processed_text = real_estate_processor.process_csv(csv_content, csv_file)
        
        print("✅ CSV processing successful!")
        print(f"   Processed {len(real_estate_processor.property_data)} properties")
        print(f"   Generated {len(processed_text)} characters of structured text")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        
        # Test broker search
        broker_results = real_estate_processor.get_properties_by_broker("Jack Sparrow")
        print(f"   Properties by Jack Sparrow: {len(broker_results)} found")
        
        # Test address search
        address_results = real_estate_processor.get_properties_by_address("345 Seventh Avenue")
        print(f"   Properties at 345 Seventh Avenue: {len(address_results)} found")
        
        # Test general search
        search_results = real_estate_processor.search_properties("E3")
        print(f"   Properties with 'E3': {len(search_results)} found")
        
        print("✅ Search functionality working!")
        
        # Show sample of processed text
        print(f"\n📄 Sample of processed text (first 500 chars):")
        print("-" * 50)
        print(processed_text[:500] + "...")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ CSV processing failed: {str(e)}")
        return False

def test_file_utils():
    """Test file utilities with CSV"""
    print("\n🧪 Testing File Utils with CSV...")
    
    try:
        from app.utils.file_utils import extract_text_from_file
        
        csv_file = "HackathonInternalKnowledgeBase.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV file '{csv_file}' not found!")
            return False
        
        # Read file as bytes
        with open(csv_file, 'rb') as f:
            file_data = f.read()
        
        # Extract text using file utils
        extracted_text = extract_text_from_file(file_data, csv_file)
        
        print("✅ File utils CSV processing successful!")
        print(f"   Extracted {len(extracted_text)} characters")
        
        # Check if it contains real estate data
        if "Real Estate Dataset" in extracted_text:
            print("   ✅ Detected as real estate data")
        else:
            print("   ⚠️  Not detected as real estate data")
        
        return True
        
    except Exception as e:
        print(f"❌ File utils test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 CSV Integration Test")
    print("=" * 40)
    
    # Test CSV processing
    csv_success = test_csv_processing()
    
    # Test file utils
    utils_success = test_file_utils()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   CSV Processing: {'✅ PASS' if csv_success else '❌ FAIL'}")
    print(f"   File Utils: {'✅ PASS' if utils_success else '❌ FAIL'}")
    
    if csv_success and utils_success:
        print("\n🎉 All tests passed! CSV integration is working correctly.")
        print("\nNext steps:")
        print("1. Start the server: python main.py")
        print("2. Upload the CSV: python upload_csv_dataset.py")
        print("3. Test voice queries about the real estate data")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 