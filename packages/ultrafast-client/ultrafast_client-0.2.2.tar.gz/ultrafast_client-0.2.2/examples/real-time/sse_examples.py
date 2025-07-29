#!/usr/bin/env python3
"""
Server-Sent Events (SSE) Examples
=================================

Examples demonstrating Server-Sent Events for real-time server-to-client streaming.
"""

import asyncio

import ultrafast_client as uc


def basic_sse_sync():
    """Basic synchronous SSE example."""
    print("=== Basic Synchronous SSE ===")

    # Create SSE client
    sse_client = uc.SSEClient(reconnect_timeout=5.0, max_reconnect_attempts=3)

    try:
        # Connect to SSE stream
        print("Connecting to SSE stream...")
        sse_client.connect("https://httpbin.org/stream/5")

        if sse_client.is_connected():
            print("✅ Connected to SSE stream")

            # Listen for events
            event_stream = sse_client.listen()
            event_count = 0
            max_events = 5

            for event in event_stream:
                if event_count >= max_events:
                    break

                print(f"📥 Event {event_count + 1}:")
                print(f"  Type: {event.event_type}")
                print(f"  Data: {event.data}")
                print(f"  ID: {event.id}")
                print(f"  Timestamp: {event.timestamp}")

                # Check if it's keepalive
                if event.is_keepalive():
                    print("  💓 Keepalive event")

                # Try to parse as JSON
                try:
                    json_data = event.json()
                    print(f"  JSON: {json_data}")
                except:
                    print("  (Not valid JSON)")

                event_count += 1
                print()

            sse_client.close()
            print("✅ SSE connection closed")
        else:
            print("❌ Failed to connect to SSE stream")

    except Exception as e:
        print(f"❌ SSE error: {e}")

    print()


async def basic_sse_async():
    """Basic asynchronous SSE example."""
    print("=== Basic Asynchronous SSE ===")

    # Create async SSE client
    sse_client = uc.AsyncSSEClient(reconnect_timeout=5.0, max_reconnect_attempts=3)

    try:
        # Connect to SSE stream
        print("Connecting to async SSE stream...")
        await sse_client.connect("https://httpbin.org/stream/3")

        if sse_client.is_connected():
            print("✅ Connected to async SSE stream")

            # Listen for events with timeout
            event_count = 0
            max_events = 3

            async for event in sse_client.listen():
                if event_count >= max_events:
                    break

                print(f"📥 Async Event {event_count + 1}:")
                print(f"  Data: {event.data[:100]}...")  # Truncate long data

                # Parse as JSON if possible
                try:
                    json_data = event.json()
                    if "url" in json_data:
                        print(f"  URL: {json_data['url']}")
                    if "id" in json_data:
                        print(f"  Request ID: {json_data['id']}")
                except:
                    pass

                event_count += 1
                print()

            await sse_client.close()
            print("✅ Async SSE connection closed")
        else:
            print("❌ Failed to connect to async SSE stream")

    except Exception as e:
        print(f"❌ Async SSE error: {e}")

    print()


def sse_with_authentication():
    """SSE with authentication headers."""
    print("=== SSE with Authentication ===")

    # Create SSE client with auth headers
    sse_client = uc.SSEClient(
        headers={
            "Authorization": "Bearer your-auth-token",
            "X-Client-Version": "1.0",
            "Accept": "text/event-stream",
        }
    )

    print("SSE client configured with authentication headers")
    print("Headers:", sse_client.headers())

    # In a real scenario, you would connect to an authenticated SSE endpoint
    # sse_client.connect("https://api.example.com/events")

    print()


