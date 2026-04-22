import time
import sys
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Feature 3 Setup ---
SHARED_KEY = b'sixteen_byte_key_sixteen_byte_ky'
aesgcm = AESGCM(SHARED_KEY)

def encrypt_f3(message):
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return (nonce + ciphertext).decode('latin-1')

def decrypt_f3(latin_str):
    data = latin_str.encode('latin-1')
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

# --- Metrics Testing Script ---
def run_metrics(test_message):
    print(f"--- Performance Analysis: '{test_message}' ---")
    
    # 1. Measure Size Impact
    original_size = len(test_message.encode())
    encrypted_str = encrypt_f3(test_message)
    encrypted_size = len(encrypted_str.encode('latin-1'))
    
    print(f"Original Size:  {original_size} bytes")
    print(f"Encrypted Size: {encrypted_size} bytes")
    print(f"Size Increase:  {((encrypted_size - original_size)/original_size)*100:.1f}%")
    
    # 2. Measure Latency Impact (Speed)
    start_time = time.perf_counter()
    
    # Run 1000 times to get a stable average
    for _ in range(1000):
        enc = encrypt_f3(test_message)
        dec = decrypt_f3(enc)
        
    end_time = time.perf_counter()
    avg_latency = ((end_time - start_time) / 1000) * 1000 # convert to milliseconds
    
    print(f"Avg processing time (Enc+Dec): {avg_latency:.4f} ms")
    print("-" * 40)

# Run tests with different message lengths
run_metrics("Hello")
run_metrics("This is a much longer secret message for testing.")
