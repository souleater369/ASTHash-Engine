"""
===============================================================================
ASTHASH ENTERPRISE: ACADEMIC METROLOGY FRAMEWORK (v1.1.0)
Target: 100-File Static Corpus
Metrics: Robust F1, Payload Density, FPR, Specificity, Wilson Score CI
===============================================================================
"""
import ast
import os
import csv
import json
import time
import math
import requests
import subprocess
import concurrent.futures
from datetime import datetime
from astrace_enterprise_encoder import KeyManager, protect_code
from astrace_enterprise_decoder import ProvenanceVerifier

# =====================================================================
# 1. THE ADVERSARIAL ATTACK TIERS
# =====================================================================
class ASTCanonicalizationAttack(ast.NodeTransformer):
    """Level 2: Semantic-preserving AST normalization adversary."""
    def visit_Expr(self, node):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return None
        return self.generic_visit(node)
    def visit_Pass(self, node):
        return None
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                if isinstance(node.op, ast.Add): return ast.Constant(value=node.left.value + node.right.value)
                if isinstance(node.op, ast.Sub): return ast.Constant(value=node.left.value - node.right.value)
            except Exception: pass
        elif isinstance(node.op, (ast.Add, ast.Mult)):
            node.left, node.right = node.right, node.left
        return node

class SemanticMutationAttack(ast.NodeTransformer):
    """Level 3: Identifier renaming to break text-based watermarks."""
    def visit_FunctionDef(self, node):
        if not node.name.startswith('__'): node.name = f"obfuscated_{node.name}"
        self.generic_visit(node)
        return node
    def visit_ClassDef(self, node):
        node.name = f"Obfuscated_{node.name}"
        self.generic_visit(node)
        return node

