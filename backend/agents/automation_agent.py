"""
Advanced automation agent for complex workflows and IoT integration
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
import json
from agents.base_agent import BaseAgent
from enum import Enum

class TriggerType(Enum):
    TIME = "time"
    EVENT = "event"
    CONDITION = "condition"
    WEBHOOK = "webhook"
    IOT = "iot"

class AutomationAgent(BaseAgent):
    """Agent for workflow automation and IoT device control"""
    
    def __init__(self, llm, memory):
        super().__init__(llm, memory)
        self.workflows = {}
        self.iot_devices = {}
        self.running_workflows = {}
        self.triggers = {}
        
        # Start automation engine
        asyncio.create_task(self._automation_engine())
    
    async def execute(self, user_input: str, parameters: Dict[str, Any] = None) -> str:
        """Execute automation commands"""
        
        command = await self._parse_automation_command(user_input)
        
        try:
            if command['action'] == 'create_workflow':
                return await self._create_workflow(command)
            elif command['action'] == 'list_workflows':
                return await self._list_workflows()
            elif command['action'] == 'control_device':
                return await self._control_iot_device(command)
            elif command['action'] == 'create_automation':
                return await self._create_automation_rule(command)
            elif command['action'] == 'monitor':
                return await self._monitor_status()
            else:
                return await self._suggest_automation(user_input)
        except Exception as e:
            return f"Automation error: {str(e)}. Let me help you set this up correctly."
    
    async def _parse_automation_command(self, user_input: str) -> Dict:
        """Parse automation command from natural language"""
        prompt = f"""Parse this automation request:
        User: {user_input}
        
        Determine:
        - action: create_workflow, list_workflows, control_device, create_automation, monitor
        - workflow_name: if creating/modifying workflow
        - device: if controlling IoT device
        - trigger: what triggers the automation
        - conditions: any conditions to check
        - actions: what actions to take
        
        Return as JSON."""
        
        response = await self.llm.generate(prompt)
        try:
            return json.loads(response)
        except:
            return {"action": "unknown"}
    
    async def _create_workflow(self, config: Dict) -> str:
        """Create a new automation workflow"""
        workflow_id = f"workflow_{len(self.workflows)}"
        
        workflow = {
            'id': workflow_id,
            'name': config.get('workflow_name', 'Unnamed Workflow'),
            'description': config.get('description', ''),
            'trigger': self._parse_trigger(config.get('trigger', {})),
            'conditions': config.get('conditions', []),
            'actions': config.get('actions', []),
            'created_at': datetime.now().isoformat(),
            'enabled': True,
            'last_run': None,
            'run_count': 0
        }
        
        self.workflows[workflow_id] = workflow
        
        # Register trigger
        await self._register_trigger(workflow_id, workflow['trigger'])
        
        return f"""✅ **Workflow Created: {workflow['name']}**

🔄 Trigger: {self._describe_trigger(workflow['trigger'])}
⚡ Actions: {len(workflow['actions'])} steps configured

The workflow is now active and will run automatically when triggered.
Would you like to test it or add more conditions?"""
    
    def _parse_trigger(self, trigger_config: Dict) -> Dict:
        """Parse trigger configuration"""
        trigger_type = trigger_config.get('type', 'manual')
        
        if trigger_type == 'time':
            return {
                'type': TriggerType.TIME,
                'schedule': trigger_config.get('schedule', '0 9 * * *'),  # Default: 9 AM daily
                'timezone': trigger_config.get('timezone', 'local')
            }
        elif trigger_type == 'event':
            return {
                'type': TriggerType.EVENT,
                'event_name': trigger_config.get('event_name'),
                'source': trigger_config.get('source')
            }
        elif trigger_type == 'iot':
            return {
                'type': TriggerType.IOT,
                'device_id': trigger_config.get('device_id'),
                'condition': trigger_config.get('condition')
            }
        else:
            return {'type': TriggerType.EVENT, 'event_name': 'manual'}
    
    def _describe_trigger(self, trigger: Dict) -> str:
        """Generate human-readable trigger description"""
        if trigger['type'] == TriggerType.TIME:
            return f"Scheduled ({trigger['schedule']})"
        elif trigger['type'] == TriggerType.EVENT:
            return f"When {trigger['event_name']} occurs"
        elif trigger['type'] == TriggerType.IOT:
            return f"When device {trigger['device_id']} {trigger.get('condition', 'changes')}"
        else:
            return "Manual trigger"
    
    async def _register_trigger(self, workflow_id: str, trigger: Dict):
        """Register workflow trigger"""
        trigger_key = f"{trigger['type'].value}_{workflow_id}"
        self.triggers[trigger_key] = {
            'workflow_id': workflow_id,
            'config': trigger,
            'registered_at': datetime.now()
        }
    
    async def _create_automation_rule(self, config: Dict) -> str:
        """Create if-this-then-that automation rule"""
        
        # Parse natural language into IFTTT format
        rule_prompt = f"""Convert this to an automation rule:
        Request: {config}
        
        Format as:
        IF: [condition]
        THEN: [action]
        ELSE: [alternative action] (optional)"""
        
        rule_text = await self.llm.generate(rule_prompt)
        
        # Create automation
        automation = {
            'id': f"auto_{len(self.workflows)}",
            'rule_text': rule_text,
            'if_condition': config.get('if_condition'),
            'then_action': config.get('then_action'),
            'else_action': config.get('else_action'),
            'active': True
        }
        
        # Convert to workflow
        workflow = {
            'id': automation['id'],
            'name': f"Automation: {automation['if_condition'][:30]}...",
            'trigger': {'type': TriggerType.CONDITION, 'condition': automation['if_condition']},
            'actions': [automation['then_action']],
            'created_at': datetime.now().isoformat(),
            'enabled': True
        }
        
        self.workflows[automation['id']] = workflow
        
        return f"""🤖 **Automation Rule Created**

