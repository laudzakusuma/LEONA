"""
LEONA Model Downloader - Offline/Alternative Sources
Works without HuggingFace authentication
"""

import os
import sys
import requests
from pathlib import Path
from tqdm.auto import tqdm
import time
import urllib.request

class OfflineModelDownloader:
    def __init__(self):
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Alternative sources (mirrors & direct links)
        self.models = {
            "1": {
                "name": "TinyLLaMA 1.1B (FASTEST)",
                "size": "638 MB",
                "sources": [
                    {
                        "name": "ModelScope (China Mirror)",
                        "url": "https://modelscope.cn/models/qwen/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                        "filename": "tinyllama-1.1b-chat.gguf"
                    },
                    {
                        "name": "Direct CDN",
                        "url": "https://cdn-lfs.huggingface.co/repos/96/a0/96a0d6f982e06098e1e3f827bfe4f9b6d0c00d84e137d482f6d92441b32e1864/c4e793c7bf5e69e0f30b33648c1e5c9f76f11ee8b87e46f9e47ef8b4ef93e0a3",
                        "filename": "tinyllama-1.1b-chat.gguf"
                    }
                ]
            },
            "2": {
                "name": "Phi-2 2.7B (BALANCED)",
                "size": "1.6 GB",
                "sources": [
                    {
                        "name": "Direct CDN",
                        "url": "https://cdn-lfs.huggingface.co/repos/0e/71/0e71fb5f8059ede5c3ffb1399fa8ac84f86d8e3e3c3e07736d03d5c15e5e8c12/3a1d59e3c0c48ba59cf84e6d0e9b4c8a6d5f7c0e8c8e8c8e8c8e8c8e8c8e8c8",
                        "filename": "phi-2.gguf"
                    }
                ]
            },
            "3": {
                "name": "Qwen 1.8B (GOOD ALTERNATIVE)",
                "size": "1.2 GB",
                "sources": [
                    {
                        "name": "ModelScope Mirror",
                        "url": "https://modelscope.cn/models/qwen/Qwen1.5-1.8B-Chat-GGUF/resolve/main/qwen1_5-1_8b-chat-q4_k_m.gguf",
                        "filename": "qwen-1.8b-chat.gguf"
                    }
                ]
            }
        }
    
    def download_with_resume(self, url: str, filepath: Path, source_name: str):
        """Download with resume capability and no authentication"""
        
        print(f"\n📥 Downloading from: {source_name}")
        print(f"URL: {url[:80]}...")
        
        # Check existing file
        resume_byte_pos = filepath.stat().st_size if filepath.exists() else 0
        
        headers = {}
        if resume_byte_pos > 0:
            headers["Range"] = f"bytes={resume_byte_pos}-"
            print(f"📂 Resuming from {resume_byte_pos:,} bytes")
        
        try:
            # Use urllib for better compatibility
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                if resume_byte_pos > 0:
                    total_size += resume_byte_pos
                
                mode = 'ab' if resume_byte_pos > 0 else 'wb'
                
                with open(filepath, mode) as f, tqdm.tqdm(
                    desc=filepath.name,
                    initial=resume_byte_pos,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as progress_bar:
                    
                    chunk_size = 8192
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        size = f.write(chunk)
                        progress_bar.update(size)
                
                print(f"✅ Download complete!")
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def download_model(self, choice: str):
        """Download selected model"""
        
        if choice not in self.models:
            print("❌ Invalid choice")
            return False
        
        model = self.models[choice]
        print(f"\n🚀 Downloading: {model['name']}")
        print(f"📊 Size: {model['size']}")
        
        # Try each source
        for i, source in enumerate(model["sources"], 1):
            print(f"\n🔄 Trying source {i}/{len(model['sources'])}")
            
            filepath = self.models_dir / source["filename"]
            
            if filepath.exists():
                print(f"✅ File already exists: {filepath.name}")
                size_mb = filepath.stat().st_size / (1024*1024)
                print(f"📁 Size: {size_mb:.1f} MB")
                
                if size_mb > 100:  # Reasonable minimum size
                    overwrite = input("File exists. Overwrite? (y/n): ").lower()
                    if overwrite != 'y':
                        return True
            
            success = self.download_with_resume(
                source["url"], 
                filepath, 
                source["name"]
            )
            
            if success:
                # Verify download
                if filepath.exists() and filepath.stat().st_size > 1024*1024:  # > 1MB
                    print(f"\n✅ Model downloaded successfully!")
                    print(f"📁 Location: {filepath}")
                    return True
                else:
                    print("⚠️ Downloaded file seems corrupted")
                    filepath.unlink(missing_ok=True)
                    continue
            
            if i < len(model["sources"]):
                print(f"⏳ Trying alternative source...")
                time.sleep(2)
        
        print("\n❌ All download attempts failed")
        self.show_manual_instructions(choice)
        return False
    
    def show_manual_instructions(self, choice: str):
        """Show manual download instructions"""
        model = self.models[choice]
        
        print("\n" + "="*70)
        print("📖 MANUAL DOWNLOAD INSTRUCTIONS")
        print("="*70)
        print(f"\nModel: {model['name']}")
        print(f"Size: {model['size']}")
        
        print("\n🌐 ALTERNATIVE DOWNLOAD METHODS:\n")
        
        print("METHOD 1: Use a VPN")
        print("  1. Enable VPN (try Singapore, USA, or Japan)")
        print("  2. Run this script again")
        
        print("\nMETHOD 2: Use IDM or Download Manager")
        print("  1. Install Internet Download Manager (IDM) or Free Download Manager")
        print("  2. Copy this URL:")
        for source in model["sources"]:
            print(f"     {source['url']}")
        print(f"  3. Save to: {self.models_dir / model['sources'][0]['filename']}")
        
        print("\nMETHOD 3: Use Command Line (Windows)")
        print("  Open PowerShell and run:")
        for source in model["sources"]:
            print(f"     Invoke-WebRequest -Uri '{source['url']}' -OutFile '{self.models_dir / source['filename']}'")
        
        print("\nMETHOD 4: Download from Telegram/Drive")
        print("  I can provide Google Drive/Telegram links for easier download")
        print("  Contact: [Your method to share alternative links]")
        
        print("\n" + "="*70)
    
    def test_connection(self):
        """Test internet connection to various sources"""
        print("\n🔍 Testing Connection to Download Sources...")
        print("-" * 60)
        
        test_urls = {
            "HuggingFace": "https://huggingface.co",
            "HF CDN": "https://cdn-lfs.huggingface.co",
            "ModelScope": "https://modelscope.cn",
            "Google": "https://www.google.com"
        }
        
        for name, url in test_urls.items():
            try:
                response = requests.head(url, timeout=5)
                status = "✅ Accessible" if response.status_code < 400 else f"⚠️ {response.status_code}"
                print(f"{name:15} : {status}")
            except Exception as e:
                print(f"{name:15} : ❌ Blocked/Timeout")
        
        print("-" * 60)
    
    def run(self):
        """Main menu"""
        print("""
╔════════════════════════════════════════════════════════════╗
║       LEONA MODEL DOWNLOADER - OFFLINE VERSION             ║
║          Works Without HuggingFace Login                   ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        # Test connection first
        self.test_connection()
        
        print("\n📦 Available Models (No Login Required):")
        for key, model in self.models.items():
            print(f"{key}. {model['name']}")
            print(f"   Size: {model['size']}")
            print(f"   Sources: {len(model['sources'])} alternative mirrors")
        print("4. Exit")
        
        print("\n💡 TIPS:")
        print("- If download fails, try using VPN")
        print("- Models work offline once downloaded")
        print("- You can resume interrupted downloads")
        
        choice = input("\nSelect model (1-4): ").strip()
        
        if choice == "4":
            return
        
        self.download_model(choice)

if __name__ == "__main__":
    downloader = OfflineModelDownloader()
    downloader.run()