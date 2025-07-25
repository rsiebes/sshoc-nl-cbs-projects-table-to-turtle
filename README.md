# CBS Projects Excel to Turtle Converter

A simple tool to convert CBS project data from Excel format to enriched Turtle/RDF format.

## What it does

Takes an Excel file containing CBS project data and transforms it into a semantic web-ready Turtle file with:

- **Projects** with titles, start/end dates, and relationships
- **Datasets** with unique URIs and alternative names  
- **Organizations** with proper classification and FOAF profiles
- **Relationships** linking projects to their datasets and organizations

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install pandas openpyxl
   ```

2. **Run the conversion:**
   ```bash
   python excel_to_turtle.py
   ```

## Input/Output

- **Input:** `data/Projecten_met_bestanden_einddatum_voor_2025_.xlsx`
- **Output:** `data/cbs_projects_before_2025.ttl`
- **Cache:** `data/organization_cache.json` (for efficiency)

## Features

- **Automatic organization classification** (University, Government, Research, Corporation)
- **Consistent dataset URIs** with random identifiers
- **Proper RDF/Turtle syntax** with all necessary namespaces
- **Organization caching** to avoid duplicate processing
- **Data validation** and proper escaping for special characters

## Output Format

The generated Turtle file includes:

```turtle
@prefix schema: <http://schema.org/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<https://w3id.org/odissei/ns/kg/cbs/project/7097>
   dc:title "Project Title" ;
   schema:startDate "2018-01-01"^^xsd:date ;
   schema:endDate "2024-12-31"^^xsd:date ;
   dc:requires <https://w3id.org/odissei/ns/kg/cbs/dataset/abc123...> ;
   schema:parentOrganization <https://w3id.org/odissei/ns/kg/cbs/organization/university_name> .
```

## Project Structure

```
├── excel_to_turtle.py                    # Main conversion script
├── data/
│   ├── Projecten_met_bestanden_einddatum_voor_2025_.xlsx  # Input Excel file
│   ├── cbs_projects_before_2025.ttl      # Output Turtle file
│   └── organization_cache.json           # Organization lookup cache
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Requirements

- Python 3.7+
- pandas
- openpyxl

That's it! Simple Excel-to-Turtle conversion with semantic enrichment.

