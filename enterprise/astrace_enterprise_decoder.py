"""
===============================================================================
ASTHASH ENTERPRISE: DECODER (Epoch V - The Master Architecture)
Author: Arna Nandi
Target: Samsung Solve for Tomorrow (Publication Grade)
Features: Majority Voting, Reed-Solomon Repair, Topological Verification
===============================================================================
"""
import ast
import os
import hashlib
import reedsolo
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.exceptions import InvalidSignature

# =====================================================================
# 1. STRUCTURAL FINGERPRINTING
# =====================================================================
def extract_structural_fingerprint(tree: ast.AST) -> bytes:
    """
    Calculates the MACRO-topological map of the AST.
    Only hashes control-flow and definition nodes to prevent the 
    watermark injection from breaking its own cryptographic seal.
    """
    macro_nodes = (
        ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, 
        ast.If, ast.For, ast.AsyncFor, ast.While, 
        ast.Try, ast.With, ast.AsyncWith, ast.Return, ast.Yield
    )
    
    topology = [type(node).__name__ for node in ast.walk(tree) if isinstance(node, macro_nodes)]
    
    if not topology:
        topology = ["ASTHASH_GLOBAL_SEAL"]
        
    return hashlib.sha256("".join(topology).encode('utf-8')).digest()

# =====================================================================
# 2. MULTI-CHANNEL EXTRACTOR (Triple Modular Redundancy)
# =====================================================================
class EpochVExtractor(ast.NodeVisitor):
    """Hunts for the TMR tuples and executes the Majority Vote."""
    def __init__(self):
        self.sequential_bits = []

    def visit_Assign(self, node):
        self.generic_visit(node)
        
        # Hunt for the TMR Tuple, but be flexible if an attacker folded the math
        if isinstance(node.value, ast.Tuple) and len(node.value.elts) == 3:
            elts = node.value.elts
            
            # We strictly check the List (Channel 1) and Type Casting (Channel 3).
            # We ALLOW Channel 2 to be either a BinOp (intact) or a Constant (destroyed by attacker).
            if isinstance(elts[0], ast.List) and isinstance(elts[2], ast.Constant):
                
                votes = 0
                
                # Channel 1: The Array Order (Is it [1, 2]?)
                if len(elts[0].elts) == 2 and isinstance(elts[0].elts[0], ast.Constant):
                    if elts[0].elts[0].value == 1: 
                        votes += 1
                        
                # Channel 2: The Math Identity (Is it an intact x + 0?)
                if isinstance(elts[1], ast.BinOp) and isinstance(elts[1].op, ast.Add): 
                    votes += 1
                # If the attacker folded the math, it yields 0 votes here, 
                # but we STILL process the surviving channels!
                    
                # Channel 3: The Type Casting (Is it an Integer?)
                if isinstance(elts[2].value, int) and not isinstance(elts[2].value, bool): 
                    votes += 1
                
                # MAJORITY VOTE: Best 2 out of 3 determines the true bit
                self.sequential_bits.append('1' if votes >= 2 else '0')


# =====================================================================
# 3. PROVENANCE VERIFIER (ECC Repair & ECDSA Validation)
# =====================================================================
class ProvenanceVerifier:
    def __init__(self, public_key_path="asthash_epoch5_public.pem"):
        self.pub_file = public_key_path
        self.anchor = "11001100"
        self.ecc_bytes = 20
        # 64 bytes (signature) + 20 bytes (ECC) = 84 bytes = 672 bits
        self.payload_length = (64 + self.ecc_bytes) * 8 

    def load_public_key(self):
        if not os.path.exists(self.pub_file):
            raise FileNotFoundError(f"[-] Missing Public Key: {self.pub_file}")
        with open(self.pub_file, "rb") as f:
            return serialization.load_pem_public_key(f.read())

    def verify_code(self, source_code: str) -> bool:
        """Executes the full recovery and cryptographic validation pipeline."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            print("[-] VERIFICATION FAILED: Invalid Python syntax.")
            return False

        # Phase 1: Rebuild the Topological Fingerprint
        fingerprint = extract_structural_fingerprint(tree)

        # Phase 2: Extract Bits via Majority Voting
        extractor = EpochVExtractor()
        extractor.visit(tree)
        raw_bitstring = "".join(extractor.sequential_bits)
        
        # Phase 3: Sliding Window Synchronization
        anchor_idx = raw_bitstring.find(self.anchor)
        if anchor_idx == -1:
            print("[-] VERIFICATION FAILED: Anchor Preamble (11001100) not found. Watermark missing or destroyed.")
            return False
            
        # Isolate exactly 672 bits (Signature + Parity Bytes)
        extracted_binary_sig = raw_bitstring[anchor_idx + len(self.anchor) : anchor_idx + len(self.anchor) + self.payload_length]
        
        if len(extracted_binary_sig) < self.payload_length:
            print(f"[-] VERIFICATION FAILED: Incomplete payload. Found {len(extracted_binary_sig)} bits, expected {self.payload_length}.")
            return False
        
        # Phase 4: Reed-Solomon Error Correction
        try:
            # Convert binary string back to raw bytes
            sig_bytes = int(extracted_binary_sig, 2).to_bytes(84, 'big')
            
            # The RSCodec automatically repairs damaged bytes and strips the 20 parity bytes
            rs = reedsolo.RSCodec(self.ecc_bytes)
            repaired_signature = bytes(rs.decode(sig_bytes)[0])
        except reedsolo.ReedSolomonError:
            print("[-] VERIFICATION FAILED: Reed-Solomon Error Correction failed. Damage exceeds 10% recovery threshold.")
            return False
        except ValueError:
            print("[-] VERIFICATION FAILED: Corrupted bitstream conversion.")
            return False

        # Phase 5: Cryptographic ECDSA Verification
        try:
            # Reconstruct the DER formatting required by the cryptography library
            r, s = int.from_bytes(repaired_signature[:32], 'big'), int.from_bytes(repaired_signature[32:], 'big')
            der_signature = encode_dss_signature(r, s)
            
            public_key = self.load_public_key()
            
            # Verify the signature specifically against this file's topological fingerprint
            public_key.verify(der_signature, fingerprint, ec.ECDSA(hashes.SHA256()))
            print("\n[+] PROVENANCE VERIFIED: Valid Asymmetric ECDSA Signature Detected!")
            print("[+] Topological Fingerprint: MATCHED")
            print("[+] Reed-Solomon Integrity:  VERIFIED")
            return True
            
        except InvalidSignature:
            print("\n[-] VERIFICATION FAILED: ECDSA Signature is Invalid.")
            print("    The watermark exists and was repaired, but the topological fingerprint does not match the signature.")
            print("    (This means the code logic was maliciously altered after the seal was applied).")
            return False

# =====================================================================
# QUICK TEST HARNESS
# =====================================================================
if __name__ == "__main__":
    import sys
    print("\n=== ASTHASH EPOCH V: PUBLIC DECODER ===")
    
    # Simple CLI for quick testing
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                source = f.read()
            verifier = ProvenanceVerifier()
            verifier.verify_code(source)
        else:
            print(f"[-] File not found: {target}")
    else:
        print("[!] Pass a python file to decode: python asthash_epoch5_decoder.py <target_file.py>")