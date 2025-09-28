"""Web browsing and information gathering agent for LEONA"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import json
from agents.base_agent import BaseAgent
from urllib.parse import urlparse, quote

class WebAgent(BaseAgent):
    """Agent for web browsing and information gathering"""
    
    def __init__(self, llm, memory):
        super().__init__(llm, memory)
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def execute(self, user_input: str, parameters: Dict[str, Any] = None) -> str:
        """Execute web-related operations"""
        
        # Parse web request
        web_action = await self._parse_web_request(user_input)
        
        try:
            if web_action['action'] == 'search':
                return await self._search_web(web_action['query'])
            elif web_action['action'] == 'fetch_page':
                return await self._fetch_webpage(web_action['url'])
            elif web_action['action'] == 'monitor':
                return await self._monitor_website(web_action)
            elif web_action['action'] == 'summarize':
                return await self._summarize_article(web_action['url'])
            elif web_action['action'] == 'research':
                return await self._research_topic(web_action['topic'])
            else:
                return "I can help you browse the web, search for information, or monitor websites. What would you like to know?"
        except Exception as e:
            return f"I encountered an issue accessing web content: {str(e)}. Let me try an alternative approach."
    
    async def _parse_web_request(self, user_input: str) -> Dict[str, Any]:
        """Parse web browsing request"""
        prompt = f"""Parse this web request:
        User: {user_input}
        
        Determine:
        - action: search, fetch_page, monitor, summarize, research
        - query: search terms if searching
        - url: specific URL if provided
        - topic: research topic if applicable
        
        Return as JSON."""
        
        response = await self.llm.generate(prompt)
        try:
            return json.loads(response)
        except:
            # Fallback to simple search
            return {"action": "search", "query": user_input}
    
    async def _search_web(self, query: str) -> str:
        """Perform web search (using a simple DuckDuckGo approach)"""
        # In production, you'd use proper search APIs
        search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(search_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                for result in soup.find_all('div', class_='result')[:5]:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results.append({
                            'title': title_elem.text.strip(),
                            'url': title_elem.get('href', ''),
                            'snippet': snippet_elem.text.strip() if snippet_elem else ''
                        })
                
                if results:
                    response_text = f"🔍 **Search Results for '{query}':**\n\n"
                    for i, r in enumerate(results, 1):
                        response_text += f"{i}. **{r['title']}**\n"
                        if r['snippet']:
                            response_text += f"   {r['snippet'][:150]}...\n"
                        response_text += "\n"
                    
                    response_text += "Would you like me to read any of these articles in detail or search for something else?"
                    return response_text
                else:
                    return f"I couldn't find results for '{query}'. Would you like me to try different search terms?"
                    
        except Exception as e:
            return f"I encountered an issue searching. Let me help you find this information another way."
    
    async def _fetch_webpage(self, url: str) -> str:
        """Fetch and parse webpage content"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract text content
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit text length
                text = text[:2000]
                
                # Generate summary
                summary_prompt = f"Summarize this webpage content concisely:\n{text}"
                summary = await self.llm.generate(summary_prompt, max_tokens=200)
                
                return f"""📄 **Webpage Summary**
                
🔗 URL: {url}
📝 Summary: {summary}

Would you like me to extract specific information or search for something else?"""
                
        except Exception as e:
            return f"I couldn't access {url}. The site might be unavailable or restricted. Can I search for this information elsewhere?"
    
    async def _summarize_article(self, url: str) -> str:
        """Fetch and create detailed article summary"""
        content = await self._fetch_webpage(url)
        
        # Additional processing for articles
        prompt = f"""Create a structured summary of this article with:
        1. Main topic
        2. Key points (3-5)
        3. Important quotes or data
        4. Conclusion
        
        Content: {content}"""
        
        detailed_summary = await self.llm.generate(prompt, max_tokens=400)
        
        return f"""📚 **Article Analysis**

{detailed_summary}

💡 Would you like me to research related topics or save this summary for later reference?"""
    
    async def _research_topic(self, topic: str) -> str:
        """Conduct comprehensive research on a topic"""
        research_queries = [
            f"{topic} overview",
            f"{topic} latest news",
            f"{topic} key facts"
        ]
        
        research_results = []
        for query in research_queries:
            result = await self._search_web(query)
            research_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        
        # Synthesize research
        synthesis_prompt = f"""Based on this research about {topic}, create a comprehensive summary:
        
        {' '.join(research_results[:1000])}
        
        Include:
        1. Overview
        2. Recent developments
        3. Key insights
        4. Recommendations for further reading"""
        
        synthesis = await self.llm.generate(synthesis_prompt, max_tokens=500)
        
        return f"""🔬 **Research Report: {topic}**

{synthesis}

📊 This research is based on current web sources. Would you like me to:
• Deep dive into any specific aspect
• Set up monitoring for updates
• Save this research to your workspace

Always one call away for your information needs. ✨"""
    
    async def _monitor_website(self, config: Dict) -> str:
        """Set up website monitoring"""
        monitor_config = {
            'url': config.get('url'),
            'frequency': config.get('frequency', 'daily'),
            'keywords': config.get('keywords', []),
            'notify_changes': True
        }
        
        # Store monitoring config
        await self.memory.update_preference(f"monitor_{config.get('url')}", monitor_config)
        
        return f"""🔔 **Website Monitor Configured**

🔗 URL: {monitor_config['url']}
📅 Check Frequency: {monitor_config['frequency']}
🔍 Watching for: {', '.join(monitor_config['keywords']) if monitor_config['keywords'] else 'All changes'}

I'll check this site regularly and notify you of any important updates. You can ask me for a status report anytime."""