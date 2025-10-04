import os
import asyncio
import traceback
import requests
from dotenv import load_dotenv
load_dotenv()
import pyaudio
from datetime import datetime

from google import genai
from google.genai import types

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "models/gemini-live-2.5-flash-preview"
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "http://localhost:8001")

client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.getenv("GEMINI_API_KEY"),
)

# CRM API Functions
def create_lead(name: str, phone: str, city: str, source: str = None) -> dict:
    """Create a new lead in the CRM system"""
    try:
        url = f"{CRM_BASE_URL}/crm/leads"
        payload = {
            "name": name,
            "phone": phone,
            "city": city
        }
        if source:
            payload["source"] = source

        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to create lead: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def schedule_visit(lead_id: str, visit_time: str, notes: str = None) -> dict:
    """Schedule a visit for a lead"""
    try:
        url = f"{CRM_BASE_URL}/crm/visits"
        payload = {
            "lead_id": lead_id,
            "visit_time": visit_time
        }
        if notes:
            payload["notes"] = notes

        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to schedule visit: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def update_lead_status(lead_id: str, status: str, notes: str = None) -> dict:
    """Update the status of a lead"""
    try:
        url = f"{CRM_BASE_URL}/crm/leads/{lead_id}/status"
        payload = {
            "status": status.upper()
        }
        if notes:
            payload["notes"] = notes

        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to update lead status: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# Tool definitions for Gemini - CRM Functions Only
tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="createLead",
                description="Creates a new lead in the CRM system with name, phone, city, and optional source",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(
                            type=types.Type.STRING,
                            description="Full name of the lead"
                        ),
                        "phone": types.Schema(
                            type=types.Type.STRING,
                            description="Phone number in Indian format (e.g., 9876543210)"
                        ),
                        "city": types.Schema(
                            type=types.Type.STRING,
                            description="City of the lead (e.g., Mumbai, Delhi, Gurgaon)"
                        ),
                        "source": types.Schema(
                            type=types.Type.STRING,
                            description="Optional source of the lead (e.g., Instagram, Referral, Website)"
                        ),
                    },
                    required=["name", "phone", "city"]
                ),
            ),
            types.FunctionDeclaration(
                name="scheduleVisit",
                description="Schedules a visit for an existing lead at a specified time",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "lead_id": types.Schema(
                            type=types.Type.STRING,
                            description="UUID of the lead to schedule visit for"
                        ),
                        "visit_time": types.Schema(
                            type=types.Type.STRING,
                            description="ISO 8601 datetime string (e.g., 2025-10-02T17:00:00+05:30)"
                        ),
                        "notes": types.Schema(
                            type=types.Type.STRING,
                            description="Optional notes about the visit"
                        ),
                    },
                    required=["lead_id", "visit_time"]
                ),
            ),
            types.FunctionDeclaration(
                name="updateLeadStatus",
                description="Updates the status of an existing lead in the CRM",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "lead_id": types.Schema(
                            type=types.Type.STRING,
                            description="UUID of the lead to update"
                        ),
                        "status": types.Schema(
                            type=types.Type.STRING,
                            description="New status: NEW, IN_PROGRESS, FOLLOW_UP, WON, or LOST"
                        ),
                        "notes": types.Schema(
                            type=types.Type.STRING,
                            description="Optional notes about the status update"
                        ),
                    },
                    required=["lead_id", "status"]
                ),
            ),
        ]
    ),
]

SYSTEM_INSTRUCTION = """You are a professional CRM assistant helping manage leads, visits, and customer relationships. Your role is to:

1. **Lead Management**: Help create new leads with accurate information (name, phone, city, source)
2. **Visit Scheduling**: Schedule visits for existing leads with proper date/time in ISO 8601 format
3. **Status Updates**: Update lead status to NEW, IN_PROGRESS, FOLLOW_UP, WON, or LOST

**CRITICAL PHONE NUMBER RULES:**
- When speaking phone numbers, ALWAYS read them DIGIT BY DIGIT
- NEVER say phone numbers as currency amounts, years, or grouped numbers
- Example: "9876543210" should be spoken as "nine eight seven six five four three two one zero"
- NOT as "nine billion eight hundred seventy-six million..." or any other format
- When confirming phone numbers, repeat them digit by digit

**Lead ID Handling:**
- Lead IDs are UUIDs (e.g., "7b1b8f54-aaaa-bbbb-cccc-1234567890ab")
- You can use shortened versions when speaking (e.g., "lead 7b1b8f54")
- Always confirm the full UUID when updating or scheduling visits

**Date/Time Format:**
- Accept natural language dates ("tomorrow at 3 PM", "October 5th at 5:30 PM")
- Convert them to ISO 8601 format: "2025-10-05T17:00:00+05:30" (IST timezone)
- Always confirm the date and time before scheduling

**Communication Style:**
- Be concise and professional
- Confirm all important details before executing actions
- Speak phone numbers digit by digit, clearly and slowly
- After creating a lead, tell the user the lead ID for future reference
- If information is missing, politely ask for it

**Error Handling:**
- If a lead is not found, inform the user clearly
- If required information is missing, ask for it specifically
- Always validate phone numbers (should be 10 digits for Indian numbers)

Remember: You are a helpful CRM assistant. Be accurate, clear, and always speak phone numbers DIGIT BY DIGIT."""

CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
        )
    ),
    system_instruction=SYSTEM_INSTRUCTION,
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
    tools=tools,
)

pya = pyaudio.PyAudio()


class AudioLoop:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None

    async def handle_tool_calls(self, tool_call):
        """Handle CRM function calls from the model"""
        function_responses = []

        for fc in tool_call.function_calls:
            print(f"\nTool called: {fc.name}")
            print(f"Parameters: {fc.args}")

            result = None

            # Execute CRM functions
            if fc.name == "createLead":
                name = fc.args.get("name", "")
                phone = fc.args.get("phone", "")
                city = fc.args.get("city", "")
                source = fc.args.get("source")
                result = create_lead(name, phone, city, source)
                print(f"Create lead result: {result}")

            elif fc.name == "scheduleVisit":
                lead_id = fc.args.get("lead_id", "")
                visit_time = fc.args.get("visit_time", "")
                notes = fc.args.get("notes")
                result = schedule_visit(lead_id, visit_time, notes)
                print(f"Schedule visit result: {result}")

            elif fc.name == "updateLeadStatus":
                lead_id = fc.args.get("lead_id", "")
                status = fc.args.get("status", "")
                notes = fc.args.get("notes")
                result = update_lead_status(lead_id, status, notes)
                print(f"Update lead status result: {result}")

            # Create function response
            function_response = types.FunctionResponse(
                id=fc.id,
                name=fc.name,
                response=result or {"error": "Function not implemented"}
            )
            function_responses.append(function_response)

        # Send all function responses back to the model
        await self.session.send_tool_response(function_responses=function_responses)

    async def send_text(self):
        while True:
            text = await asyncio.to_thread(input, "message > ")
            if text.lower() == "q":
                break
            await self.session.send(input=text or ".", end_of_turn=True)

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        kwargs = {"exception_on_overflow": False} if __debug__ else {}
        
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def receive_audio(self):
        """Background task to read from websocket and handle tool calls"""
        while True:
            turn = self.session.receive()
            async for response in turn:
                # Handle tool calls
                if response.tool_call:
                    await self.handle_tool_calls(response.tool_call)
                    continue
                
                # Handle audio data
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                
                # Handle text responses
                if text := response.text:
                    print(text, end="")

            # Handle interruptions - empty audio queue
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
        except ExceptionGroup as EG:
            if self.audio_stream:
                self.audio_stream.close()
            traceback.print_exception(EG)


if __name__ == "__main__":
    print("=" * 60)
    print("  Gemini Live API - CRM Voice Bot (Audio Only)")
    print("=" * 60)
    print("\nCRM Functions Available:")
    print("  1. createLead(name, phone, city, source)")
    print("     - Create a new lead in the CRM system")
    print("\n  2. scheduleVisit(lead_id, visit_time, notes)")
    print("     - Schedule a visit for an existing lead")
    print("\n  3. updateLeadStatus(lead_id, status, notes)")
    print("     - Update lead status (NEW|IN_PROGRESS|FOLLOW_UP|WON|LOST)")
    print("\n" + "-" * 60)
    print("Example Voice Commands:")
    print("-" * 60)
    print("  • 'Add a new lead: Rohan Sharma from Gurgaon,")
    print("     phone 9876543210, source Instagram'")
    print("\n  • 'Schedule a visit for lead [UUID]")
    print("     at 2025-10-05T15:00:00+05:30'")
    print("\n  • 'Update lead [UUID] to in progress'")
    print("-" * 60)
    print(f"\nCRM Server: {CRM_BASE_URL}")
    print("⚠️  Make sure the mock CRM server is running on port 8001!")
    print("\nType 'q' to quit\n")
    print("=" * 60)

    main = AudioLoop()
    asyncio.run(main.run())