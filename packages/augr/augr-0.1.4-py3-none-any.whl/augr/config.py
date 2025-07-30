"""
Configuration management for AUGR
"""

import os
import json
from pathlib import Path
from typing import Optional


class AugrConfig:
    """Manages AUGR configuration in ~/.augr/"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".augr"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """Create ~/.augr/ directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment or config file"""
        # Check environment first
        api_key = os.getenv("BRAINTRUST_API_KEY")
        if api_key:
            return api_key
        
        # Check config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get("braintrust_api_key")
            except (json.JSONDecodeError, IOError):
                pass
        
        return None
    
    def save_api_key(self, api_key: str):
        """Save API key to config file"""
        config = {}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                config = {}
        
        config["braintrust_api_key"] = api_key
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set restrictive permissions (user only)
        os.chmod(self.config_file, 0o600)
    
    def remove_config(self):
        """Remove the entire ~/.augr/ directory"""
        import shutil
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)
            return True
        return False
    
    def interactive_setup(self) -> str:
        """Interactive setup for first-time users"""
        print("🎉 Welcome to AUGR! Let's get you set up.")
        print()
        print("AUGR needs a Braintrust API key to function.")
        print()
        print("📋 To get your API key:")
        print("1. Go to: https://www.braintrust.dev/app/settings/api-keys")
        print("2. Sign up or log in to your Braintrust account")
        print("3. Click 'Create API Key'")
        print("4. Copy the key (it starts with 'sk-bt-')")
        print()
        
        while True:
            print("Do you want to:")
            print("1. Enter your Braintrust API key now")
            print("2. Set it as an environment variable instead")
            print("3. Exit and set it up later")
            
            choice = input("\nChoice (1/2/3): ").strip()
            
            if choice == "1":
                api_key = input("\nPaste your Braintrust API key: ").strip()
                
                if not api_key:
                    print("❌ No API key entered. Please try again.")
                    continue
                
                if not api_key.startswith("sk-bt-"):
                    print("⚠️  Warning: API key doesn't look like a Braintrust key (should start with 'sk-bt-')")
                    confirm = input("Continue anyway? (y/N): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                # Save the key
                self.save_api_key(api_key)
                print(f"✅ API key saved to: {self.config_file}")
                print("🔒 File permissions set to user-only for security.")
                print()
                return api_key
            
            elif choice == "2":
                print()
                print("💡 To set as environment variable:")
                print("Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
                print(f"   export BRAINTRUST_API_KEY=your_api_key_here")
                print()
                print("Then restart your terminal or run: source ~/.bashrc")
                print()
                print("❌ Exiting for now. Run 'augr' again after setting the environment variable.")
                exit(0)
            
            elif choice == "3":
                print()
                print("❌ Setup cancelled. Run 'augr' again when you're ready to configure.")
                exit(0)
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")


def get_configured_api_key() -> str:
    """Get API key with interactive setup if needed"""
    config = AugrConfig()
    api_key = config.get_api_key()
    
    if not api_key:
        # First time setup
        api_key = config.interactive_setup()
    
    return api_key


def remove_all_config() -> bool:
    """Remove all AUGR configuration"""
    config = AugrConfig()
    return config.remove_config() 