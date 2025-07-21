#!/usr/bin/env python3
"""
Setup script for ETF Trading Strategy System
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    print("\n🔧 Setting up virtual environment...")
    
    # Create virtual environment
    success, output = run_command("python3 -m venv etf_trading_env")
    if not success:
        print(f"❌ Failed to create virtual environment: {output}")
        return False
    
    print("✅ Virtual environment created successfully!")
    
    # Install required packages
    print("\n📦 Installing required packages...")
    
    packages = [
        "pandas>=1.3.0",
        "openpyxl>=3.0.0", 
        "python-telegram-bot>=20.0",
        "requests>=2.25.0"
    ]
    
    pip_command = "source etf_trading_env/bin/activate && pip install " + " ".join(packages)
    success, output = run_command(pip_command)
    
    if not success:
        print(f"❌ Failed to install packages: {output}")
        return False
    
    print("✅ All packages installed successfully!")
    return True

def create_sample_config():
    """Create sample configuration files"""
    print("\n📝 Creating sample configuration...")
    
    # Create sample bot token file
    bot_config_content = '''# Telegram Bot Configuration
# Replace YOUR_BOT_TOKEN_HERE with your actual bot token from @BotFather

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# To get a bot token:
# 1. Open Telegram and search for @BotFather
# 2. Send /start and then /newbot
# 3. Follow the instructions to create your bot
# 4. Copy the token and replace the value above
'''
    
    try:
        with open("bot_config.py", "w") as f:
            f.write(bot_config_content)
        print("✅ Created bot_config.py")
    except Exception as e:
        print(f"❌ Failed to create bot_config.py: {e}")
        return False
    
    return True

def display_usage_instructions():
    """Display usage instructions"""
    print("\n" + "="*60)
    print("🎉 ETF TRADING STRATEGY SYSTEM SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 USAGE INSTRUCTIONS:")
    print("-" * 30)
    
    print("\n1️⃣ COMMAND LINE INTERFACE (Recommended for testing):")
    print("   source etf_trading_env/bin/activate")
    print("   python3 etf_cli.py")
    
    print("\n2️⃣ TELEGRAM BOT (For mobile/remote access):")
    print("   a) Edit bot_config.py and add your bot token")
    print("   b) Activate environment: source etf_trading_env/bin/activate")
    print("   c) Run: python3 telegram_bot.py")
    
    print("\n📊 GETTING STARTED:")
    print("-" * 20)
    print("1. Start with the CLI interface using option 1 above")
    print("2. Load sample data (option 8 in CLI menu)")
    print("3. View daily strategy recommendations (option 1)")
    print("4. Update real ETF prices (option 2)")
    print("5. Execute mock buy/sell transactions (options 5-6)")
    
    print("\n📁 FILES CREATED:")
    print("-" * 20)
    print("• etf_data_manager.py - Core data management")
    print("• trading_strategy.py - Strategy implementation")
    print("• etf_cli.py - Command line interface")
    print("• telegram_bot.py - Telegram bot interface")
    print("• bot_config.py - Bot configuration (edit this!)")
    print("• etf_data.json - Data storage (auto-created)")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("-" * 20)
    print("• This is for MOCK TRADING only - no real trades executed")
    print("• Update ETF prices manually or via API integration")
    print("• Data is stored locally in JSON format")
    print("• Backup etf_data.json regularly to preserve your data")
    
    print("\n🔗 BOT TOKEN SETUP:")
    print("-" * 22)
    print("1. Open Telegram, search for @BotFather")
    print("2. Send /start, then /newbot")
    print("3. Follow instructions to create your bot")
    print("4. Copy the token to bot_config.py")
    print("5. Run telegram_bot.py and start chatting with your bot!")

def main():
    """Main setup function"""
    print("🚀 ETF Trading Strategy System Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment and install packages
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Create sample configuration
    if not create_sample_config():
        sys.exit(1)
    
    # Display usage instructions
    display_usage_instructions()
    
    print(f"\n✅ Setup completed successfully!")
    print("Run the CLI to get started: source etf_trading_env/bin/activate && python3 etf_cli.py")

if __name__ == "__main__":
    main()