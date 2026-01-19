# 🚀 **QUICK SETUP SCRIPT**

import os
import subprocess

def setup_project():
    """Automatically set up RetailMind Lite project structure"""
    
    print("🚀 Setting up RetailMind Lite...")
    
    # Create folder structure
    folders = ['data', 'models', 'utils']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, '__init__.py'), 'w').close()
        print(f"📁 Created {folder}/")
    
    # Create all required files
    files = {
        'requirements.txt': '''streamlit==1.28.1
pandas==2.1.4
numpy==1.24.3
plotly==5.18.0
prophet==1.1.5
scikit-learn==1.3.2''',
        
        'README.md': '''# RetailMind Lite - AI Market Intelligence Copilot

## Quick Start
1. pip install -r requirements.txt
2. streamlit run app.py
3. Open http://localhost:8501'''
    }
    
    for filename, content in files.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"📄 Created {filename}")
    
    print("\n✅ Project structure created!")
    print("\n📋 Next steps:")
    print("1. Copy the provided codes to respective files")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the app: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    setup_project()