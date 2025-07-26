#!/usr/bin/env python3
"""
Excel to Turtle Converter

Transforms CBS project data from Excel format to enriched Turtle/RDF format.

Input: Excel file with project data
Output: Turtle file with projects, datasets, and organizations

Features:
- Converts project data to RDF triples
- Creates dataset URIs with random identifiers
- Enriches with organization information using caching
- Generates proper Turtle syntax with all necessary namespaces
"""

import pandas as pd
import json
import re
import string
import random
import os
from datetime import datetime

# Configuration
EXCEL_FILE = "data/Projecten_met_bestanden_einddatum_voor_2025_.xlsx"
OUTPUT_FILE = "data/cbs_projects_before_2025.ttl"
CACHE_FILE = "data/organization_cache.json"

def generate_random_id(length=32):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_organization_uri(org_name):
    """Generate a consistent URI for an organization."""
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', org_name)
    clean_name = re.sub(r'\s+', '_', clean_name.strip()).lower()
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    return f"https://w3id.org/odissei/ns/kg/cbs/organization/{clean_name}"

def classify_organization(org_name):
    """Classify organization type based on name patterns."""
    name_lower = org_name.lower()
    
    if any(word in name_lower for word in ['universiteit', 'university', 'hogeschool', 'college']):
        return 'schema:EducationalOrganization'
    elif any(word in name_lower for word in ['ministerie', 'ministry', 'gemeente', 'provincie', 'government']):
        return 'schema:GovernmentOrganization'
    elif any(word in name_lower for word in ['onderzoek', 'research', 'instituut', 'institute', 'planbureau']):
        return 'schema:ResearchOrganization'
    elif any(word in name_lower for word in ['bv', 'nv', 'ltd', 'inc', 'corp', 'company']):
        return 'schema:Corporation'
    else:
        return 'schema:Organization'

def load_organization_cache():
    """Load organization cache if it exists."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_organization_cache(cache):
    """Save organization cache."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def escape_turtle_string(text):
    """Escape special characters for Turtle format."""
    if pd.isna(text):
        return ""
    text = str(text)
    # Escape backslashes and quotes
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return text

def format_date(date_value):
    """Format date for RDF."""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, str):
        try:
            date_obj = pd.to_datetime(date_value)
        except:
            return None
    else:
        date_obj = date_value
    
    return date_obj.strftime('%Y-%m-%d')

def process_excel_to_turtle():
    """Main function to convert Excel to Turtle format."""
    print("Excel to Turtle Converter")
    print("=" * 30)
    
    # Check if Excel file exists
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Excel file not found: {EXCEL_FILE}")
        return
    
    print(f"Reading Excel file: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    
    print(f"Loaded {len(df)} rows from Excel")
    
    # Load organization cache
    org_cache = load_organization_cache()
    print(f"Loaded organization cache with {len(org_cache)} entries")
    
    # Set random seed for consistent dataset URIs
    random.seed(42)
    
    # Process data
    projects = {}
    datasets = {}
    organizations = {}
    
    print("Processing data...")
    
    for _, row in df.iterrows():
        project_num = row.get('Projectnummer')
        project_title = row.get('Onderzoek', '')
        start_date = row.get('Startdatum')
        end_date = row.get('Einddatum')
        dataset_name = row.get('Bestandsnaam', '')
        institution = row.get('Instelling', '')
        
        if pd.notna(project_num):
            project_uri = f"https://w3id.org/odissei/ns/kg/cbs/project/{project_num}"
            
            # Store project info
            if project_uri not in projects:
                projects[project_uri] = {
                    'title': escape_turtle_string(project_title),
                    'start_date': format_date(start_date),
                    'end_date': format_date(end_date),
                    'datasets': set(),
                    'organizations': set()
                }
            
            # Process dataset
            if pd.notna(dataset_name) and dataset_name.strip():
                if dataset_name not in datasets:
                    dataset_uri = f"https://w3id.org/odissei/ns/kg/cbs/dataset/{generate_random_id()}"
                    datasets[dataset_name] = {
                        'uri': dataset_uri,
                        'name': escape_turtle_string(dataset_name)
                    }
                
                projects[project_uri]['datasets'].add(datasets[dataset_name]['uri'])
            
            # Process organization
            if pd.notna(institution) and institution.strip():
                org_uri = generate_organization_uri(institution)
                
                if org_uri not in organizations:
                    # Check cache first
                    if institution in org_cache:
                        org_info = org_cache[institution]
                    else:
                        org_info = {
                            'name': institution,
                            'type': classify_organization(institution)
                        }
                        org_cache[institution] = org_info
                    
                    organizations[org_uri] = {
                        'name': escape_turtle_string(org_info['name']),
                        'type': org_info['type']
                    }
                
                projects[project_uri]['organizations'].add(org_uri)
    
    # Save updated cache
    save_organization_cache(org_cache)
    
    print(f"Processed:")
    print(f"  - {len(projects)} projects")
    print(f"  - {len(datasets)} datasets")
    print(f"  - {len(organizations)} organizations")
    
    # Generate Turtle content
    print(f"Generating Turtle file: {OUTPUT_FILE}")
    
    turtle_content = []
    
    # Add prefixes
    turtle_content.extend([
        "@prefix schema: <http://schema.org/> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix dc: <http://purl.org/dc/elements/1.1/> .",
        "@prefix foaf: <http://xmlns.com/foaf/0.1/> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "# CBS Projects with end dates before 2025",
        "# Generated from Excel data",
        ""
    ])
    
    # Add projects
    for project_uri, project_data in projects.items():
        turtle_content.append(f"<{project_uri}>")
        
        if project_data['title']:
            turtle_content.append(f'   dc:title "{project_data["title"]}" ;')
        
        if project_data['start_date']:
            turtle_content.append(f'   schema:startDate "{project_data["start_date"]}"^^xsd:date ;')
        
        if project_data['end_date']:
            turtle_content.append(f'   schema:endDate "{project_data["end_date"]}"^^xsd:date ;')
        
        # Add dataset requirements
        for dataset_uri in sorted(project_data['datasets']):
            turtle_content.append(f'   dc:requires <{dataset_uri}> ;')
        
        # Add organization relationships
        org_list = sorted(project_data['organizations'])
        for i, org_uri in enumerate(org_list):
            if i == len(org_list) - 1:  # Last organization
                turtle_content.append(f'   schema:parentOrganization <{org_uri}> .')
            else:
                turtle_content.append(f'   schema:parentOrganization <{org_uri}> ;')
        
        turtle_content.append("")
    
    # Add datasets
    turtle_content.append("# Datasets")
    for dataset_info in datasets.values():
        turtle_content.extend([
            f"<{dataset_info['uri']}>",
            f'   dc:alternative "{dataset_info["name"]}" .',
            ""
        ])
    
    # Add organizations
    turtle_content.append("# Organizations")
    for org_uri, org_data in organizations.items():
        turtle_content.extend([
            f"<{org_uri}>",
            f'   rdf:type {org_data["type"]} ;',
            f'   foaf:name "{org_data["name"]}" .',
            ""
        ])
    
    # Write to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(turtle_content))
    
    print(f"Turtle file generated successfully!")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Lines: {len(turtle_content)}")

if __name__ == "__main__":
    process_excel_to_turtle()

