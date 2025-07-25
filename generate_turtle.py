#!/usr/bin/env python3
"""
Generate Turtle RDF file from Excel project data

This script processes the Excel file and creates RDF triples
with project URIs and schema:startDate properties.
"""

import pandas as pd
import sys
import os
import random
import string
from datetime import datetime

def format_date_for_rdf(date_value):
    """Format date value for RDF (xsd:date format)."""
    if pd.isna(date_value):
        return None
    
    try:
        # If it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        
        # If it's a string, try to parse it
        if isinstance(date_value, str):
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        # If it's a pandas Timestamp
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y-%m-%d')
        
        return None
    except Exception as e:
        print(f"Warning: Could not format date '{date_value}': {e}")
        return None

def generate_random_id(length=32):
    """Generate a random alphanumeric string of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_turtle_rdf(excel_file_path, output_file_path):
    """Generate Turtle RDF file from Excel data."""
    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Use Dutch column names as found in the analysis
        project_col = 'Projectnummer'
        start_date_col = 'Startdatum'
        end_date_col = 'Einddatum'
        title_col = 'Onderzoek'
        dataset_col = 'Bestandsnaam'
        
        if project_col not in df.columns:
            raise ValueError(f"Column '{project_col}' not found in Excel file")
        if start_date_col not in df.columns:
            raise ValueError(f"Column '{start_date_col}' not found in Excel file")
        if end_date_col not in df.columns:
            raise ValueError(f"Column '{end_date_col}' not found in Excel file")
        if title_col not in df.columns:
            raise ValueError(f"Column '{title_col}' not found in Excel file")
        if dataset_col not in df.columns:
            raise ValueError(f"Column '{dataset_col}' not found in Excel file")
        
        print(f"Processing {len(df)} rows...")
        
        # Get unique project numbers with their start dates, end dates, and titles
        # Group by project number and take the first occurrence of each field
        unique_projects = df.groupby(project_col).agg({
            start_date_col: 'first',
            end_date_col: 'first',
            title_col: 'first'
        }).reset_index()
        unique_projects = unique_projects.dropna(subset=[project_col])
        
        # Get unique datasets and create consistent URI mapping
        unique_datasets = df[dataset_col].dropna().unique()
        
        # Create a consistent mapping from dataset names to URIs
        # Use a fixed seed for reproducible random IDs
        random.seed(42)  # Fixed seed for consistency
        dataset_uri_mapping = {}
        for dataset_name in unique_datasets:
            random_id = generate_random_id(32)
            dataset_uri_mapping[dataset_name] = f"https://w3id.org/odissei/ns/kg/cbs/dataset/{random_id}"
        
        # Get project-dataset relationships
        project_dataset_pairs = df[[project_col, dataset_col]].dropna()
        project_datasets = project_dataset_pairs.groupby(project_col)[dataset_col].apply(list).to_dict()
        
        print(f"Found {len(unique_projects)} unique projects")
        print(f"Found {len(unique_datasets)} unique datasets")
        print(f"Found {len(project_dataset_pairs)} project-dataset relationships")
        
        # Generate Turtle RDF content
        turtle_content = []
        
        # Add prefixes
        turtle_content.append("@prefix schema: <http://schema.org/> .")
        turtle_content.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
        turtle_content.append("@prefix dc: <http://purl.org/dc/elements/1.1/> .")
        turtle_content.append("")
        
        # Process each unique project
        valid_projects = 0
        for _, row in unique_projects.iterrows():
            project_number = row[project_col]
            start_date = row[start_date_col]
            end_date = row[end_date_col]
            title = row[title_col]
            
            # Skip if project number is not valid
            if pd.isna(project_number) or project_number == '':
                continue
            
            # Format the dates
            formatted_start_date = format_date_for_rdf(start_date)
            formatted_end_date = format_date_for_rdf(end_date)
            
            # Skip if both dates are invalid and no title
            if formatted_start_date is None and formatted_end_date is None and (pd.isna(title) or title == ''):
                print(f"Warning: Skipping project {project_number} due to no valid data")
                continue
            
            # Create URI
            project_uri = f"<https://w3id.org/odissei/ns/kg/cbs/project/{project_number}>"
            
            # Build properties list
            properties = []
            
            # Add title if available
            if not pd.isna(title) and title != '':
                # Escape quotes in title for proper RDF literal
                escaped_title = str(title).replace('"', '\\"')
                properties.append(f'   dc:title "{escaped_title}"')
            
            # Add startDate if valid
            if formatted_start_date is not None:
                start_date_literal = f'"{formatted_start_date}"^^xsd:date'
                properties.append(f"   schema:startDate {start_date_literal}")
            
            # Add endDate if valid
            if formatted_end_date is not None:
                end_date_literal = f'"{formatted_end_date}"^^xsd:date'
                properties.append(f"   schema:endDate {end_date_literal}")
            
            # Add dc:requires properties for datasets
            if project_number in project_datasets:
                for dataset_name in project_datasets[project_number]:
                    if dataset_name in dataset_uri_mapping:
                        dataset_uri = f"<{dataset_uri_mapping[dataset_name]}>"
                        properties.append(f"   dc:requires {dataset_uri}")
            
            # Add grouped RDF statement
            if properties:
                turtle_content.append(f"{project_uri}")
                for i, prop in enumerate(properties):
                    if i == len(properties) - 1:  # Last property
                        turtle_content.append(f"{prop} .")
                    else:  # Not last property
                        turtle_content.append(f"{prop} ;")
                turtle_content.append("")  # Empty line between subjects
                valid_projects += 1
        
        # Process each unique dataset
        valid_datasets = 0
        for dataset_name in unique_datasets:
            if pd.isna(dataset_name) or dataset_name == '':
                continue
            
            # Use the consistent URI from mapping
            dataset_uri = f"<{dataset_uri_mapping[dataset_name]}>"
            
            # Escape quotes in dataset name for proper RDF literal
            escaped_dataset_name = str(dataset_name).replace('"', '\\"')
            
            # Add dataset RDF statement
            turtle_content.append(f"{dataset_uri}")
            turtle_content.append(f'   dc:alternative "{escaped_dataset_name}" .')
            turtle_content.append("")  # Empty line between subjects
            valid_datasets += 1
        
        # Write to file
        print(f"Writing {valid_projects} projects and {valid_datasets} datasets to: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(turtle_content))
        
        print(f"Successfully generated Turtle RDF file with {valid_projects} projects and {valid_datasets} datasets")
        return True
        
    except Exception as e:
        print(f"Error generating Turtle RDF: {e}")
        return False

def main():
    """Main function."""
    excel_file = "resources/data/Projecten_met_bestanden_einddatum_voor_2025_.xlsx"
    output_file = "resources/data/projects_start_dates.ttl"
    
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found: {excel_file}")
        return False
    
    success = generate_turtle_rdf(excel_file, output_file)
    
    if success:
        print(f"\nTurtle RDF file generated successfully: {output_file}")
        
        # Show first few lines of the generated file
        print("\nFirst 10 lines of generated Turtle file:")
        print("-" * 50)
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10]):
                print(f"{i+1:2d}: {line.rstrip()}")
        
        if len(lines) > 10:
            print(f"... and {len(lines) - 10} more lines")
    
    return success

if __name__ == "__main__":
    main()