def sse_event_types():
    """Demonstrate different SSE event handling."""
    print("=== SSE Event Types and Parsing ===")

    # Create sample events manually for demonstration
    sample_events = [
        {"event_type": "message", "data": "Hello World!", "id": "msg_1", "retry": None},
        {
            "event_type": "user_update",
            "data": '{"user_id": 123, "name": "John Doe", "status": "online"}',
            "id": "user_123",
            "retry": None,
        },
        {
            "event_type": "system",
            "data": "Server maintenance in 10 minutes",
            "id": "sys_001",
            "retry": 5000,
        },
        {
            "event_type": None,  # Default event
            "data": "No event type specified",
            "id": None,
            "retry": None,
        },
    ]

    for i, event_data in enumerate(sample_events, 1):
        # Create SSE event
        event = uc.SSEEvent.new(
            event_type=event_data["event_type"],
            data=event_data["data"],
            id=event_data["id"],
            retry=event_data["retry"],
        )

        print(f"Event {i}:")
        print(f"  Type: {event.event_type}")
        print(f"  Data: {event.data}")
        print(f"  ID: {event.id}")
        print(f"  Retry: {event.retry}")
        print(f"  Timestamp: {event.timestamp}")
        print(f"  Is keepalive: {event.is_keepalive()}")
        print(f"  Is retry: {event.is_retry()}")

        # Try to parse as JSON
        try:
            json_data = event.json()
            print(f"  JSON parsed: {json_data}")
        except:
            print("  (Not JSON data)")

        print()


async def sse_with_timeout():
    """SSE connection with timeout handling."""
    print("=== SSE with Timeout Handling ===")

    sse_client = uc.AsyncSSEClient()

    try:
        await sse_client.connect("https://httpbin.org/stream/10")

        if sse_client.is_connected():
            print("✅ Connected, listening with timeout...")

            event_count = 0
            timeout_count = 0
            max_timeouts = 3

            while timeout_count < max_timeouts and event_count < 5:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(
                        sse_client.listen().__anext__(), timeout=3.0
                    )

                    print(f"📥 Event {event_count + 1}: {event.data[:50]}...")
                    event_count += 1

                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"⏰ Timeout {timeout_count}/{max_timeouts}")
                except StopAsyncIteration:
                    print("📡 Stream ended")
                    break

            await sse_client.close()
            print(f"✅ Completed with {event_count} events, {timeout_count} timeouts")

    except Exception as e:
        print(f"❌ SSE timeout demo error: {e}")

    print()


async def sse_event_filtering():
    """Filter and process specific SSE event types."""
    print("=== SSE Event Filtering ===")

    class SSEEventProcessor:
        def __init__(self):
            self.event_handlers = {
                "message": self.handle_message,
                "user_update": self.handle_user_update,
                "system": self.handle_system,
                "notification": self.handle_notification,
            }
            self.stats = {"total_events": 0, "processed_events": 0, "unknown_events": 0}

        def handle_message(self, event):
            """Handle message events."""
            print(f"💬 Message: {event.data}")
            return True

        def handle_user_update(self, event):
            """Handle user update events."""
            try:
                user_data = event.json()
                print(
                    f"👤 User update: {user_data.get('name', 'Unknown')} is {user_data.get('status', 'unknown')}"
                )
                return True
            except:
                print(f"👤 User update: {event.data}")
                return True

        def handle_system(self, event):
            """Handle system events."""
            print(f"⚙️  System: {event.data}")
            if event.is_retry():
                print(f"  Retry after: {event.retry}ms")
            return True

        def handle_notification(self, event):
            """Handle notification events."""
            print(f"🔔 Notification: {event.data}")
            return True

        def process_event(self, event):
            """Process an incoming event."""
            self.stats["total_events"] += 1

            event_type = event.event_type or "message"  # Default to message

            if event_type in self.event_handlers:
                try:
                    if self.event_handlers[event_type](event):
                        self.stats["processed_events"] += 1
                except Exception as e:
                    print(f"❌ Error processing {event_type} event: {e}")
            else:
                self.stats["unknown_events"] += 1
                print(f"❓ Unknown event type: {event_type}")

        def get_stats(self):
            """Get processing statistics."""
            return self.stats

    # Create event processor
    processor = SSEEventProcessor()

    # Simulate processing events (using httpbin stream)
    sse_client = uc.AsyncSSEClient()

    try:
        await sse_client.connect("https://httpbin.org/stream/5")

        if sse_client.is_connected():
            print("✅ Connected, filtering events...")

            async for event in sse_client.listen():
                processor.process_event(event)

                # Stop after processing a few events
                if processor.stats["total_events"] >= 5:
                    break

            await sse_client.close()

            # Show statistics
            stats = processor.get_stats()
            print("\n📊 Processing Statistics:")
            print(f"  Total events: {stats['total_events']}")
            print(f"  Processed: {stats['processed_events']}")
            print(f"  Unknown: {stats['unknown_events']}")

    except Exception as e:
        print(f"❌ Event filtering error: {e}")

    print()


