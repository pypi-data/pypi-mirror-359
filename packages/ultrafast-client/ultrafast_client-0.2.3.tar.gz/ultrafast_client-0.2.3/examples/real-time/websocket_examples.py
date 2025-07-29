#!/usr/bin/env python3
"""
WebSocket Examples
=================

Examples demonstrating WebSocket functionality for real-time bidirectional communication.
"""

import asyncio
import json
import time

import ultrafast_client as uc


def basic_websocket_sync():
    """Basic synchronous WebSocket example."""
    print("=== Basic Synchronous WebSocket ===")

    # Create WebSocket client
    ws_client = uc.WebSocketClient(
        auto_reconnect=True, max_reconnect_attempts=3, reconnect_delay=1.0
    )

    try:
        # Connect to echo server
        print("Connecting to WebSocket echo server...")
        if ws_client.connect("wss://echo.websocket.org/"):
            print("✅ Connected successfully")

            # Send text message using WebSocketMessage
            text_msg = uc.WebSocketMessage.new_text("Hello WebSocket!")
            ws_client.send(text_msg)
            print("📤 Sent text message via WebSocketMessage")

            # Send text message directly
            ws_client.send_text("Hello from send_text!")
            print("📤 Sent text message directly")

            # Send binary message using WebSocketMessage
            binary_msg = uc.WebSocketMessage.new_binary(list(b"Binary data"))
            ws_client.send(binary_msg)
            print("📤 Sent binary message via WebSocketMessage")

            # Send binary message directly
            ws_client.send_bytes(list(b"Direct binary data"))
            print("📤 Sent binary message directly")

            # Send ping message
            ws_client.ping(list(b"ping"))
            print("📤 Sent ping message")

            # Receive messages
            message_count = 0
            max_attempts = 5
            while ws_client.is_connected() and message_count < max_attempts:
                message = ws_client.receive()
                if message:
                    if message.is_text():
                        print(f"📥 Received text: {message.text()}")
                    elif message.is_binary():
                        print(f"📥 Received binary: {len(message.data())} bytes")
                    elif message.is_ping():
                        print("📥 Received ping message")
                        # Respond with pong
                        ws_client.pong(list(b"pong"))
                        print("📤 Sent pong response")
                    elif message.is_pong():
                        print("📥 Received pong message")
                    elif message.is_close():
                        print("📥 Received close message")
                        break

                    message_count += 1
                else:
                    # Try receiving with timeout
                    timeout_message = ws_client.receive_timeout(2.0)
                    if timeout_message:
                        print(f"📥 Received via timeout: {timeout_message.message_type}")
                        message_count += 1
                    else:
                        print("⏰ No message received within timeout")
                        break

            # Try to receive all pending messages
            all_messages = ws_client.receive_all()
            if all_messages:
                print(f"📥 Received {len(all_messages)} pending messages")

            # Close connection
            ws_client.close()
            print("✅ Connection closed")
        else:
            print("❌ Failed to connect")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


