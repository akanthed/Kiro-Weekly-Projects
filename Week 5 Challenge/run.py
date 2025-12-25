#!/usr/bin/env python3
"""
Simple runner script for the Indore Night Food Guide app
"""

import subprocess
import sys
import os

def main():
    print("🌙 Starting Indore Night Food Guide...")
    print("=" * 50)
    
    # Check if .kiro/product.md exists
    if not os.path.exists('.kiro/product.md'):
        print("❌ Error: .kiro/product.md not found!")
        print("   This file contains the local knowledge base.")
        print("   Please ensure it exists before running the app.")
        return 1
    
    print("✅ Knowledge base found: .kiro/product.md")
    print("🚀 Launching Streamlit app...")
    print("\nOnce started, open: http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Please install requirements:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())