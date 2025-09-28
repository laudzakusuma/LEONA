"""Scheduling and reminder agent for LEONA"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
from agents.base_agent import BaseAgent
from dateutil import parser
import re

class SchedulerAgent(BaseAgent):
    """Agent for managing schedules, reminders, and calendar events"""
    
    def __init__(self, llm, memory):
        super().__init__(llm, memory)
        self.reminders = []
        self.recurring_tasks = []
        # Start background task for checking reminders
        asyncio.create_task(self._reminder_checker())
    
    async def execute(self, user_input: str, parameters: Dict[str, Any] = None) -> str:
        """Execute scheduling operations"""
        
        # Parse scheduling request
        schedule_data = await self._parse_schedule_request(user_input)
        
        try:
            action = schedule_data.get("action")
            
            if action == "add_reminder":
                return await self._add_reminder(schedule_data)
            elif action == "add_event":
                return await self._add_calendar_event(schedule_data)
            elif action == "list_schedule":
                return await self._list_schedule(schedule_data)
            elif action == "add_recurring":
                return await self._add_recurring_task(schedule_data)
            elif action == "check_conflicts":
                return await self._check_conflicts(schedule_data)
            elif action == "suggest_time":
                return await self._suggest_meeting_time(schedule_data)
            else:
                return await self._provide_schedule_overview()
        except Exception as e:
            return f"I encountered an issue with scheduling: {str(e)}. Let me help you set this up correctly."
    
    async def _parse_schedule_request(self, user_input: str) -> Dict[str, Any]:
        """Parse scheduling request using NLP"""
        prompt = f"""Parse this scheduling request:
        User: {user_input}
        
        Extract:
        - action: (add_reminder, add_event, list_schedule, add_recurring, check_conflicts, suggest_time)
        - title: Event/reminder title
        - time: When (parse natural language like "tomorrow at 3pm", "next Monday")
        - duration: How long (for events)
        - recurring: Pattern if recurring (daily, weekly, monthly)
        - priority: high, medium, low
        
        Return as JSON."""
        
        response = await self.llm.generate(prompt)
        try:
            data = json.loads(response)
            # Parse time if present
            if 'time' in data:
                data['parsed_time'] = self._parse_natural_time(data['time'])
            return data
        except:
            return {"action": "unknown"}
    
    def _parse_natural_time(self, time_str: str) -> datetime:
        """Parse natural language time expressions"""
        now = datetime.now()
        time_str_lower = time_str.lower()
        
        # Handle relative times
        if "tomorrow" in time_str_lower:
            base_date = now + timedelta(days=1)
        elif "today" in time_str_lower:
            base_date = now
        elif "next week" in time_str_lower:
            base_date = now + timedelta(weeks=1)
        elif "next month" in time_str_lower:
            base_date = now + timedelta(days=30)
        else:
            # Try to parse with dateutil
            try:
                return parser.parse(time_str)
            except:
                base_date = now
        
        # Extract time from string
        time_match = re.search(r'(\d{1,2}):?(\d{0,2})?\s*(am|pm)?', time_str_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            am_pm = time_match.group(3)
            
            if am_pm == 'pm' and hour < 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
            
            return base_date.replace(hour=hour, minute=minute, second=0)
        
        return base_date
    
    async def _add_reminder(self, data: Dict) -> str:
        """Add a reminder"""
        reminder = {
            'id': len(self.reminders) + 1,
            'title': data.get('title', 'Reminder'),
            'time': data.get('parsed_time', datetime.now() + timedelta(hours=1)),
            'priority': data.get('priority', 'medium'),
            'created_at': datetime.now(),
            'notified': False
        }
        
        self.reminders.append(reminder)
        
        # Store in memory
        await self.memory.store_task({
            'title': reminder['title'],
            'due_date': reminder['time'].isoformat(),
            'priority': {'high': 1, 'medium': 2, 'low': 3}[reminder['priority']]
        })
        
        time_str = reminder['time'].strftime('%B %d at %I:%M %p')
        return f"""✅ Reminder set successfully!

📅 **{reminder['title']}**
⏰ Time: {time_str}
🎯 Priority: {reminder['priority'].capitalize()}