async def basic_websocket_async():
    """Basic asynchronous WebSocket example."""
    print("=== Basic Asynchronous WebSocket ===")

    # Create async WebSocket client
    ws_client = uc.AsyncWebSocketClient(
        auto_reconnect=True, max_reconnect_attempts=3, reconnect_delay=1.0
    )

    try:
        # Connect to echo server
        print("Connecting to async WebSocket echo server...")
        if await ws_client.connect("wss://echo.websocket.org/"):
            print("✅ Connected successfully")

            # Send text message using WebSocketMessage
            text_msg = uc.WebSocketMessage.new_text("Hello Async WebSocket!")
            await ws_client.send(text_msg)
            print("📤 Sent text message via WebSocketMessage")

            # Send text message directly
            await ws_client.send_text("Hello from async send_text!")
            print("📤 Sent text message directly")

            # Send binary message using WebSocketMessage
            binary_msg = uc.WebSocketMessage.new_binary(list(b"Async binary data"))
            await ws_client.send(binary_msg)
            print("📤 Sent binary message via WebSocketMessage")

            # Send binary message directly
            await ws_client.send_bytes(list(b"Direct async binary data"))
            print("📤 Sent binary message directly")

            # Send ping message
            await ws_client.ping(list(b"async ping"))
            print("📤 Sent async ping message")

            # Receive messages
            received_count = 0
            timeout_count = 0
            max_timeout = 3
            max_messages = 5

            while received_count < max_messages and timeout_count < max_timeout:
                try:
                    message = await asyncio.wait_for(ws_client.receive(), timeout=2.0)

                    if message:
                        if message.is_text():
                            print(f"📥 Received text: {message.text()}")
                        elif message.is_binary():
                            print(f"📥 Received binary: {len(message.data())} bytes")
                        elif message.is_ping():
                            print("📥 Received ping message")
                            # Respond with pong
                            await ws_client.pong(list(b"async pong"))
                            print("📤 Sent async pong response")
                        elif message.is_pong():
                            print("📥 Received pong message")
                        elif message.is_close():
                            print("📥 Received close message")
                            break

                        received_count += 1
                    else:
                        # Try receiving with timeout
                        timeout_message = await ws_client.receive_timeout(1.0)
                        if timeout_message:
                            print(
                                f"📥 Received via async timeout: {timeout_message.message_type}"
                            )
                            received_count += 1
                        else:
                            timeout_count += 1
                            print(f"⏰ Async timeout {timeout_count}/{max_timeout}")

                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"⏰ Asyncio timeout {timeout_count}/{max_timeout}")

            # Try to receive all pending messages
            all_messages = await ws_client.receive_all()
            if all_messages:
                print(f"📥 Received {len(all_messages)} pending async messages")

            # Close connection
            await ws_client.close()
            print("✅ Async connection closed")
        else:
            print("❌ Failed to connect")

    except Exception as e:
        print(f"❌ Async error: {e}")

    print()


def websocket_reconnection_sync():
    """Demonstrate synchronous WebSocket auto-reconnection."""
    print("=== Synchronous WebSocket Reconnection ===")

    ws_client = uc.WebSocketClient(
        auto_reconnect=True, max_reconnect_attempts=2, reconnect_delay=0.5
    )

    try:
        # Initial connection
        if ws_client.connect("wss://echo.websocket.org/"):
            print("✅ Initial connection successful")
            print(
                f"🔄 Current reconnect attempts: {ws_client.current_reconnect_attempts}"
            )

            # Simulate connection loss by manually closing
            ws_client.close()
            print("🔌 Simulated connection loss")

            # Attempt reconnection
            try:
                if ws_client.reconnect():
                    print("✅ Reconnection successful")
                    print(
                        f"🔄 Reconnect attempts used: {ws_client.current_reconnect_attempts}"
                    )
                else:
                    print("❌ Reconnection failed")
            except Exception as e:
                print(f"❌ Reconnection error: {e}")

        else:
            print("❌ Initial connection failed")

    except Exception as e:
        print(f"❌ Reconnection demo error: {e}")

    print()


def websocket_message_types():
    """Demonstrate different WebSocket message types."""
    print("=== WebSocket Message Types ===")

    # Create different message types
    messages = [
        ("Text Message", uc.WebSocketMessage.new_text("Hello World!")),
        ("Binary Message", uc.WebSocketMessage.new_binary(b"Binary data here")),
        ("Ping Message", uc.WebSocketMessage.new_ping(b"ping")),
        ("Pong Message", uc.WebSocketMessage.new_pong(b"pong")),
        ("Close Message", uc.WebSocketMessage.new_close()),
    ]

    for name, message in messages:
        print(f"{name}:")
        print(f"  Type: {message.message_type}")
        print(f"  Is text: {message.is_text()}")
        print(f"  Is binary: {message.is_binary()}")
        print(f"  Is ping: {message.is_ping()}")
        print(f"  Is pong: {message.is_pong()}")
        print(f"  Is close: {message.is_close()}")
        print(f"  Data size: {len(message.data)} bytes")

        # Try to get text content
        if message.is_text():
            try:
                print(f"  Text content: {message.text()}")
            except Exception as e:
                print(f"  Text content error: {e}")

        print()


