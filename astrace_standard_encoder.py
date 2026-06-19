"""
===============================================================================
ASTrace Standard Edition: Encoder
Version: 2.0.0 (The Anchor Protocol & Weighted Heuristics)
Author: Arna Nandi
License: MIT License (Defensive Publication)
===============================================================================
"""

import ast
import hashlib
import os
import sys
from typing import Set, List, Dict

def generate_bitstream(secret_key: str) -> str:
    """Generates a 264-bit payload: 8-bit Anchor + 256-bit Key Hash."""
    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    payload = bin(int(hex_digest, 16))[2:].zfill(256)
    
    # THE ANCHOR PROTOCOL: 8-bit Preamble to guarantee 100% Precision
    anchor = "11001100" 
    return anchor + payload

def is_safe_leaf_node(node: ast.BinOp) -> bool:
    """Enforces Leaf-Node Isolation to guarantee synchronization."""
    for child in ast.walk(node.left):
        if isinstance(child, (ast.Call, ast.BinOp)): return False
    for child in ast.walk(node.right):
        if isinstance(child, (ast.Call, ast.BinOp)): return False
    return True

class ASTWatermarker(ast.NodeTransformer):
    """Deterministically transposes nodes, embedding the Anchor and Payload."""
    def __init__(self, bitstream: str):
        self.bitstream = bitstream
        self.bit_index = 0
        self.nodes_modified = 0

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if not is_safe_leaf_node(node): return node
                
            left_str = ast.unparse(node.left)
            right_str = ast.unparse(node.right)
            
            # Symmetrical Node Evasion
            if left_str == right_str: return node
                
            if self.bit_index < len(self.bitstream):
                bit = self.bitstream[self.bit_index]
                self.bit_index += 1
                
                is_currently_one = left_str > right_str
                
                if bit == '1' and not is_currently_one:
                    node.left, node.right = node.right, node.left
                    self.nodes_modified += 1
                elif bit == '0' and is_currently_one:
                    node.left, node.right = node.right, node.left
                    self.nodes_modified += 1
        return node

def count_commutative_nodes(tree: ast.AST) -> int:
    """Calculates available native cryptographic entropy."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mult)):
            if is_safe_leaf_node(node):
                if ast.unparse(node.left) != ast.unparse(node.right):
                    count += 1
    return count

def auto_detect_profile(tree: ast.AST) -> Dict[str, float]:
    """Weighted Heuristic: Returns a probability distribution of the domain."""
    scores: Dict[str, int] = {"web": 0, "ml": 0, "game": 0, "cyber": 0, "cli": 0, "web3": 0, "iot": 0, "lib": 0}
    
    domain_imports = {
        "web": ["flask", "django", "fastapi", "requests", "http", "urllib"],
        "ml": ["numpy", "pandas", "torch", "tensorflow", "sklearn", "keras"],
        "game": ["pygame", "arcade", "pyglet", "turtle"],
        "cyber": ["socket", "scapy", "cryptography", "hashlib", "paramiko"],
        "cli": ["argparse", "sys", "os", "click", "subprocess", "rich"],
        "web3": ["web3", "eth_account", "solcx", "brownie"],
        "iot": ["rpi.gpio", "machine", "micropython", "serial"]
    }
    
    domain_vocab = {
        "web": ["request", "response", "app", "get", "post", "html", "json"],
        "ml": ["tensor", "weight", "bias", "loss", "epoch", "predict", "train"],
        "game": ["player", "sprite", "screen", "fps", "render", "collision"],
        "cyber": ["payload", "buffer", "packet", "shell", "ip", "encrypt"],
        "cli": ["args", "parser", "command", "exit_code", "stdout", "console"],
        "web3": ["contract", "transaction", "gas", "wallet", "block"],
        "iot": ["gpio", "pin", "sensor", "voltage", "i2c", "pwm"]
    }

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name.lower() for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module.lower())
            for profile, keywords in domain_imports.items():
                if any(kw in name for name in names for kw in keywords):
                    scores[profile] += 3
        elif isinstance(node, ast.Name):
            for profile, keywords in domain_vocab.items():
                if any(kw in node.id.lower() for kw in keywords):
                    scores[profile] += 1
        elif isinstance(node, ast.FunctionDef):
            for profile, keywords in domain_vocab.items():
                if any(kw in node.name.lower() for kw in keywords):
                    scores[profile] += 1
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult):
            scores["ml"] += 3

    total_score = sum(scores.values())
    if total_score == 0:
        return {"lib": 1.0}

    distribution = {profile: (score / total_score) for profile, score in scores.items() if score > 0}
    return dict(sorted(distribution.items(), key=lambda item: item[1], reverse=True))

def get_existing_names(tree: ast.AST) -> Set[str]:
    """AST Symbol Table builder: Prevents Namespace Shadowing."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name): names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)): names.add(node.name)
        elif isinstance(node, ast.arg): names.add(node.arg)
    return names

