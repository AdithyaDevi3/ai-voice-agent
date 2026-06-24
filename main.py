import asyncio
import base64
import json
import os
import websockets

from dotenv import load_dotenv

load_dotenv()

def sts_connect():
    # Get the Deepgram API key from environment variables
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        raise ValueError("Deepgram API key not found in environment variables.")
    sts_ws = websockets.connect(
        "wss://api.deepgram.com/v1/agent/converse",
        subprotocols=["token", deepgram_api_key]
    )
    return sts_ws

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
    
async def handle_barge_in(decoded, twilio_ws, streamsid):
    if decoded['type'] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))

async def handle_text_message(decoded, twilio_ws, sts_ws, streamsid):
    await handle_barge_in(decoded, twilio_ws, streamsid)

async def sts_sender(sts_ws, audio_queue):
    while True:
        audio_chunk = await audio_queue.get()
        if audio_chunk is None:
            break
        await sts_ws.send(audio_chunk)

async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    print("Starting STS receiver...")
    streamsid = await streamsid_queue.get()
    async for message in sts_ws:
        if type(message) is str:
            print(message)
            decoded = json.loads(message)
            await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            continue
        raw_mulaw = message
        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")}
        }
        await twilio_ws.send(json.dumps(media_message))
        
async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")
    
    async for message in twilio_ws:
        try:
            data = json.loads(message)
            event = data["event"]
            if event == "start":
                print("Twilio connection started.")
                start = data["start"]
                streamsid = data["streamsid"]
                streamsid_queue.put_nowait(streamsid)
            elif event == "connected":
                continue
            elif event == "media":
                media = data["media"]
                payload = media["payload"]
                chunk = base64.b64decode(payload)
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif event == "stop":
                break
            while len(inbuffer) >= BUFFER_SIZE:
                    audio_chunk = inbuffer[:BUFFER_SIZE]
                    audio_queue.put_nowait(audio_chunk)
                    inbuffer = inbuffer[BUFFER_SIZE:]
        except:
            break

async def twilio_handler(twilio_ws):
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue() 
    
    async with sts_connect() as sts_ws:
        config_messge = load_config()
        await sts_ws.send(json.dumps(config_messge))
        
        await asyncio.wait(
            [
            asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
            asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
            asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue)),
            ]
        )
        
        await twilio_ws.close()

async def main():
    await websockets.serve(twilio_handler, "localhost", 5000)
    print("Started server.")
    await asyncio.Future()  # Run forever
    
    
if __name__ == "__main__":
    asyncio.run(main())