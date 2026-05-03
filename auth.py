"""
Authentication & Security Module
API key management, user authentication, rate limiting
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import logging
from functools import wraps
from fastapi import HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
import json
import os

logger = logging.getLogger(__name__)

# ========================
# API KEY MANAGEMENT
# ========================

API_KEYS_FILE = "api_keys.json"
RATE_LIMIT_FILE = "rate_limits.json"

def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

class APIKeyManager:
    """Manage API keys for authentication"""
    
    @staticmethod
    def load_keys() -> dict:
        """Load API keys from file"""
        if os.path.exists(API_KEYS_FILE):
            try:
                with open(API_KEYS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_keys(keys: dict):
        """Save API keys to file"""
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=2)
    
    @staticmethod
    def generate_api_key(name: str = "default", admin: bool = False) -> str:
        """Generate new API key"""
        api_key = secrets.token_urlsafe(32)
        hashed = hash_api_key(api_key)
        
        keys = APIKeyManager.load_keys()
        keys[hashed] = {
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            "admin": admin,
            "enabled": True,
            "last_used": None,
            "usage_count": 0
        }
        APIKeyManager.save_keys(keys)
        logger.info(f"✅ API key generated: {name}")
        
        return api_key
    
    @staticmethod
    def verify_api_key(api_key: str) -> bool:
        """Verify if API key is valid"""
        hashed = hash_api_key(api_key)
        keys = APIKeyManager.load_keys()
        
        if hashed in keys:
            key_info = keys[hashed]
            if key_info.get("enabled", False):
                # Update last used and usage count
                key_info["last_used"] = datetime.utcnow().isoformat()
                key_info["usage_count"] = key_info.get("usage_count", 0) + 1
                APIKeyManager.save_keys(keys)
                return True
        return False
    
    @staticmethod
    def list_keys() -> dict:
        """List all API keys (hashed, safe to display)"""
        return APIKeyManager.load_keys()
    
    @staticmethod
    def revoke_api_key(api_key: str) -> bool:
        """Revoke an API key"""
        hashed = hash_api_key(api_key)
        keys = APIKeyManager.load_keys()
        
        if hashed in keys:
            keys[hashed]["enabled"] = False
            APIKeyManager.save_keys(keys)
            logger.info(f"✅ API key revoked: {keys[hashed]['name']}")
            return True
        return False
    
    @staticmethod
    def is_admin_key(api_key: str) -> bool:
        """Check if API key has admin privileges"""
        hashed = hash_api_key(api_key)
        keys = APIKeyManager.load_keys()
        
        if hashed in keys:
            return keys[hashed].get("admin", False)
        return False

# ========================
# API KEY DEPENDENCY
# ========================

async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """FastAPI dependency for API key verification"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header."
        )
    
    if not APIKeyManager.verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    return x_api_key

async def verify_admin_api_key(x_api_key: str = Header(None)) -> str:
    """FastAPI dependency for admin API key verification"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    if not APIKeyManager.verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    if not APIKeyManager.is_admin_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return x_api_key

# ========================
# RATE LIMITING
# ========================

class RateLimiter:
    """Simple rate limiting system"""
    
    @staticmethod
    def load_limits() -> dict:
        """Load rate limits from file"""
        if os.path.exists(RATE_LIMIT_FILE):
            try:
                with open(RATE_LIMIT_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_limits(limits: dict):
        """Save rate limits to file"""
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump(limits, f, indent=2)
    
    @staticmethod
    def check_rate_limit(api_key: str, max_requests: int = 100, 
                        window_seconds: int = 3600) -> bool:
        """Check if request is within rate limit"""
        hashed = hash_api_key(api_key)
        limits = RateLimiter.load_limits()
        now = datetime.utcnow().timestamp()
        
        if hashed not in limits:
            limits[hashed] = {"requests": [], "blocked_until": None}
        
        # Check if key is temporarily blocked
        if limits[hashed].get("blocked_until"):
            if now < limits[hashed]["blocked_until"]:
                return False
            else:
                limits[hashed]["blocked_until"] = None
        
        # Clean old requests outside the window
        limits[hashed]["requests"] = [
            ts for ts in limits[hashed]["requests"]
            if now - ts < window_seconds
        ]
        
        # Check if limit exceeded
        if len(limits[hashed]["requests"]) >= max_requests:
            limits[hashed]["blocked_until"] = now + 300  # Block for 5 minutes
            RateLimiter.save_limits(limits)
            return False
        
        # Add current request
        limits[hashed]["requests"].append(now)
        RateLimiter.save_limits(limits)
        return True
    
    @staticmethod
    def get_limit_status(api_key: str, max_requests: int = 100, 
                        window_seconds: int = 3600) -> dict:
        """Get rate limit status for API key"""
        hashed = hash_api_key(api_key)
        limits = RateLimiter.load_limits()
        now = datetime.utcnow().timestamp()
        
        if hashed not in limits:
            return {
                "requests_used": 0,
                "requests_limit": max_requests,
                "requests_remaining": max_requests,
                "window_reset_seconds": window_seconds,
                "blocked": False
            }
        
        # Clean old requests
        limits[hashed]["requests"] = [
            ts for ts in limits[hashed]["requests"]
            if now - ts < window_seconds
        ]
        
        requests_used = len(limits[hashed]["requests"])
        blocked = limits[hashed].get("blocked_until", 0) > now
        
        return {
            "requests_used": requests_used,
            "requests_limit": max_requests,
            "requests_remaining": max(0, max_requests - requests_used),
            "window_reset_seconds": window_seconds,
            "blocked": blocked
        }

# ========================
# INITIALIZATION
# ========================

def init_auth():
    """Initialize authentication system with default keys"""
    try:
        # Create default admin key if none exists
        keys = APIKeyManager.load_keys()
        if not keys:
            admin_key = APIKeyManager.generate_api_key("admin-default", admin=True)
            user_key = APIKeyManager.generate_api_key("user-default", admin=False)
            logger.info(f"✅ Default keys created!")
            logger.info(f"   Admin Key: {admin_key}")
            logger.info(f"   User Key: {user_key}")
            return admin_key, user_key
    except Exception as e:
        logger.error(f"❌ Auth initialization failed: {e}")
    
    return None, None

if __name__ == "__main__":
    admin_key, user_key = init_auth()
    if admin_key:
        print(f"✅ Authentication system initialized!")
        print(f"Admin Key: {admin_key}")
        print(f"User Key: {user_key}")
