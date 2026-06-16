"""
===============================================================================
ASTrace: Verification Decoder
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
from typing import Tuple

def is_safe_leaf_node(node: ast.BinOp) -> bool:
    """Validates that the node complies with Leaf-Node Isolation standards."""
    for child in ast.walk(node.left):
        if isinstance(child, (ast.Call, ast.BinOp)): return False
    for child in ast.walk(node.right):
        if isinstance(child, (ast.Call, ast.BinOp)): return False
    return True

class ASTSignatureExtractor(ast.NodeVisitor):
    """Traverses the AST and chronologically extracts the binary structural state."""
    def __init__(self):
        self.extracted_bits: list[str] = []

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.generic_visit(node) 
        
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if not is_safe_leaf_node(node):
                return 
                
            left_str = ast.unparse(node.left)
            right_str = ast.unparse(node.right)
            
            # --- SECURITY PATCH: Symmetrical Node Evasion ---
            if left_str == right_str:
                return 
            # ------------------------------------------------
            
            if left_str > right_str:
                self.extracted_bits.append('1')
            else:
                self.extracted_bits.append('0')

def verify_provenance(file_path: str, secret_key: str) -> Tuple[bool, str]:
    """Executes the verification logic and calculates cryptographic confidence."""
    if not os.path.exists(file_path): 
        return False, "[-] FATAL ERROR: File not found or inaccessible."
        
    try:
        with open(file_path, "r", encoding="utf-8") as f: 
            source = f.read()
    except PermissionError:
        return False, "[-] FATAL ERROR: Permission denied."
        
    try: 
        tree = ast.parse(source)
    except SyntaxError as e: 
        return False, f"[-] FATAL ERROR: Invalid Python syntax. The graph cannot be parsed.\n    Details: {e}"

    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    expected_binary = bin(int(hex_digest, 16))[2:].zfill(256)

    extractor = ASTSignatureExtractor()
    extractor.visit(tree)
    actual_bits = extractor.extracted_bits

    if not actual_bits: 
        return False, "[-] VERIFICATION FAILED: No valid structural blocks found. Entropy is zero."
        
    nodes_to_check = min(len(actual_bits), 256)
    target_segment = expected_binary[:nodes_to_check]
    actual_segment = actual_bits[:nodes_to_check]
    
    match_count = sum(1 for a, b in zip(actual_segment, target_segment) if a == b)
    confidence = (match_count / nodes_to_check) * 100
    
    if confidence >= 99.0:
        return True, f"[+] PROVENANCE VERIFIED: Structure matches keyholder ({confidence:.1f}% Match Confidence)"
    else:
        return False, f"[-] VERIFICATION FAILED: Structure mismatch ({confidence:.1f}% Match Confidence)"

if __name__ == "__main__":
    print("\n===============================================")
    print("    ASTrace Verification Decoder")
    print("    Enterprise Release v1.0.1")
    print("===============================================\n")
    
    target_file = input("Enter path to verified file: ").strip().strip("\"'")
    key_to_test = input("Enter Secret Key: ").strip()
    
    print("\n[*] Initializing structural graph traversal...")
    success, message = verify_provenance(target_file, key_to_test)
    print(f"{message}")
    print("\n===============================================\n")
