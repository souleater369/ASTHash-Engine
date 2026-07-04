"""
===============================================================================
ASTHASH ENTERPRISE: ENCODER (Epoch V - The Master Architecture)
Author: Arna Nandi
Target: Samsung Solve for Tomorrow (Publication Grade)
Features: Topological Fingerprinting, Reed-Solomon ECC, Triple Modular Redundancy
===============================================================================
"""
import ast
import math
import random
import os
import hashlib
import reedsolo
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

# =====================================================================
# 1. CRYPTOGRAPHIC BINDING & ERROR CORRECTION
# =====================================================================
class KeyManager:
    def __init__(self, key_name="asthash_epoch5"):
        self.priv_file = f"{key_name}_private.pem"
        self.pub_file = f"{key_name}_public.pem"
        self.anchor = "11001100"
        self.ecc_bytes = 20 # Reed-Solomon parity bytes

    def generate_and_save_keys(self):
        private_key = ec.generate_private_key(ec.SECP256R1())
        with open(self.priv_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(self.pub_file, "wb") as f:
            f.write(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        return private_key

    def load_private_key(self):
        with open(self.priv_file, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def get_binary_payload(self, fingerprint: bytes) -> str:
        """Signs the structural fingerprint and applies Reed-Solomon ECC."""
        priv_key = self.load_private_key()
        der_signature = priv_key.sign(fingerprint, ec.ECDSA(hashes.SHA256()))
        
        # 1. Normalize ECDSA signature to exactly 64 bytes (512 bits)
        r, s = decode_dss_signature(der_signature)
        raw_signature = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
        
        # 2. Apply Reed-Solomon Error Correction (64 bytes + 20 bytes ECC = 84 bytes)
        rs = reedsolo.RSCodec(self.ecc_bytes)
        encoded_payload = rs.encode(raw_signature)
        
        # 3. Convert to binary and prepend the Anchor
        binary_sig = "".join(f"{byte:08b}" for byte in encoded_payload)
        return self.anchor + binary_sig

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
# 2. THE INTELLIGENCE LAYER (Deep Camouflage & Safety)
# =====================================================================
class DeepHeuristicScanner(ast.NodeVisitor):
    """Deep 7-Domain Softmax Vocabulary Scanning for true stealth."""
    def __init__(self):
        self.scores = {"web": 0, "ml": 0, "game": 0, "cyber": 0, "cli": 0, "web3": 0, "iot": 0, "lib": 0}
        self.domain_imports = {
            "web": ["flask", "django", "fastapi", "requests", "http", "urllib"],
            "ml": ["numpy", "pandas", "torch", "tensorflow", "sklearn", "keras"],
            "game": ["pygame", "arcade", "pyglet", "turtle"],
            "cyber": ["socket", "scapy", "cryptography", "hashlib", "paramiko"],
            "cli": ["argparse", "sys", "os", "click", "subprocess", "rich"],
            "web3": ["web3", "eth_account", "solcx", "brownie"],
            "iot": ["rpi.gpio", "machine", "micropython", "serial"]
        }
        self.domain_vocab = {
            "web": ["request", "response", "app", "get", "post", "html", "json"],
            "ml": ["tensor", "weight", "bias", "loss", "epoch", "predict", "train"],
            "game": ["player", "sprite", "screen", "fps", "render", "collision"],
            "cyber": ["payload", "buffer", "packet", "shell", "ip", "encrypt"],
            "cli": ["args", "parser", "command", "exit_code", "stdout", "console"],
            "web3": ["contract", "transaction", "gas", "wallet", "block"],
            "iot": ["gpio", "pin", "sensor", "voltage", "i2c", "pwm"]
        }

    def visit_Import(self, node):
        names = [alias.name.lower() for alias in node.names]
        self._score_imports(names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        names = [alias.name.lower() for alias in node.names]
        if node.module: names.append(node.module.lower())
        self._score_imports(names)
        self.generic_visit(node)

    def _score_imports(self, names):
        for profile, keywords in self.domain_imports.items():
            if any(kw in name for name in names for kw in keywords):
                self.scores[profile] += 3

    def visit_Name(self, node):
        for profile, keywords in self.domain_vocab.items():
            if any(kw in node.id.lower() for kw in keywords):
                self.scores[profile] += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for profile, keywords in self.domain_vocab.items():
            if any(kw in node.name.lower() for kw in keywords):
                self.scores[profile] += 1
        self.generic_visit(node)

    def generate_weighted_vocabulary(self, total_bits: int) -> list:
        total_score = sum(self.scores.values())
        if total_score == 0:
            return ["flag_cache"] * total_bits
            
        distribution = {profile: (score / total_score) for profile, score in self.scores.items() if score > 0}
        prefixes = {
            "web": "sys_buf", "ml": "layer_alpha", "cli": "err_mem_fault",
            "game": "sprite_offset", "cyber": "tcp_socket_node",
            "web3": "tx_gas_limit", "iot": "gpio_clock_sync", "lib": "flag_cache"
        }
        
        allocated = []
        for domain, probability in distribution.items():
            count = int(round(total_bits * probability))
            allocated.extend([prefixes[domain]] * count)
            
        while len(allocated) < total_bits:
            allocated.append(prefixes[list(distribution.keys())[0]])
            
        random.shuffle(allocated)
        return allocated[:total_bits]

def get_existing_names(tree: ast.AST) -> set:
    """Complete recursive identifier extraction to prevent namespace collisions."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name): names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)): names.add(node.name)
        elif isinstance(node, ast.arg): names.add(node.arg)
    return names


# =====================================================================
# 3. TRIPLE MODULAR REDUNDANCY INJECTOR
# =====================================================================
class EpochVEncoder(ast.NodeTransformer):
    """Injects bits across 3 independent AST channels flatly to evade control-flow analysis."""
    def __init__(self, bitstream: str, safe_zones: list, camouflage_pool: list, existing_names: set):
        self.bitstream = bitstream
        self.safe_zones = safe_zones
        self.camouflage = camouflage_pool
        self.existing_names = existing_names
        self.bit_idx = 0
        self.chunk_size = math.ceil(len(self.bitstream) / len(self.safe_zones)) if self.safe_zones else len(self.bitstream)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        
        if node.name in self.safe_zones and self.bit_idx < len(self.bitstream):
            chunk = self.bitstream[self.bit_idx : self.bit_idx + self.chunk_size]
            
            # Safe docstring preservation (prevent IndexError on empty bodies)
            docstring = None
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                docstring = node.body.pop(0)

            injections = []
            for bit in chunk:
                base_prefix = self.camouflage[self.bit_idx]
                
                # Namespace collision resolver
                safe_name = f"{base_prefix}_{self.bit_idx}"
                while safe_name in self.existing_names:
                    safe_name = f"{base_prefix}_{random.randint(1000, 9999)}_{self.bit_idx}"
                self.existing_names.add(safe_name)

                # TRIPLE MODULAR REDUNDANCY
                # Channel 1: The Array Order ([1, 2] vs [2, 1])
                list_elts = [ast.Constant(1), ast.Constant(2)] if bit == '1' else [ast.Constant(2), ast.Constant(1)]
                
                # Channel 2: The Math Identity (x + 0 vs x - 0)
                math_op = ast.Add() if bit == '1' else ast.Sub()
                math_node = ast.BinOp(left=ast.Constant(1), op=math_op, right=ast.Constant(0))
                
                # Channel 3: The Type Casting (Integer 1 vs Float 1.0)
                type_val = 1 if bit == '1' else 1.0
                type_node = ast.Constant(value=type_val)

                # Combine all 3 channels into a single flat Tuple assignment (Semantic Stealth)
                redundant_tuple = ast.Tuple(elts=[ast.List(elts=list_elts, ctx=ast.Load()), math_node, type_node], ctx=ast.Load())
                assign = ast.Assign(targets=[ast.Name(id=safe_name, ctx=ast.Store())], value=redundant_tuple)
                
                injections.append(assign)
                self.bit_idx += 1
                
            # Inject flatly, no if-statements required
            node.body = ([docstring] if docstring else []) + injections + node.body
            
        return node

def protect_code(source_code: str, key_manager: KeyManager) -> str:
    tree = ast.parse(source_code)
    
    # 1. Cryptographic Topological Fingerprint
    fingerprint = extract_structural_fingerprint(tree)
    bitstream = key_manager.get_binary_payload(fingerprint)
    
    # 2. Deterministic Reproducibility
    random.seed(int.from_bytes(fingerprint, 'big'))
    
    # 3. Namespace Safety
    existing_names = get_existing_names(tree)
    
    # 4. Safe-Zone Filtering (Exclude performance-critical loops)
    safe_zones = [
        node.name for node in ast.walk(tree) 
        if isinstance(node, ast.FunctionDef) 
        and not any(isinstance(n, (ast.For, ast.While, ast.AsyncFor)) for n in ast.walk(node))
    ]
    
    # 5. Deep Domain Camouflage
    scanner = DeepHeuristicScanner()
    scanner.visit(tree)
    camouflage_pool = scanner.generate_weighted_vocabulary(len(bitstream))
    
    # 6. AST Injection
    encoder = EpochVEncoder(bitstream, safe_zones, camouflage_pool, existing_names)
    protected_tree = encoder.visit(tree)
    ast.fix_missing_locations(protected_tree)
    
    return ast.unparse(protected_tree)