from github import Github
import time

# GitHub token
token = "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"

# Initialize Github instance
g = Github(token)

# Get authenticated user
user = g.get_user()
print(f"Authenticated as: {user.login}")

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
for repo_info in repositories:
    try:
        # Check if repository exists
        try:
            repo = user.get_repo(repo_info["name"])
            print(f"Repository {repo_info['name']} already exists")
        except Exception:
            # Create repository
            print(f"Creating repository {repo_info['name']}...")
            user.create_repo(
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
        print(f"Error creating repository {repo_info['name']}: {str(e)}")

print("GitHub setup script completed")
