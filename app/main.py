from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import auth, files
from .db.database import init_db, test_connection

app = FastAPI(title="Secure File Sharing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    if await test_connection():
        await init_db()
    else:
        raise Exception("Failed to connect to MongoDB. Make sure MongoDB is running.")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(files.router, prefix="/files", tags=["files"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Secure File Sharing API",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "signup": "/auth/signup",
                "verify": "/auth/verify",
                "login": "/auth/login"
            },
            "files": {
                "upload": "/files/upload",
                "list": "/files/list",
                "download": "/files/download/{file_id}"
            }
        }
    } 