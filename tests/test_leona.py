"""
Comprehensive test suite for LEONA
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timedelta

# Import LEONA components
from backend.main import app
from backend.core.llm_engine import LLMEngine
from backend.core.memory_manager import MemoryManager
from backend.core.agent_orchestrator import AgentOrchestrator
from backend.agents.scheduler_agent import SchedulerAgent
from backend.agents.file_agent import FileAgent
from backend.core.security_manager import SecurityManager

# Test client
client = TestClient(app)

class TestLeonaCore:
    """Test core LEONA functionality"""
    
    @pytest.fixture
    def llm_engine(self):
        """Create LLM engine for testing"""
        with patch('backend.core.llm_engine.Llama') as mock_llama:
            mock_llama.return_value = Mock()
            engine = LLMEngine()
            engine.model = mock_llama.return_value
            return engine
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager for testing"""
        return MemoryManager()
    
    @pytest.mark.asyncio
    async def test_llm_generation(self, llm_engine):
        """Test LLM text generation"""
        llm_engine.model.return_value = {
            'choices': [{'text': 'Test response from LEONA'}]
        }
        
        response = await llm_engine.generate("Test prompt")
        
        assert response == 'Test response from LEONA'
        llm_engine.model.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_storage(self, memory_manager):
        """Test memory storage and retrieval"""
        # Store conversation
        await memory_manager.store_conversation(
            "Test input",
            "Test response",
            "test_context"
        )
        
        # Retrieve conversations
        conversations = await memory_manager.get_recent_conversations(1)
        
        assert len(conversations) > 0
        assert conversations[0]['user_input'] == "Test input"
        assert conversations[0]['leona_response'] == "Test response"
    
    @pytest.mark.asyncio
    async def test_task_management(self, memory_manager):
        """Test task storage and retrieval"""
        task = {
            'title': 'Test Task',
            'description': 'Test description',
            'due_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'priority': 1
        }
        
        await memory_manager.store_task(task)
        tasks = await memory_manager.get_pending_tasks()
        
        assert len(tasks) > 0
        assert tasks[0]['title'] == 'Test Task'

class TestAgents:
    """Test LEONA agents"""
    
    @pytest.fixture
    def scheduler_agent(self, llm_engine, memory_manager):
        """Create scheduler agent for testing"""
        return SchedulerAgent(llm_engine, memory_manager)
    
    @pytest.fixture
    def file_agent(self, llm_engine, memory_manager):
        """Create file agent for testing"""
        return FileAgent(llm_engine, memory_manager)
    
    @pytest.mark.asyncio
    async def test_scheduler_reminder(self, scheduler_agent):
        """Test reminder creation"""
        scheduler_agent.llm.generate = AsyncMock(return_value=json.dumps({
            'action': 'add_reminder',
            'title': 'Test Reminder',
            'time': 'tomorrow at 3pm',
            'priority': 'high'
        }))
        
        response = await scheduler_agent.execute("Remind me to test tomorrow at 3pm")
        
        assert "Reminder set successfully" in response
        assert len(scheduler_agent.reminders) > 0
    
    @pytest.mark.asyncio
    async def test_file_operations(self, file_agent):
        """Test file operations"""
        file_agent.llm.generate = AsyncMock(return_value=json.dumps({
            'action': 'create',
            'filename': 'test.txt',
            'content': 'Test content'
        }))
        
        response = await file_agent.execute("Create a test file")
        
        assert "created" in response.lower()
        # Verify file was created in workspace
        test_file = file_agent.workspace / 'test.txt'
        if test_file.exists():
            test_file.unlink()  # Clean up

