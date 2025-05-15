"""
Development run script that bypasses email verification.
Use this for development only!
"""

import os
import uvicorn

# Set development environment variables
os.environ["DEV_MODE"] = "true"
os.environ["BYPASS_EMAIL_VERIFICATION"] = "true"

print("Development environment variables set:")
print("DEV_MODE =", os.environ.get("DEV_MODE"))
print("BYPASS_EMAIL_VERIFICATION =", os.environ.get("BYPASS_EMAIL_VERIFICATION"))
print("\nWARNING: Email verification is bypassed. Users will be created even if email sending fails.")
print("This should only be used for development!\n")

if __name__ == "__main__":
    print("Starting FastAPI User Authentication API in DEVELOPMENT mode...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 