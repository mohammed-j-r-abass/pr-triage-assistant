# check_requirements.py

import sys

requirements = [
    "flask",
    "requests", 
    "python_dotenv",
    "httpx",
    "PyGithub",
    "cryptography"
]

print("Checking installed packages...")
print("-" * 40)

missing = []
installed = []

for package in requirements:
    try:
        # Convert package name to import name (PyGithub -> github)
        import_name = package
        if package == "PyGithub":
            import_name = "github"
        elif package == "python_dotenv":
            import_name = "dotenv"
            
        __import__(import_name)
        installed.append(package)
        print(f"{package} - installed")
    except ImportError:
        missing.append(package)
        print(f"{package} - MISSING")

print("-" * 40)

if missing:
    print(f"\nMissing packages: {', '.join(missing)}")
    print("\nInstall them with:")
    print(f"pip install {' '.join(missing)}")
else:
    print("\nAll requirements are installed!")

print(f"\nPython version: {sys.version}")