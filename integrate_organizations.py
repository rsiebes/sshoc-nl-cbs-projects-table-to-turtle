#!/usr/bin/env python3
"""
Integrate Organization FOAF Profiles with Main Turtle File

This script integrates the generated organization FOAF profiles with the main
projects_start_dates.ttl file and adds relationships between projects and organizations.
"""

import pandas as pd
import json
import re

def load_organization_cache():
    """Load the organization cache to get URI mappings."""
    try:
        with open('resources/data/organization_cache.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading organization cache: {e}")
        return {}

def generate_organization_uri(org_name):
    """Generate a consistent URI for an organization (same as in lookup script)."""
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', org_name)
    clean_name = re.sub(r'\s+', '_', clean_name.strip()).lower()
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    return f"https://w3id.org/odissei/ns/kg/cbs/organization/{clean_name}"

def create_project_organization_mappings():
    """Create mappings between projects and organizations from Excel data."""
    print("Creating project-organization mappings...")
    
    # Load Excel file
    df = pd.read_excel('resources/data/Projecten_met_bestanden_einddatum_voor_2025_.xlsx')
    
    # Create mappings
    project_org_map = {}
    
    for _, row in df.iterrows():
        project_num = row.get('Projectnummer')
        institution = row.get('Instelling')
        
        if pd.notna(project_num) and pd.notna(institution):
            project_uri = f"https://w3id.org/odissei/ns/kg/cbs/project/{project_num}"
            org_uri = generate_organization_uri(institution)
            
            if project_uri not in project_org_map:
                project_org_map[project_uri] = set()
            project_org_map[project_uri].add(org_uri)
    
    print(f"Created mappings for {len(project_org_map)} projects")
    return project_org_map

def integrate_turtle_files():
    """Integrate organization FOAF profiles with the main Turtle file."""
    print("Integrating FOAF profiles with main Turtle file...")
    
    # Read the main projects file
    with open('resources/data/projects_start_dates.ttl', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Read the organization FOAF profiles
    with open('resources/data/organizations_foaf_profiles.ttl', 'r', encoding='utf-8') as f:
        org_content = f.read()
    
    # Create project-organization mappings
    project_org_map = create_project_organization_mappings()
    
    # Parse the main content to add organization relationships
    lines = main_content.split('\n')
    new_lines = []
    current_project_uri = None
    
    for line in lines:
        # Check if this is a project URI line
        if line.strip().startswith('<https://w3id.org/odissei/ns/kg/cbs/project/'):
            current_project_uri = line.strip().rstrip('>')
            if current_project_uri.startswith('<'):
                current_project_uri = current_project_uri[1:]
            new_lines.append(line)
        
        # Check if this is the end of a project definition (line ending with ' .')
        elif line.strip().endswith(' .') and current_project_uri:
            # Add organization relationships before the final period
            if current_project_uri in project_org_map:
                # Remove the final period and semicolon
                modified_line = line.rstrip(' .').rstrip(' ;')
                new_lines.append(modified_line + ' ;')
                
                # Add organization relationships
                org_uris = sorted(project_org_map[current_project_uri])
                for i, org_uri in enumerate(org_uris):
                    if i == len(org_uris) - 1:  # Last organization
                        new_lines.append(f'   foaf:member <{org_uri}> .')
                    else:
                        new_lines.append(f'   foaf:member <{org_uri}> ;')
            else:
                new_lines.append(line)
            current_project_uri = None
        else:
            new_lines.append(line)
    
    # Combine the content
    # First, update the prefixes to include FOAF
    prefix_section = []
    content_section = []
    in_content = False
    
    for line in new_lines:
        if line.startswith('@prefix') or (not in_content and line.strip() == ''):
            prefix_section.append(line)
        else:
            in_content = True
            content_section.append(line)
    
    # Add FOAF prefix if not present
    foaf_prefix_exists = any('foaf:' in line for line in prefix_section)
    if not foaf_prefix_exists:
        prefix_section.insert(-1, '@prefix foaf: <http://xmlns.com/foaf/0.1/> .')
    
    # Extract organization profiles from org_content (skip the prefix section)
    org_lines = org_content.split('\n')
    org_profiles = []
    skip_prefixes = True
    
    for line in org_lines:
        if skip_prefixes and (line.startswith('@prefix') or line.strip() == '' or line.startswith('#')):
            continue
        else:
            skip_prefixes = False
            org_profiles.append(line)
    
    # Combine everything
    final_content = []
    final_content.extend(prefix_section)
    final_content.append('')
    final_content.append('# Projects with datasets and organization relationships')
    final_content.extend(content_section)
    final_content.append('')
    final_content.append('# Organization FOAF Profiles')
    final_content.extend(org_profiles)
    
    # Write the integrated file
    output_file = 'resources/data/projects_start_dates.ttl'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content))
    
    print(f"Integration completed. Updated file: {output_file}")
    
    # Print statistics
    total_projects = len(project_org_map)
    total_relationships = sum(len(orgs) for orgs in project_org_map.values())
    print(f"Added {total_relationships} project-organization relationships for {total_projects} projects")

def main():
    """Main function."""
    print("Organization FOAF Profile Integration")
    print("=" * 40)
    
    try:
        integrate_turtle_files()
        print("Integration completed successfully!")
    except Exception as e:
        print(f"Error during integration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

