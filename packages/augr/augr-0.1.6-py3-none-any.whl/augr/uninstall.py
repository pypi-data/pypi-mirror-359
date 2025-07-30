"""
Uninstall functionality for AUGR
"""

import subprocess
import sys
from pathlib import Path

from .config import remove_all_config


def uninstall_augr():
    """Uninstall AUGR and remove all configuration"""
    print("🗑️  AUGR Uninstall")
    print("=" * 20)
    print()
    
    # Confirm with user
    print("This will:")
    print("- Remove all AUGR configuration from ~/.augr/")
    print("- Uninstall the AUGR package")
    print()
    
    response = input("Are you sure you want to uninstall AUGR? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Uninstall cancelled.")
        return
    
    print()
    print("🧹 Removing configuration...")
    
    # Remove config directory
    config_removed = remove_all_config()
    if config_removed:
        print("✅ Removed ~/.augr/ directory")
    else:
        print("ℹ️  No ~/.augr/ directory found")
    
    print()
    print("📦 Uninstalling package...")
    
    # Try different uninstall methods
    try:
        # Try pip uninstall first
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "augr", "-y"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Successfully uninstalled AUGR package")
        else:
            # Try uv uninstall as fallback
            print("💡 Trying uv tool uninstall...")
            result = subprocess.run(
                ["uv", "tool", "uninstall", "augr"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Successfully uninstalled AUGR package with uv")
            else:
                print("⚠️  Could not automatically uninstall the package.")
                print("Please manually run one of:")
                print("   pip uninstall augr")
                print("   uv tool uninstall augr")
                print("   pipx uninstall augr")
    
    except Exception as e:
        print(f"⚠️  Error during uninstall: {e}")
        print("Please manually run: pip uninstall augr")
    
    print()
    print("👋 AUGR has been uninstalled.")
    print("Thanks for using AUGR! If you reinstall, you'll need to set up your API key again.")


def main():
    """Entry point for uninstall command"""
    uninstall_augr() 