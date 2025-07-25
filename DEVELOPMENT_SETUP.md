# Development Environment Setup Guide

## Overview

Your coding environment has been successfully set up with Git version control and GitHub synchronization for the SSHOC-NL Zotero CBS Enrichment project.

## Repository Information

- **Repository URL**: https://github.com/rsiebes/sshoc-nl-zotero-cbs-enrichment
- **Local Path**: `/home/ubuntu/projects/sshoc-nl-zotero-cbs-enrichment`
- **Authentication**: HTTPS with Personal Access Token
- **Default Branch**: main

## Project Structure

```
sshoc-nl-zotero-cbs-enrichment/
├── .git/                    # Git repository data
├── .gitignore              # Python-specific ignore patterns
├── LICENSE                 # Project license
├── README.md               # Project documentation
├── main.py                 # Main Python entry point
├── requirements.txt        # Python dependencies
├── dev_workflow.py         # Development workflow helper
└── DEVELOPMENT_SETUP.md    # This setup guide
```

## Git Configuration

- **User Name**: Manus AI
- **User Email**: manus@example.com
- **Credential Helper**: Configured to store credentials
- **Default Branch**: main

## Python Environment

- **Python Version**: 3.11.0rc1
- **Available Commands**: `python3.11`, `pip3`
- **Project Dependencies**: See `requirements.txt`

### Core Dependencies
- requests>=2.28.0
- pandas>=1.5.0
- numpy>=1.24.0

### Development Dependencies
- pytest>=7.0.0
- black>=22.0.0
- flake8>=5.0.0

## Development Workflow

### Basic Git Commands

```bash
# Check status
git status

# Pull latest changes
git pull origin main

# Add and commit changes
git add .
git commit -m "Your commit message"

# Push changes
git push origin main
```

### Using the Workflow Helper

A Python script `dev_workflow.py` is provided for common operations:

```bash
# Check git status
python3 dev_workflow.py status

# Pull latest changes
python3 dev_workflow.py pull

# Commit changes
python3 dev_workflow.py commit -m "Your commit message"

# Push changes
python3 dev_workflow.py push

# Full sync (pull, commit, push)
python3 dev_workflow.py sync -m "Your commit message"
```

## Getting Started

1. **Navigate to project directory**:
   ```bash
   cd /home/ubuntu/projects/sshoc-nl-zotero-cbs-enrichment
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the main script**:
   ```bash
   python3 main.py
   ```

4. **Start developing**:
   - Edit files using your preferred method
   - Test your changes
   - Commit and push using Git commands or the workflow helper

## Security Notes

- Personal access token is securely stored in Git credentials
- Token has been configured for HTTPS authentication
- All Git operations will use the stored credentials automatically

## Next Steps

1. Install project dependencies: `pip3 install -r requirements.txt`
2. Start developing your Zotero CBS enrichment functionality
3. Use the workflow helper for easy Git operations
4. Regularly sync your changes with GitHub

The environment is ready for collaborative Python development with full Git integration!

