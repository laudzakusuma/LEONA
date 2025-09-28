import sqlite3
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiosqlite
from config import settings

class MemoryManager:
    def __init__(self):
        self.db_path = settings.MEMORY_DB_PATH
        self.preferences_path = settings.PREFERENCES_PATH
        asyncio.create_task(self._initialize_db())
    
    async def _initialize_db(self):
        """Initialize SQLite databases"""
        async with aiosqlite.connect(self.db_path) as db:
            # Conversations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT,
                    leona_response TEXT,
                    context TEXT
                )
            """)
            
            # Tasks table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    due_date DATETIME,
                    title TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 3
                )
            """)
            
            # User preferences table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    async def store_conversation(self, user_input: str, leona_response: str, context: str = ""):
        """Store conversation in memory"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO conversations (user_input, leona_response, context) VALUES (?, ?, ?)",
                (user_input, leona_response, context)
            )
            await db.commit()
    
    async def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversations"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "user_input": row[2],
                    "leona_response": row[3],
                    "context": row[4]
                }
                for row in rows
            ]
    
    async def get_context(self, user_input: str, limit: int = 5) -> str:
        """Get relevant context from memory"""
        # Simple keyword matching - can be enhanced with embeddings
        keywords = user_input.lower().split()
        
        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT user_input, leona_response 
                FROM conversations 
                WHERE """ + " OR ".join([f"LOWER(user_input) LIKE '%{kw}%'" for kw in keywords])
            query += " ORDER BY timestamp DESC LIMIT ?"
            
            cursor = await db.execute(query, (limit,))
            rows = await cursor.fetchall()
            
            if rows:
                context = "Previous related conversations:\n"
                for row in rows:
                    context += f"User: {row[0]}\nLEONA: {row[1]}\n---\n"
                return context
            return ""
    
    async def store_task(self, task: Dict[str, Any]):
        """Store a task"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO tasks (title, description, due_date, priority) 
                   VALUES (?, ?, ?, ?)""",
                (task.get('title'), task.get('description'), 
                 task.get('due_date'), task.get('priority', 3))
            )
            await db.commit()
    
    async def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, due_date ASC"
            )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "created_at": row[1],
                    "due_date": row[2],
                    "title": row[3],
                    "description": row[4],
                    "status": row[5],
                    "priority": row[6]
                }
                for row in rows
            ]
    
    async def update_preference(self, key: str, value: Any):
        """Update user preference"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)""",
                (key, json.dumps(value))
            )
            await db.commit()
    
    async def get_preference(self, key: str) -> Optional[Any]:
        """Get user preference"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value FROM preferences WHERE key = ?",
                (key,)
            )
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None