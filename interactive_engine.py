import ast
import hashlib
import os

def generate_bitstream(secret_key):
    """Converts the secret key into a 256-bit binary stream using SHA-256."""
    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    return bin(int(hex_digest, 16))[2:].zfill(256)

def contains_side_effect(node):
    """Safety scanner: checks if a node contains function calls to avoid breaking logic."""
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            return True
    return False

class ASTWatermarker(ast.NodeTransformer):
    """Walks the AST and transposes commutative nodes based on absolute lexical state."""
    def __init__(self, bitstream):
        self.bitstream = bitstream
        self.bit_index = 0
        self.nodes_modified = 0

    def visit_BinOp(self, node):
        # 1. Visit children first (post-order traversal) to build from the bottom up
        self.generic_visit(node)
        
        # 2. Target only safe commutative operations (Addition and Multiplication)
        if isinstance(node.op, (ast.Add, ast.Mult)):
            # 3. Safety check: skip if either side has a function call
            if contains_side_effect(node.left) or contains_side_effect(node.right):
                return node
                
            if self.bit_index < len(self.bitstream):
                bit = self.bitstream[self.bit_index]
                self.bit_index += 1
                
                # 4. Determine the absolute current state of the node
                left_str = ast.unparse(node.left)
                right_str = ast.unparse(node.right)
                is_currently_one = left_str > right_str
                
                # 5. Force the node into the absolute state required by the password bit
                if bit == '1' and not is_currently_one:
                    # It needs to be '1', but it is currently '0'. Swap them.
                    node.left, node.right = node.right, node.left
                    self.nodes_modified += 1
                elif bit == '0' and is_currently_one:
                    # It needs to be '0', but it is currently '1'. Swap them.
                    node.left, node.right = node.right, node.left
                    self.nodes_modified += 1
                    
        return node

def count_commutative_nodes(tree):
    """Counts available valid nodes to check if entropy padding is needed."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mult)):
            if not contains_side_effect(node.left) and not contains_side_effect(node.right):
                count += 1
    return count

def inject_opaque_predicate(tree, num_needed):
    """Injects neutral dummy equations (e.g., _wm_cache = (1*1)+0) for padding."""
    for i in range(num_needed):
        dummy_stmt = ast.Assign(
            targets=[ast.Name(id=f'_wm_cache_{i}', ctx=ast.Store())],
            value=ast.BinOp(
                left=ast.BinOp(
                    left=ast.Constant(value=1),
                    op=ast.Mult(),
                    right=ast.Constant(value=1)
                ),
                op=ast.Add(),
                right=ast.Constant(value=0)
            )
        )
        tree.body.insert(i, dummy_stmt)
    return tree

def process_file(file_path, secret_key):
    if not os.path.exists(file_path):
        print("Error: File not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        print("Error: Target file contains invalid Python syntax.")
        return
    
    # --- PHASE 1: Entropy Check & Padding ---
    available_nodes = count_commutative_nodes(tree)
    required_nodes = 32 # Minimum secure threshold
    
    if available_nodes < required_nodes:
        padding_needed = required_nodes - available_nodes
        print(f"[*] Low entropy detected. Injecting {padding_needed} opaque predicates...")
        tree = inject_opaque_predicate(tree, padding_needed)
    else:
        print("[*] Entropy sufficient. No padding required.")
    
    # --- PHASE 2: Cryptographic Transposition ---
    bitstream = generate_bitstream(secret_key)
    watermarker = ASTWatermarker(bitstream)
    watermarked_tree = watermarker.visit(tree)
    ast.fix_missing_locations(watermarked_tree)
    
    # --- PHASE 3: Reserialize Code ---
    watermarked_code = ast.unparse(watermarked_tree)
    
    output_path = file_path.replace(".py", "_watermarked.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(watermarked_code)
        
    print(f"[+] Success! Watermarked file saved as: {output_path}")
    print(f"[+] Total nodes aligned to signature: {watermarker.nodes_modified}")

if __name__ == "__main__":
    print("\n--- ASTrace Provenance Engine ---")
    target = input("Enter target file path (e.g., script.py): ").strip().strip("\"'")
    key = input("Enter your secret cryptographic key: ").strip()
    process_file(target, key)
    print("---------------------------------\n")
