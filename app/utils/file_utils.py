"""
File utility functions for document processing and validation
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file type based on extension
    
    Args:
        filename: File name
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if valid, False otherwise
    """
    if not filename:
        return False
    
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in allowed_extensions


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return file_size <= max_size


def get_file_hash(file_data: bytes) -> str:
    """
    Calculate file hash
    
    Args:
        file_data: File data
        
    Returns:
        File hash
    """
    return hashlib.md5(file_data).hexdigest()


def extract_text_from_file(file_data: bytes, filename: str) -> str:
    """
    Extract text from file based on type
    
    Args:
        file_data: File data
        filename: File name
        
    Returns:
        Extracted text
    """
    try:
        # Basic text extraction (in production, use proper parsers)
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension in ['.txt', '.md']:
            return file_data.decode('utf-8')
        elif file_extension == '.json':
            # Try to extract text from JSON
            data = json.loads(file_data.decode('utf-8'))
            return json.dumps(data, indent=2)
        elif file_extension == '.csv':
            # Process CSV file with specialized processor for real estate data
            csv_content = file_data.decode('utf-8')
            
            # Check if this looks like real estate data
            if 'Property Address' in csv_content or 'Rent' in csv_content or 'Size' in csv_content:
                from app.utils.csv_processor import real_estate_processor
                return real_estate_processor.process_csv(csv_content, filename)
            else:
                return process_csv_file(csv_content, filename)
        else:
            # Try to decode as text
            return file_data.decode('utf-8')
            
    except UnicodeDecodeError:
        raise Exception(f"Could not decode file as text: {filename}")
    except Exception as e:
        raise Exception(f"Failed to extract text from {filename}: {str(e)}")


def process_csv_file(csv_content: str, filename: str) -> str:
    """
    Process CSV file and convert to structured text
    
    Args:
        csv_content: CSV file content
        filename: CSV filename
        
    Returns:
        Structured text representation
    """
    try:
        import csv
        from io import StringIO
        
        # Parse CSV
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        # Get column names
        fieldnames = csv_reader.fieldnames
        if not fieldnames:
            return csv_content
        
        # Process each row
        processed_rows = []
        for i, row in enumerate(csv_reader, 1):
            # Create a structured description of each row
            row_text = f"Record {i}:\n"
            for field, value in row.items():
                if value and value.strip():  # Skip empty values
                    row_text += f"  {field}: {value}\n"
            processed_rows.append(row_text)
        
        # Create summary
        total_records = len(processed_rows)
        summary = f"CSV Dataset: {filename}\n"
        summary += f"Total Records: {total_records}\n"
        summary += f"Columns: {', '.join(fieldnames)}\n\n"
        
        # Add all processed rows
        full_content = summary + "\n".join(processed_rows)
        
        return full_content
        
    except Exception as e:
        raise Exception(f"Failed to process CSV file {filename}: {str(e)}")


def save_file(file_data: bytes, filename: str, directory: str) -> str:
    """
    Save file to directory
    
    Args:
        file_data: File data
        filename: File name
        directory: Target directory
        
    Returns:
        Full path to saved file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate unique filename if needed
        base_name, extension = os.path.splitext(filename)
        counter = 1
        final_filename = filename
        
        while os.path.exists(os.path.join(directory, final_filename)):
            final_filename = f"{base_name}_{counter}{extension}"
            counter += 1
        
        # Save file
        file_path = os.path.join(directory, final_filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return file_path
        
    except Exception as e:
        raise Exception(f"Failed to save file {filename}: {str(e)}")


def get_file_info(file_data: bytes, filename: str) -> Dict[str, Any]:
    """
    Get file information
    
    Args:
        file_data: File data
        filename: File name
        
    Returns:
        File information dictionary
    """
    return {
        "filename": filename,
        "size": len(file_data),
        "hash": get_file_hash(file_data),
        "mime_type": mimetypes.guess_type(filename)[0],
        "extension": os.path.splitext(filename)[1].lower()
    }


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Clean up old files in directory
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
        
    Returns:
        Number of files deleted
    """
    import time
    
    try:
        if not os.path.exists(directory):
            return 0
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
        
        return deleted_count
        
    except Exception as e:
        raise Exception(f"Failed to cleanup files: {str(e)}")


def list_files(directory: str, extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    List files in directory
    
    Args:
        directory: Directory to list
        extensions: Optional list of file extensions to filter
        
    Returns:
        List of file information dictionaries
    """
    try:
        if not os.path.exists(directory):
            return []
        
        files = []
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                # Check extension filter
                if extensions:
                    file_extension = os.path.splitext(filename)[1].lower()
                    if file_extension not in extensions:
                        continue
                
                file_info = {
                    "filename": filename,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path),
                    "extension": os.path.splitext(filename)[1].lower()
                }
                
                files.append(file_info)
        
        return files
        
    except Exception as e:
        raise Exception(f"Failed to list files: {str(e)}") 