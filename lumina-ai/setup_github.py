from github import Github
import os
import time

# GitHub token
token = "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"

# Initialize Github instance
g = Github(token)

# Get authenticated user
user = g.get_user()
print(f"Authenticated as: {user.login}")

# Check if LuminaAI organization exists, create if not
try:
    org = g.get_organization("LuminaAI")
    print(f"Organization LuminaAI already exists")
except Exception as e:
    print(f"Creating LuminaAI organization...")
    # Note: Organization creation requires a different API endpoint
    # For this implementation, we'll assume the organization exists or
    # will be created manually via the GitHub web interface
    print("Please create the LuminaAI organization manually through the GitHub web interface")
    print("Then run this script again")
    # exit(1)

# Create repositories
repositories = [
    {
        "name": "lumina-core",
        "description": "Central orchestration and core services for Lumina AI",
        "has_wiki": True,
        "has_issues": True,
        "auto_init": True
    },
    {
        "name": "lumina-providers",
        "description": "AI provider integration for Lumina AI",
        "has_wiki": True,
        "has_issues": True,
        "auto_init": True
    },
    {
        "name": "lumina-memory",
        "description": "State and context management for Lumina AI",
        "has_wiki": True,
        "has_issues": True,
        "auto_init": True
    },
    {
        "name": "lumina-security",
        "description": "Authentication and authorization for Lumina AI",
        "has_wiki": True,
        "has_issues": True,
        "auto_init": True
    }
]

# Create repositories if they don't exist
try:
    org = g.get_organization("LuminaAI")
    for repo_info in repositories:
        try:
            repo = org.get_repo(repo_info["name"])
            print(f"Repository {repo_info['name']} already exists")
        except Exception as e:
            print(f"Creating repository {repo_info['name']}...")
            org.create_repo(
                name=repo_info["name"],
                description=repo_info["description"],
                has_wiki=repo_info["has_wiki"],
                has_issues=repo_info["has_issues"],
                auto_init=repo_info["auto_init"]
            )
            print(f"Repository {repo_info['name']} created successfully")
            # Sleep to avoid rate limiting
            time.sleep(1)
except Exception as e:
    print(f"Error working with organization: {str(e)}")

print("GitHub setup script completed")
