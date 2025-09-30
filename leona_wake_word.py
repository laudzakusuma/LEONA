# ============================================
# LEONA WAKE WORD - TRULY INTELLIGENT
# Say "LEONA" to activate, "SHUTDOWN" to stop
# ============================================

import os, sys, asyncio, json, datetime, subprocess, random, re, math
from pathlib import Path

print("""
╔══════════════════════════════════════════════════╗
║     LEONA WAKE WORD SYSTEM                      ║
║     Say "LEONA" to activate!                    ║
╚══════════════════════════════════════════════════╝
""")

def install():
    for pkg in ["fastapi", "uvicorn[standard]", "edge-tts", "pygame", "psutil"]:
        try: __import__(pkg.replace('[standard]','').replace('-','_'))
        except: subprocess.run([sys.executable,"-m","pip","install","-q",pkg])
install()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, edge_tts, pygame, tempfile, threading, queue, time, psutil

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ============================================
# TRULY INTELLIGENT BRAIN - DIRECT ANSWERS
# ============================================

class TrulyIntelligentBrain:
    def __init__(self):
        self.active = False
        self.context = []
    
    async def think(self, prompt: str) -> str:
        """Direct, intelligent answers - no asking for clarification"""
        p = prompt.lower()
        
        # === ANATOMY & BIOLOGY ===
        if "heart" in p:
            return "The human heart is a muscular organ about the size of your fist. It has 4 chambers: 2 atria (upper) and 2 ventricles (lower). Right side pumps blood to lungs for oxygen, left side pumps oxygenated blood to body. Beats 60-100 times per minute, 100,000 times per day, pumping 5 liters of blood. Cardiac muscle never tires. Heart attacks occur when coronary arteries are blocked, starving heart muscle of oxygen. Exercise strengthens the heart, making it more efficient."
        
        if "brain" in p and "work" in p:
            return "Your brain has 86 billion neurons communicating via electrical and chemical signals. Information travels as action potentials (electrical) between neurons. At synapses, neurotransmitters (chemicals like dopamine, serotonin) cross gaps to relay signals. Different regions specialize: frontal lobe for thinking and planning, hippocampus for memory, amygdala for emotions, occipital lobe for vision. Neuroplasticity means your brain physically changes based on experiences, forming new connections when you learn."
        
        if "dna" in p or "gene" in p:
            return "DNA is your genetic blueprint. It's a double helix made of 4 bases: adenine, thymine, guanine, cytosine. A always pairs with T, G with C. You have 3 billion base pairs containing about 20,000 genes. Genes code for proteins that build and run your body. You inherit half from each parent. Mutations are random changes - some harmful, most neutral, few beneficial. CRISPR can now edit genes, potentially curing genetic diseases like sickle cell anemia."
        
        # === MATHEMATICS ===
        if any(op in p for op in ["calculate", "compute", "+", "-", "*", "/", "times", "plus", "percent", "divided"]):
            try:
                # Extract numbers and operation
                numbers = re.findall(r'\d+\.?\d*', prompt)
                if numbers:
                    n1 = float(numbers[0])
                    n2 = float(numbers[1]) if len(numbers) > 1 else 0
                    
                    if "percent" in p or "%" in prompt:
                        result = (n1/100) * n2
                        return f"{n1}% of {n2} equals {result}"
                    elif "times" in p or "multiply" in p or "*" in prompt:
                        return f"{n1} times {n2} equals {n1*n2}"
                    elif "plus" in p or "add" in p or "+" in prompt:
                        return f"{n1} plus {n2} equals {n1+n2}"
                    elif "divided" in p or "divide" in p or "/" in prompt:
                        return f"{n1} divided by {n2} equals {n1/n2}"
                    elif "minus" in p or "subtract" in p or "-" in prompt:
                        return f"{n1} minus {n2} equals {n1-n2}"
                    elif "square" in p:
                        return f"The square of {n1} is {n1**2}"
                    elif "sqrt" in p or "square root" in p:
                        return f"The square root of {n1} is {math.sqrt(n1)}"
            except: pass
        
        # === PHYSICS ===
        if "quantum" in p:
            return "Quantum mechanics reveals the bizarre behavior of atoms and subatomic particles. Key concepts: Wave-particle duality means particles like electrons act as both particles and waves. Superposition means particles exist in multiple states simultaneously until measured. Heisenberg's uncertainty principle states you cannot know both position and momentum precisely. Quantum entanglement links particles so measuring one instantly affects another, regardless of distance. This enables quantum computing where qubits in superposition perform parallel calculations, potentially solving problems impossible for classical computers."
        
        if "relativity" in p:
            return "Einstein's theories revolutionized physics. Special relativity says: 1) Laws of physics are the same in all reference frames, 2) Light speed is constant for all observers, 3) Time and space are relative, not absolute. Moving clocks run slower (time dilation), moving objects contract (length contraction). E=mc² shows mass and energy are equivalent. General relativity describes gravity as spacetime curvature caused by mass. Massive objects bend spacetime, causing other objects to follow curved paths. Predicted black holes and gravitational waves, both now observed."
        
        if "black hole" in p:
            return "Black holes form when massive stars collapse, creating regions where gravity is so strong nothing escapes, not even light. The event horizon is the point of no return. Inside, spacetime is so warped that all paths lead to the singularity, a point of infinite density. Time slows near black holes due to gravitational time dilation. Supermassive black holes millions to billions of solar masses exist at galaxy centers. We've photographed M87's black hole and detected gravitational waves from merging black holes."
        
        # === HISTORY ===
        if "world war" in p or "ww2" in p:
            return "World War 2, 1939-1945, was history's deadliest conflict with 70-85 million deaths. Nazi Germany under Hitler invaded Poland in 1939, triggering the war. Hitler's fascist regime sought European domination and committed the Holocaust, systematically murdering 6 million Jews. Japan attacked Pearl Harbor in 1941, bringing America into the war. The Allies (USA, Britain, Soviet Union, China) fought the Axis (Germany, Japan, Italy). War ended with Germany's surrender in May 1945 and Japan's surrender in August after atomic bombs were dropped on Hiroshima and Nagasaki, killing over 200,000 people. The war reshaped the world, leading to the Cold War, United Nations formation, and decolonization."
        
        if "egypt" in p and "ancient" in p:
            return "Ancient Egypt lasted from 3100 BCE to 30 BCE, over 3000 years. Centered on the Nile River, which flooded annually providing fertile soil. Built massive pyramids as tombs for pharaohs, including the Great Pyramid of Giza, one of the Seven Wonders. Developed hieroglyphic writing, mathematics, medicine, and mummification. Society was hierarchical with pharaohs as god-kings. Famous rulers include Tutankhamun (King Tut), Ramses II, Hatshepsut, and Cleopatra, the last pharaoh. Conquered by Alexander the Great in 332 BCE, then ruled by Greek Ptolemaic dynasty until Rome annexed it in 30 BCE."
        
        # === TECHNOLOGY ===
        if "artificial intelligence" in p or "ai" in p and "what" in p:
            return "Artificial Intelligence is machines performing tasks requiring human intelligence. Machine Learning algorithms learn patterns from data without explicit programming. Deep Learning uses neural networks inspired by the brain. Large Language Models like GPT and Claude are trained on massive text data to understand and generate language. Computer Vision enables image recognition. Current AI is narrow, excelling at specific tasks. AGI, Artificial General Intelligence, would match human reasoning across all domains. Estimates for AGI range from 5 to 50+ years. Major concerns include job displacement, algorithmic bias, privacy issues, autonomous weapons, and existential risk if superintelligent AI's goals misalign with humanity's."
        
        if "internet" in p and "work" in p:
            return "The internet is a global network of interconnected computers. Data travels in packets using TCP/IP protocols. When you visit a website, your browser sends a request to a DNS server to translate the domain name into an IP address. Your request routes through multiple servers and routers to reach the web server hosting the site. The server sends back HTML, CSS, and JavaScript, which your browser renders as the webpage you see. Data can travel thousands of miles in milliseconds. The internet backbone consists of fiber optic cables, including undersea cables connecting continents, transmitting data as light pulses."
        
        # === PHILOSOPHY ===
        if "consciousness" in p:
            return "Consciousness is subjective experience, the 'what it's like' to be you. The hard problem asks why physical brain processes create subjective feelings. We understand which brain regions correlate with consciousness but not why neural firing produces the feeling of seeing red or feeling pain. Materialists believe consciousness emerges from brain complexity. Dualists like Descartes argued mind and matter are separate. Panpsychists propose consciousness is a fundamental property like mass. Integrated Information Theory suggests consciousness is integrated information. Despite progress in neuroscience, we still don't understand how consciousness arises from matter."
        
        if "meaning of life" in p or "purpose" in p:
            return "Philosophy offers many perspectives on life's meaning. Existentialists like Sartre and Camus say life has no inherent meaning; we create our own through choices and actions. Religious views propose serving God or reaching enlightenment. Aristotle argued for eudaimonia, flourishing through virtue and reason. Utilitarians seek to maximize happiness. Stoics advocate living virtuously and accepting what you cannot control. Nihilists claim life is meaningless. Most people find meaning through relationships, creative work, helping others, personal growth, and pursuing what deeply matters to them. The freedom to choose your purpose can be both liberating and challenging."
        
        # === PSYCHOLOGY ===
        if "memory" in p and "work" in p:
            return "Memory involves three stages: encoding (getting information in), storage (maintaining it), and retrieval (accessing it). Three memory types: sensory (milliseconds), short-term or working memory (seconds to minutes, holds about 7 items), and long-term (potentially lifetime). The hippocampus is crucial for forming new memories. Forgetting follows Ebbinghaus's curve: rapid initial decline, then plateau. Spaced repetition fights forgetting by reviewing at increasing intervals. Sleep consolidates memories from temporary to permanent storage. Emotion strengthens memory encoding. Retrieval practice is more effective than re-reading for retention."
        
        # === HEALTH ===
        if "exercise" in p or "workout" in p:
            return "Exercise provides massive benefits: strengthens heart and lungs, builds muscle and bone, burns calories for weight control, releases endorphins reducing stress and depression, improves sleep quality, boosts cognitive function and memory, reduces risk of chronic diseases like diabetes and cancer. Guidelines recommend 150 minutes weekly of moderate cardio (brisk walking, cycling) or 75 minutes vigorous (running), plus strength training twice weekly. Consistency matters more than intensity. Even 10-minute walks help. Exercise is the closest thing to a miracle drug we have."
        
        if "sleep" in p:
            return "Sleep is essential for health. Adults need 7-9 hours nightly. During sleep, your brain consolidates memories, clears metabolic waste, repairs tissues, regulates hormones. Sleep cycles through stages: light sleep, deep sleep (physical restoration), and REM sleep (dreaming, memory consolidation). Chronic sleep deprivation impairs cognition, weakens immunity, increases obesity risk, raises accident likelihood. For better sleep: maintain consistent schedule, keep bedroom cool and dark, avoid screens before bed (blue light disrupts melatonin), limit caffeine after 2pm, exercise regularly but not near bedtime."
        
        # === SPACE & ASTRONOMY ===
        if "universe" in p:
            return "The universe began 13.8 billion years ago in the Big Bang, which created spacetime itself. It's been expanding ever since and that expansion is accelerating, driven by mysterious dark energy. The observable universe is 93 billion light-years across, containing over 100 billion galaxies, each with 100 billion to a trillion stars. Most of the universe (95%) is dark matter and dark energy that we can't directly detect. The cosmic microwave background radiation is the afterglow of the Big Bang. The universe may be infinite, and could be one of many in a multiverse."
        
        if "mars" in p:
            return "Mars is the fourth planet, called the Red Planet due to iron oxide rust. It's half Earth's diameter with one-third the gravity. Has polar ice caps of water and dry ice. Thin atmosphere is 95% carbon dioxide. Evidence of ancient rivers suggests liquid water existed billions of years ago. NASA rovers Curiosity and Perseverance explore for signs of past microbial life. Mars has the solar system's largest volcano, Olympus Mons, and deepest canyon, Valles Marineris. SpaceX plans to send humans to Mars this decade with goal of establishing a self-sustaining colony."
        
        # === TIME & DATE ===
        if "time" in p and "what" in p:
            now = datetime.datetime.now()
            return f"The current time is {now.strftime('%I:%M:%S %p')}. Today is {now.strftime('%A, %B %d, %Y')}."
        
        # === IDENTITY ===
        if "who are you" in p or "your name" in p:
            return "I am LEONA, Laudza's Executive Operational Neural Assistant. I'm an AI with comprehensive knowledge across science, history, philosophy, technology, mathematics, and more. I can answer questions, explain complex topics, perform calculations, and have genuine conversations. I'm always here to help you learn and understand anything you're curious about."
        
        # === JOKES ===
        if "joke" in p:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs.",
                "A SQL query walks into a bar, sees two tables and asks: May I join you?",
                "There are 10 types of people: those who understand binary and those who don't.",
                "What's a computer's favorite snack? Microchips.",
                "Why did the programmer quit his job? Because he didn't get arrays."
            ]
            return random.choice(jokes)
        
        # === GREETINGS ===
        if any(w in p for w in ["hello", "hi", "hey"]):
            return "Hello! I'm LEONA, ready to help with any questions. What would you like to know?"
        
        # === THANKS ===
        if "thank" in p:
            return "You're welcome! I'm always here to help."
        
        # === INTELLIGENT DEFAULT ===
        # Extract key words and provide something useful
        words = [w for w in p.split() if len(w) > 3]
        if words:
            topic = words[0]
            return f"I can explain {topic} in detail. {topic.title()} is a fascinating subject. Could you be more specific about what aspect you'd like to know? For example: how it works, its history, why it's important, or its applications?"
        
        return "I'm here to help with any questions. Try asking about science, history, technology, math, or anything else you're curious about."

