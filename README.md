# 🎙️ Voice-Style CRM Bot Service

A **real-time voice-based CRM bot** built with Google's Gemini Live API that manages leads, schedules visits, and updates lead status through natural voice commands.

---

## 📋 Problem Statement

Build a minimal voice-style bot service that:
- Accepts text transcripts (simulating speech-to-text output)
- Understands user intent using NLP/LLM techniques
- Extracts entities from natural language
- Integrates with CRM APIs to manage leads
- Returns structured JSON responses

---

## 🎯 Features

### Three Main Intents Supported:

1. **LEAD_CREATE** - Create new leads with name, phone, city, and optional source
2. **VISIT_SCHEDULE** - Schedule visits for existing leads
3. **LEAD_UPDATE** - Update lead status (NEW|IN_PROGRESS|FOLLOW_UP|WON|LOST)

### Technical Capabilities:

- ✅ **Real-time voice interaction** using Gemini Live API
- ✅ **Function calling** for CRM operations
- ✅ **Natural language entity extraction**
- ✅ **Audio streaming** (16kHz input, 24kHz output)
- ✅ **CSV logging** for all CRM operations
- ✅ **Terminal output** with formatted displays
- ✅ **Error handling** with validation
- ✅ **Retry logic** for CRM API calls

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Voice Input                        │
│                  (Real-time Microphone)                     │
└─────────────────┬───────────────────────────────────────────┘
                  │ 16kHz PCM Audio
                  ▼
┌─────────────────────────────────────────────────────────────┐
│            Gemini Live API (Native Audio)                   │
│          gemini-live-2.5-flash-preview                      │
│  • Intent Classification                                    │
│  • Entity Extraction                                        │
│  • Function Calling                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │ Function Calls
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              CRM Function Dispatcher                        │
│   createLead | scheduleVisit | updateLeadStatus            │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP POST
                  ▼
┌─────────────────────────────────────────────────────────────┐
│               Mock CRM Server (FastAPI)                     │
│                http://localhost:8001                        │
│  • In-memory storage                                        │
│  • CSV persistence                                          │
│  • Terminal logging                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │ JSON Response
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Audio Response (24kHz)                    │
│                  Spoken back to user                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Capserve/
├── live_voice_bot.py         # Main voice bot with Gemini Live API
├── mock_crm.py                # FastAPI CRM server with CSV logging
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── tests/                     # Unit tests
│   ├── test_lead_create.py    # Tests for lead creation
│   ├── test_visit_schedule.py # Tests for visit scheduling
│   └── test_lead_update.py    # Tests for lead status updates
│
└── CSV Files (auto-generated):
    ├── crm_leads.csv          # All created leads
    ├── crm_visits.csv         # All scheduled visits
    └── crm_updates.csv        # All status updates
```

---

## 📋 Prerequisites

- **python 3.11+** ([Download Python](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** (optional, for cloning)
- **Gemini API Key** (free - see setup below)
- **Microphone** (for voice input)
- **Speakers/Headphones** (for audio output)

---

## 🚀 Complete Setup Guide (Step-by-Step)

### Step 1: Get Your Gemini API Key (Free)

1. **Visit Google AI Studio:**
   - Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   - Sign in with your Google account

2. **Create API Key:**
   - Click **"Create API Key"** button
   - Select **"Create API key in new project"** (recommended)
   - Copy the generated API key (starts with `AIza...`)
   - ⚠️ **Important:** Keep this key secure and never commit it to Git!

3. **Verify API Key (Optional):**
   ```bash
   # Test your API key with a simple curl command
   curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"
   ```
   If you see a JSON response with model names, your key is valid! ✅

---

### Step 2: Clone/Download the Project

**Option A: Using Git (Recommended)**
```bash
git clone <repository-url>
cd Capserve
```

**Option B: Download ZIP**
- Download the project ZIP file
- Extract to a folder (e.g., `Capserve`)
- Open terminal/command prompt in that folder

---

### Step 3: Set Up Python Environment (Recommended)

**Create a virtual environment:**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.115.0 uvicorn-0.30.6 google-genai-1.0.0 ...
```