async def websocket_concurrent_connections():
    """Multiple concurrent WebSocket connections."""
    print("=== Concurrent WebSocket Connections ===")

    async def create_connection(connection_id):
        """Create a single WebSocket connection."""
        ws_client = uc.AsyncWebSocketClient()

        try:
            if await ws_client.connect("wss://echo.websocket.org/"):
                print(f"✅ Connection {connection_id} established")

                # Send a message using the new async method signature
                message = uc.WebSocketMessage.new_text(
                    f"Hello from connection {connection_id}"
                )
                await ws_client.send(message)
                print(f"📤 Connection {connection_id} sent message")

                # Wait for response
                try:
                    response = await asyncio.wait_for(ws_client.receive(), timeout=5.0)
                    if response and response.is_text():
                        print(
                            f"📥 Connection {connection_id} received: {response.text()}"
                        )
                except asyncio.TimeoutError:
                    print(f"⏰ Connection {connection_id} receive timeout")

                await ws_client.close()
                print(f"✅ Connection {connection_id} closed")
                return True

        except Exception as e:
            print(f"❌ Connection {connection_id} failed: {e}")
            return False

    # Create multiple concurrent connections
    num_connections = 3
    tasks = [create_connection(i + 1) for i in range(num_connections)]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = sum(1 for result in results if result is True)
    print(f"\n✅ {successful}/{num_connections} connections successful")
    print()


def websocket_chat_simulation():
    """Simulate a chat application with WebSocket."""
    print("=== WebSocket Chat Simulation ===")

    class ChatClient:
        def __init__(self, username):
            self.username = username
            self.ws_client = uc.WebSocketClient(auto_reconnect=True)
            self.connected = False

        def connect(self, url):
            """Connect to chat server."""
            try:
                if self.ws_client.connect(url):
                    self.connected = True

                    # Send join message
                    join_msg = {
                        "type": "join",
                        "username": self.username,
                        "timestamp": time.time(),
                    }
                    self.send_message("system", json.dumps(join_msg))
                    return True
            except Exception as e:
                print(f"❌ Chat connection error: {e}")
            return False

        def send_message(self, msg_type, content):
            """Send a chat message."""
            if not self.connected:
                print("❌ Not connected to chat server")
                return

            try:
                chat_msg = {
                    "type": msg_type,
                    "username": self.username,
                    "content": content,
                    "timestamp": time.time(),
                }

                # Send as text message
                self.ws_client.send_text(json.dumps(chat_msg))

            except Exception as e:
                print(f"❌ Send message error: {e}")

        def receive_message(self):
            """Receive a chat message."""
            if not self.connected:
                return None

            try:
                message = self.ws_client.receive_timeout(1.0)
                if message and message.is_text():
                    return json.loads(message.text())
            except Exception as e:
                print(f"❌ Receive message error: {e}")
            return None

        def disconnect(self):
            """Disconnect from chat server."""
            if self.connected:
                # Send leave message
                leave_msg = {
                    "type": "leave",
                    "username": self.username,
                    "timestamp": time.time(),
                }
                self.send_message("system", json.dumps(leave_msg))
                self.ws_client.close()
                self.connected = False

    # Simulate chat (using echo server for demo)
    print("Creating chat client...")
    chat_client = ChatClient("DemoUser")

    if chat_client.connect("wss://echo.websocket.org/"):
        print("✅ Connected to chat server")

        # Send some chat messages
        chat_messages = [
            "Hello everyone!",
            "How is everyone doing?",
            "This is a WebSocket chat demo",
        ]

        for msg in chat_messages:
            chat_client.send_message("chat", msg)
            print(f"📤 Sent: {msg}")

            # Try to receive echo
            response = chat_client.receive_message()
            if response:
                print(f"📥 Echo: {response}")

        chat_client.disconnect()
        print("✅ Disconnected from chat")
    else:
        print("❌ Failed to connect to chat server")

    print()


async def websocket_with_heartbeat():
    """WebSocket connection with heartbeat/keepalive."""
    print("=== WebSocket with Heartbeat ===")

    ws_client = uc.AsyncWebSocketClient()

    async def heartbeat_sender():
        """Send periodic ping messages."""
        while ws_client.connected:
            try:
                await ws_client.ping(list(b"heartbeat"))
                print("💓 Sent heartbeat ping")
                await asyncio.sleep(10)  # Send ping every 10 seconds
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                break

    async def message_receiver():
        """Receive messages and handle pongs."""
        while ws_client.connected:
            try:
                message = await asyncio.wait_for(ws_client.receive(), timeout=1.0)
                if message:
                    if message.is_pong():
                        print("💓 Received heartbeat pong")
                    elif message.is_text():
                        print(f"📥 Received message: {message.text()}")
                    elif message.is_close():
                        print("📥 Received close message")
                        break
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Receiver error: {e}")
                break

    try:
        if await ws_client.connect("wss://echo.websocket.org/"):
            print("✅ Connected with heartbeat")

            # Start heartbeat and receiver tasks
            heartbeat_task = asyncio.create_task(heartbeat_sender())
            receiver_task = asyncio.create_task(message_receiver())

            # Send a test message
            test_msg = uc.WebSocketMessage.new_text("Testing with heartbeat")
            await ws_client.send(test_msg)
            print("📤 Sent test message")

            # Run for a short time to demonstrate heartbeat
            await asyncio.sleep(5)

            # Cancel tasks and close
            heartbeat_task.cancel()
            receiver_task.cancel()

            try:
                await asyncio.gather(
                    heartbeat_task, receiver_task, return_exceptions=True
                )
            except:
                pass

            await ws_client.close()
            print("✅ Heartbeat demo completed")
        else:
            print("❌ Failed to connect")

    except Exception as e:
        print(f"❌ Heartbeat demo error: {e}")

    print()


async def websocket_context_managers():
    """Demonstrate async context manager usage."""
    print("=== WebSocket Async Context Managers ===")

    try:
        # Using async context manager
        async with uc.AsyncWebSocketClient() as ws_client:
            print("✅ Entered async context manager")

            if await ws_client.connect("wss://echo.websocket.org/"):
                print("✅ Connected via async context manager")

                # Send a message
                await ws_client.send_text("Context manager test")
                print("📤 Sent message via context manager")

                # Try to receive
                try:
                    message = await asyncio.wait_for(ws_client.receive(), timeout=2.0)
                    if message:
                        print(
                            f"📥 Received: {message.text() if message.is_text() else 'Non-text message'}"
                        )
                except asyncio.TimeoutError:
                    print("⏰ No response received")

            print("✅ Context manager will auto-close connection")

        print("✅ Exited async context manager")

    except Exception as e:
        print(f"❌ Context manager error: {e}")

    print()


# Main execution
def main():
    """Run all WebSocket examples."""
    print("🚀 UltraFast WebSocket Examples\n")

    # Synchronous examples
    basic_websocket_sync()
    websocket_reconnection_sync()
    websocket_chat_simulation()

    # Asynchronous examples
    asyncio.run(basic_websocket_async())
    asyncio.run(websocket_concurrent_connections())
    asyncio.run(websocket_with_heartbeat())
    asyncio.run(websocket_context_managers())

    print("✅ All WebSocket examples completed!")


if __name__ == "__main__":
    main()
