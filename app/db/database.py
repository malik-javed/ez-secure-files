import motor.motor_asyncio
from typing import Optional, List, Dict, Any
from ..core import config
from ..models.user import UserType
import datetime
from bson import ObjectId
from ..core.security import get_password_hash

# Create MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URL)
database = client[config.DATABASE_NAME]
user_collection = database[config.COLLECTION_NAME]
file_collection = database["files"]

# User database operations
async def add_user(user_data: dict) -> dict:
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return new_user

async def find_user_by_email(email: str) -> Optional[dict]:
    return await user_collection.find_one({"email": email})

async def find_user_by_username(username: str) -> Optional[dict]:
    return await user_collection.find_one({"username": username})

async def find_user_by_id(user_id: str) -> Optional[dict]:
    try:
        return await user_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None

async def update_user_verification(email: str, is_verified: bool) -> bool:
    result = await user_collection.update_one(
        {"email": email},
        {"$set": {"is_verified": is_verified}}
    )
    return result.modified_count > 0

async def store_verification_token(email: str, token: str) -> bool:
    result = await user_collection.update_one(
        {"email": email},
        {"$set": {"verification_token": token}}
    )
    return result.modified_count > 0

async def verify_token(email: str, token: str) -> bool:
    user = await user_collection.find_one(
        {"email": email, "verification_token": token}
    )
    if user:
        await update_user_verification(email, True)
        await user_collection.update_one(
            {"email": email},
            {"$unset": {"verification_token": ""}}
        )
        return True
    return False

# File database operations
async def add_file(file_data: dict) -> dict:
    file_data["upload_date"] = datetime.datetime.now().isoformat()
    file = await file_collection.insert_one(file_data)
    new_file = await file_collection.find_one({"_id": file.inserted_id})
    return new_file

async def get_file_by_id(file_id: str) -> Optional[dict]:
    try:
        return await file_collection.find_one({"_id": ObjectId(file_id)})
    except:
        return None

async def list_all_files() -> List[dict]:
    cursor = file_collection.find({})
    files = await cursor.to_list(length=100)  # Limit to 100 files
    return files

# Initialize database
async def init_db():
    try:
        # Create unique indexes for users
        await user_collection.create_index("email", unique=True)
        await user_collection.create_index("username", unique=True)
        
        # Create indexes for files
        await file_collection.create_index("filename")
        await file_collection.create_index("uploaded_by")
        
        print("Database initialized successfully!")
        
        # Create default OPS users if they don't exist
        await create_default_ops_users()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Create default OPS users
async def create_default_ops_users():
    try:
        # Define the default OPS users
        default_users = [
            {
                "username": "ops_admin1",
                "email": "ops_admin1@example.com",
                "password": "password123",
                "user_type": UserType.OPS
            },
            {
                "username": "ops_admin2",
                "email": "ops_admin2@example.com",
                "password": "password123",
                "user_type": UserType.OPS
            }
        ]
        
        # Check and create each default user if they don't exist
        for user in default_users:
            existing_user = await find_user_by_email(user["email"])
            if not existing_user:
                # Create the user
                hashed_password = get_password_hash(user["password"])
                user_data = {
                    "username": user["username"],
                    "email": user["email"],
                    "hashed_password": hashed_password,
                    "user_type": user["user_type"],
                    "is_verified": True,  # Default users are pre-verified
                }
                await add_user(user_data)
                print(f"Created default OPS user: {user['email']}")
            else:
                print(f"Default OPS user already exists: {user['email']}")
    except Exception as e:
        print(f"Error creating default OPS users: {e}")

# Test database connection
async def test_connection():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False 