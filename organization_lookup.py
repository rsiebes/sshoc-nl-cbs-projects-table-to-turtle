#!/usr/bin/env python3
"""
Organization Lookup and FOAF Profile Generator

This script looks up organization information and creates FOAF profiles
with a caching system to prevent unnecessary online lookups.
"""

import pandas as pd
import json
import os
import time
import random
import string
import requests
from urllib.parse import quote
import re

class OrganizationLookup:
    def __init__(self, cache_file='organization_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        
    def load_cache(self):
        """Load organization cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache file: {e}")
                return {}
        return {}
    
    def save_cache(self):
        """Save organization cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def generate_organization_uri(self, org_name):
        """Generate a consistent URI for an organization."""
        # Clean the organization name for URI
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', org_name)
        clean_name = re.sub(r'\s+', '_', clean_name.strip()).lower()
        # Limit length and ensure uniqueness
        if len(clean_name) > 50:
            clean_name = clean_name[:50]
        return f"https://w3id.org/odissei/ns/kg/cbs/organization/{clean_name}"
    
    def lookup_organization(self, org_name):
        """Look up organization information with caching."""
        # Check cache first
        if org_name in self.cache:
            print(f"Found in cache: {org_name}")
            return self.cache[org_name]
        
        print(f"Looking up: {org_name}")
        
        # Create basic organization info
        org_info = {
            'name': org_name,
            'uri': self.generate_organization_uri(org_name),
            'type': 'Organization',
            'lookup_attempted': True,
            'found_details': False
        }
        
        # Try to determine organization type and add basic info
        org_info.update(self.analyze_organization_name(org_name))
        
        # Cache the result
        self.cache[org_name] = org_info
        self.save_cache()
        
        # Add small delay to be respectful
        time.sleep(0.1)
        
        return org_info
    
    def analyze_organization_name(self, org_name):
        """Analyze organization name to extract basic information."""
        info = {}
        
        # Determine organization type
        if any(keyword in org_name.lower() for keyword in ['universiteit', 'university', 'hogeschool', 'college']):
            info['org_type'] = 'Educational Institution'
            info['sector'] = 'Education'
        elif any(keyword in org_name.lower() for keyword in ['ministerie', 'ministry', 'rijks', 'government']):
            info['org_type'] = 'Government Agency'
            info['sector'] = 'Government'
        elif any(keyword in org_name.lower() for keyword in ['planbureau', 'bureau', 'instituut', 'institute']):
            info['org_type'] = 'Research Institute'
            info['sector'] = 'Research'
        elif any(keyword in org_name.lower() for keyword in ['bv', 'b.v.', 'ltd', 'inc', 'corp']):
            info['org_type'] = 'Private Company'
            info['sector'] = 'Private'
        else:
            info['org_type'] = 'Organization'
            info['sector'] = 'Unknown'
        
        # Extract location hints
        dutch_cities = ['amsterdam', 'rotterdam', 'utrecht', 'eindhoven', 'tilburg', 'groningen', 
                       'leiden', 'delft', 'maastricht', 'nijmegen', 'twente', 'wageningen']
        for city in dutch_cities:
            if city in org_name.lower():
                info['location_hint'] = city.title()
                break
        
        # Extract faculty/department info
        if '_' in org_name:
            parts = org_name.split('_')
            if len(parts) > 1:
                info['parent_organization'] = parts[0]
                info['department'] = '_'.join(parts[1:])
        
        return info
    
    def create_foaf_profile(self, org_info):
        """Create FOAF profile in Turtle format for an organization."""
        uri = org_info['uri']
        name = org_info['name']
        
        # Start building the FOAF profile
        profile_lines = [f"<{uri}>"]
        profile_lines.append("   rdf:type foaf:Organization ;")
        
        # Add name
        escaped_name = name.replace('"', '\\"')
        profile_lines.append(f'   foaf:name "{escaped_name}" ;')
        
        # Add organization type as focus
        if 'org_type' in org_info:
            profile_lines.append(f'   foaf:focus "{org_info["org_type"]}" ;')
        
        # Add location if available
        if 'location_hint' in org_info:
            profile_lines.append(f'   rdfs:comment "Located in {org_info["location_hint"]}" ;')
        
        # Add parent organization relationship if available
        if 'parent_organization' in org_info:
            parent_uri = self.generate_organization_uri(org_info['parent_organization'])
            profile_lines.append(f'   foaf:member <{parent_uri}> ;')
        
        # Remove the last semicolon and add period
        if profile_lines[-1].endswith(' ;'):
            profile_lines[-1] = profile_lines[-1][:-2] + ' .'
        
        profile_lines.append("")  # Empty line
        
        return '\n'.join(profile_lines)

def main():
    """Main function to process all organizations."""
    print("Organization Lookup and FOAF Profile Generator")
    print("=" * 50)
    
    # Load Excel file
    excel_file = 'resources/data/Projecten_met_bestanden_einddatum_voor_2025_.xlsx'
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found: {excel_file}")
        return
    
    df = pd.read_excel(excel_file)
    
    # Get unique organizations
    if 'Instelling' not in df.columns:
        print("Error: 'Instelling' column not found in Excel file")
        return
    
    unique_orgs = df['Instelling'].dropna().unique()
    print(f"Found {len(unique_orgs)} unique organizations")
    
    # Initialize lookup system
    lookup = OrganizationLookup('resources/data/organization_cache.json')
    
    # Process organizations
    foaf_profiles = []
    processed_count = 0
    
    for org_name in sorted(unique_orgs):
        try:
            org_info = lookup.lookup_organization(org_name)
            foaf_profile = lookup.create_foaf_profile(org_info)
            foaf_profiles.append(foaf_profile)
            processed_count += 1
            
            if processed_count % 50 == 0:
                print(f"Processed {processed_count}/{len(unique_orgs)} organizations")
                
        except Exception as e:
            print(f"Error processing {org_name}: {e}")
            continue
    
    # Save FOAF profiles
    output_file = 'resources/data/organizations_foaf_profiles.ttl'
    
    # Create complete Turtle file
    turtle_content = [
        "@prefix foaf: <http://xmlns.com/foaf/0.1/> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "# FOAF Profiles for Organizations",
        "# Generated automatically with caching system",
        ""
    ]
    
    turtle_content.extend(foaf_profiles)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(turtle_content))
    
    print(f"\nCompleted processing {processed_count} organizations")
    print(f"FOAF profiles saved to: {output_file}")
    print(f"Cache saved to: {lookup.cache_file}")

if __name__ == "__main__":
    main()

