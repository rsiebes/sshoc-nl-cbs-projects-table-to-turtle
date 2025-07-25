#!/usr/bin/env python3
"""
Generate Turtle RDF file from Excel project data

This script processes the Excel file and creates RDF triples
with project URIs and schema:startDate properties.
"""

import pandas as pd
import sys
import os
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
        
        if project_col not in df.columns:
            raise ValueError(f"Column '{project_col}' not found in Excel file")
        if start_date_col not in df.columns:
            raise ValueError(f"Column '{start_date_col}' not found in Excel file")
        if end_date_col not in df.columns:
            raise ValueError(f"Column '{end_date_col}' not found in Excel file")
        
        print(f"Processing {len(df)} rows...")
        
        # Get unique project numbers with their start and end dates
        # Group by project number and take the first start date and end date for each project
        unique_projects = df.groupby(project_col).agg({
            start_date_col: 'first',
            end_date_col: 'first'
        }).reset_index()
        unique_projects = unique_projects.dropna(subset=[project_col])
        
        print(f"Found {len(unique_projects)} unique projects")
        
        # Generate Turtle RDF content
        turtle_content = []
        
        # Add prefixes
        turtle_content.append("@prefix schema: <http://schema.org/> .")
        turtle_content.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
        turtle_content.append("")
        
        # Process each unique project
        valid_triples = 0
        for _, row in unique_projects.iterrows():
            project_number = row[project_col]
            start_date = row[start_date_col]
            end_date = row[end_date_col]
            
            # Skip if project number is not valid
            if pd.isna(project_number) or project_number == '':
                continue
            
            # Format the dates
            formatted_start_date = format_date_for_rdf(start_date)
            formatted_end_date = format_date_for_rdf(end_date)
            
            # Skip if both dates are invalid
            if formatted_start_date is None and formatted_end_date is None:
                print(f"Warning: Skipping project {project_number} due to invalid dates")
                continue
            
            # Create URI
            project_uri = f"<https://w3id.org/odissei/ns/kg/cbs/project/{project_number}>"
            
            # Add startDate triple if valid
            if formatted_start_date is not None:
                start_date_literal = f'"{formatted_start_date}"^^xsd:date'
                turtle_content.append(f"{project_uri} schema:startDate {start_date_literal} .")
                valid_triples += 1
            
            # Add endDate triple if valid
            if formatted_end_date is not None:
                end_date_literal = f'"{formatted_end_date}"^^xsd:date'
                turtle_content.append(f"{project_uri} schema:endDate {end_date_literal} .")
                valid_triples += 1
        
        # Write to file
        print(f"Writing {valid_triples} RDF triples to: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(turtle_content))
        
        print(f"Successfully generated Turtle RDF file with {valid_triples} triples")
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

