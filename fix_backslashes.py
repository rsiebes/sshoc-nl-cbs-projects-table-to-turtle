#!/usr/bin/env python3
"""
Fix Backslashes in dc:alternative Property Values

This script finds all dc:alternative property values and replaces single backslashes
with double backslashes for proper RDF/Turtle escaping.
"""

import re

def fix_backslashes_in_turtle(file_path):
    """Fix backslashes in dc:alternative property values in a Turtle file."""
    print(f"Processing file: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count original backslashes in dc:alternative values
    original_pattern = r'dc:alternative\s+"([^"]*)"'
    original_matches = re.findall(original_pattern, content)
    original_backslash_count = sum(value.count('\\') for value in original_matches)
    
    print(f"Found {len(original_matches)} dc:alternative properties")
    print(f"Original single backslashes in dc:alternative values: {original_backslash_count}")
    
    # Function to replace backslashes in the matched value
    def replace_backslashes(match):
        property_part = match.group(1)  # The part before the quoted value
        quoted_value = match.group(2)   # The quoted value
        
        # Replace single backslashes with double backslashes in the value
        # But be careful not to replace already escaped backslashes
        fixed_value = quoted_value.replace('\\', '\\\\')
        
        return f'{property_part}"{fixed_value}"'
    
    # Pattern to match dc:alternative with quoted values
    # This captures the property part and the quoted value separately
    pattern = r'(dc:alternative\s+)"([^"]*)"'
    
    # Replace backslashes in dc:alternative values
    fixed_content = re.sub(pattern, replace_backslashes, content)
    
    # Count fixed backslashes
    fixed_matches = re.findall(original_pattern, fixed_content)
    fixed_backslash_count = sum(value.count('\\\\') for value in fixed_matches)
    
    print(f"Fixed double backslashes in dc:alternative values: {fixed_backslash_count}")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"File updated successfully!")
    return len(original_matches), original_backslash_count, fixed_backslash_count

def main():
    """Main function."""
    print("Backslash Fixer for dc:alternative Properties")
    print("=" * 45)
    
    turtle_file = 'resources/data/projects_start_dates.ttl'
    
    try:
        properties_count, original_count, fixed_count = fix_backslashes_in_turtle(turtle_file)
        
        print(f"\nSummary:")
        print(f"- dc:alternative properties processed: {properties_count}")
        print(f"- Single backslashes found: {original_count}")
        print(f"- Double backslashes created: {fixed_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

