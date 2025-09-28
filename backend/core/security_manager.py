"""
Security and authentication module for LEONA
"""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import aiosqlite
from pathlib import Path

class SecurityManager:
    """Handle authentication, authorization, and encryption for LEONA"""
    
    def __init__(self, secret_key: str = None, db_path: str = "data/security.db"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.db_path = db_path
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
        self._init_db()
    
    def _init_db(self):
        """Initialize security database"""
        import asyncio
        asyncio.create_task(self._create_tables())
    
    async def _create_tables(self):
        """Create security tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    role TEXT DEFAULT 'user'
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    permissions TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    resource TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            await db.commit()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def generate_token(self, user_id: int, username: str, role: str = "user") -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + self.token_expiry,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def create_user(self, username: str, password: str, email: str = None) -> int:
        """Create new user"""
        password_hash = self.hash_password(password)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = await cursor.fetchone()
            
            if user and self.verify_password(password, user[2]):
                # Update last login
                await db.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user[0],)
                )
                await db.commit()
                
                return {
                    "id": user[0],
                    "username": user[1],
                    "role": user[3],
                    "token": self.generate_token(user[0], user[1], user[3])
                }
        return None
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"leona_{secrets.token_urlsafe(32)}"
    
    async def create_api_key(self, user_id: int, name: str = None, permissions: str = "read") -> str:
        """Create and store API key"""
        api_key = self.generate_api_key()
        key_hash = self.hash_password(api_key)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO api_keys (key_hash, user_id, name, permissions) VALUES (?, ?, ?, ?)",
                (key_hash, user_id, name, permissions)
            )
            await db.commit()
        
        return api_key
    
    async def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """Verify API key and return associated user info"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, key_hash, user_id, permissions FROM api_keys WHERE is_active = 1"
            )
            keys = await cursor.fetchall()
            
            for key_data in keys:
                if self.verify_password(api_key, key_data[1]):
                    # Update last used
                    await db.execute(
                        "UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE id = ?",
                        (key_data[0],)
                    )
                    await db.commit()
                    
                    return {
                        "key_id": key_data[0],
                        "user_id": key_data[2],
                        "permissions": key_data[3]
                    }
        return None
    
    async def log_action(self, user_id: int, action: str, resource: str, 
                        success: bool, ip_address: str = None, user_agent: str = None):
        """Log user action for audit trail"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO audit_log (user_id, action, resource, success, ip_address, user_agent) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, action, resource, success, ip_address, user_agent)
            )
            await db.commit()

# FastAPI Security Dependencies
security_bearer = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_bearer)):
    """Get current user from JWT token"""
    token = credentials.credentials
    security_manager = SecurityManager()  # In production, this should be a singleton
    
    payload = security_manager.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload