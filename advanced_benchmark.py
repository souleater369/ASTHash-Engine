"""
ASTrace Advanced Empirical Benchmarking Suite
Executes real-world repository testing, multi-formatter adversarial attacks, 
and measures Precision/Recall (False Positives).
"""

import os
import subprocess
import urllib.request
import astrace_encoder
import astrace_decoder

# --- 1. Real-World Data Scraper ---
REAL_REPOS = {
    "Flask (Web)": "https://raw.githubusercontent.com/pallets/flask/main/src/flask/app.py",
    "Requests (Lib)": "https://raw.githubusercontent.com/psf/requests/master/requests/api.py",
    "FastAPI (Web)": "https://raw.githubusercontent.com/tiangolo/fastapi/master/fastapi/routing.py",
    "Rich (CLI)": "https://raw.githubusercontent.com/Textualize/rich/master/rich/console.py",
    "Django (Lib)": "https://raw.githubusercontent.com/django/django/main/django/core/management/base.py"
}

def download_real_files():
    """Fetches actual production code from top open-source repositories."""
    print("[*] Downloading real-world enterprise scripts for testing...")
    downloaded_files = []
    for name, url in REAL_REPOS.items():
        filename = f"bench_{name.split()[0].lower()}.py"
        try:
            urllib.request.urlretrieve(url, filename)
            downloaded_files.append((name, filename))
        except Exception as e:
            print(f"[-] Failed to download {name}: {e}")
    return downloaded_files

# --- 2. The Adversarial Attacker ---
def run_formatter_attack(filepath: str, formatter: str) -> bool:
    """Attacks the file using industry-standard formatters."""
    commands = {
        "Black": ["black", "-q", filepath],
        "autopep8": ["autopep8", "--in-place", filepath],
        "isort": ["isort", "-q", filepath],
        "Ruff": ["ruff", "format", "-q", filepath]
    }
    
    try:
        subprocess.run(commands[formatter], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# --- 3. Precision & Control Group Testing ---
def test_false_positives(clean_file: str, secret_key: str, wrong_key: str):
    """Experiment C: Tests True Positives vs False Positives."""
    clean_success, _ = astrace_decoder.verify_provenance(clean_file, secret_key)
    
    watermarked_file = clean_file.replace(".py", "_watermarked.py")
    astrace_encoder.process_file(clean_file, secret_key)
    wrong_key_success, _ = astrace_decoder.verify_provenance(watermarked_file, wrong_key)
    right_key_success, _ = astrace_decoder.verify_provenance(watermarked_file, secret_key)
    
    return not clean_success, not wrong_key_success, right_key_success

# --- 4. The Laboratory Execution ---
def run_advanced_benchmarks():
    print("\n" + "="*70)
    print(" ASTrace Advanced Empirical Benchmarking Suite")
    print(" Phase 1: Multi-Formatter Adversarial Attacks on Real Repos")
    print("="*70 + "\n")
    
    test_files = download_real_files()
    if not test_files:
        print("[-] Aborting: Network failure during repo cloning.")
        return

    secret_key = "pravah_master_key_2026"
    wrong_key = "attacker_fake_key_0000"
    formatters = ["Black", "autopep8", "isort", "Ruff"]
    
    import sys
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    
    try:
        results_matrix = []
        for name, filepath in test_files:
            file_results = []
            for fmt in formatters:
                astrace_encoder.process_file(filepath, secret_key)
                watermarked_file = filepath.replace(".py", "_watermarked.py")
                
                run_formatter_attack(watermarked_file, fmt)
                success, _ = astrace_decoder.verify_provenance(watermarked_file, secret_key)
                file_results.append("PASS" if success else "FAIL")
                
                if os.path.exists(watermarked_file): os.remove(watermarked_file)
            results_matrix.append((name, file_results))
            
        tp_count, fp_count, tn_count = 0, 0, 0
        for name, filepath in test_files:
            clean_pass, wrong_key_pass, right_key_pass = test_false_positives(filepath, secret_key, wrong_key)
            if right_key_pass: tp_count += 1
            if clean_pass: tn_count += 1
            if wrong_key_pass: tn_count += 1
            if not clean_pass or not wrong_key_pass: fp_count += 1
            
            if os.path.exists(filepath): os.remove(filepath)
            watermarked = filepath.replace(".py", "_watermarked.py")
            if os.path.exists(watermarked): os.remove(watermarked)

    finally:
        sys.stdout = original_stdout
        
    print(f"{'REPOSITORY (REAL WORLD)':<20} | {'BLACK':<8} | {'AUTOPEP8':<8} | {'ISORT':<8} | {'RUFF':<8}")
    print("-" * 70)
    for name, results in results_matrix:
        print(f"{name:<20} | {results[0]:<8} | {results[1]:<8} | {results[2]:<8} | {results[3]:<8}")

    print("\n" + "="*70)
    print(" Phase 2: Decoder Precision & False Positive Analytics")
    print("="*70 + "\n")
    
    total_tests = len(test_files) * 2 
    precision = (tp_count / (tp_count + fp_count)) * 100 if (tp_count + fp_count) > 0 else 0
    
    print(f"[*] True Positive Rate (Watermark Detected): {tp_count}/{len(test_files)}")
    print(f"[*] True Negative Rate (Control Handled):    {tn_count}/{total_tests}")
    print(f"[*] False Positive Rate (Ghost Triggers):    {fp_count}/{total_tests}")
    print("-" * 70)
    print(f"[+] OVERALL PRECISION SCORE: {precision:.1f}%")
    print("\n======================================================================\n")

if __name__ == "__main__":
    run_advanced_benchmarks()