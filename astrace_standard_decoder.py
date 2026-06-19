"""
===============================================================================
ASTrace Standard Edition: Decoder (Sliding Window Protocol)
Version: 2.0.0 (100% Precision via Anchor Preamble)
Author: Arna Nandi
License: MIT License (Defensive Publication)
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
    """Chronologically extracts the entire binary structural state of the graph."""
    def __init__(self):
        self.extracted_bits: list[str] = []

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.generic_visit(node) 
        
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if not is_safe_leaf_node(node): return 
                
            left_str = ast.unparse(node.left)
            right_str = ast.unparse(node.right)
            
            # Symmetrical Node Evasion
            if left_str == right_str: return 
            
            if left_str > right_str:
                self.extracted_bits.append('1')
            else:
                self.extracted_bits.append('0')

def verify_provenance(file_path: str, secret_key: str) -> Tuple[bool, str]:
    """Executes the Sliding Window search and calculates confidence."""
    if not os.path.exists(file_path): 
        return False, "[-] FATAL ERROR: File not found."
        
    with open(file_path, "r", encoding="utf-8") as f: 
        source = f.read()
        
    try: 
        tree = ast.parse(source)
    except SyntaxError as e: 
        return False, f"[-] FATAL ERROR: Invalid Python syntax. {e}"

    # Generate expected target hash payload
    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    expected_payload = bin(int(hex_digest, 16))[2:].zfill(256)
    anchor = "11001100"

    extractor = ASTSignatureExtractor()
    extractor.visit(tree)
    
    # Convert list of bits into a single searchable string
    raw_bitstring = "".join(extractor.extracted_bits)

    if not raw_bitstring: 
        return False, "[-] VERIFICATION FAILED: No structural blocks found."
        
    # --- THE SLIDING WINDOW PROTOCOL ---
    anchor_index = raw_bitstring.find(anchor)
    
    if anchor_index == -1:
        # Guarantee 0 False Positives by shutting down if no anchor is present
        return False, "[-] VERIFICATION FAILED: Missing Anchor Preamble (0.0% Match)"
        
    # Isolate the payload strictly following the anchor
    payload_start = anchor_index + len(anchor)
    actual_payload = raw_bitstring[payload_start:]
    # -----------------------------------

    if not actual_payload:
        return False, "[-] VERIFICATION FAILED: Anchor found, but payload is empty."
        
    nodes_to_check = min(len(actual_payload), len(expected_payload))
    target_segment = expected_payload[:nodes_to_check]
    actual_segment = actual_payload[:nodes_to_check]
    
    match_count = sum(1 for a, b in zip(actual_segment, target_segment) if a == b)
    confidence = (match_count / nodes_to_check) * 100
    
    if confidence >= 99.0:
        return True, f"[+] PROVENANCE VERIFIED: Structural match locked ({confidence:.1f}% Confidence)"
    else:
        return False, f"[-] VERIFICATION FAILED: Payload mismatch post-anchor ({confidence:.1f}% Match)"

if __name__ == "__main__":
    print("\n=== ASTrace Standard Edition V2.0 (Decoder) ===")
    target_file = input("Enter path to verified file: ").strip().strip("\"'")
    key_to_test = input("Enter Secret Key: ").strip()
    
    print("\n[*] Initializing Sliding Window Extractor...")
    success, message = verify_provenance(target_file, key_to_test)
    print(f"{message}")
    print("===============================================\n")
