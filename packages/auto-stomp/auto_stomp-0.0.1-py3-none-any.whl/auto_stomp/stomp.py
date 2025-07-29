import websockets
import asyncio
import logging
from frame import *
import inspect

class Client:
    def __init__(self, brockerURL, connectHeaders=None, heartbeat=(0, 0), debug=False):
        self.logger = logging.getLogger("stomp-client")
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        self.brockerURL = brockerURL
        self.connectHeaders = connectHeaders or {}
        self.heartbeat = heartbeat
        self.debug = debug
        self.connected = False
        self.subscribers = {}
        self.id_to_destination = {}

    async def connect(self, login=None, passcode=None, host=""):
        self.ws = await websockets.connect(self.brockerURL)
        frame = generate_connect_frame(
            login=login, passcode=passcode, host=host,
            heartbeat=self.heartbeat, connectHeaders=self.connectHeaders
        )
        await self.ws.send(frame)
        self.reader_task = asyncio.create_task(self._read_frames())
 
    async def send(self, destination, body, content_type="text/plain"):
        if not self.connected:
            raise RuntimeError("Client is not connected. Please connect before sending messages.")

        frame = generate_send_frame(
            destination=destination, body=body, content_type=content_type
        )
        await self.ws.send(frame)

    async def subscribe(self, id, destination, callback, ack="auto"):
        if not self.connected:
            raise RuntimeError("Client is not connected. Please connect before subscribing.")

        frame = generate_subscribe_frame(
            id=id, destination=destination, ack=ack
        )
        await self.ws.send(frame)

        if id in self.id_to_destination:
            raise ValueError(f"ID {id} already subscribed to {self.id_to_destination[id]}")

        if destination in self.subscribers:
            raise ValueError(f"Destination {destination} already has a subscriber")
        
        if callback:
            self.subscribers[destination] = callback
            self.id_to_destination[id] = destination

    async def unsubscribe(self, id):
        if not self.connected:
            raise RuntimeError("Client is not connected. Please connect before unsubscribing.")

        frame = generate_unsubscribe_frame(id)
        await self.ws.send(frame)
        dest = self.id_to_destination.pop(id, None)

        if dest and dest in self.subscribers:
            del self.subscribers[dest]

    async def disconnect(self, receipt):
        if not self.connected:
            raise RuntimeError("Client is not connected. Please connect before disconnecting.")
        
        frame = generate_disconnect_frame(receipt=receipt)
        await self.ws.send(frame)
        await self.ws.close()

    async def run_forever(self):
        await asyncio.Event().wait()
        
    async def _read_frames(self):
        while True:
            try:
                frame = await self.ws.recv()
                frame_data = parse_frame(frame)

                if frame_data.get("command") == "CONNECTED":
                    self.version = frame_data.get("headers", {}).get("version")
                    self.logger.info(f"Connected to STOMP broker with version: {self.version}")
                    self.connected = True
                elif frame_data.get("command") == "MESSAGE":
                    await self._handle_message(frame_data.get("headers", {}), frame_data.get("body", ""))
                elif frame_data.get("command") == "RECEIPT":
                    self._handle_receipt(frame_data.get("headers", {}))
                elif frame_data.get("command") == "ERROR":
                    self.logger.error(f"Error frame received: {frame_data.get('body', '')}")
            except websockets.ConnectionClosed:
                self.logger.error("Connection closed by the server.")
                break
            except Exception as e:
                self.logger.error(f"Error reading frame: {e}")

    async def _handle_message(self, headers, body):
        self.logger.warning(f"Message received: {body} with headers: {headers}")
        destination = headers.get("destination")
        if destination in self.subscribers:
            callback = self.subscribers[destination]
            if inspect.iscoroutinefunction(callback):
                await callback(body)
            else:
                callback(body)
        else:
            self.logger.warning(f"No subscriber for destination: {destination}")
    
    def _handle_receipt(self, headers):
        receipt_id = headers.get("receipt-id")
        self.logger.info(f"Receipt received: {receipt_id}")