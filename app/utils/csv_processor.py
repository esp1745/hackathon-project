"""
Specialized CSV processor for real estate data
"""

import csv
import json
from typing import List, Dict, Any, Optional
from io import StringIO


class RealEstateCSVProcessor:
    """Specialized processor for real estate CSV data"""
    
    def __init__(self):
        """Initialize the processor"""
        self.property_data = []
        self.fieldnames = []
        self.summary_stats = {}
    
    def process_csv(self, csv_content: str, filename: str) -> str:
        """
        Process real estate CSV data
        
        Args:
            csv_content: CSV file content
            filename: CSV filename
            
        Returns:
            Structured text representation
        """
        try:
            # Parse CSV
            csv_reader = csv.DictReader(StringIO(csv_content))
            self.fieldnames = csv_reader.fieldnames or []
            
            # Load all data
            self.property_data = list(csv_reader)
            
            # Generate summary statistics
            self._generate_summary_stats()
            
            # Create structured text
            return self._create_structured_text(filename)
            
        except Exception as e:
            raise Exception(f"Failed to process real estate CSV: {str(e)}")
    
    def _generate_summary_stats(self):
        """Generate summary statistics for the dataset"""
        if not self.property_data:
            return
        
        # Basic stats
        total_properties = len(self.property_data)
        
        # Property types (Floor column)
        floor_types = {}
        for row in self.property_data:
            floor = row.get('Floor', 'Unknown')
            floor_types[floor] = floor_types.get(floor, 0) + 1
        
        # Price ranges
        rent_prices = []
        for row in self.property_data:
            try:
                rent_str = row.get('Rent/SF/Year', '').replace('$', '').replace(',', '')
                if rent_str:
                    rent_prices.append(float(rent_str))
            except:
                continue
        
        # Size ranges
        sizes = []
        for row in self.property_data:
            try:
                size_str = row.get('Size (SF)', '').replace(',', '')
                if size_str:
                    sizes.append(float(size_str))
            except:
                continue
        
        # Brokers
        brokers = {}
        for row in self.property_data:
            broker = row.get('Associate 1', 'Unknown')
            brokers[broker] = brokers.get(broker, 0) + 1
        
        self.summary_stats = {
            'total_properties': total_properties,
            'floor_types': floor_types,
            'rent_range': {
                'min': min(rent_prices) if rent_prices else 0,
                'max': max(rent_prices) if rent_prices else 0,
                'avg': sum(rent_prices) / len(rent_prices) if rent_prices else 0
            },
            'size_range': {
                'min': min(sizes) if sizes else 0,
                'max': max(sizes) if sizes else 0,
                'avg': sum(sizes) / len(sizes) if sizes else 0
            },
            'top_brokers': dict(sorted(brokers.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _create_structured_text(self, filename: str) -> str:
        """Create structured text representation"""
        if not self.property_data:
            return f"CSV Dataset: {filename}\nNo data found."
        
        # Header
        text = f"Real Estate Dataset: {filename}\n"
        text += "=" * 50 + "\n\n"
        
        # Summary statistics
        text += "SUMMARY STATISTICS:\n"
        text += f"Total Properties: {self.summary_stats['total_properties']}\n"
        text += f"Rent Range: ${self.summary_stats['rent_range']['min']:.2f} - ${self.summary_stats['rent_range']['max']:.2f} per SF/year\n"
        text += f"Average Rent: ${self.summary_stats['rent_range']['avg']:.2f} per SF/year\n"
        text += f"Size Range: {self.summary_stats['size_range']['min']:.0f} - {self.summary_stats['size_range']['max']:.0f} SF\n"
        text += f"Average Size: {self.summary_stats['size_range']['avg']:.0f} SF\n\n"
        
        # Floor types
        text += "PROPERTY TYPES (by Floor):\n"
        for floor_type, count in self.summary_stats['floor_types'].items():
            text += f"  {floor_type}: {count} properties\n"
        text += "\n"
        
        # Top brokers
        text += "TOP BROKERS:\n"
        for broker, count in self.summary_stats['top_brokers'].items():
            text += f"  {broker}: {count} properties\n"
        text += "\n"
        
        # Column information
        text += f"DATA COLUMNS: {', '.join(self.fieldnames)}\n\n"
        
        # Sample properties (first 10)
        text += "SAMPLE PROPERTIES:\n"
        text += "-" * 30 + "\n"
        
        for i, row in enumerate(self.property_data[:10], 1):
            text += f"Property {i}:\n"
            text += f"  Address: {row.get('Property Address', 'N/A')}\n"
            text += f"  Floor/Suite: {row.get('Floor', 'N/A')}/{row.get('Suite', 'N/A')}\n"
            text += f"  Size: {row.get('Size (SF)', 'N/A')} SF\n"
            text += f"  Rent: {row.get('Rent/SF/Year', 'N/A')} per SF/year\n"
            text += f"  Annual Rent: {row.get('Annual Rent', 'N/A')}\n"
            text += f"  Monthly Rent: {row.get('Monthly Rent', 'N/A')}\n"
            text += f"  Broker: {row.get('Associate 1', 'N/A')}\n"
            text += "\n"
        
        if len(self.property_data) > 10:
            text += f"... and {len(self.property_data) - 10} more properties\n\n"
        
        return text
    
    def search_properties(self, query: str) -> List[Dict[str, Any]]:
        """
        Search properties based on query
        
        Args:
            query: Search query
            
        Returns:
            List of matching properties
        """
        if not self.property_data:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for row in self.property_data:
            # Search in key fields
            searchable_text = f"{row.get('Property Address', '')} {row.get('Floor', '')} {row.get('Suite', '')} {row.get('Associate 1', '')} {row.get('Associate 2', '')} {row.get('Associate 3', '')} {row.get('Associate 4', '')}".lower()
            
            if query_lower in searchable_text:
                matches.append(row)
        
        return matches
    
    def get_property_by_id(self, unique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get property by unique ID
        
        Args:
            unique_id: Property unique ID
            
        Returns:
            Property data or None
        """
        for row in self.property_data:
            if row.get('unique_id') == unique_id:
                return row
        return None
    
    def get_properties_by_broker(self, broker_name: str) -> List[Dict[str, Any]]:
        """
        Get properties by broker
        
        Args:
            broker_name: Broker name
            
        Returns:
            List of properties
        """
        broker_lower = broker_name.lower()
        matches = []
        
        for row in self.property_data:
            for i in range(1, 5):  # Check Associate 1-4
                associate_key = f'Associate {i}'
                if associate_key in row and broker_lower in row[associate_key].lower():
                    matches.append(row)
                    break
        
        return matches
    
    def get_properties_by_address(self, address: str) -> List[Dict[str, Any]]:
        """
        Get properties by address
        
        Args:
            address: Property address
            
        Returns:
            List of properties
        """
        address_lower = address.lower()
        matches = []
        
        for row in self.property_data:
            if address_lower in row.get('Property Address', '').lower():
                matches.append(row)
        
        return matches


# Create global processor instance
real_estate_processor = RealEstateCSVProcessor() 