class TestAPI:
    """Test LEONA API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "LEONA" in response.text
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'online'
        assert data['name'] == 'LEONA'
        assert data['tagline'] == 'Always One Call Away'
    
    def test_chat_endpoint(self):
        """Test chat endpoint"""
        with patch('backend.main.app.state.orchestrator') as mock_orchestrator:
            mock_orchestrator.process_input = AsyncMock(
                return_value="Test response from LEONA"
            )
            
            response = client.post(
                "/api/chat",
                json={"message": "Hello LEONA"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert 'response' in data

class TestSecurity:
    """Test security features"""
    
    @pytest.fixture
    def security_manager(self):
        """Create security manager for testing"""
        return SecurityManager(secret_key="test_secret_key")
    
    def test_password_hashing(self, security_manager):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = security_manager.hash_password(password)
        
        assert hashed != password
        assert security_manager.verify_password(password, hashed)
        assert not security_manager.verify_password("wrong_password", hashed)
    
    def test_token_generation(self, security_manager):
        """Test JWT token generation and verification"""
        token = security_manager.generate_token(1, "test_user", "admin")
        
        payload = security_manager.verify_token(token)
        
        assert payload is not None
        assert payload['user_id'] == 1
        assert payload['username'] == "test_user"
        assert payload['role'] == "admin"
    
    def test_api_key_generation(self, security_manager):
        """Test API key generation"""
        api_key = security_manager.generate_api_key()
        
        assert api_key.startswith("leona_")
        assert len(api_key) > 40

class TestVectorMemory:
    """Test vector memory system"""
    
    @pytest.fixture
    def vector_memory(self):
        """Create vector memory for testing"""
        from backend.core.vector_memory import VectorMemory
        return VectorMemory()
    
    @pytest.mark.asyncio
    async def test_memory_encoding(self, vector_memory):
        """Test text encoding to vectors"""
        text = "This is a test memory"
        embedding = await vector_memory.encode_text(text)
        
        assert embedding is not None
        assert embedding.shape[0] == vector_memory.embedding_dim
    
    @pytest.mark.asyncio
    async def test_memory_search(self, vector_memory):
        """Test semantic memory search"""
        # Add test memories
        await vector_memory.add_memory(
            "I like to schedule meetings in the morning",
            category="preferences"
        )
        await vector_memory.add_memory(
            "My favorite programming language is Python",
            category="preferences"
        )
        
        # Search for related memory
        results = await vector_memory.search_memories(
            "morning meetings",
            k=1
        )
        
        assert len(results) > 0
        assert "morning" in results[0]['content'].lower()

class TestAutomation:
    """Test automation features"""
    
    @pytest.fixture
    def automation_agent(self, llm_engine, memory_manager):
        """Create automation agent for testing"""
        from backend.agents.automation_agent import AutomationAgent
        return AutomationAgent(llm_engine, memory_manager)
    
    @pytest.mark.asyncio
    async def test_workflow_creation(self, automation_agent):
        """Test workflow creation"""
        automation_agent.llm.generate = AsyncMock(return_value=json.dumps({
            'action': 'create_workflow',
            'workflow_name': 'Test Workflow',
            'trigger': {'type': 'time', 'schedule': '0 9 * * *'},
            'actions': ['send_email', 'update_calendar']
        }))
        
        response = await automation_agent.execute("Create a morning workflow")
        
        assert "Workflow Created" in response
        assert len(automation_agent.workflows) > 0
    
    @pytest.mark.asyncio
    async def test_iot_device_control(self, automation_agent):
        """Test IoT device control"""
        automation_agent.llm.generate = AsyncMock(return_value=json.dumps({
            'action': 'control_device',
            'device': 'living_room_lights',
            'device_action': 'turn_on'
        }))
        
        response = await automation_agent.execute("Turn on living room lights")
        
        assert "Device Control" in response
        assert 'living_room_lights' in automation_agent.iot_devices

# Performance tests
class TestPerformance:
    """Test performance metrics"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test response time is within acceptable limits"""
        import time
        
        start = time.time()
        response = client.get("/api/status")
        end = time.time()
        
        response_time = end - start
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import aiohttp
        import asyncio
        
        async def make_request(session):
            async with session.get("http://localhost:8000/api/status") as response:
                return response.status
        
        async def test_concurrency():
            async with aiohttp.ClientSession() as session:
                tasks = [make_request(session) for _ in range(10)]
                results = await asyncio.gather(*tasks)
                
                assert all(status == 200 for status in results)
        
        # Note: This test requires the server to be running
        # await test_concurrency()

# Integration tests
class TestIntegration:
    """Integration tests for LEONA"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test complete conversation flow"""
        # This would test the full flow from input to response
        # Including LLM, memory, and agent orchestration
        pass
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self):
        """Test multiple agents working together"""
        # Test scenario where multiple agents collaborate
        pass

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])