"""
===============================================================================
ASTHASH: AUTOMATED CORPUS GENERATOR
Target: 200 Production-Grade Python Modules (10 Repositories x 20 Files)
Output: asthash_academic_corpus.csv
===============================================================================
"""
import os
import csv
import requests

def generate_academic_corpus():
    # Fetch your GitHub Token from environment variables to bypass rate limits
    github_token = os.environ.get("GITHUB_PAT")
    headers = {'Authorization': f"token {github_token}"} if github_token else {}
    
    # Establish a diverse portfolio of top-tier source domains
    targets = {
        "django/django": "Web Development",
        "pytorch/pytorch": "Machine Learning",
        "pandas-dev/pandas": "Data Science",
        "tiangolo/fastapi": "Web Development",
        "scikit-learn/scikit-learn": "Machine Learning",
        "huggingface/transformers": "Machine Learning",
        "psf/requests": "Utilities",
        "pallets/flask": "Web Development",
        "ansible/ansible": "DevOps/System",
        "matplotlib/matplotlib": "Data Visualization"
    }
    
    corpus = []
    files_per_repo = 20  # 10 repositories * 20 files = 200 files
    
    print("[*] Contacting GitHub API to build the 200-file production corpus...")
    
    for repo, domain in targets.items():
        print(f"  -> Scraping directory mapping: {repo} ({domain})")
        
        # 1. Dynamically identify default branch (main vs master)
        repo_url = f"https://api.github.com/repos/{repo}"
        try:
            res = requests.get(repo_url, headers=headers, timeout=10)
            if res.status_code != 200:
                print(f"     [!] API Rate limit or access issue on {repo}. Status: {res.status_code}")
                continue
            default_branch = res.json().get("default_branch", "main")
            
            # 2. Retrieve recursive repository directory tree
            tree_url = f"https://api.github.com/repos/{repo}/git/trees/{default_branch}?recursive=1"
            tree_res = requests.get(tree_url, headers=headers, timeout=15)
            if tree_res.status_code != 200:
                print(f"     [!] Failed to download directory tree for {repo}.")
                continue
            
            tree_data = tree_res.json()
            py_paths = []
            
            # 3. Filter for active, logical code files (skip tests, setups, and templates)
            for node in tree_data.get("tree", []):
                path = node.get("path", "")
                if (path.endswith(".py") and 
                    "test" not in path.lower() and 
                    "setup.py" not in path and 
                    "__init__.py" not in path and
                    "example" not in path.lower() and
                    node.get("type") == "blob"):
                    py_paths.append(path)
            
            # Sort by file path complexity to target robust production files
            py_paths.sort(key=len)
            selected_paths = py_paths[:files_per_repo]
            
            for path_index, p in enumerate(selected_paths):
                raw_url = f"https://raw.githubusercontent.com/{repo}/{default_branch}/{p}"
                corpus.append({
                    "Project": repo,
                    "Domain": domain,
                    "Raw_URL": raw_url
                })
                
        except Exception as e:
            print(f"     [!] Network failure on {repo}: {str(e)}")
            
    # Write directly to your target CSV file
    output_file = "asthash_academic_corpus.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Project", "Domain", "Raw_URL"])
        writer.writeheader()
        writer.writerows(corpus)
        
    print(f"\n[+] Generation Complete! Created {len(corpus)} items inside '{output_file}'.")
    if len(corpus) < 200:
        print("[-] Note: API limits may have shortened collection. Ensure GITHUB_PAT is set correctly.")

if __name__ == "__main__":
    generate_academic_corpus()