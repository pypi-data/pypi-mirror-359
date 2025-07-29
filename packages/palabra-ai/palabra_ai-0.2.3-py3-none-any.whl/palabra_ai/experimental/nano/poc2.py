# We recommend manage dependencies via https://astral.sh/uv/
# $> uv pip install httpx livekit numpy sounddevice websockets

### Step 1: Create a Session ###
import httpx


async def create_session(client_id: str, client_secret: str) -> dict:
    url = "https://api.palabra.ai/session-storage/session"
    headers = {"ClientId": client_id, "ClientSecret": client_secret}
    payload = {"data": {"subscriber_count": 0, "publisher_can_subscribe": True}}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


### Step 2: Connect to the Translation Room ###
from livekit import rtc


async def connect_translation_room(webrtc_url: str, publisher: str) -> rtc.Room:
    room = rtc.Room()
    await room.connect(webrtc_url, publisher, rtc.RoomOptions(auto_subscribe=True))
    print("💫 Connected to room")
    return room


### Step 3: Publish the Original Audio Stream ###
import asyncio
import queue
import threading

import numpy as np
import sounddevice as sd
from livekit import rtc


async def publish_audio_track(room: rtc.Room) -> rtc.AudioSource:
    # Create audio source
    audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)

    # Create and publish track
    track = rtc.LocalAudioTrack.create_audio_track("microphone", audio_source)
    await room.local_participant.publish_track(
        track, rtc.TrackPublishOptions(dtx=False, red=False)
    )
    print("🗣️ Microphone published")

    # Start capturing in background
    asyncio.create_task(capture_microphone(audio_source))
    return audio_source


async def capture_microphone(audio_source: rtc.AudioSource):
    sample_rate = 48000
    frame = rtc.AudioFrame.create(sample_rate, 1, 480)
    audio_queue = queue.Queue(maxsize=100)
    stop_event = threading.Event()

    def input_callback(indata, frames, time_info, status):
        try:
            audio_queue.put_nowait(np.frombuffer(indata, dtype=np.int16).copy())
        except queue.Full:
            pass

    def recording_thread():
        with sd.RawInputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            callback=input_callback,
            blocksize=480,
        ):
            while not stop_event.is_set():
                time.sleep(0.01)

    threading.Thread(target=recording_thread, daemon=True).start()
    print("🎤 Mic started")

    buffer = np.array([], dtype=np.int16)
    while True:
        try:
            audio_data = audio_queue.get(timeout=0.1)
            buffer = np.concatenate([buffer, audio_data])

            while len(buffer) >= 480:
                chunk = buffer[:480]
                buffer = buffer[480:]
                np.copyto(np.frombuffer(frame.data, dtype=np.int16), chunk)
                await audio_source.capture_frame(frame)

        except queue.Empty:
            await asyncio.sleep(0.001)


### Step 4: Handle Translated Audio Track ###
from livekit import rtc


def on_track_subscribed(track, publication, participant):
    if track.kind == rtc.TrackKind.KIND_AUDIO and "translation_" in publication.name:
        lang = publication.name.split("translation_")[-1]
        play_track(track, lang)


def play_track(track: rtc.Track, lang: str):
    def run_playback():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def play():
            audio_stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
            audio_queue = queue.Queue(maxsize=100)

            def audio_callback(outdata, frames, time_info, status):
                try:
                    data = audio_queue.get_nowait()
                    outdata[:] = data.reshape(-1, 1)
                except queue.Empty:
                    outdata.fill(0)

            output_stream = sd.OutputStream(
                samplerate=48000,
                channels=1,
                dtype="int16",
                callback=audio_callback,
                blocksize=480,
            )
            output_stream.start()
            print(f"🔊 Playing: {lang}")

            async for event in audio_stream:
                frame_data = np.frombuffer(event.frame.data, dtype=np.int16)
                try:
                    audio_queue.put_nowait(frame_data)
                except queue.Full:
                    pass

        loop.run_until_complete(play())

    threading.Thread(target=run_playback, daemon=True).start()


### Step 5: Start the Translation ###
import json

from livekit import rtc


