from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Header, Depends, status
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import socketio
import asyncio
import random
import aiofiles
import hashlib
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=True)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'video_sentiment')

if mongo_url:
    try:
        logging.info(f"Attempting to connect to MongoDB at {mongo_url.split('@')[-1] if '@' in mongo_url else '...'}")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        logging.info("Connected to MongoDB")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        client = None
else:
    client = None

if not client:
    logging.warning("Using in-memory MockDB (Data will be lost on restart)")
    from mock_db import MockDB
    db = MockDB()
    client = None # Mock client

# Upload directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Socket.IO setup
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    role: str = "editor"  # viewer, editor, admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "editor"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Video(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    filename: str
    original_name: str
    file_size: int
    duration: Optional[float] = None
    status: str = "uploading"  # uploading, processing, completed, failed
    sensitivity: Optional[str] = None  # safe, flagged
    upload_progress: int = 0
    processing_progress: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VideoResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    duration: Optional[float]
    status: str
    sensitivity: Optional[str]
    upload_progress: int
    processing_progress: int
    created_at: str
    updated_at: str

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Mock video processing function
async def process_video(video_id: str, user_id: str, filename: str):
    try:
        # Simulate processing with progress updates
        for progress in range(0, 101, 10):
            await asyncio.sleep(0.5)  # Simulate work
            
            # Update database
            await db.videos.update_one(
                {"id": video_id},
                {
                    "$set": {
                        "processing_progress": progress,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # Emit progress via Socket.IO
            await sio.emit('processing_progress', {
                'video_id': video_id,
                'progress': progress,
                'status': 'processing'
            }, room=user_id)
        
        # Random sensitivity detection (mock)
        sensitivity = random.choice(["safe", "safe", "safe", "flagged"])  # 75% safe, 25% flagged
        
        # Update to completed
        await db.videos.update_one(
            {"id": video_id},
            {
                "$set": {
                    "status": "completed",
                    "sensitivity": sensitivity,
                    "processing_progress": 100,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Emit completion
        await sio.emit('processing_complete', {
            'video_id': video_id,
            'sensitivity': sensitivity,
            'status': 'completed'
        }, room=user_id)
        
    except Exception as e:
        logging.error(f"Error processing video {video_id}: {e}")
        await db.videos.update_one(
            {"id": video_id},
            {
                "$set": {
                    "status": "failed",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        await sio.emit('processing_failed', {
            'video_id': video_id,
            'status': 'failed'
        }, room=user_id)

# Auth endpoints
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            role=user_data.role
        )
        
        user_dict = user.model_dump()
        user_dict['password_hash'] = get_password_hash(user_data.password)
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        
        await db.users.insert_one(user_dict)
        
        # Create token
        access_token = create_access_token(data={"sub": user.id})
        
        return Token(access_token=access_token, token_type="bearer", user=user)
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_obj = User(**user)
    access_token = create_access_token(data={"sub": user_obj.id})
    
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Video endpoints
@api_router.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only video files are allowed.")
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Create video record
    video = Video(
        user_id=current_user.id,
        filename=unique_filename,
        original_name=file.filename,
        file_size=0,  # Will update after saving
        status="uploading"
    )
    
    video_dict = video.model_dump()
    video_dict['created_at'] = video_dict['created_at'].isoformat()
    video_dict['updated_at'] = video_dict['updated_at'].isoformat()
    
    await db.videos.insert_one(video_dict)
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        file_size = len(content)
        
        # Update video with file size and status
        await db.videos.update_one(
            {"id": video.id},
            {
                "$set": {
                    "file_size": file_size,
                    "status": "processing",
                    "upload_progress": 100,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Start background processing
        asyncio.create_task(process_video(video.id, current_user.id, unique_filename))
        
        return {"video_id": video.id, "message": "Video uploaded successfully"}
    
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        await db.videos.delete_one({"id": video.id})
        raise HTTPException(status_code=500, detail="Failed to upload video")

@api_router.get("/videos", response_model=List[VideoResponse])
async def list_videos(
    status: Optional[str] = None,
    sensitivity: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    # Build query based on user role
    query = {}
    
    if current_user.role != "admin":
        query["user_id"] = current_user.id
    
    if status:
        query["status"] = status
    
    if sensitivity:
        query["sensitivity"] = sensitivity
    
    videos = await db.videos.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [
        VideoResponse(
            id=v["id"],
            filename=v["filename"],
            original_name=v["original_name"],
            file_size=v["file_size"],
            duration=v.get("duration"),
            status=v["status"],
            sensitivity=v.get("sensitivity"),
            upload_progress=v["upload_progress"],
            processing_progress=v["processing_progress"],
            created_at=v["created_at"],
            updated_at=v["updated_at"]
        )
        for v in videos
    ]

@api_router.get("/videos/{video_id}")
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user)
):
    video = await db.videos.find_one({"id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check permissions
    if current_user.role != "admin" and video["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return VideoResponse(
        id=video["id"],
        filename=video["filename"],
        original_name=video["original_name"],
        file_size=video["file_size"],
        duration=video.get("duration"),
        status=video["status"],
        sensitivity=video.get("sensitivity"),
        upload_progress=video["upload_progress"],
        processing_progress=video["processing_progress"],
        created_at=video["created_at"],
        updated_at=video["updated_at"]
    )

@api_router.get("/videos/{video_id}/stream")
async def stream_video(
    video_id: str,
    range: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user)
):
    video = await db.videos.find_one({"id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check permissions
    if current_user.role != "admin" and video["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if video["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video is not ready for streaming")
    
    file_path = UPLOAD_DIR / video["filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    file_size = file_path.stat().st_size
    
    # Handle range requests for video streaming
    if range:
        range_str = range.replace("bytes=", "")
        start, end = range_str.split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
        
        async def iterfile():
            async with aiofiles.open(file_path, mode='rb') as f:
                await f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    data = await f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1),
            'Content-Type': 'video/mp4',
        }
        
        return StreamingResponse(iterfile(), status_code=206, headers=headers)
    else:
        return FileResponse(file_path, media_type='video/mp4')

@api_router.delete("/videos/{video_id}")
async def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user)
):
    video = await db.videos.find_one({"id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check permissions (only owner or admin can delete)
    if current_user.role not in ["admin", "editor"] or (current_user.role == "editor" and video["user_id"] != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file
    file_path = UPLOAD_DIR / video["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    await db.videos.delete_one({"id": video_id})
    
    return {"message": "Video deleted successfully"}

# Socket.IO events
@sio.event
async def connect(sid, environ):
    logging.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logging.info(f"Client disconnected: {sid}")

@sio.event
async def join_room(sid, data):
    user_id = data.get('user_id')
    if user_id:
        sio.enter_room(sid, user_id)
        logging.info(f"Client {sid} joined room {user_id}")

# Include the router in the main app
app.include_router(api_router)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# CORS configuration - allow both CORS_ORIGINS and FRONTEND_URL
frontend_url = os.environ.get('FRONTEND_URL', '')
cors_origins = os.environ.get('CORS_ORIGINS', '*')

# If FRONTEND_URL is set, use it; otherwise use CORS_ORIGINS
if frontend_url:
    allowed_origins = [frontend_url]
else:
    allowed_origins = cors_origins.split(',') if cors_origins != '*' else ['*']

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log CORS configuration for debugging
logger.info(f"CORS Origins configured: {allowed_origins}")
logger.info(f"FRONTEND_URL: {frontend_url}")
logger.info(f"CORS_ORIGINS: {cors_origins}")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

# Export the socket app for ASGI server
app = socket_app