**If you encounter errors:**
- Windows: Use `py -m pip install -r requirements.txt`
- macOS/Linux: Use `pip3 install -r requirements.txt`
- If PyAudio fails, see [PyAudio Installation Guide](#pyaudio-installation)

---

### Step 5: Configure Environment Variables

1. **Copy the example file:**
   ```bash
   # On Windows
   copy .env.example .env

   # On macOS/Linux
   cp .env.example .env
   ```

2. **Edit the `.env` file:**
   ```bash
   # Open in your favorite text editor
   # Windows: notepad .env
   # macOS: open -e .env
   # Linux: nano .env
   ```

3. **Add your Gemini API Key:**
   ```env
   # .env file
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX  # Replace with your actual key
   CRM_BASE_URL=http://localhost:8001
   ```

4. **Save and close** the file

---

### Step 6: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Check if dependencies are installed
python -c "import fastapi, google.genai; print('✅ Dependencies OK')"
```

---

### Step 7: Start the Application

**You need TWO terminal windows/tabs:**

#### **Terminal 1: Start Mock CRM Server**

```bash
# Make sure you're in the Capserve directory
cd Capserve

# Activate virtual environment (if using)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start CRM server
python mock_crm.py
```

**✅ Expected Output:**
```
============================================================
  🚀 MOCK CRM SERVER STARTING
============================================================
  Server URL   : http://localhost:8001
  Leads CSV    : crm_leads.csv
  Visits CSV   : crm_visits.csv
  Updates CSV  : crm_updates.csv
============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Keep this terminal running!** ⚠️

---

#### **Terminal 2: Start Voice Bot**

Open a **new terminal window/tab** in the same directory:

```bash
# Navigate to project directory
cd Capserve

# Activate virtual environment (if using)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start voice bot
python live_voice_bot.py
```

**✅ Expected Output:**
```
============================================================
  Gemini Live API - CRM Voice Bot (Audio Only)
============================================================

CRM Functions Available:
  1. createLead(name, phone, city, source)
     - Create a new lead in the CRM system

  2. scheduleVisit(lead_id, visit_time, notes)
     - Schedule a visit for an existing lead

  3. updateLeadStatus(lead_id, status, notes)
     - Update lead status (NEW|IN_PROGRESS|FOLLOW_UP|WON|LOST)

------------------------------------------------------------
Example Voice Commands:
------------------------------------------------------------
  • 'Add a new lead: Rohan Sharma from Gurgaon,
     phone 9876543210, source Instagram'

  • 'Schedule a visit for lead [UUID]
     at 2025-10-05T15:00:00+05:30'

  • 'Update lead [UUID] to in progress'
------------------------------------------------------------

CRM Server: http://localhost:8001
⚠️  Make sure the mock CRM server is running on port 8001!

Type 'q' to quit

============================================================

message >
```

---

### Step 8: Start Using the Voice Bot! 🎤

**You can interact in two ways:**

#### **Method 1: Voice Input (Recommended)**
- Just speak into your microphone
- The bot will listen, understand, and respond with audio
- Example: Say **"Add a new lead: Rohan Sharma from Gurgaon, phone 9876543210, source Instagram"**

#### **Method 2: Text Input (For Testing)**
- Type at the `message >` prompt
- Press Enter to send
- Example: Type `Add a new lead: Rohan Sharma from Gurgaon, phone 9876543210, source Instagram`

---

### Step 9: Monitor CRM Operations

**In Terminal 1 (CRM Server)**, you'll see real-time logs:

```
============================================================
📝 NEW LEAD CREATED
============================================================
Lead ID    : a1b2c3d4-e5f6-7890-abcd-ef1234567890
Name       : Rohan Sharma
Phone      : 9876543210
City       : Gurgaon
Source     : Instagram
Status     : NEW
Created At : 2025-10-04T14:30:00.123456
============================================================
```

**Check the generated CSV files:**
```bash
# View leads
cat crm_leads.csv        # macOS/Linux
type crm_leads.csv       # Windows
```

---

### Step 10: Stop the Application

**To stop:**
1. In **Terminal 2** (Voice Bot): Type `q` and press Enter
2. In **Terminal 1** (CRM Server): Press `Ctrl+C`

**To restart:**
- Just repeat Step 7 (both terminals)

---

## 🎯 Quick Start (TL;DR - For Experienced Users)

```bash
# 1. Get Gemini API Key from https://aistudio.google.com/apikey

# 2. Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# 3. Run (2 terminals)
# Terminal 1:
python mock_crm.py

# Terminal 2:
python live_voice_bot.py

# 4. Speak or type commands!
```

---

## 📝 PyAudio Installation

If `pip install -r requirements.txt` fails on PyAudio, follow these OS-specific instructions:

### Windows

```bash
# Download pre-built wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

# Example for python 3.11 64-bit:
pip install PyAudio-0.2.14-cp310-cp310-win_amd64.whl

# Or use pipwin:
pip install pipwin
pipwin install pyaudio
```

### macOS

```bash
# Install portaudio first
brew install portaudio

# Then install PyAudio
pip install pyaudio
```

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt-get install portaudio19-dev python3-pyaudio

# Then install PyAudio
pip install pyaudio
```


---

## 🎤 Usage Examples

### Example 1: Create Lead

**Voice Command:**
> "Add a new lead: Rohan Sharma from Gurgaon, phone 9876543210, source Instagram"

**CRM Server Output:**
```
============================================================
📝 NEW LEAD CREATED
============================================================
Lead ID    : a1b2c3d4-e5f6-7890-abcd-ef1234567890
Name       : Rohan Sharma
Phone      : 9876543210
City       : Gurgaon
Source     : Instagram
Status     : NEW
Created At : 2025-10-04T14:30:00.123456
============================================================
```

**CSV Entry (crm_leads.csv):**
```csv
lead_id,name,phone,city,source,status,created_at
a1b2c3d4-e5f6-7890-abcd-ef1234567890,Rohan Sharma,9876543210,Gurgaon,Instagram,NEW,2025-10-04T14:30:00.123456
```

---

### Example 2: Schedule Visit

**Voice Command:**
> "Schedule a visit for lead a1b2c3d4-e5f6-7890-abcd-ef1234567890 at 2025-10-05T15:00:00+05:30"

**CRM Server Output:**
```
============================================================
📅 VISIT SCHEDULED
============================================================
Visit ID   : v1v2v3v4-v5v6-v7v8-v9v0-v12345678901
Lead ID    : a1b2c3d4-e5f6-7890-abcd-ef1234567890
Lead Name  : Rohan Sharma
Visit Time : 2025-10-05 15:00:00+05:30
Notes      : N/A
Status     : SCHEDULED
Created At : 2025-10-04T14:35:00.123456
============================================================
```

---

### Example 3: Update Lead Status

**Voice Command:**
> "Update lead a1b2c3d4 to WON with notes: booked unit A2"

**CRM Server Output:**
```
============================================================
🔄 LEAD STATUS UPDATED
============================================================
Lead ID      : a1b2c3d4-e5f6-7890-abcd-ef1234567890
Lead Name    : Rohan Sharma
Old Status   : NEW
New Status   : WON
Notes        : booked unit A2
Updated At   : 2025-10-04T14:40:00.123456
============================================================
```

---

## 🔧 CRM API Specification

### Base URL
```
http://localhost:8001
```

### Endpoints

#### 1. Create Lead
```http
POST /crm/leads
Content-Type: application/json

{
  "name": "Rohan Sharma",
  "phone": "9876543210",
  "city": "Gurgaon",
  "source": "Instagram"
}

Response:
{
  "lead_id": "uuid",
  "status": "NEW"
}
```

#### 2. Schedule Visit
```http
POST /crm/visits
Content-Type: application/json

{
  "lead_id": "uuid",
  "visit_time": "2025-10-05T15:00:00+05:30",
  "notes": "Follow up call"
}

Response:
{
  "visit_id": "uuid",
  "status": "SCHEDULED"
}
```

#### 3. Update Lead Status
```http
POST /crm/leads/{lead_id}/status
Content-Type: application/json

{
  "status": "WON",
  "notes": "booked unit A2"
}

Response:
{
  "lead_id": "uuid",
  "status": "WON"
}
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_lead_create.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Manual Testing with curl

```bash
# Test Create Lead
curl -X POST http://localhost:8001/crm/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "phone": "9999999999",
    "city": "Mumbai",
    "source": "Website"
  }'

# Test Schedule Visit (use lead_id from above)
curl -X POST http://localhost:8001/crm/visits \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "YOUR_LEAD_ID_HERE",
    "visit_time": "2025-10-06T10:00:00+05:30",
    "notes": "Test visit"
  }'

# Test Update Status
curl -X POST http://localhost:8001/crm/leads/YOUR_LEAD_ID_HERE/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "IN_PROGRESS",
    "notes": "Follow up scheduled"
  }'

# View all leads
curl http://localhost:8001/crm/leads

# View all visits
curl http://localhost:8001/crm/visits
```

---

## 🎨 System Prompt Design

The bot uses a carefully crafted system instruction that:

- ✅ **Identifies as a professional CRM assistant**
- ✅ **Reads phone numbers DIGIT BY DIGIT** (not as currency/years)
- ✅ **Handles natural language date/time** → converts to ISO 8601
- ✅ **Extracts entities** accurately from voice input
- ✅ **Confirms important details** before executing
- ✅ **Provides lead IDs** after creation for future reference
- ✅ **Validates phone numbers** (10 digits for Indian format)

**Key Feature:** Phone numbers are spoken as **"nine eight seven six five four three two one zero"** instead of currency format.

---

## 📊 CSV Data Storage

All CRM operations are logged to CSV files:

### crm_leads.csv
```csv
lead_id,name,phone,city,source,status,created_at
a1b2c3d4...,Rohan Sharma,9876543210,Gurgaon,Instagram,NEW,2025-10-04T14:30:00
```

### crm_visits.csv
```csv
visit_id,lead_id,visit_time,notes,status,created_at
v1v2v3v4...,a1b2c3d4...,2025-10-05 15:00:00+05:30,Follow up,SCHEDULED,2025-10-04T14:35:00
```

### crm_updates.csv
```csv
lead_id,old_status,new_status,notes,updated_at
a1b2c3d4...,NEW,WON,booked unit A2,2025-10-04T14:40:00
```

---

## ⚠️ Error Handling

The system handles three types of errors:

### 1. VALIDATION_ERROR
Missing or invalid required entities

```json
{
  "intent": "LEAD_CREATE",
  "error": {
    "type": "VALIDATION_ERROR",
    "details": "Missing required field: phone number"
  }
}
```

### 2. CRM_ERROR
CRM API failures (non-2xx responses)

```json
{
  "intent": "VISIT_SCHEDULE",
  "error": {
    "type": "CRM_ERROR",
    "details": "Lead not found"
  }
}
```

### 3. PARSING_ERROR
Unable to parse intent/entities

```json
{
  "intent": "UNKNOWN",
  "error": {
    "type": "PARSING_ERROR",
    "details": "Could not extract required entities"
  }
}
```

---

## 🐛 Troubleshooting

### 1. "API key not found"
```bash
# Set in .env file
GEMINI_API_KEY=your_actual_key

# Or export directly
export GEMINI_API_KEY=your_actual_key  # Linux/Mac
set GEMINI_API_KEY=your_actual_key     # Windows
```

### 2. "Connection refused to CRM"
- Ensure `mock_crm.py` is running on port 8001
- Check if port 8001 is already in use
- Verify firewall settings

### 3. "Microphone not detected"
```bash
# Check audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(p.get_device_info_by_index(i)) for i in range(p.get_device_count())]"
```

### 4. "Phone numbers spoken incorrectly"
- This is fixed in the system prompt
- Bot now reads digits individually
- If issue persists, check Gemini API version

---

## 📚 Technical Details

### Audio Formats

**Input Audio:**
- Format: 16-bit PCM, mono
- Sample rate: 16kHz
- MIME type: `audio/pcm;rate=16000`

**Output Audio:**
- Sample rate: 24kHz
- Format: WAV (16-bit PCM, mono)

### Model Configuration

```python
MODEL = "models/gemini-live-2.5-flash-preview"

CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Zephyr"
            )
        )
    ),
    system_instruction=SYSTEM_INSTRUCTION,
    tools=tools,
)
```

### Retry Logic

CRM API calls include:
- **Timeout:** 5 seconds
- **Error handling** for connection failures
- **Graceful fallback** with error messages

---

## 📦 Dependencies

```
fastapi==0.115.0          # CRM server framework
uvicorn==0.30.6           # ASGI server
pydantic==2.9.0           # Data validation
google-genai>=1.0.0       # Gemini Live API client
pyaudio>=0.2.14           # Audio I/O
requests>=2.31.0          # HTTP client
python-dotenv>=1.0.0      # Environment management
pytest>=8.0.0             # Testing framework
pytest-asyncio>=0.23.0    # Async test support
```

---

## 🎯 Design Decisions

### Why Gemini Live API?
- **Native audio processing** (no separate STT/TTS needed)
- **Function calling** built-in for tool use
- **Low latency** real-time streaming
- **Natural conversation** flow

### Why Mock CRM?
- **Quick testing** without external dependencies
- **CSV persistence** for debugging
- **Terminal output** for visibility
- **Easy to extend** for production use

### Why Audio-Only Mode?
- **Simplicity** - focus on voice interaction
- **Better UX** - natural conversation
- **Alignment** with problem statement (voice-style bot)

---

## 🚧 Future Enhancements

- [ ] Add confidence scores for intent classification
- [ ] Implement conversation context management
- [ ] Add support for multiple languages
- [ ] Build REST API wrapper for Flutter integration
- [ ] Add authentication and authorization
- [ ] Implement database persistence (PostgreSQL)
- [ ] Add analytics dashboard
- [ ] Support multiple concurrent sessions
- [ ] Add voice activity detection (VAD) tuning
- [ ] Implement webhook notifications

---

## 📚 References

- [Gemini Live API Documentation](https://ai.google.dev/gemini-api/docs/live)
- [Function Calling Guide](https://ai.google.dev/gemini-api/docs/function-calling)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google AI Studio](https://aistudio.google.com/)

---

## 📄 License

This is an assignment project. See `problem-statement.txt` for original requirements.

---

## ✨ Author Notes

**What I would improve with more time:**

1. **Better Entity Extraction:**
   - Add regex patterns for Indian phone numbers
   - Implement city name validation against known list
   - Add name capitalization and formatting

2. **Enhanced Error Handling:**
   - Add retry logic with exponential backoff
   - Implement circuit breaker for CRM calls
   - Better user-facing error messages

3. **Testing:**
   - Add integration tests for end-to-end flows
   - Mock Gemini API responses for unit tests
   - Add load testing for concurrent requests

4. **Production Readiness:**
   - Add logging with structured logs (JSON)
   - Implement rate limiting
   - Add health check endpoints
   - Database migration system

5. **UX Improvements:**
   - Add confirmation prompts before destructive actions
   - Support for ambiguous date parsing ("next Tuesday")
   - Multi-turn conversations for gathering information
   - Support for editing/canceling recent actions

---

**Built with ❤️ using:**
- Google Gemini Live API (`gemini-live-2.5-flash-preview`)
- FastAPI (Mock CRM server)
- python 3.11+
- PyAudio (Real-time audio streaming)

---

**⭐ Setup Time: < 10 minutes**