def apply_ast_attack(code: str, attack_class) -> str:
    tree = ast.parse(code)
    attacker = attack_class()
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
# 2. THREAD-SAFE METROLOGY WORKER
# =====================================================================
def evaluate_single_file(row):
    km = KeyManager()
    verifier = ProvenanceVerifier()
    
    repo, domain, url = row["Project"], row["Domain"], row["Raw_URL"]
    temp_file = f"temp_{repo.replace('/', '_')}_{time.time_ns()}.py"
    
    metrics = {
        "Project": repo, "Domain": domain, "AST_Nodes": 0, "Payload_Bits": 672,
        "Encode_Time_ms": 0, "Verify_Time_ms": 0,
        "False_Positive_Check": "ERROR", "Baseline_Verify": "ERROR",
        "Black_Survival": "ERROR", "Ruff_Survival": "ERROR", 
        "Canonical_Survival": "ERROR", "Semantic_Survival": "ERROR"
    }
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200: return metrics
        original_code = response.text
        
        tree = ast.parse(original_code)
        metrics["AST_Nodes"] = sum(1 for _ in ast.walk(tree))
        
        # 1. FALSE POSITIVE CHECK
        metrics["False_Positive_Check"] = verifier.verify_code(original_code)
        
        # 2. ENCODING
        t0 = time.perf_counter()
        protected_code = protect_code(original_code, km)
        metrics["Encode_Time_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        
        # 3. BASELINE VERIFICATION
        t1 = time.perf_counter()
        metrics["Baseline_Verify"] = verifier.verify_code(protected_code)
        metrics["Verify_Time_ms"] = round((time.perf_counter() - t1) * 1000, 2)
        
        if not metrics["Baseline_Verify"]: return metrics 

        # 4. ROBUSTNESS ATTACKS (Levels 1, 2, and 3)
        with open(temp_file, "w", encoding="utf-8") as f: f.write(protected_code)
        apply_formatter(temp_file, "Black")
        with open(temp_file, "r", encoding="utf-8") as f: metrics["Black_Survival"] = verifier.verify_code(f.read())
            
        with open(temp_file, "w", encoding="utf-8") as f: f.write(protected_code)
        apply_formatter(temp_file, "Ruff")
        with open(temp_file, "r", encoding="utf-8") as f: metrics["Ruff_Survival"] = verifier.verify_code(f.read())

        attacked_code_l2 = apply_ast_attack(protected_code, ASTCanonicalizationAttack)
        metrics["Canonical_Survival"] = verifier.verify_code(attacked_code_l2)
        
        attacked_code_l3 = apply_ast_attack(protected_code, SemanticMutationAttack)
        metrics["Semantic_Survival"] = verifier.verify_code(attacked_code_l3)

    except Exception:
        pass 
    finally:
        if os.path.exists(temp_file): os.remove(temp_file)
        
    return metrics

# =====================================================================
# 3. MATH & REPORTING
# =====================================================================
def calc_wilson_ci(p, n, z=1.96):
    """Calculates Wilson Score Interval margin of error."""
    if n == 0: return 0.0
    denominator = 1 + z**2 / n
    center = p + z**2 / (2 * n)
    margin = z * math.sqrt((p * (1 - p)) / n + z**2 / (4 * n**2))
    return margin / denominator

def run_metrology_framework():
    print("\n" + "="*80)
    print(" ASTHASH EPOCH V: ACADEMIC METROLOGY FRAMEWORK (Wilson CI Edition)")
    print("="*80)
    
    KeyManager().generate_and_save_keys()
    
    import sys
    sys_stdout_backup = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    
    results = []
    csv_path = "enterprise/asthash_academic_corpus.csv" if os.path.exists("enterprise/asthash_academic_corpus.csv") else "asthash_academic_corpus.csv"
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        sys.stdout = sys_stdout_backup
        print(f"[-] ERROR: Could not find {csv_path}.")
        return

    sys.stdout = sys_stdout_backup
    print(f"[*] Loaded {len(rows)} files. Initiating multi-tier threaded attacks...")
    sys.stdout = open(os.devnull, 'w')

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(evaluate_single_file, row) for row in rows]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            results.append(res)
            sys.stdout = sys_stdout_backup
            status = "✅ PASS" if res.get("Baseline_Verify") is True else "❌ FAIL"
            print(f"[{idx+1}/{len(rows)}] {res['Project']:<25} | Nodes: {res['AST_Nodes']:<5} | Status: {status}")
            sys.stdout = open(os.devnull, 'w')

    sys.stdout = sys_stdout_backup
    
    total_files = len(results)
    
    tn = sum(1 for r in results if r["False_Positive_Check"] is False)
    fp = sum(1 for r in results if r["False_Positive_Check"] is True)
    neg_err = sum(1 for r in results if r["False_Positive_Check"] == "ERROR")
    
    tp = sum(1 for r in results if r["Baseline_Verify"] is True)
    fn = sum(1 for r in results if r["Baseline_Verify"] is False or r["Baseline_Verify"] == "ERROR")
    
    robust_tp = sum(1 for r in results if 
                    r["Baseline_Verify"] is True and r["Black_Survival"] is True and 
                    r["Ruff_Survival"] is True and r["Canonical_Survival"] is True and 
                    r["Semantic_Survival"] is True)
    robust_fn = (tp + fn) - robust_tp 

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    robust_precision = robust_tp / (robust_tp + fp) if (robust_tp + fp) > 0 else 0.0
    robust_recall = robust_tp / (robust_tp + robust_fn) if (robust_tp + robust_fn) > 0 else 0.0
    robust_f1 = (2 * robust_precision * robust_recall) / (robust_precision + robust_recall) if (robust_precision + robust_recall) > 0 else 0.0
    
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    rec_ci = calc_wilson_ci(recall, total_files)
    rob_rec_ci = calc_wilson_ci(robust_recall, total_files)

    attackable = [r for r in results if r["Baseline_Verify"] is True]
    attack_base = len(attackable)
    
    black_surv = (sum(1 for r in attackable if r["Black_Survival"] is True) / attack_base) if attack_base > 0 else 0.0
    ruff_surv = (sum(1 for r in attackable if r["Ruff_Survival"] is True) / attack_base) if attack_base > 0 else 0.0
    nuke_surv = (sum(1 for r in attackable if r["Canonical_Survival"] is True) / attack_base) if attack_base > 0 else 0.0
    sem_surv = (sum(1 for r in attackable if r["Semantic_Survival"] is True) / attack_base) if attack_base > 0 else 0.0
    
    valid_encodes = [r for r in results if r["Encode_Time_ms"] > 0]
    avg_encode = sum(r["Encode_Time_ms"] for r in valid_encodes) / len(valid_encodes) if valid_encodes else 0.0
    avg_verify = sum(r["Verify_Time_ms"] for r in valid_encodes) / len(valid_encodes) if valid_encodes else 0.0
    avg_density = sum(r["Payload_Bits"] / r["AST_Nodes"] for r in attackable if r["AST_Nodes"] > 0) / attack_base if attack_base > 0 else 0.0

    print("\n" + "="*80)
    print(" 📊 FINAL ACADEMIC METRICS (EPOCH V)")
    print("="*80)
    print(f"Total Files Attempted       : {total_files}")
    print(f"Successfully Protected Files: {attack_base}")
    print(f"Average Encoding Time       : {avg_encode:.2f} ms")
    print(f"Average Verification Time   : {avg_verify:.2f} ms")
    print(f"Average Payload Density     : {avg_density:.4f} bits/node")
    print("-" * 80)
    print(" --- CONFUSION MATRIX & SPECIFICITY ---")
    print(f"True Positives (TP)  : {tp}")
    print(f"True Negatives (TN)  : {tn}")
    print(f"False Positives (FP) : {fp}")
    print(f"False Negatives (FN) : {fn}")
    print(f"Negative Errors      : {neg_err}")
    print(f"Specificity          : {specificity:.4f} (True Negative Rate)")
    print("-" * 80)
    print(" --- SECURITY & ROBUSTNESS SCORES ---")
    print(f"False Positive Rate (FPR) : {fpr:.4f}")
    print(f"Base Detection Recall     : {recall:.3f}  [95% Wilson CI: ±{rec_ci:.3f}]")
    print(f"Robust Detection F1-Score : {robust_f1:.3f}")
    print("-" * 80)
    print(" --- ADVERSARIAL SURVIVAL RATES ---")
    print(f"[Level 1] Black Formatter        : {black_surv*100:.1f}%")
    print(f"[Level 1] Ruff Formatter         : {ruff_surv*100:.1f}%")
    print(f"[Level 2] AST Canonicalization   : {nuke_surv*100:.1f}%")
    print(f"[Level 3] Semantic Mutation      : {sem_surv*100:.1f}%  <-- (Identifier Renaming)")
    print("="*80)

    # Output pure CSV
    out_csv = "enterprise/asthash_metrology_results.csv" if os.path.exists("enterprise") else "asthash_metrology_results.csv"
    with open(out_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Output pure JSON Metadata
    out_json = "enterprise/asthash_metadata.json" if os.path.exists("enterprise") else "asthash_metadata.json"
    metadata = {
        "project": "ASTHASH Enterprise Metrology",
        "date": datetime.now().isoformat(),
        "engine_version": "Epoch V (Macro-Topological)",
        "payload_bits": 672,
        "ci_method": "Wilson Score Interval"
    }
    with open(out_json, "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    run_metrology_framework()