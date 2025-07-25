#!/usr/bin/env python3
"""
Analyze Excel file structure for Turtle RDF generation

This script examines the Excel file to understand the structure
and identify the relevant columns for RDF generation.
"""

import pandas as pd
import sys
import os

def analyze_excel_file(file_path):
    """Analyze the Excel file structure."""
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        print("Excel File Analysis")
        print("==================")
        print(f"File: {file_path}")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print()
        
        print("Column Names:")
        for i, col in enumerate(df.columns):
            print(f"{i+1:2d}. {col}")
        print()
        
        # Check for the required columns
        required_columns = ['Project number', 'Start date']
        print("Required Columns Check:")
        for col in required_columns:
            if col in df.columns:
                print(f"✓ '{col}' found")
            else:
                print(f"✗ '{col}' NOT found")
                # Try to find similar column names
                similar = [c for c in df.columns if col.lower() in c.lower() or c.lower() in col.lower()]
                if similar:
                    print(f"  Similar columns: {similar}")
        print()
        
        # Show first few rows
        print("First 5 rows:")
        print(df.head())
        print()
        
        # Check for Project number column specifically
        project_col = None
        start_date_col = None
        
        for col in df.columns:
            if 'project' in col.lower() and 'number' in col.lower():
                project_col = col
            elif 'start' in col.lower() and 'date' in col.lower():
                start_date_col = col
        
        if project_col:
            print(f"Project Number Column: '{project_col}'")
            print(f"Unique project numbers: {df[project_col].nunique()}")
            print(f"Sample values: {df[project_col].dropna().head().tolist()}")
            print()
        
        if start_date_col:
            print(f"Start Date Column: '{start_date_col}'")
            print(f"Date range: {df[start_date_col].min()} to {df[start_date_col].max()}")
            print(f"Sample values: {df[start_date_col].dropna().head().tolist()}")
            print()
        
        return df, project_col, start_date_col
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None, None, None

if __name__ == "__main__":
    file_path = "resources/data/Projecten_met_bestanden_einddatum_voor_2025_.xlsx"
    
    if os.path.exists(file_path):
        analyze_excel_file(file_path)
    else:
        print(f"File not found: {file_path}")
        print("Please ensure the Excel file is in the resources/data directory.")

