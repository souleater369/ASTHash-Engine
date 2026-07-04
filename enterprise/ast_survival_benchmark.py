"""
===============================================================================
ASTHASH ENTERPRISE: MASS BENCHMARKING ENGINE (Epoch V)
Target: High-Throughput Publication Data Generation (100+ Repositories)
Outputs: benchmark_results.csv (For LaTeX/Matplotlib Graphing)
===============================================================================
"""
import ast
import os
import csv
import time
import requests
import subprocess
import traceback
import concurrent.futures
from astrace_enterprise_encoder import KeyManager, protect_code
from astrace_enterprise_decoder import ProvenanceVerifier

# =====================================================================
# 1. GITHUB CRAWLER (Dynamic Corpus Generation)
# =====================================================================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_PAT_HERE") # Replace with your token
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN != "YOUR_GITHUB_PAT_HERE" else {}

def fetch_target_files(target_count=100) -> list:
    """Crawls the GitHub API to find real, complex Python files from top repos."""
    print(f"[*] Crawling GitHub for {target_count} production Python files...")
    files_to_test = []
    page = 1
    
    while len(files_to_test) < target_count:
        # Search for popular Python repositories
        search_url = f"https://api.github.com/search/repositories?q=language:python&sort=stars&per_page=50&page={page}"
        response = requests.get(search_url, headers=HEADERS)
        
        if response.status_code != 200:
            print("[-] GitHub API Rate Limit Hit or Network Error.")
            break
            
        repos = response.json().get("items", [])
        if not repos: break
        
        for repo in repos:
            if len(files_to_test) >= target_count: break
            
            # Grab the default branch and look for a core file (like models.py, app.py, or main.py)
            # For robustness in this benchmark, we'll try to pull their setup.py or core module
            repo_name = repo['name']
            owner = repo['owner']['login']
            branch = repo.get('default_branch', 'main')
            
            # Construct raw URLs for common dense Python files
            candidate_urls = [
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/setup.py",
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/main.py",
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{repo_name}/__init__.py"
            ]
            
            for url in candidate_urls:
                if requests.head(url).status_code == 200:
                    files_to_test.append((f"{owner}_{repo_name}", url))
                    break # Just take one heavy file per repository to maintain diversity
                    
        page += 1
        
    print(f"[+] Successfully mapped {len(files_to_test)} raw file URLs.")
    return files_to_test

# =====================================================================
# 2. THE HOSTILE AST ATTACKER (Level 4 Canonicalization)
# =====================================================================
class HostileASTCanonicalizer(ast.NodeTransformer):
    """Simulates a highly aggressive compiler optimization pass."""
    def visit_FunctionDef(self, node):
        # Level 3: Strip docstrings to test topological shifts
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            node.body.pop(0)
        self.generic_visit(node)
        return node

    def visit_BinOp(self, node):
        # Level 4: Aggressive Constant Folding
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                # Attempt to fold safe math operations
                if isinstance(node.op, ast.Add): return ast.Constant(value=node.left.value + node.right.value)
                if isinstance(node.op, ast.Sub): return ast.Constant(value=node.left.value - node.right.value)
            except Exception: pass
        self.generic_visit(node)
        return node

def apply_hostile_ast_attack(code: str) -> str:
    tree = ast.parse(code)
    attacker = HostileASTCanonicalizer()
    attacked_tree = attacker.visit(tree)
    ast.fix_missing_locations(attacked_tree)
    return ast.unparse(attacked_tree)

def apply_formatter(filepath: str, tool: str):
    commands = {
        "Black": ["black", "-q", filepath],
        "Ruff": ["ruff", "format", "-q", filepath]
    }
    subprocess.run(commands[tool], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# =====================================================================
# 3. THE THREADED TESTING WORKER
# =====================================================================
def process_single_repository(repo_data, km, verifier):
    repo_name, url = repo_data
    temp_file = f"temp_{repo_name}.py"
    
    result_row = {
        "Repository": repo_name,
        "Downloaded": False,
        "Baseline_Encoded": False,
        "Black_Survived": False,
        "Ruff_Survived": False,
        "AST_Attack_Survived": False,
        "Error_Log": ""
    }
    
    try:
        # 1. Download
        code = requests.get(url).text
        result_row["Downloaded"] = True
        
        # 2. Encode & Baseline Verify
        protected_code = protect_code(code, km)
        if not verifier.verify_code(protected_code):
            result_row["Error_Log"] = "Baseline injection failed."
            return result_row
        result_row["Baseline_Encoded"] = True
        
        # 3. Test Black Formatter
        with open(temp_file, "w", encoding="utf-8") as f: f.write(protected_code)
        apply_formatter(temp_file, "Black")
        with open(temp_file, "r", encoding="utf-8") as f: black_code = f.read()
        result_row["Black_Survived"] = verifier.verify_code(black_code)
        
        # 4. Test Ruff Formatter
        with open(temp_file, "w", encoding="utf-8") as f: f.write(protected_code)
        apply_formatter(temp_file, "Ruff")
        with open(temp_file, "r", encoding="utf-8") as f: ruff_code = f.read()
        result_row["Ruff_Survived"] = verifier.verify_code(ruff_code)
        
        # 5. Test Hostile AST Canonicalizer
        ast_attacked_code = apply_hostile_ast_attack(protected_code)
        result_row["AST_Attack_Survived"] = verifier.verify_code(ast_attacked_code)
        
    except Exception as e:
        result_row["Error_Log"] = str(e).replace('\n', ' | ')
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    return result_row

# =====================================================================
# 4. EXECUTION & CSV EXPORT
# =====================================================================
def run_mass_benchmark(target_count=100):
    print("="*80)
    print(f" ASTHASH EPOCH V: MASS BENCHMARK LABORATORY (Target: {target_count})")
    print("="*80)
    
    km = KeyManager()
    km.generate_and_save_keys()
    verifier = ProvenanceVerifier()
    
    targets = fetch_target_files(target_count)
    results = []
    
    print("\n[*] Commencing Threaded Adversarial Attacks...")
    start_time = time.time()
    
    # Run attacks in parallel to save massive amounts of time
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_single_repository, target, km, verifier) for target in targets]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            results.append(res)
            # Print a progress ticker
            if res["Baseline_Encoded"]:
                status = "✅ PASS" if res["AST_Attack_Survived"] else "❌ FAIL"
                print(f"[{idx+1}/{len(targets)}] {res['Repository'][:25]:<25} -> {status}")
            else:
                print(f"[{idx+1}/{len(targets)}] {res['Repository'][:25]:<25} -> ⚠️ SKIP (Download/Baseline Error)")

    elapsed = time.time() - start_time
    
    # Export to CSV for the Research Paper
    csv_file = "asthash_benchmark_results.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    print("="*80)
    print(f"[+] Benchmark Complete in {elapsed:.2f} seconds.")
    print(f"[+] Raw data exported to: {csv_file}")
    print("="*80)

if __name__ == "__main__":
    # Set this to 100, 500, or 1000 depending on your hardware and time limits
    run_mass_benchmark(target_count=100)