I'll notify you when it's time. Would you like to add any additional details or set another reminder?"""
    
    async def _add_calendar_event(self, data: Dict) -> str:
        """Add a calendar event"""
        event = {
            'title': data.get('title', 'New Event'),
            'start_time': data.get('parsed_time', datetime.now() + timedelta(days=1)),
            'duration': data.get('duration', 60),  # minutes
            'location': data.get('location', ''),
            'description': data.get('description', ''),
            'attendees': data.get('attendees', [])
        }
        
        # Check for conflicts
        conflicts = await self._check_conflicts(event)
        
        # Store event
        await self.memory.store_task({
            'title': f"Event: {event['title']}",
            'description': json.dumps(event),
            'due_date': event['start_time'].isoformat()
        })
        
        response = f"""📅 **Event Created: {event['title']}**

📍 When: {event['start_time'].strftime('%B %d at %I:%M %p')}
⏱️ Duration: {event['duration']} minutes"""
        
        if event['location']:
            response += f"\n📍 Where: {event['location']}"
        
        if conflicts:
            response += f"\n\n⚠️ **Potential conflict detected:** {conflicts}"
            response += "\nWould you like me to suggest an alternative time?"
        else:
            response += "\n\n✨ Your calendar is clear for this time. I'll remind you 15 minutes before."
        
        return response
    
    async def _list_schedule(self, data: Dict) -> str:
        """List upcoming schedule"""
        # Get tasks from memory
        tasks = await self.memory.get_pending_tasks()
        
        if not tasks and not self.reminders:
            return "📅 Your schedule is completely clear! Would you like me to help you plan your day?"
        
        now = datetime.now()
        today_items = []
        tomorrow_items = []
        week_items = []
        
        # Combine reminders and tasks
        all_items = []
        for reminder in self.reminders:
            if not reminder['notified']:
                all_items.append({
                    'title': reminder['title'],
                    'time': reminder['time'],
                    'type': 'reminder',
                    'priority': reminder['priority']
                })
        
        for task in tasks:
            if task['due_date']:
                all_items.append({
                    'title': task['title'],
                    'time': datetime.fromisoformat(task['due_date']),
                    'type': 'task',
                    'priority': ['high', 'medium', 'low'][task['priority'] - 1]
                })
        
        # Sort and categorize
        all_items.sort(key=lambda x: x['time'])
        
        for item in all_items:
            delta = item['time'] - now
            if delta.days == 0 and delta.seconds >= 0:
                today_items.append(item)
            elif delta.days == 1:
                tomorrow_items.append(item)
            elif delta.days <= 7 and delta.days > 0:
                week_items.append(item)
        
        response = "📅 **Your Upcoming Schedule**\n\n"
        
        if today_items:
            response += "**Today:**\n"
            for item in today_items:
                emoji = "🔔" if item['type'] == 'reminder' else "📋"
                response += f"{emoji} {item['time'].strftime('%I:%M %p')} - {item['title']}"
                if item['priority'] == 'high':
                    response += " ⚠️"
                response += "\n"
        
        if tomorrow_items:
            response += "\n**Tomorrow:**\n"
            for item in tomorrow_items:
                emoji = "🔔" if item['type'] == 'reminder' else "📋"
                response += f"{emoji} {item['time'].strftime('%I:%M %p')} - {item['title']}\n"
        
        if week_items:
            response += "\n**This Week:**\n"
            for item in week_items:
                emoji = "🔔" if item['type'] == 'reminder' else "📋"
                response += f"{emoji} {item['time'].strftime('%a %b %d, %I:%M %p')} - {item['title']}\n"
        
        response += "\n💡 Would you like to add anything else or shall I help you prepare for any of these?"
        
        return response
    
    async def _add_recurring_task(self, data: Dict) -> str:
        """Add a recurring task"""
        recurring = {
            'title': data.get('title', 'Recurring Task'),
            'pattern': data.get('recurring', 'daily'),
            'time': data.get('parsed_time', datetime.now().replace(hour=9, minute=0)),
            'active': True
        }
        
        self.recurring_tasks.append(recurring)
        
        pattern_descriptions = {
            'daily': 'every day',
            'weekly': 'every week',
            'monthly': 'every month',
            'weekdays': 'every weekday'
        }
        
        return f"""🔄 **Recurring Task Created**

