from __future__ import annotations  # Type checking

from PyQt5.QtCore import QThread
from fastapi import FastAPI, Request #not standard lib
from uvicorn import Config, Server #not standard lib
from pydantic import BaseModel
import asyncio
import socket
import typing
import server.handlers.elector_actions as elector_actions

if typing.TYPE_CHECKING:
    from ui.api_events import APIEvents
    from threads.server_thread import ServerThread

class Credentials(BaseModel):
    public_key: str  # PEM-encoded string
    private_key: str


def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0

class APIServerThread(QThread):
    api_events : APIEvents
    def __init__(self, api_events : APIEvents,  start_port: int = 5000, max_attempts: int = 10):
        super().__init__()
        self.api_events = api_events
        self.start_port = start_port
        self.max_attempts = max_attempts
        self.running_port = None

    def set_server_thread(self , server_thread : ServerThread):
        self.server_thread = server_thread

    def run(self):
        app = FastAPI()

        @app.post("/test")
        async def test_echo(request : Request):
            data = await request.json()
            print(data)
            return {"status": "ok"}
        
        @app.get("/test")
        async def test_get():
            return {"message": "working!"}

        @app.post("/credentials")
        async def receive_credentials(creds: Credentials):
            self.api_events.credentials_loaded.emit(creds.public_key , creds.private_key)
            if self.server_thread.server is not None and self.server_thread.loop is not None:
                self.server_thread.loop.call_soon_threadsafe(
                    elector_actions.load_credentials_from_api,
                    self.server_thread.server,
                    creds
                )
            return {"status": "ok"}

        for offset in range(self.max_attempts):
            port = self.start_port + offset
            if not is_port_available(port):
                continue

            config = Config(
                app=app,
                host="0.0.0.0",
                port=port,
                log_level="info",
                ssl_keyfile="key.pem",
                ssl_certfile="cert.pem",
            )
            server = Server(config)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                self.running_port = port
                print(f"FastAPI running on port {port}")
                self.api_events.api_started.emit(self.running_port)
                loop.run_until_complete(server.serve())

                break
            except OSError as e:
                print(f"Failed on port {port}: {e}")
                continue
            finally:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