def inject_scattered_padding(tree: ast.AST, num_needed: int, profile_distribution: Dict[str, float]) -> ast.AST:
    """Scatters entropy proportionally based on the heuristic distribution."""
    prefixes = {
        "web": "sys_buf_", "ml": "layer_alpha_", "cli": "err_mem_fault_",
        "game": "sprite_offset_", "cyber": "tcp_socket_node_",
        "web3": "_tx_gas_limit_buffer_", "iot": "_gpio_clock_cycle_sync_", "lib": "flag_cache_"
    }
    
    # Calculate exact allocation of prefixes based on probability
    allocated_profiles = []
    for profile, probability in profile_distribution.items():
        count = int(round(num_needed * probability))
        allocated_profiles.extend([profile] * count)
        
    while len(allocated_profiles) < num_needed:
        allocated_profiles.append(list(profile_distribution.keys())[0])
    allocated_profiles = allocated_profiles[:num_needed]

    existing_names = get_existing_names(tree)
    blocks: List[List[ast.stmt]] = [tree.body]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            blocks.append(node.body)

    current_idx = 0
    for i in range(num_needed):
        current_profile = allocated_profiles[i]
        prefix = prefixes.get(current_profile, "flag_cache_")
        
        while True:
            safe_name = f"{prefix}{current_idx}"
            if safe_name not in existing_names:
                existing_names.add(safe_name)
                current_idx += 1
                break
            current_idx += 1
        
        assign_stmt = ast.Assign(
            targets=[ast.Name(id=safe_name, ctx=ast.Store())],
            value=ast.BinOp(left=ast.Constant(value=1), op=ast.Add(), right=ast.Constant(value=2))
        )
        
        target_block = blocks[i % len(blocks)]
        start_idx = 0
        if len(target_block) > 0 and isinstance(target_block[0], ast.Expr) and \
           isinstance(target_block[0].value, ast.Constant) and \
           isinstance(target_block[0].value.value, str):
            start_idx = 1
            
        if target_block is tree.body:
            for j in range(start_idx, len(target_block)):
                if not isinstance(target_block[j], (ast.Import, ast.ImportFrom)):
                    start_idx = j
                    break
            else:
                start_idx = len(target_block)
                
        available_slots = len(target_block) - start_idx
        insert_idx = start_idx if available_slots <= 0 else start_idx + (i % (available_slots + 1))
        target_block.insert(insert_idx, assign_stmt)
        
    return tree

def process_file(file_path: str, secret_key: str) -> None:
    if not os.path.exists(file_path):
        sys.exit(f"[-] FATAL ERROR: File '{file_path}' not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        sys.exit(f"[-] FATAL ERROR: Invalid Python syntax. {e}")
    
    distribution = auto_detect_profile(tree)
    print("\n[*] Weighted Heuristic Distribution:")
    for prof, pct in distribution.items():
        print(f"    - {prof.upper()}: {pct*100:.1f}%")
    
    available_nodes = count_commutative_nodes(tree)
    required_nodes = 64 # Increased to guarantee Anchor placement
    
    if available_nodes < required_nodes:
        padding = required_nodes - available_nodes
        print(f"[*] Entropy low. Blending {padding} proportional dummy nodes...")
        tree = inject_scattered_padding(tree, padding, distribution)
    else:
        print("[*] Natural entropy sufficient. No padding required.")
    
    bitstream = generate_bitstream(secret_key)
    watermarker = ASTWatermarker(bitstream)
    watermarked_tree = watermarker.visit(tree)
    ast.fix_missing_locations(watermarked_tree)
    
    watermarked_code = ast.unparse(watermarked_tree)
    output_path = file_path.replace(".py", "_watermarked.py")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(watermarked_code)
        
    print(f"[+] SUCCESS: Anchor and Payload embedded.")
    print(f"[+] Output: {output_path}")

if __name__ == "__main__":
    print("\n=== ASTrace Standard Edition V2.0 (Encoder) ===")
    target = input("Enter target file path: ").strip().strip("\"'")
    key = input("Enter secret key: ").strip()
    process_file(target, key)
    print("===============================================\n")