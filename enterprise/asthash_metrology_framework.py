"""
===============================================================================
ASTHASH PROTOCOL V2: ADVANCED ACADEMIC METROLOGY FRAMEWORK
Target: 200-File Corporate Corpus (Python 3.12)
Metrics: Precision/F1, Pattern-Guided Attack, Node Deltas, Wilson Bounds, 
         Independent Formatters (Black, Ruff, Pyupgrade, Autoflake)
===============================================================================
"""
import ast
import os
import csv
import json
import time
import math
import uuid
import hashlib
import requests
import subprocess
import concurrent.futures
from datetime import datetime

# Import your core architecture
from astrace_enterprise_encoder import KeyManager, protect_code
from astrace_enterprise_decoder import ProvenanceVerifier

# =====================================================================
# 1. ADVANCED ADVERSARIAL ATTACKS (Game 1 & White-Box)
# =====================================================================
class ASTCanonicalizationAttack(ast.NodeTransformer):
    """Level 2: Semantic-preserving AST normalization adversary."""
    def _clean_body(self, body):
        new_body = []
        for node in body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                continue
            if isinstance(node, ast.Pass):
                continue
            visited_node = self.visit(node)
            if isinstance(visited_node, list):
                new_body.extend(visited_node)
            elif visited_node is not None:
                new_body.append(visited_node)
        if not new_body:
            new_body.append(ast.Pass())
        return new_body

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.body = self._clean_body(node.body)
        return node
        
    def visit_ClassDef(self, node):
        self.generic_visit(node)
        node.body = self._clean_body(node.body)
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            if not node.test.value: return node.orelse if node.orelse else None
            else: return node.body
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                if isinstance(node.op, ast.Add): return ast.Constant(value=node.left.value + node.right.value)
                if isinstance(node.op, ast.Sub): return ast.Constant(value=node.left.value - node.right.value)
                if isinstance(node.op, ast.Mult): return ast.Constant(value=node.left.value * node.right.value)
                if isinstance(node.op, ast.FloorDiv) and node.right.value != 0: 
                    return ast.Constant(value=node.left.value // node.right.value)
            except Exception: pass
        return node

class SemanticMutationAttack(ast.NodeTransformer):
    """Level 3: Global identifier renaming to break lexical/hash signatures."""
    def visit_FunctionDef(self, node):
        if not node.name.startswith('__'): node.name = f"obfuscated_{node.name}"
        self.generic_visit(node)
        return node
    def visit_ClassDef(self, node):
        node.name = f"Obfuscated_{node.name}"
        self.generic_visit(node)
        return node

class PatternGuidedWhiteBoxAttack(ast.NodeTransformer):
    """White-Box Target Attack: Active structural filtering of TMR patterns."""
    def visit_Tuple(self, node):
        self.generic_visit(node)
        if len(node.elts) == 3:
            has_list = any(isinstance(e, ast.List) for e in node.elts)
            has_binop = any(isinstance(e, ast.BinOp) for e in node.elts)
            has_const = any(isinstance(e, ast.Constant) for e in node.elts)
            
            if has_list and has_binop and has_const:
                return None # Adversary actively strips the TMR tuple
        return node

def apply_ast_attack(code: str, attack_class) -> str:
    tree = ast.parse(code)
    attacker = attack_class()
    attacked_tree = attacker.visit(tree)
    ast.fix_missing_locations(attacked_tree)
    return ast.unparse(attacked_tree)

def apply_formatter(filepath: str, tool: str):
    """Independent 3rd-party transformation tools."""
    commands = {
        "Black": ["black", "-q", filepath],
        "Ruff": ["ruff", "format", "-q", filepath],
        "Autoflake": ["autoflake", "--remove-all-unused-imports", "--in-place", filepath],
        "Pyupgrade": ["pyupgrade", filepath]
    }
    subprocess.run(commands[tool], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# =====================================================================
# 2. METROLOGY WORKER ENGINE
# =====================================================================
def evaluate_single_file(row, github_token, run_seed, key_id):
    km = KeyManager()
    verifier = ProvenanceVerifier()
    
    repo, domain, url = row["Project"], row["Domain"], row["Raw_URL"]
    temp_file = f"temp_{uuid.uuid4().hex[:8]}.py"
    
    metrics = {
        "Run_Seed": run_seed, "Key_ID": key_id,
        "Project": repo, "Domain": domain, 
        "Original_Nodes": 0, "Watermarked_Nodes": 0, "Payload_Bits": 0, 
        "Encode_Time_ms": 0, "Verify_Time_ms": 0,
        "False_Positive_Check": "ERROR", "Baseline_Verify": "ERROR",
        "Black_Survival": "ERROR", "Ruff_Survival": "ERROR", 
        "Autoflake_Survival": "ERROR", "Pyupgrade_Survival": "ERROR",
        "Canonical_Survival": "ERROR", "Semantic_Survival": "ERROR", "PatternGuided_Survival": "ERROR",
        "Canonical_Node_Delta": 0.0, "Semantic_Node_Delta": 0.0, "PatternGuided_Node_Delta": 0.0,
        "Failure_Reason": "None"
    }
    
    headers = {'Authorization': f"token {github_token}"} if github_token else {}
    
    try:
        time.sleep(0.5) # Anti-abuse threading block delay
        
        # Network Phase
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                metrics["Failure_Reason"] = f"HTTP Error {response.status_code}"
                return metrics
            original_code = response.text
        except requests.RequestException as e:
            metrics["Failure_Reason"] = f"Network Timeout: {type(e).__name__}"
            return metrics
            
        # Parse Phase
        try:
            tree = ast.parse(original_code)
            metrics["Original_Nodes"] = len(list(ast.walk(tree)))
        except SyntaxError as e:
            metrics["Failure_Reason"] = f"AST Compilation Error: {str(e)}"
            return metrics
        
        # GAME 3: COLLISION RESISTANCE
        metrics["False_Positive_Check"] = verifier.verify_code(original_code)
        
        # BASELINE ENCODING & SPECIFIC OVERHEAD DENSITY LOGGING
        t0 = time.perf_counter()
        protected_code = protect_code(original_code, km)
        metrics["Encode_Time_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        
        protected_tree = ast.parse(protected_code)
        metrics["Watermarked_Nodes"] = len(list(ast.walk(protected_tree)))
        metrics["Payload_Bits"] = km.get_payload_bit_length() if hasattr(km, 'get_payload_bit_length') else 672
        
        t1 = time.perf_counter()
        metrics["Baseline_Verify"] = verifier.verify_code(protected_code)
        metrics["Verify_Time_ms"] = round((time.perf_counter() - t1) * 1000, 2)
        
        if not metrics["Baseline_Verify"]:
            metrics["Failure_Reason"] = "Watermark Encoding Rejection"
            return metrics 

        # ADVERSARIAL TRANSFORMATION MATRIX (GAME 1)
        with open(temp_file, "w", encoding="utf-8") as f: f.write(protected_code)
        
        for tool in ["Black", "Ruff", "Autoflake", "Pyupgrade"]:
            try:
                apply_formatter(temp_file, tool)
                with open(temp_file, "r", encoding="utf-8") as f:
                    metrics[f"{tool}_Survival"] = verifier.verify_code(f.read())
            except Exception as e:
                metrics[f"{tool}_Survival"] = f"Crash: {type(e).__name__}"
            
            with open(temp_file, "w", encoding="utf-8") as f: f.write(protected_code)

        # Level 2 & Delta Node Logging
        attacked_code_l2 = apply_ast_attack(protected_code, ASTCanonicalizationAttack)
        metrics["Canonical_Survival"] = verifier.verify_code(attacked_code_l2)
        l2_nodes = len(list(ast.walk(ast.parse(attacked_code_l2))))
        metrics["Canonical_Node_Delta"] = round(abs(metrics["Watermarked_Nodes"] - l2_nodes) / metrics["Watermarked_Nodes"], 4)
        
        # Level 3 & Delta Node Logging
        attacked_code_l3 = apply_ast_attack(protected_code, SemanticMutationAttack)
        metrics["Semantic_Survival"] = verifier.verify_code(attacked_code_l3)
        l3_nodes = len(list(ast.walk(ast.parse(attacked_code_l3))))
        metrics["Semantic_Node_Delta"] = round(abs(metrics["Watermarked_Nodes"] - l3_nodes) / metrics["Watermarked_Nodes"], 4)
        
        # Pattern-Guided White-Box Attack & Delta Node Logging
        attacked_code_pg = apply_ast_attack(protected_code, PatternGuidedWhiteBoxAttack)
        metrics["PatternGuided_Survival"] = verifier.verify_code(attacked_code_pg)
        pg_nodes = len(list(ast.walk(ast.parse(attacked_code_pg))))
        metrics["PatternGuided_Node_Delta"] = round(abs(metrics["Watermarked_Nodes"] - pg_nodes) / metrics["Watermarked_Nodes"], 4)

    except Exception as e:
        metrics["Failure_Reason"] = f"Runtime Crash: {str(e)}"
    finally:
        if os.path.exists(temp_file): os.remove(temp_file)
        
    return metrics

# =====================================================================
# 3. STATISTICAL VALIDATION ENGINE
# =====================================================================
def get_wilson_interval_string(p, n, z=1.96):
    if n == 0: return "[0.0000, 0.0000]"
    denominator = 1 + z**2 / n
    center_adjusted = p + z**2 / (2 * n)
    margin = z * math.sqrt((p * (1 - p)) / n + z**2 / (4 * n**2))
    lower = max(0.0, (center_adjusted - margin) / denominator)
    upper = min(1.0, (center_adjusted + margin) / denominator)
    return f"[{lower:.4f}, {upper:.4f}]"

def run_metrology_framework():
    print("\n" + "="*80)
    print(" ASTHASH PROTOCOL V2: ADVANCED ACADEMIC METROLOGY FRAMEWORK")
    print("="*80)
    
    # Reproducibility Metadata
    RUN_SEED = str(uuid.uuid4())
    km = KeyManager()
    km.generate_and_save_keys()
    
    try:
        with open("public_key.pem", "rb") as f:
            KEY_ID = hashlib.sha256(f.read()).hexdigest()[:12]
    except FileNotFoundError:
        KEY_ID = "DEV_KEY_001"
        
    print(f"[*] Run Seed (UUID) : {RUN_SEED}")
    print(f"[*] Key ID (SHA-256): {KEY_ID}")
    
    github_token = os.environ.get("GITHUB_PAT")
    if github_token:
        print("[+] GitHub API Token active. Authenticated session initialized.")
    else:
        print("[-] WARNING: GITHUB_PAT empty. Standard limits may drop parsing workers.")
    
    import sys
    sys_stdout_backup = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    
    csv_path = "asthash_academic_corpus.csv"
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        sys.stdout = sys_stdout_backup
        print(f"[-] ERROR: Missing target data file: {csv_path}. Please run generate_corpus.py first.")
        return

    sys.stdout = sys_stdout_backup
    print(f"[*] Parsing target corpus scope: {len(rows)} files. Tuning pipeline threads...")
    sys.stdout = open(os.devnull, 'w')

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(evaluate_single_file, row, github_token, RUN_SEED, KEY_ID) for row in rows]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            results.append(res)
            sys.stdout = sys_stdout_backup
            status = "✅ PASS" if res.get("Baseline_Verify") is True else ("❌ FAIL" if "Network" not in res["Failure_Reason"] and "HTTP" not in res["Failure_Reason"] else "⚠️ DROP")
            print(f"[{idx+1}/{len(rows)}] {res['Project']:<25} | Nodes: {res['Original_Nodes']:<5} | Status: {status} | {res['Failure_Reason']}")
            sys.stdout = open(os.devnull, 'w')

    sys.stdout = sys_stdout_backup
    
    # --- METROLOGY ANALYSIS PARSING LOOP ---
    total_attempted = len(results)
    network_errors = sum(1 for r in results if "Network" in r["Failure_Reason"] or "HTTP" in r["Failure_Reason"])
    valid_results = [r for r in results if "Network" not in r["Failure_Reason"] and "HTTP" not in r["Failure_Reason"]]
    valid_total = len(valid_results)
    
    # CONFUSION MATRIX BASE
    tn = sum(1 for r in valid_results if r["False_Positive_Check"] is False)
    fp = sum(1 for r in valid_results if r["False_Positive_Check"] is True)
    tp = sum(1 for r in valid_results if r["Baseline_Verify"] is True)
    fn = sum(1 for r in valid_results if r["Baseline_Verify"] is False)
    
    attackable = [r for r in valid_results if r["Baseline_Verify"] is True]
    attack_base = len(attackable)

    # ROBUST CONFUSION MATRIX (Survived ALL attacks)
    robust_tp = sum(1 for r in attackable if 
                    r["Black_Survival"] is True and r["Ruff_Survival"] is True and
                    r["Autoflake_Survival"] is True and r["Pyupgrade_Survival"] is True and
                    r["Canonical_Survival"] is True and r["Semantic_Survival"] is True and
                    r["PatternGuided_Survival"] is True)
    robust_fn = (tp + fn) - robust_tp
    
    # PRECISION, RECALL, F1 SCORES
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    robust_precision = robust_tp / (robust_tp + fp) if (robust_tp + fp) > 0 else 0.0
    robust_recall = robust_tp / (robust_tp + robust_fn) if (robust_tp + robust_fn) > 0 else 0.0
    robust_f1 = (2 * robust_precision * robust_recall) / (robust_precision + robust_recall) if (robust_precision + robust_recall) > 0 else 0.0
    
    fpr_calc = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    # SURVIVAL SCORING WITH MATH LOOPS
    b_rate = sum(1 for r in attackable if r["Black_Survival"] is True) / attack_base if attack_base > 0 else 0
    r_rate = sum(1 for r in attackable if r["Ruff_Survival"] is True) / attack_base if attack_base > 0 else 0
    a_rate = sum(1 for r in attackable if r["Autoflake_Survival"] is True) / attack_base if attack_base > 0 else 0
    p_rate = sum(1 for r in attackable if r["Pyupgrade_Survival"] is True) / attack_base if attack_base > 0 else 0
    c_rate = sum(1 for r in attackable if r["Canonical_Survival"] is True) / attack_base if attack_base > 0 else 0
    s_rate = sum(1 for r in attackable if r["Semantic_Survival"] is True) / attack_base if attack_base > 0 else 0
    pg_rate = sum(1 for r in attackable if r["PatternGuided_Survival"] is True) / attack_base if attack_base > 0 else 0
    
    # DELTA STATISTICS (NODE CHANGE RATIO)
    avg_c_delta = sum(r["Canonical_Node_Delta"] for r in attackable) / attack_base if attack_base > 0 else 0
    avg_s_delta = sum(r["Semantic_Node_Delta"] for r in attackable) / attack_base if attack_base > 0 else 0
    avg_pg_delta = sum(r["PatternGuided_Node_Delta"] for r in attackable) / attack_base if attack_base > 0 else 0

    # DYNAMIC PERFORMANCE CHECKERS (OVERHEAD)
    valid_encodes = [r for r in valid_results if r["Encode_Time_ms"] > 0]
    avg_encode = sum(r["Encode_Time_ms"] for r in valid_encodes) / len(valid_encodes) if valid_encodes else 0.0
    avg_verify = sum(r["Verify_Time_ms"] for r in valid_encodes) / len(valid_encodes) if valid_encodes else 0.0
    avg_density = sum(r["Payload_Bits"] / r["Watermarked_Nodes"] for r in attackable if r["Watermarked_Nodes"] > 0) / attack_base if attack_base > 0 else 0.0
    avg_growth = sum((r["Watermarked_Nodes"] - r["Original_Nodes"]) / r["Original_Nodes"] for r in attackable if r["Original_Nodes"] > 0) / attack_base if attack_base > 0 else 0.0

    print("\n" + "="*80)
    print(" 📊 ASTHASH PROTOCOL V2: IEEE METRICS PANE (Unified Edition)")
    print("="*80)
    print(f"Total Files Attempted       : {total_attempted}")
    print(f"Network API Drops (Dropped) : {network_errors}")
    print(f"Valid Evaluation Corpus     : {valid_total} Files")
    print(f"Successfully Encoded (TP)   : {attack_base}")
    print("-" * 80)
    print(" --- EMBEDDING OVERHEAD & PERFORMANCE ---")
    print(f"Average Compiler Tree Growth: +{avg_growth*100:.2f}% (Node Count Increase)")
    print(f"Average Signal Density      : {avg_density:.4f} bits/node")
    print(f"Average Encoding Pipeline   : {avg_encode:.2f} ms")
    print(f"Average Verification Engine : {avg_verify:.2f} ms")
    print("-" * 80)
    print(" --- GAME 3: COLLISION RESISTANCE ---")
    print(f"True Negatives (TN)         : {tn}")
    print(f"False Positives (FP)        : {fp}")
    print(f"Dynamic False Positive Rate : {fpr_calc:.4f}")
    print(f"Specificity Score           : {specificity:.4f}")
    print("-" * 80)
    print(" --- MACRO METRICS (PRECISION, RECALL, F1) ---")
    print(f"Base Detection Recall       : {recall:.3f}  | 95% CI: {get_wilson_interval_string(recall, valid_total)}")
    print(f"Base F1-Score               : {f1_score:.3f}")
    print(f"Robust Detection Recall     : {robust_recall:.3f}  | 95% CI: {get_wilson_interval_string(robust_recall, valid_total)}")
    print(f"Robust F1-Score             : {robust_f1:.3f}")
    print("-" * 80)
    print(" --- GAME 1: ADVERSARIAL ROBUSTNESS & NODE CHANGE RATIO (ΔN) ---")
    print(" [INDEPENDENT FORMATTERS]")
    print(f" Level 1: Black Formatter     : {b_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(b_rate, attack_base)}")
    print(f" Level 1: Ruff Formatter      : {r_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(r_rate, attack_base)}")
    print(f" Level 1: Autoflake Refactor  : {a_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(a_rate, attack_base)}")
    print(f" Level 1: Pyupgrade Syntax    : {p_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(p_rate, attack_base)}")
    print("\n [CUSTOM ADVERSARIAL TRANSFORMS]")
    print(f" Level 2: AST Canonicalizer   : {c_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(c_rate, attack_base)}  [ΔN: {avg_c_delta*100:.1f}%]")
    print(f" Level 3: Identifier Rename   : {s_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(s_rate, attack_base)}  [ΔN: {avg_s_delta*100:.1f}%]")
    print(f" Pattern-Guided White-Box     : {pg_rate*100:.1f}%  | 95% CI: {get_wilson_interval_string(pg_rate, attack_base)}  [ΔN: {avg_pg_delta*100:.1f}%]")
    print("="*80)

    # Write out data arrays
    out_csv = "enterprise/asthash_metrology_results.csv" if os.path.exists("enterprise") else "asthash_metrology_results.csv"
    with open(out_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    out_json = "enterprise/asthash_metadata.json" if os.path.exists("enterprise") else "asthash_metadata.json"
    metadata = {
        "Project": "ASTHASH Protocol V2 Metrology",
        "Run_Seed": RUN_SEED,
        "Key_ID": KEY_ID,
        "Timestamp": datetime.now().isoformat(),
        "CI_Method": "Wilson Score Interval",
        "Target_Files": valid_total,
        "Payload_Bits": 672
    }
    with open(out_json, "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    run_metrology_framework()