async def start_translation(room: rtc.Room, translation_settings: dict):
    # Create the set_task message
    payload = {"message_type": "set_task", "data": translation_settings}

    # Send through data channel
    message_bytes = json.dumps(payload).encode("utf-8")
    await room.local_participant.publish_data(message_bytes, True)

    langs = [
        t["target_language"] for t in translation_settings["pipeline"]["translations"]
    ]
    print(f"⚙️ Settings sent: {langs}")


### SUPPORTING CODE ###
import time

import websockets

# Minimal translation settings
MINIMAL_SETTINGS = {
    "input_stream": {"content_type": "audio", "source": {"type": "webrtc"}},
    "output_stream": {"content_type": "audio", "target": {"type": "webrtc"}},
    "pipeline": {
        "preprocessing": {},
        "transcription": {"source_language": "en"},
        "translations": [
            {
                "target_language": "es",
                "speech_generation": {
                    "tts_model": "auto",
                    "voice_timbre_detection": {"enabled": False},
                },
            }
        ],
    },
}


# WebSocket handler (for keeping connection alive)
class SimpleWebSocket:
    def __init__(self, url: str, token: str):
        self.url = f"{url}?token={token}"
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.url, ping_interval=10, ping_timeout=30)
        print("🔌 WebSocket connected")
        asyncio.create_task(self._receive_loop())

    async def _receive_loop(self):
        while self.ws:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=60)
                data = json.loads(msg)
                if data.get("message_type") == "current_task":
                    print("📝 Task confirmed")
            except:
                pass

    async def send(self, message: dict):
        if self.ws:
            await self.ws.send(json.dumps(message))


# Wait for translator helper
async def wait_for_translator(room: rtc.Room, timeout: int = 10):
    start = time.time()
    while time.time() - start < timeout:
        for participant in room.remote_participants.values():
            if participant.identity.startswith("palabra_translator"):
                print(f"🌐 Translator joined: {participant.identity}")
                return participant
        await asyncio.sleep(0.1)
    raise TimeoutError("No translator joined")


# Data handler for transcriptions
def on_data_received(packet):
    try:
        data = json.loads(packet.data.decode())
        msg_type = data.get("message_type")
        if msg_type in [
            "partial_transcription",
            "validated_transcription",
            "translated_transcription",
        ]:
            text = data["data"]["transcription"]["text"]
            lang = data["data"]["transcription"]["language"]
            part = msg_type == "partial_transcription"
            print(
                f"\r\033[K{'💬' if part else '✅'} [{lang}] {text}",
                end="" if part else "\n",
                flush=True,
            )
    except:
        pass


### RUNNER ###
import os
import signal


async def main():
    signal.signal(signal.SIGINT, lambda s, f: os._exit(0))
    print("🚀 Palabra Client - Minimal")

    # Step 2: Create session
    session = await create_session(
        os.getenv("PALABRA_CLIENT_ID"), os.getenv("PALABRA_CLIENT_SECRET")
    )
    webrtc_url = session["data"]["webrtc_url"]
    ws_url = session["data"]["ws_url"]
    publisher = session["data"]["publisher"]

    # Connect WebSocket for keepalive
    ws = SimpleWebSocket(ws_url, publisher)
    await ws.connect()

    # Step 3: Connect to room
    room = rtc.Room()
    room.on("track_subscribed", on_track_subscribed)
    room.on("data_received", on_data_received)
    await room.connect(webrtc_url, publisher, rtc.RoomOptions(auto_subscribe=True))

    # Wait for translator
    try:
        await wait_for_translator(room)
    except TimeoutError:
        print("⚠️ No translator, continuing...")

    # Step 6: Send settings first (before publishing audio)
    await ws.send({"message_type": "set_task", "data": MINIMAL_SETTINGS})
    langs = [t["target_language"] for t in MINIMAL_SETTINGS["pipeline"]["translations"]]
    print(f"⚙️ Settings sent: {langs}")

    # Wait for settings to process
    await asyncio.sleep(3)

    # Step 4: Publish microphone AFTER settings
    await publish_audio_track(room)

    print("\n🎧 Listening... Press Ctrl+C to stop\n")

    try:
        await asyncio.Event().wait()
    except:  # noqa: E722
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown complete")
        os._exit(0)
