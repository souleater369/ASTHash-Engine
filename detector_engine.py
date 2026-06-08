import ast
import hashlib
import os

def contains_side_effect(node):
    """Safety scanner: must perfectly match the encoder's safety rules."""
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            return True
    return False

class ASTSignatureExtractor(ast.NodeVisitor):
    """Walks the tree and extracts the absolute structural state of valid nodes."""
    def __init__(self):
        self.extracted_bits = []

    def visit_BinOp(self, node):
        # 1. Visit children first (post-order traversal) for stability
        self.generic_visit(node)
        
        # 2. Target only safe commutative operations
        if isinstance(node.op, (ast.Add, ast.Mult)):
            # 3. Skip if it contains a side effect (matching encoder rules)
            if contains_side_effect(node.left) or contains_side_effect(node.right):
                return 
            
            # 4. Extract absolute lexical state
            left_str = ast.unparse(node.left)
            right_str = ast.unparse(node.right)
            
            if left_str > right_str:
                self.extracted_bits.append('1')
            else:
                self.extracted_bits.append('0')

def verify_provenance(file_path, secret_key):
    if not os.path.exists(file_path):
        return False, "File not found."

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False, "Invalid Python syntax in target file."

    # --- PHASE 1: Regenerate expected bitstream ---
    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    expected_binary = bin(int(hex_digest, 16))[2:].zfill(256)

    # --- PHASE 2: Extract actual layout from the file ---
    extractor = ASTSignatureExtractor()
    extractor.visit(tree)
    actual_bits = extractor.extracted_bits

    if not actual_bits:
        return False, "No verified structural blocks found in this file."

    # --- PHASE 3: Compare sequences ---
    nodes_to_check = len(actual_bits)
    
    # We only check up to 256 bits (the length of SHA-256).
    # If the file is massive, we only need the first 256 nodes to prove ownership.
    if nodes_to_check > 256:
        nodes_to_check = 256
        
    target_segment = expected_binary[:nodes_to_check]
    actual_segment = actual_bits[:nodes_to_check]
    
    match_count = sum(1 for a, b in zip(actual_segment, target_segment) if a == b)
    confidence = (match_count / nodes_to_check) * 100

    print(f"\n--- ASTrace Verification Report ---")
    print(f"Valid Nodes Analyzed: {nodes_to_check}")
    print(f"Cryptographic Match Confidence: {confidence:.2f}%")
    
    # In cryptography, a 100% match on an infused file proves origin
    if confidence >= 99.0:
        return True, "PROVENANCE VERIFIED: Structural graph matches the keyholder."
    else:
        return False, "VERIFICATION FAILED: Structure does not match the key."

if __name__ == "__main__":
    print("\n--- ASTrace Detector Subsystem ---")
    target_file = input("Path to file for verification: ").strip().strip("\"'")
    key_to_test = input("Enter Secret Key to verify ownership: ").strip()
    
    success, message = verify_provenance(target_file, key_to_test)
    print(f"Result: {message}")
    print("----------------------------------\n")
if __name__ == "__main__":
    print("--- ASTrace Detector Subsystem ---")
    target_file = input("Path to file for verification: ").strip()
    key_to_test = input("Enter Secret Key to verify ownership: ").strip()
    
    success, message = verify_provenance(target_file, key_to_test)
    print(f"Result: {message}\n")