async def sse_multiple_streams():
    """Handle multiple SSE streams concurrently."""
    print("=== Multiple SSE Streams ===")

    async def monitor_stream(stream_name, url, max_events=3):
        """Monitor a single SSE stream."""
        sse_client = uc.AsyncSSEClient()

        try:
            await sse_client.connect(url)

            if sse_client.is_connected():
                print(f"✅ {stream_name} connected")

                event_count = 0
                async for event in sse_client.listen():
                    if event_count >= max_events:
                        break

                    print(
                        f"📥 {stream_name} Event {event_count + 1}: {event.data[:50]}..."
                    )
                    event_count += 1

                await sse_client.close()
                print(f"✅ {stream_name} completed ({event_count} events)")
                return event_count
            else:
                print(f"❌ {stream_name} failed to connect")
                return 0

        except Exception as e:
            print(f"❌ {stream_name} error: {e}")
            return 0

    # Monitor multiple streams concurrently
    streams = [
        ("Stream A", "https://httpbin.org/stream/3"),
        ("Stream B", "https://httpbin.org/stream/4"),
        ("Stream C", "https://httpbin.org/stream/2"),
    ]

    tasks = [monitor_stream(name, url) for name, url in streams]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_events = sum(r for r in results if isinstance(r, int))
    print(f"\n📊 Total events across all streams: {total_events}")
    print()


def sse_utility_functions():
    """Demonstrate SSE utility functions."""
    print("=== SSE Utility Functions ===")

    # Parse SSE lines
    sample_lines = [
        "data: Hello World",
        "event: user_update",
        "id: msg_123",
        "retry: 5000",
        ": this is a comment",
        "data: Multi-line",
        "data: message",
    ]

    print("Parsing SSE lines:")
    for line in sample_lines:
        try:
            field, value = uc.parse_sse_line(line)
            if field and value:
                print(f"  '{line}' -> Field: '{field}', Value: '{value}'")
            else:
                print(f"  '{line}' -> Comment or empty line")
        except Exception as e:
            print(f"  '{line}' -> Error: {e}")

    print()

    # Build SSE event from fields
    print("Building SSE event from fields:")
    fields = {
        "event": ["user_login"],
        "data": ['{"user_id": 456, "username": "alice"}'],
        "id": ["evt_456"],
        "retry": ["3000"],
    }

    try:
        event = uc.build_sse_event(fields)
        print("✅ Built event:")
        print(f"  Type: {event.event_type}")
        print(f"  Data: {event.data}")
        print(f"  ID: {event.id}")
        print(f"  Retry: {event.retry}")

        # Parse the JSON data
        user_data = event.json()
        print(f"  Parsed JSON: {user_data}")

    except Exception as e:
        print(f"❌ Error building event: {e}")

    print()


async def main():
    """Run all SSE examples."""
    print("📡 UltraFast HTTP Client - Server-Sent Events Examples\n")

    basic_sse_sync()
    await basic_sse_async()
    sse_with_authentication()
    sse_event_types()
    await sse_with_timeout()
    await sse_event_filtering()
    await sse_multiple_streams()
    sse_utility_functions()

    print("✅ All SSE examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
