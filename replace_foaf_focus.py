#!/usr/bin/env python3
"""
Replace foaf:focus with rdf:type and Schema.org Classes

This script replaces all foaf:focus properties with rdf:type and converts
text values to appropriate Schema.org class URIs.
"""

import re

def replace_foaf_focus_with_schema_types(file_path):
    """Replace foaf:focus properties with rdf:type and Schema.org classes."""
    print(f"Processing file: {file_path}")
    
    # Define the mapping from text values to Schema.org classes
    value_mapping = {
        "Educational Institution": "schema:EducationalOrganization",
        "Organization": "schema:Organization",
        "Research Institute": "schema:ResearchOrganization", 
        "Private Company": "schema:Corporation",
        "Government Agency": "schema:GovernmentOrganization"
    }
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count original foaf:focus occurrences
    original_pattern = r'foaf:focus\s+"([^"]*)"'
    original_matches = re.findall(original_pattern, content)
    
    print(f"Found {len(original_matches)} foaf:focus properties")
    
    # Count occurrences by value
    value_counts = {}
    for value in original_matches:
        value_counts[value] = value_counts.get(value, 0) + 1
    
    print("Original value distribution:")
    for value, count in sorted(value_counts.items(), key=lambda x: x[1], reverse=True):
        schema_class = value_mapping.get(value, f"UNMAPPED: {value}")
        print(f"  {count:3d}: '{value}' → {schema_class}")
    
    # Function to replace foaf:focus with rdf:type and Schema.org class
    def replace_focus(match):
        property_part = match.group(1)  # The whitespace before the quoted value
        quoted_value = match.group(2)   # The quoted value
        
        # Map the value to Schema.org class
        schema_class = value_mapping.get(quoted_value)
        if schema_class:
            return f'rdf:type {schema_class}'
        else:
            print(f"Warning: Unmapped value '{quoted_value}' - keeping as foaf:focus")
            return match.group(0)  # Return original if no mapping found
    
    # Pattern to match foaf:focus with quoted values
    # This captures the property and the quoted value separately
    pattern = r'foaf:focus(\s+)"([^"]*)"'
    
    # Replace foaf:focus with rdf:type and Schema.org classes
    fixed_content = re.sub(pattern, replace_focus, content)
    
    # Count the results
    rdf_type_pattern = r'rdf:type\s+(schema:\w+)'
    rdf_type_matches = re.findall(rdf_type_pattern, fixed_content)
    
    print(f"\nReplacement results:")
    print(f"Total rdf:type properties created: {len(rdf_type_matches)}")
    
    # Count new Schema.org class usage
    schema_counts = {}
    for schema_class in rdf_type_matches:
        schema_counts[schema_class] = schema_counts.get(schema_class, 0) + 1
    
    print("New Schema.org class distribution:")
    for schema_class, count in sorted(schema_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {count:3d}: {schema_class}")
    
    # Check for any remaining foaf:focus
    remaining_focus = re.findall(original_pattern, fixed_content)
    if remaining_focus:
        print(f"\nWarning: {len(remaining_focus)} foaf:focus properties remain unmapped:")
        for value in set(remaining_focus):
            print(f"  - '{value}'")
    else:
        print(f"\nSuccess: All foaf:focus properties have been replaced!")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"File updated successfully!")
    return len(original_matches), len(rdf_type_matches), len(remaining_focus)

def main():
    """Main function."""
    print("FOAF Focus to Schema.org Type Converter")
    print("=" * 40)
    
    turtle_file = 'resources/data/projects_start_dates.ttl'
    
    try:
        original_count, new_count, remaining_count = replace_foaf_focus_with_schema_types(turtle_file)
        
        print(f"\nSummary:")
        print(f"- Original foaf:focus properties: {original_count}")
        print(f"- New rdf:type properties: {new_count}")
        print(f"- Remaining foaf:focus properties: {remaining_count}")
        print(f"- Conversion success rate: {((original_count - remaining_count) / original_count * 100):.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

