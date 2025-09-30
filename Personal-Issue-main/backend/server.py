from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models for Personal Issue App
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    name: str

class ProtectedApp(BaseModel):
    name: str
    icon: str  # base64 encoded icon
    package_name: str
    added_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    protected_apps: List[ProtectedApp] = []
    password_hash: str = ""
    protection_state: str = "OFF"  # OFF, BACKGROUND, ACTIVE
    click_count: int = 0
    theme: str = "purple"  # purple or red
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileCreate(BaseModel):
    user_id: str

class AppAddRequest(BaseModel):
    name: str
    icon: str
    package_name: str

class AppRemoveRequest(BaseModel):
    package_name: str

class PasswordSetRequest(BaseModel):
    password: str

class PasswordVerifyRequest(BaseModel):
    password: str

class StateUpdateRequest(BaseModel):
    protection_state: str
    theme: str
    click_count: int

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()

# User endpoints
@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    
    # Create user profile
    profile = UserProfile(user_id=user_obj.id)
    await db.profiles.insert_one(profile.dict())
    
    return user_obj

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# Profile endpoints
@api_router.get("/profiles/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return UserProfile(**profile)

@api_router.post("/profiles/{user_id}/apps")
async def add_protected_app(user_id: str, app: AppAddRequest):
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check if app already exists
    protected_apps = profile.get("protected_apps", [])
    if any(app_item["package_name"] == app.package_name for app_item in protected_apps):
        raise HTTPException(status_code=400, detail="App already protected")
    
    # Check limit (20 apps max)
    if len(protected_apps) >= 20:
        raise HTTPException(status_code=400, detail="Maximum 20 apps allowed")
    
    new_app = ProtectedApp(**app.dict()).dict()
    protected_apps.append(new_app)
    
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": {"protected_apps": protected_apps, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "App added successfully"}

@api_router.delete("/profiles/{user_id}/apps")
async def remove_protected_app(user_id: str, app: AppRemoveRequest):
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    protected_apps = profile.get("protected_apps", [])
    protected_apps = [app_item for app_item in protected_apps if app_item["package_name"] != app.package_name]
    
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": {"protected_apps": protected_apps, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "App removed successfully"}

# Password endpoints
@api_router.post("/profiles/{user_id}/password")
async def set_password(user_id: str, password_req: PasswordSetRequest):
    if len(password_req.password) > 8:
        raise HTTPException(status_code=400, detail="Password must be 8 characters or less")
    
    password_hash = hash_password(password_req.password)
    
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": {"password_hash": password_hash, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password set successfully"}

@api_router.post("/profiles/{user_id}/verify-password")
async def verify_password(user_id: str, password_req: PasswordVerifyRequest):
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    password_hash = hash_password(password_req.password)
    
    if profile.get("password_hash") == password_hash:
        return {"valid": True}
    else:
        return {"valid": False}

# State management endpoints
@api_router.put("/profiles/{user_id}/state")
async def update_state(user_id: str, state_req: StateUpdateRequest):
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": {
            "protection_state": state_req.protection_state,
            "theme": state_req.theme,
            "click_count": state_req.click_count,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "State updated successfully"}

# Mock popular apps endpoint
@api_router.get("/mock-apps")
async def get_mock_apps():
    mock_apps = [
        {"name": "Facebook", "package_name": "com.facebook.katana", "icon": "📘"},
        {"name": "WhatsApp", "package_name": "com.whatsapp", "icon": "💬"},
        {"name": "Instagram", "package_name": "com.instagram.android", "icon": "📷"},
        {"name": "TikTok", "package_name": "com.zhiliaoapp.musically", "icon": "🎵"},
        {"name": "YouTube", "package_name": "com.google.android.youtube", "icon": "▶️"},
        {"name": "Twitter", "package_name": "com.twitter.android", "icon": "🐦"},
        {"name": "Snapchat", "package_name": "com.snapchat.android", "icon": "👻"},
        {"name": "Netflix", "package_name": "com.netflix.mediaclient", "icon": "🎬"},
        {"name": "Spotify", "package_name": "com.spotify.music", "icon": "🎶"},
        {"name": "Games", "package_name": "com.games.app", "icon": "🎮"},
        {"name": "Amazon", "package_name": "com.amazon.mShop.android.shopping", "icon": "📦"},
        {"name": "Google Maps", "package_name": "com.google.android.apps.maps", "icon": "🗺️"},
        {"name": "Gmail", "package_name": "com.google.android.gm", "icon": "📧"},
        {"name": "Chrome", "package_name": "com.android.chrome", "icon": "🌐"},
        {"name": "Discord", "package_name": "com.discord", "icon": "💬"},
        {"name": "Telegram", "package_name": "org.telegram.messenger", "icon": "📤"},
        {"name": "Pinterest", "package_name": "com.pinterest", "icon": "📌"},
        {"name": "Reddit", "package_name": "com.reddit.frontpage", "icon": "🤖"},
        {"name": "Uber", "package_name": "com.ubercab", "icon": "🚗"},
        {"name": "Banking", "package_name": "com.banking.app", "icon": "🏦"}
    ]
    return mock_apps

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()