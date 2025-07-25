#!/usr/bin/env python3
"""
Basic Enrichment Example

This example demonstrates how to use the SSHOC-NL Zotero CBS enrichment tool
to enhance Zotero library items with CBS (Statistics Netherlands) data.
"""

import json
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_config(config_path="resources/config/config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        print("Please copy config.example.json to config.json and update with your settings")
        return None

def example_enrichment():
    """Example function showing basic enrichment workflow."""
    print("SSHOC-NL Zotero CBS Enrichment Example")
    print("=====================================")
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    print("Configuration loaded successfully")
    
    # Example workflow steps:
    print("1. Connect to Zotero API")
    print("2. Fetch library items")
    print("3. Identify items for CBS enrichment")
    print("4. Query CBS Open Data API")
    print("5. Enrich Zotero items with CBS data")
    print("6. Save enriched data")
    
    print("\nThis is a placeholder example.")
    print("Implement actual enrichment logic in the main application.")

if __name__ == "__main__":
    example_enrichment()