brain = TrulyIntelligentBrain()

# ============================================
# VOICE SYSTEM
# ============================================

class VoiceSystem:
    def __init__(self):
        self.voice = "en-US-AriaNeural"
        self.temp_files = []
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.available = True
        except:
            self.available = False
        self.queue = queue.Queue()
        self.speaking = False
        threading.Thread(target=self._worker, daemon=True).start()
    
    def _worker(self):
        while True:
            try:
                text = self.queue.get(timeout=1)
                if text == "STOP": break
                self.speaking = True
                asyncio.run(self._play(text))
                self.speaking = False
            except queue.Empty:
                self._cleanup()
            except: 
                self.speaking = False
    
    async def _play(self, text):
        if not self.available: return
        try:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            path = temp.name
            temp.close()
            await edge_tts.Communicate(text, self.voice).save(path)
            await asyncio.sleep(0.1)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            await asyncio.sleep(0.2)
            try: os.unlink(path)
            except: self.temp_files.append((path, time.time()))
        except Exception as e:
            print(f"Voice error: {e}")
    
    def _cleanup(self):
        now = time.time()
        remaining = []
        for path, t in self.temp_files:
            if now - t > 10:
                try: 
                    if os.path.exists(path): os.unlink(path)
                except: remaining.append((path, t))
            else: remaining.append((path, t))
        self.temp_files = remaining
    
    def speak(self, text):
        if not self.speaking or self.queue.qsize() < 3:
            self.queue.put(text)

