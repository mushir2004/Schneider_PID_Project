import torch
print("------------------------------------------")
print("Checking NVIDIA GPU Status...")
if torch.cuda.is_available():
    print(f"✅ SUCCESS! GPU Detected: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print("   We are ready for Local AI.")
else:
    print("❌ ERROR: Python cannot see your GPU.")
    print("   Did you run the pip install command with --index-url?")
print("------------------------------------------")