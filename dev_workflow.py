#!/usr/bin/env python3
"""
Development Workflow Helper

This script provides common Git operations for the development workflow.
"""

import subprocess
import sys
import argparse

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def git_status():
    """Show git status."""
    return run_command("git status", "Checking git status")

def git_pull():
    """Pull latest changes from remote."""
    return run_command("git pull origin main", "Pulling latest changes")

def git_push():
    """Push changes to remote."""
    return run_command("git push origin main", "Pushing changes to remote")

def git_commit(message):
    """Add all changes and commit with message."""
    commands = [
        ("git add .", "Adding all changes"),
        (f'git commit -m "{message}"', f"Committing with message: {message}")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def sync_changes(commit_message):
    """Full sync: pull, commit, and push."""
    print("Starting full sync workflow...")
    
    if not git_pull():
        print("Failed to pull changes")
        return False
    
    if not git_commit(commit_message):
        print("Failed to commit changes")
        return False
    
    if not git_push():
        print("Failed to push changes")
        return False
    
    print("Sync completed successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Development workflow helper")
    parser.add_argument("action", choices=["status", "pull", "push", "commit", "sync"],
                       help="Action to perform")
    parser.add_argument("-m", "--message", help="Commit message (required for commit and sync)")
    
    args = parser.parse_args()
    
    if args.action == "status":
        git_status()
    elif args.action == "pull":
        git_pull()
    elif args.action == "push":
        git_push()
    elif args.action == "commit":
        if not args.message:
            print("Error: Commit message required for commit action")
            sys.exit(1)
        git_commit(args.message)
    elif args.action == "sync":
        if not args.message:
            print("Error: Commit message required for sync action")
            sys.exit(1)
        sync_changes(args.message)

if __name__ == "__main__":
    main()

