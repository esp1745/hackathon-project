#!/usr/bin/env python3
"""
Script to upload the CSV dataset to the RAG system
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_csv_dataset():
    """Upload the CSV dataset to the RAG system"""
    
    csv_file = "HackathonInternalKnowledgeBase.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file '{csv_file}' not found!")
        return False
    
    print(f"📁 Uploading CSV dataset: {csv_file}")
    
    try:
        # Upload the CSV file
        with open(csv_file, 'rb') as f:
            files = {"files": (csv_file, f, "text/csv")}
            response = requests.post(
                "http://localhost:8000/api/v1/upload-documents",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV dataset uploaded successfully!")
            print(f"   Files processed: {result['files_processed']}")
            print(f"   Documents added: {result['documents_added']}")
            
            if result.get('errors'):
                print("   Errors:", result['errors'])
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return False

def test_rag_with_csv():
    """Test RAG functionality with the uploaded CSV data"""
    
    print("\n🧪 Testing RAG functionality with CSV data...")
    
    test_queries = [
        "How many properties are in the dataset?",
        "What is the average rent per square foot?",
        "Show me properties by Jack Sparrow",
        "What properties are available at 345 Seventh Avenue?",
        "What are the different floor types in the dataset?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat",
                json={"message": query, "conversation_id": None},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Response: {result['message'][:200]}...")
                if result.get('context_used'):
                    print("   ✅ RAG context was used")
                else:
                    print("   ⚠️  No RAG context used")
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Query error: {str(e)}")

def main():
    """Main function"""
    print("🚀 CSV Dataset Upload Script")
    print("=" * 40)
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code != 200:
            print("❌ Server is not running. Please start the server first:")
            print("   python main.py")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python main.py")
        return
    
    print("✅ Server is running")
    
    # Upload CSV dataset
    if upload_csv_dataset():
        print("\n✅ CSV dataset uploaded successfully!")
        
        # Test RAG functionality
        test_rag_with_csv()
        
        print("\n🎉 Setup complete!")
        print("You can now ask questions about the real estate dataset:")
        print("   - 'How many properties are available?'")
        print("   - 'Show me properties by [broker name]'")
        print("   - 'What properties are at [address]?'")
        print("   - 'What is the average rent?'")
        print("\n🌐 Web Interface: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
    else:
        print("\n❌ Failed to upload CSV dataset")

if __name__ == "__main__":
    main() 