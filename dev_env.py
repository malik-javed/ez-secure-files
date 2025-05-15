"""
Development environment setup script.
Run this before starting the application in development mode.
"""

import os

# Set development environment variables
os.environ["DEV_MODE"] = "true"

# Uncomment the line below to bypass email verification in development
# os.environ["BYPASS_EMAIL_VERIFICATION"] = "true"

print("Development environment variables set.")
print("DEV_MODE =", os.environ.get("DEV_MODE"))
print("BYPASS_EMAIL_VERIFICATION =", os.environ.get("BYPASS_EMAIL_VERIFICATION", "false"))

if __name__ == "__main__":
    print("\nTo start the application with these settings, run:")
    print("python -m dev_env && python run.py")
    print("\nOr to bypass email verification (for development only):")
    print("BYPASS_EMAIL_VERIFICATION=true python run.py") 