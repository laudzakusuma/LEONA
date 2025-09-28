"""File management agent for LEONA"""

import os
import shutil
import json
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent

class FileAgent(BaseAgent):
    """Agent for file and document operations"""
    
    def __init__(self, llm, memory):
        super().__init__(llm, memory)
        self.workspace = Path.home() / "LEONA_Workspace"
        self.workspace.mkdir(exist_ok=True)
        
    async def execute(self, user_input: str, parameters: Dict[str, Any] = None) -> str:
        """Execute file operations based on user input"""
        
        # Parse the file operation request
        operation = await self._parse_operation(user_input)
        
        try:
            if operation["action"] == "create":
                return await self._create_file(operation)
            elif operation["action"] == "read":
                return await self._read_file(operation)
            elif operation["action"] == "organize":
                return await self._organize_files(operation)
            elif operation["action"] == "search":
                return await self._search_files(operation)
            elif operation["action"] == "backup":
                return await self._backup_files(operation)
            elif operation["action"] == "analyze":
                return await self._analyze_directory(operation)
            else:
                return await self._suggest_file_action(user_input)
        except Exception as e:
            return f"I encountered an issue with the file operation: {str(e)}. Let me help you resolve this."
    
    async def _parse_operation(self, user_input: str) -> Dict[str, Any]:
        """Parse file operation from natural language"""
        prompt = f"""Analyze this file operation request:
        User: {user_input}
        
        Determine the action and parameters:
        - create: Create new file/document
        - read: Read file contents
        - organize: Organize files in directory
        - search: Search for files
        - backup: Create backups
        - analyze: Analyze directory structure
        
        Return as JSON with action and relevant parameters."""
        
        response = await self.llm.generate(prompt)
        try:
            import json
            return json.loads(response)
        except:
            return {"action": "unknown", "parameters": {}}
    
    async def _create_file(self, operation: Dict) -> str:
        """Create a new file or document"""
        filename = operation.get("filename", f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        content = operation.get("content", "")
        file_path = self.workspace / filename
        
        # Determine file type and create appropriate content
        if filename.endswith('.md'):
            content = f"# {filename.replace('.md', '')}\n\nCreated by LEONA on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{content}"
        elif filename.endswith('.json'):
            content = json.dumps({"created_by": "LEONA", "timestamp": datetime.now().isoformat(), "data": {}}, indent=2)
        
        file_path.write_text(content)
        
        return f"✨ I've created '{filename}' in your workspace. The file is ready for your use. Would you like me to open it or add any initial content?"
    
    async def _read_file(self, operation: Dict) -> str:
        """Read and summarize file contents"""
        filename = operation.get("filename")
        search_paths = [
            self.workspace,
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.cwd()
        ]
        
        file_path = None
        for path in search_paths:
            potential_path = path / filename if filename else None
            if potential_path and potential_path.exists():
                file_path = potential_path
                break
        
        if not file_path:
            return f"I couldn't locate '{filename}'. Would you like me to search in a specific directory or create this file for you?"
        
        try:
            content = file_path.read_text()[:2000]  # Limit content for summary
            
            # Generate intelligent summary
            summary_prompt = f"Summarize this document concisely:\n{content}"
            summary = await self.llm.generate(summary_prompt, max_tokens=200)
            
            return f"📄 **{filename}**\n\nSummary: {summary}\n\nThe file is {file_path.stat().st_size:,} bytes. Would you like me to perform any operations on it?"
        except Exception as e:
            return f"I can see the file but encountered an issue reading it. It might be a binary file or require special permissions."
    
    async def _organize_files(self, operation: Dict) -> str:
        """Organize files in a directory"""
        target_dir = Path(operation.get("directory", self.workspace))
        
        # Create organization structure
        categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.md'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg'],
            'Videos': ['.mp4', '.avi', '.mov', '.mkv'],
            'Audio': ['.mp3', '.wav', '.flac', '.m4a'],
            'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java'],
            'Data': ['.csv', '.json', '.xml', '.sql'],
            'Archives': ['.zip', '.tar', '.gz', '.rar']
        }
        
        organized_count = 0
        for category, extensions in categories.items():
            category_dir = target_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for ext in extensions:
                for file in target_dir.glob(f'*{ext}'):
                    if file.is_file() and file.parent == target_dir:
                        shutil.move(str(file), str(category_dir / file.name))
                        organized_count += 1
        
        # Organize by date for remaining files
        misc_dir = target_dir / 'Miscellaneous'
        misc_dir.mkdir(exist_ok=True)
        
        for file in target_dir.iterdir():
            if file.is_file():
                shutil.move(str(file), str(misc_dir / file.name))
                organized_count += 1
        
        return f"✨ Successfully organized {organized_count} files into categories. Your workspace is now beautifully arranged. Would you like a detailed report of the organization?"
    
    async def _search_files(self, operation: Dict) -> str:
        """Search for files with advanced filters"""
        query = operation.get("query", "")
        search_type = operation.get("type", "name")  # name, content, or modified
        
        results = []
        search_dir = Path(operation.get("directory", Path.home()))
        
        if search_type == "name":
            # Search by filename
            for file in search_dir.rglob(f"*{query}*"):
                if file.is_file():
                    results.append({
                        'path': str(file),
                        'size': file.stat().st_size,
                        'modified': datetime.fromtimestamp(file.stat().st_mtime)
                    })
                    if len(results) >= 10:
                        break
        
        elif search_type == "content":
            # Search file contents
            text_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']
            for ext in text_extensions:
                for file in search_dir.rglob(f"*{ext}"):
                    try:
                        content = file.read_text()
                        if query.lower() in content.lower():
                            results.append({
                                'path': str(file),
                                'match': content[max(0, content.lower().find(query.lower())-50):content.lower().find(query.lower())+50]
                            })
                            if len(results) >= 10:
                                break
                    except:
                        continue
        
        if results:
            response = f"📁 Found {len(results)} files matching '{query}':\n\n"
            for i, result in enumerate(results[:5], 1):
                response += f"{i}. {result['path']}\n"
                if 'size' in result:
                    response += f"   Size: {result['size']:,} bytes\n"
                if 'match' in result:
                    response += f"   Match: ...{result['match']}...\n"
            
            if len(results) > 5:
                response += f"\n...and {len(results)-5} more results."
            
            return response + "\n\nWould you like me to open, copy, or perform operations on any of these files?"
        else:
            return f"I couldn't find any files matching '{query}'. Would you like me to search in a different location or with different criteria?"
    
    async def _backup_files(self, operation: Dict) -> str:
        """Create intelligent backups"""
        source = Path(operation.get("source", self.workspace))
        backup_dir = Path.home() / "LEONA_Backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_backed_up = 0
        total_size = 0
        
        if source.is_file():
            shutil.copy2(source, backup_dir / source.name)
            files_backed_up = 1
            total_size = source.stat().st_size
        else:
            for file in source.rglob("*"):
                if file.is_file():
                    relative_path = file.relative_to(source)
                    backup_path = backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, backup_path)
                    files_backed_up += 1
                    total_size += file.stat().st_size
        
        # Create backup manifest
        manifest = {
            "backup_date": datetime.now().isoformat(),
            "source": str(source),
            "files_count": files_backed_up,
            "total_size": total_size,
            "created_by": "LEONA"
        }
        
        (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        
        return f"✅ Backup complete! I've secured {files_backed_up} files ({total_size:,} bytes) to:\n{backup_dir}\n\nYour data is safe and timestamped. Always one call away. ✨"
    
    async def _analyze_directory(self, operation: Dict) -> str:
        """Analyze directory structure and provide insights"""
        directory = Path(operation.get("directory", self.workspace))
        
        if not directory.exists():
            return f"The directory '{directory}' doesn't exist. Would you like me to create it?"
        
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'largest_files': [],
            'newest_files': [],
            'oldest_files': []
        }
        
        all_files = []
        for file in directory.rglob("*"):
            if file.is_file():
                stats['total_files'] += 1
                size = file.stat().st_size
                stats['total_size'] += size
                
                ext = file.suffix.lower()
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                all_files.append({
                    'path': file,
                    'size': size,
                    'modified': file.stat().st_mtime
                })
        
        # Sort and get top files
        all_files.sort(key=lambda x: x['size'], reverse=True)
        stats['largest_files'] = [f"{f['path'].name} ({f['size']:,} bytes)" for f in all_files[:3]]
        
        all_files.sort(key=lambda x: x['modified'], reverse=True)
        stats['newest_files'] = [f['path'].name for f in all_files[:3]]
        
        all_files.sort(key=lambda x: x['modified'])
        stats['oldest_files'] = [f['path'].name for f in all_files[:3]]
        
        # Generate report
        report = f"""📊 **Directory Analysis: {directory.name}**

📁 **Overview:**
• Total Files: {stats['total_files']:,}
• Total Size: {stats['total_size']/1024/1024:.2f} MB

📋 **File Types:**"""
        
        for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"\n• {ext or 'No extension'}: {count} files"
        
        report += f"""

🏆 **Largest Files:**"""
        for f in stats['largest_files']:
            report += f"\n• {f}"
        
        report += f"""

⏰ **Recently Modified:**"""
        for f in stats['newest_files']:
            report += f"\n• {f}"
        
        report += "\n\n💡 Would you like me to organize these files, create a backup, or perform any cleanup?"
        
        return report
    
    async def _suggest_file_action(self, user_input: str) -> str:
        """Suggest helpful file actions based on context"""
        suggestions = [
            "organize your documents by type and date",
            "create a backup of important files",
            "search for duplicate files",
            "analyze disk usage",
            "create a project template structure"
        ]
        
        return f"""I can help you with various file operations:

📁 **Available Actions:**
• Create documents and templates
• Organize files intelligently
• Search by name or content
• Create automated backups
• Analyze directory structures

💡 **Quick suggestions:** I could {suggestions[0]} or {suggestions[1]}.

What would you like me to help with?"""