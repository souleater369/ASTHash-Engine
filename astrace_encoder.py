"""
===============================================================================
ASTrace: Transformation-Invariant Code Provenance Engine
Version: 1.0.1 (Enterprise Release - Symmetrical Evasion Patch)
Author: Arna Nandi
License: MIT License (Defensive Publication)

COPYRIGHT (c) 2026 Arna Nandi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
===============================================================================
"""

import ast
import hashlib
import os
import sys
from typing import Set, List, Dict

def generate_bitstream(secret_key: str) -> str:
    """Generates a 256-bit binary sequence from the cryptographic key."""
    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    return bin(int(hex_digest, 16))[2:].zfill(256)

def is_safe_leaf_node(node: ast.BinOp) -> bool:
    """Enforces Leaf-Node Isolation to guarantee synchronization and short-circuit safety."""
    for child in ast.walk(node.left):
        if isinstance(child, (ast.Call, ast.BinOp)):
            return False
    for child in ast.walk(node.right):
        if isinstance(child, (ast.Call, ast.BinOp)):
            return False
    return True

class ASTWatermarker(ast.NodeTransformer):
    """Deterministically transposes commutative nodes via Post-Order Traversal."""
    def __init__(self, bitstream: str):
        self.bitstream = bitstream
        self.bit_index = 0
        self.nodes_modified = 0

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if not is_safe_leaf_node(node):
                return node
                
            left_str = ast.unparse(node.left)
            right_str = ast.unparse(node.right)
            
            # --- SECURITY PATCH: Symmetrical Node Evasion ---
            if left_str == right_str:
                return node
            # ------------------------------------------------
                
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
                left_str = ast.unparse(node.left)
                right_str = ast.unparse(node.right)
                if left_str != right_str:
                    count += 1
    return count

def auto_detect_profile(tree: ast.AST) -> str:
    """Multi-Factor Heuristic Scanner for 8 distinct enterprise domains."""
    scores: Dict[str, int] = {"web": 0, "ml": 0, "game": 0, "cyber": 0, "cli": 0, "web3": 0, "iot": 0, "lib": 0}
    
    domain_imports = {
        "web": ["flask", "django", "fastapi", "requests", "http", "urllib", "starlette"],
        "ml": ["numpy", "pandas", "torch", "tensorflow", "sklearn", "keras", "scipy"],
        "game": ["pygame", "arcade", "pyglet", "turtle"],
        "cyber": ["socket", "scapy", "cryptography", "hashlib", "paramiko"],
        "cli": ["argparse", "sys", "os", "click", "subprocess", "typer", "rich"],
        "web3": ["web3", "eth_account", "solcx", "brownie", "vyper"],
        "iot": ["rpi.gpio", "machine", "micropython", "smbus", "serial"]
    }
    
    domain_vocab = {
        "web": ["request", "response", "app", "get", "post", "html", "session", "json"],
        "ml": ["tensor", "weight", "bias", "loss", "epoch", "predict", "train", "dataset"],
        "game": ["player", "sprite", "screen", "fps", "render", "collision", "draw"],
        "cyber": ["payload", "buffer", "packet", "shell", "ip", "port", "encrypt"],
        "cli": ["args", "parser", "command", "exit_code", "stdin", "stdout", "console"],
        "web3": ["contract", "transaction", "gas", "wallet", "block", "chain", "wei"],
        "iot": ["gpio", "pin", "sensor", "voltage", "i2c", "pwm", "baud"]
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
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', '') in ["route", "get", "post", "put"]:
                    scores["web"] += 2

        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.MatMult):
                scores["ml"] += 3

    best_profile = max(scores, key=scores.get)
    return best_profile if scores[best_profile] > 0 else "lib"

def get_existing_names(tree: ast.AST) -> Set[str]:
    """AST Symbol Table builder: Prevents Namespace Shadowing."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name): names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)): names.add(node.name)
        elif isinstance(node, ast.arg): names.add(node.arg)
    return names

def inject_scattered_padding(tree: ast.AST, num_needed: int, profile: str) -> ast.AST:
    """Scatters asymmetric entropy safely with Execution Flow Protection."""
    prefixes = {
        "web": "sys_buf_", "ml": "layer_alpha_", "cli": "err_mem_fault_",
        "game": "sprite_offset_", "cyber": "tcp_socket_node_",
        "web3": "_tx_gas_limit_buffer_", "iot": "_gpio_clock_cycle_sync_", "lib": "flag_cache_"
    }
    prefix = prefixes.get(profile, "flag_cache_")
    existing_names = get_existing_names(tree)
    
    blocks: List[List[ast.stmt]] = [tree.body]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            blocks.append(node.body)

    current_idx = 0
    for i in range(num_needed):
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
    """Main execution pipeline."""
    if not os.path.exists(file_path):
        sys.exit(f"[-] FATAL ERROR: File '{file_path}' not found or inaccessible.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except PermissionError:
        sys.exit(f"[-] FATAL ERROR: Permission denied when attempting to read '{file_path}'.")

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        sys.exit(f"[-] FATAL ERROR: Target file contains invalid Python syntax.\n    Details: {e}")
    
    detected_profile = auto_detect_profile(tree)
    print(f"[*] Heuristic Scanner: Environment classified as [{detected_profile.upper()}]")
    
    available_nodes = count_commutative_nodes(tree)
    required_nodes = 32 
    
    if available_nodes < required_nodes:
        padding = required_nodes - available_nodes
        print(f"[*] Entropy validation failed. Scattering {padding} dummy nodes using '{detected_profile}' camouflage...")
        tree = inject_scattered_padding(tree, padding, detected_profile)
    else:
        print("[*] Natural entropy sufficient. No artificial padding required.")
    
    bitstream = generate_bitstream(secret_key)
    watermarker = ASTWatermarker(bitstream)
    watermarked_tree = watermarker.visit(tree)
    ast.fix_missing_locations(watermarked_tree)
    
    watermarked_code = ast.unparse(watermarked_tree)
    output_path = file_path.replace(".py", "_watermarked.py")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(watermarked_code)
    except IOError as e:
        sys.exit(f"[-] FATAL ERROR: Could not write output file.\n    Details: {e}")
        
    print(f"[+] SUCCESS: Provenance established.")
    print(f"[+] Output File: {output_path}")
    print(f"[+] Nodes Mathematically Transposed: {watermarker.nodes_modified}")

if __name__ == "__main__":
    print("\n===============================================")
    print("    ASTrace Autonomous Provenance Engine")
    print("    Enterprise Release v1.0.1")
    print("===============================================\n")
    target = input("Enter target file path: ").strip().strip("\"'")
    key = input("Enter secret key: ").strip()
    
    process_file(target, key)
    print("\n===============================================\n")