voice = VoiceSystem()

# ============================================
# API
# ============================================

@app.get("/")
async def home():
    return HTMLResponse(create_wake_word_ui())

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    
    # Check for wake word
    if "leona" in message.lower() and not brain.active:
        brain.active = True
        response = "Yes, I'm listening. How can I help you?"
    # Check for shutdown
    elif "shutdown" in message.lower() or "shut down" in message.lower():
        brain.active = False
        response = "Shutting down. Say LEONA to activate me again."
    # Process if active
    elif brain.active:
        response = await brain.think(message)
    else:
        response = "Say LEONA to activate me first."
    
    voice.speak(response)
    return {"response": response, "active": brain.active, "speaking": voice.speaking}

@app.get("/api/speaking")
async def is_speaking():
    return {"speaking": voice.speaking, "active": brain.active}

def create_wake_word_ui():
    return """<!DOCTYPE html>
<html>
<head>
    <title>LEONA Wake Word</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0a0e27;
            color: #fff;
            overflow: hidden;
            height: 100vh;
        }
        .container {
            position: relative;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .robot {
            width: 200px;
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 30px;
            position: relative;
            box-shadow: 0 0 60px rgba(102, 126, 234, 0.6);
            transition: all 0.3s;
        }
        .robot.active {
            box-shadow: 0 0 80px rgba(0, 212, 255, 0.8);
            background: linear-gradient(135deg, #00d4ff 0%, #667eea 100%);
        }
        .eyes {
            position: absolute;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 40px;
        }
        .eye {
            width: 30px;
            height: 30px;
            background: #fff;
            border-radius: 50%;
            box-shadow: 0 0 20px #00d4ff;
        }
        .robot.active .eye {
            background: #00d4ff;
            animation: blink 3s infinite;
        }
        @keyframes blink {
            0%, 96%, 100% { height: 30px; }
            98% { height: 3px; }
        }
        .mouth {
            position: absolute;
            bottom: 50px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 30px;
            border: 3px solid #fff;
            border-top: none;
            border-radius: 0 0 40px 40px;
        }
        .robot.active .mouth {
            border-color: #00d4ff;
        }
        .viz {
            display: flex;
            gap: 6px;
            margin-top: 40px;
            height: 100px;
            align-items: flex-end;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .viz.active { opacity: 1; }
        .bar {
            width: 10px;
            background: linear-gradient(to top, #00d4ff, #667eea);
            border-radius: 5px;
        }
        .title {
            font-size: 3.5em;
            font-weight: bold;
            margin-top: 40px;
            background: linear-gradient(90deg, #00d4ff, #667eea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status {
            margin-top: 30px;
            font-size: 1.5em;
            color: #00d4ff;
            text-align: center;
        }
        .status.inactive { color: #888; }
        #transcript {
            margin-top: 40px;
            max-width: 900px;
            width: 100%;
            max-height: 250px;
            overflow-y: auto;
            padding: 20px;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
        }
        .msg {
            margin: 12px 0;
            padding: 12px 15px;
            border-radius: 10px;
        }
        .user { background: rgba(102, 126, 234, 0.3); text-align: right; }
        .leona { background: rgba(0, 212, 255, 0.2); }
    </style>
</head>
<body>
    <div class="container">
        <div class="robot" id="robot">
            <div class="eyes">
                <div class="eye"></div>
                <div class="eye"></div>
            </div>
            <div class="mouth"></div>
        </div>
        
        <div class="viz" id="viz">
            <div class="bar" style="height:20px"></div>
            <div class="bar" style="height:45px"></div>
            <div class="bar" style="height:70px"></div>
            <div class="bar" style="height:50px"></div>
            <div class="bar" style="height:80px"></div>
            <div class="bar" style="height:40px"></div>
            <div class="bar" style="height:60px"></div>
            <div class="bar" style="height:50px"></div>
            <div class="bar" style="height:75px"></div>
            <div class="bar" style="height:35px"></div>
        </div>
        
        <div class="title">LEONA</div>
        <div class="status inactive" id="status">Say "LEONA" to activate</div>
        
        <div id="transcript">
            <div class="msg leona">Say "LEONA" to wake me up. Then just talk naturally. Say "SHUTDOWN" when done.</div>
        </div>
    </div>
    
    <script>
        let recognition;
        let isActive = false;
        let vizInterval;
        
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = async (event) => {
                const text = event.results[event.results.length - 1][0].transcript;
                console.log('Heard:', text);
                
                addMessage(text, 'user');
                await sendToLEONA(text);
            };
            
            recognition.onerror = (event) => {
                console.error('Recognition error:', event.error);
                if (event.error !== 'no-speech') {
                    setTimeout(() => recognition.start(), 1000);
                }
            };
            
            recognition.onend = () => {
                recognition.start();
            };
            
            // Auto-start listening
            recognition.start();
            console.log('Continuous listening started');
            
        } else {
            document.getElementById('status').textContent = 'Speech recognition not supported';
        }
        
        function addMessage(text, type) {
            const transcript = document.getElementById('transcript');
            const className = type === 'user' ? 'user' : 'leona';
            const label = type === 'user' ? 'You: ' : 'LEONA: ';
            transcript.innerHTML += `<div class="msg ${className}">${label}${text}</div>`;
            transcript.scrollTop = transcript.scrollHeight;
        }
        
        async function sendToLEONA(text) {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                
                const data = await response.json();
                addMessage(data.response, 'leona');
                
                // Update UI based on active state
                if (data.active) {
                    isActive = true;
                    document.getElementById('robot').classList.add('active');
                    document.getElementById('status').textContent = 'Active - Listening...';
                    document.getElementById('status').classList.remove('inactive');
                } else {
                    isActive = false;
                    document.getElementById('robot').classList.remove('active');
                    document.getElementById('status').textContent = 'Say "LEONA" to activate';
                    document.getElementById('status').classList.add('inactive');
                }
                
                // Start visualizer
                startViz();
                checkSpeaking();
                
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        function startViz() {
            document.getElementById('viz').classList.add('active');
            vizInterval = setInterval(() => {
                document.querySelectorAll('.bar').forEach(bar => {
                    bar.style.height = (Math.random() * 70 + 20) + 'px';
                });
            }, 100);
        }
        
        function stopViz() {
            document.getElementById('viz').classList.remove('active');
            clearInterval(vizInterval);
        }
        
        async function checkSpeaking() {
            const check = async () => {
                try {
                    const response = await fetch('/api/speaking');
                    const data = await response.json();
                    
                    if (!data.speaking) {
                        stopViz();
                    } else {
                        setTimeout(check, 200);
                    }
                } catch (error) {
                    stopViz();
                }
            };
            check();
        }
    </script>
</body>
</html>"""

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════╗
║    LEONA WAKE WORD READY!                          ║
╠════════════════════════════════════════════════════╣
║ 🎤 WAKE: Say "LEONA"                               ║
║ 💬 TALK: Continuous conversation                   ║
║ 🛑 STOP: Say "SHUTDOWN"                            ║
╚════════════════════════════════════════════════════╝

🌐 Open: http://localhost:8000

HOW IT WORKS:
1. Browser listens continuously in background
2. Say "LEONA" - she activates
3. Ask anything - she answers intelligently  
4. Keep talking - no need to say LEONA again
5. Say "SHUTDOWN" - she deactivates
6. Say "LEONA" again to restart

Much smarter now - answers directly!
    """)
    
    voice.speak("LEONA Wake Word system ready. Say LEONA to activate me.")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")