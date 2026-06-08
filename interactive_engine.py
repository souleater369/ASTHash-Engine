import ast
import hashlib
import os

def generate_bitstream(secret_key):
    """Converts the secret key into a 256-bit binary stream using SHA-256."""
    hex_digest = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    return bin(int(hex_digest, 16))[2:].zfill(256)

class ASTWatermarker(ast.NodeTransformer):
    """Walks the AST and transposes commutative nodes based on the bitstream."""
    def __init__(self, bitstream):
        self.bitstream = bitstream
        self.bit_index = 0
        self.nodes_modified = 0

    def visit_BinOp(self, node):
        self.generic_visit(node)
        # Target only safe commutative operations: Addition and Multiplication
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if self.bit_index < len(self.bitstream):
                bit = self.bitstream[self.bit_index]
                self.bit_index += 1
                
                # If the bit is '1', physically swap the left and right nodes
                if bit == '1':
                    node.left, node.right = node.right, node.left
                    self.nodes_modified += 1
        return node

def count_commutative_nodes(tree):
    """Counts available + and * operations to check if padding is needed."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mult)):
            count += 1
    return count

def inject_opaque_predicate(tree, num_needed):
    """Injects neutral dummy equations (e.g., _wm_cache = (1*1)+0) for entropy padding."""
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

    tree = ast.parse(source)
    
    # 1. Entropy Check & Padding
    available_nodes = count_commutative_nodes(tree)
    required_nodes = 32 # Minimum secure threshold
    
    if available_nodes < required_nodes:
        padding_needed = required_nodes - available_nodes
        print(f"[*] Low entropy detected. Injecting {padding_needed} opaque predicates...")
        tree = inject_opaque_predicate(tree, padding_needed)
    
    # 2. Cryptographic Transposition
    bitstream = generate_bitstream(secret_key)
    watermarker = ASTWatermarker(bitstream)
    watermarked_tree = watermarker.visit(tree)
    ast.fix_missing_locations(watermarked_tree)
    
    # 3. Reserialize Code
    watermarked_code = ast.unparse(watermarked_tree)
    
    output_path = file_path.replace(".py", "_watermarked.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(watermarked_code)
        
    print(f"[+] Success! Watermarked file saved as: {output_path}")
    print(f"[+] Structural nodes transposed: {watermarker.nodes_modified}")

if __name__ == "__main__":
    print("--- ASTrace Provenance Engine ---")
    target = input("Enter target file path (e.g., script.py): ").strip()
    key = input("Enter your secret cryptographic key: ").strip()
    process_file(target, key)