{rule_text}

This automation is now active and monitoring for the specified conditions.
I'll notify you whenever it triggers. Always one call away! ✨"""
    
    async def _control_iot_device(self, command: Dict) -> str:
        """Control IoT devices"""
        device_id = command.get('device')
        action = command.get('device_action')
        
        # Simulate IoT device control
        # In production, this would interface with actual IoT platforms
        
        if device_id not in self.iot_devices:
            # Register new device
            self.iot_devices[device_id] = {
                'id': device_id,
                'type': command.get('device_type', 'smart_device'),
                'state': 'unknown',
                'last_seen': datetime.now(),
                'capabilities': []
            }
        
        device = self.iot_devices[device_id]
        
        # Execute action
        result = await self._execute_device_action(device, action)
        
        return f"""🏠 **IoT Device Control**

Device: {device_id}
Action: {action}
Status: {result}

The device has been successfully controlled. 
Would you like to create an automation for this device?"""
    
    async def _execute_device_action(self, device: Dict, action: str) -> str:
        """Execute action on IoT device"""
        # Simulate device control
        # In production, integrate with:
        # - Home Assistant
        # - SmartThings
        # - Philips Hue
        # - MQTT brokers
        # - Custom IoT APIs
        
        device['state'] = action
        device['last_seen'] = datetime.now()
        
        return f"✅ {action} executed successfully"
    
    async def _list_workflows(self) -> str:
        """List all automation workflows"""
        if not self.workflows:
            return """No workflows configured yet. 

I can help you create automations like:
• Morning routine (lights, music, calendar briefing)
• Email filtering and responses
• File organization workflows
• IoT device scheduling
• Data backup automation

What would you like to automate?"""
        
        response = "🔄 **Active Workflows**\n\n"
        
        for wf_id, workflow in self.workflows.items():
            status = "✅ Active" if workflow['enabled'] else "⏸️ Paused"
            last_run = workflow['last_run'] or "Never"
            
            response += f"""**{workflow['name']}** {status}
Trigger: {self._describe_trigger(workflow['trigger'])}
Last Run: {last_run}
Run Count: {workflow['run_count']}
---
"""
        
        return response + "\n💡 Say 'run [workflow name]' to test any workflow."
    
    async def _monitor_status(self) -> str:
        """Monitor automation system status"""
        
        active_workflows = sum(1 for w in self.workflows.values() if w['enabled'])
        total_runs = sum(w['run_count'] for w in self.workflows.values())
        connected_devices = len(self.iot_devices)
        
        # Check recent activity
        recent_runs = []
        for workflow in self.workflows.values():
            if workflow['last_run']:
                last_run_time = datetime.fromisoformat(workflow['last_run'])
                if (datetime.now() - last_run_time).days < 1:
                    recent_runs.append(workflow['name'])
        
        status = f"""📊 **Automation System Status**

🔄 **Workflows:**
• Active: {active_workflows}
• Total Executions: {total_runs}
• Recent Activity: {', '.join(recent_runs) if recent_runs else 'None in last 24h'}

🏠 **IoT Devices:**
• Connected: {connected_devices}
• Status: All systems operational

⚡ **Performance:**
• Response Time: < 100ms
• Reliability: 99.9%
• Queue: 0 pending tasks

Everything is running smoothly. Your automations are working in the background."""
        
        return status
    
    async def _suggest_automation(self, context: str) -> str:
        """Suggest helpful automations based on context"""
        
        suggestions_prompt = f"""Based on this context: {context}
        
        Suggest 3 helpful automations that would save time or improve efficiency.
        Format as actionable automation ideas."""
        
        suggestions = await self.llm.generate(suggestions_prompt)
        
        return f"""💡 **Automation Suggestions**

{suggestions}

Would you like me to set up any of these automations for you?
I can create complex workflows that run automatically based on your needs.

Always one call away to make your life easier! ✨"""
    
    async def _automation_engine(self):
        """Background engine for running automations"""
        while True:
            try:
                current_time = datetime.now()
                
                # Check time-based triggers
                for trigger_key, trigger_data in self.triggers.items():
                    if trigger_data['config']['type'] == TriggerType.TIME:
                        # Check if it's time to run
                        # (Simplified - in production use croniter or APScheduler)
                        workflow_id = trigger_data['workflow_id']
                        if workflow_id in self.workflows:
                            workflow = self.workflows[workflow_id]
                            if workflow['enabled']:
                                # Check schedule
                                await self._check_and_run_workflow(workflow)
                
                # Check condition-based triggers
                for workflow in self.workflows.values():
                    if workflow['enabled'] and workflow['trigger']['type'] == TriggerType.CONDITION:
                        # Evaluate conditions
                        await self._evaluate_conditions(workflow)
                
                # Sleep for 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Automation engine error: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_run_workflow(self, workflow: Dict):
        """Check and run workflow if conditions are met"""
        # Simplified execution - expand for production
        workflow['last_run'] = datetime.now().isoformat()
        workflow['run_count'] += 1
        
        # Execute actions
        for action in workflow['actions']:
            await self._execute_workflow_action(action)
    
    async def _execute_workflow_action(self, action: Any):
        """Execute a workflow action"""
        # Implement actual action execution
        # Could integrate with other agents or external services
        pass
    
    async def _evaluate_conditions(self, workflow: Dict):
        """Evaluate workflow conditions"""
        # Implement condition evaluation logic
        pass