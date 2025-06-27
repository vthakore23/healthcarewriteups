#!/usr/bin/env python3
"""
Setup script for Healthcare News Automation
"""
import os
import sys
import subprocess
import platform


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8 or higher is required. You have {sys.version}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def create_virtual_environment():
    """Create virtual environment"""
    print("\nCreating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def get_pip_command():
    """Get the correct pip command for the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "pip")
    else:
        return os.path.join("venv", "bin", "pip")


def get_python_command():
    """Get the correct python command for the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python")
    else:
        return os.path.join("venv", "bin", "python")


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    pip_cmd = get_pip_command()
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print("\n✅ .env file already exists")
        return True
    
    print("\nCreating .env file...")
    
    env_content = """# AI Configuration (Choose one)
# For OpenAI (GPT-4)
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-4-turbo-preview

# For Anthropic (Claude)
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# AI_MODEL=claude-3-opus-20240229

# Email Configuration
# For SendGrid (Recommended)
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_FROM=healthcare-automation@yourdomain.com

# For SMTP (Alternative)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password

# Optional
LOG_LEVEL=INFO
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please edit .env file and add your API keys before running")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    directories = ["data", "reports", "cache"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created")
    return True


def test_imports():
    """Test if all modules can be imported"""
    print("\nTesting imports...")
    python_cmd = get_python_command()
    
    test_script = """
import sys
try:
    import config
    import scraper
    import ai_generator
    import email_sender
    print("✅ All modules imported successfully")
    sys.exit(0)
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run(
            [python_cmd, "-c", test_script],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(result.stdout.strip())
            print(result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ Failed to test imports: {e}")
        return False


def main():
    """Main setup function"""
    print_header("Healthcare News Automation Setup")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Test imports
    test_imports()
    
    print_header("Setup Complete!")
    
    print("Next steps:")
    print("1. Edit the .env file and add your API keys")
    print("2. Test email configuration:")
    print(f"   {get_python_command()} main.py --test-email")
    print("3. Run the automation:")
    print(f"   {get_python_command()} main.py --run-now")
    print("4. Schedule for automatic runs:")
    print(f"   {get_python_command()} main.py --schedule")
    
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main() 