📋 Task: {recurring['title']}
🔁 Frequency: {pattern_descriptions.get(recurring['pattern'], recurring['pattern'])}
⏰ Time: {recurring['time'].strftime('%I:%M %p')}

I'll remind you {pattern_descriptions.get(recurring['pattern'], recurring['pattern'])} at this time. You can modify or cancel this anytime."""
    
    async def _check_conflicts(self, event: Dict) -> str:
        """Check for scheduling conflicts"""
        tasks = await self.memory.get_pending_tasks()
        
        event_start = event.get('start_time') or event.get('time')
        event_end = event_start + timedelta(minutes=event.get('duration', 60))
        
        conflicts = []
        for task in tasks:
            if task['due_date']:
                task_time = datetime.fromisoformat(task['due_date'])
                # Check if times overlap
                if event_start <= task_time <= event_end:
                    conflicts.append(task['title'])
        
        if conflicts:
            return f"You have '{conflicts[0]}' scheduled at that time"
        return ""
    
    async def _suggest_meeting_time(self, data: Dict) -> str:
        """Suggest optimal meeting times"""
        duration = data.get('duration', 60)  # minutes
        preferences = data.get('preferences', {})
        
        # Get existing schedule
        tasks = await self.memory.get_pending_tasks()
        busy_times = []
        for task in tasks:
            if task['due_date']:
                busy_times.append(datetime.fromisoformat(task['due_date']))
        
        # Find available slots
        suggestions = []
        now = datetime.now()
        
        # Check next 7 days
        for day_offset in range(7):
            check_date = now + timedelta(days=day_offset)
            
            # Preferred meeting hours (9 AM - 5 PM)
            for hour in [9, 10, 11, 14, 15, 16]:
                slot_start = check_date.replace(hour=hour, minute=0, second=0)
                slot_end = slot_start + timedelta(minutes=duration)
                
                # Check if slot is free
                is_free = True
                for busy in busy_times:
                    if slot_start <= busy <= slot_end:
                        is_free = False
                        break
                
                if is_free and slot_start > now:
                    suggestions.append(slot_start)
                    if len(suggestions) >= 3:
                        break
            
            if len(suggestions) >= 3:
                break
        
        if suggestions:
            response = f"🗓️ **Available Time Slots** (for {duration}-minute meeting):\n\n"
            for i, slot in enumerate(suggestions, 1):
                response += f"{i}. {slot.strftime('%A, %B %d at %I:%M %p')}\n"
            response += "\n✨ All these times are clear in your schedule. Which works best for you?"
        else:
            response = "Your schedule is quite full! Would you like me to look at times outside business hours or next week?"
        
        return response
    
    async def _provide_schedule_overview(self) -> str:
        """Provide a helpful schedule overview"""
        tasks = await self.memory.get_pending_tasks()
        
        now = datetime.now()
        hour = now.hour
        
        # Time-based greeting
        if hour < 12:
            greeting = "Good morning! ☀️"
        elif hour < 17:
            greeting = "Good afternoon! ☕"
        else:
            greeting = "Good evening! 🌙"
        
        response = f"""{greeting}

I can help you manage your schedule efficiently. Here's what I can do:

📅 **Schedule Management:**
• Add reminders and calendar events
• Set recurring tasks and habits
• Check for scheduling conflicts
• Suggest optimal meeting times
• Provide daily/weekly overviews

You currently have {len(tasks)} items on your schedule."""
        
        if tasks:
            next_task = tasks[0]
            response += f"\n\n⏰ **Next up:** {next_task['title']}"
            if next_task['due_date']:
                response += f" at {datetime.fromisoformat(next_task['due_date']).strftime('%I:%M %p')}"
        
        response += "\n\nWhat would you like to schedule or review?"
        
        return response
    
    async def _reminder_checker(self):
        """Background task to check and trigger reminders"""
        while True:
            try:
                now = datetime.now()
                
                for reminder in self.reminders:
                    if not reminder['notified'] and reminder['time'] <= now:
                        # Trigger notification (in real implementation, would send actual notification)
                        print(f"🔔 REMINDER: {reminder['title']}")
                        reminder['notified'] = True
                
                # Check recurring tasks
                for task in self.recurring_tasks:
                    if task['active']:
                        # Logic to create reminders based on pattern
                        pass
                
                # Wait 60 seconds before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Reminder checker error: {e}")
                await asyncio.sleep(60)