#!/usr/bin/env python3
"""
Simple example demonstrating the HMI protocol usage in Python.

This example shows how to:
1. Create and serialize protocol messages
2. Send commands from web app to device
3. Process events from device to web app
4. Handle different widget types
"""

import time
from hmi_protocol_pb2 import *


class HMIWebApp:
    """Simulates a web application using the HMI protocol."""
    
    def __init__(self):
        self.message_counter = 0
    
    def create_message_id(self):
        """Generate unique message ID."""
        self.message_counter += 1
        return f"webapp_msg_{self.message_counter}"
    
    def send_button_press(self, button_id: str) -> bytes:
        """Create and serialize a button press command."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.command.request_id = f"req_{self.message_counter}"
        msg.command.button_press.button_id.id = button_id
        
        return msg.SerializeToString()
    
    def send_slider_change(self, slider_id: str, new_value: float) -> bytes:
        """Create and serialize a slider change command."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.command.request_id = f"req_{self.message_counter}"
        msg.command.slider_change.slider_id.id = slider_id
        msg.command.slider_change.new_value = new_value
        
        return msg.SerializeToString()
    
    def send_switch_toggle(self, switch_id: str, new_state: bool) -> bytes:
        """Create and serialize a switch toggle command."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.command.request_id = f"req_{self.message_counter}"
        msg.command.switch_toggle.switch_id.id = switch_id
        msg.command.switch_toggle.new_state = new_state
        
        return msg.SerializeToString()
    
    def send_heartbeat(self) -> bytes:
        """Create and serialize a heartbeat message."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.heartbeat.source = "webapp"
        msg.heartbeat.sequence_number = self.message_counter
        
        return msg.SerializeToString()


class HMIDevice:
    """Simulates a device using the HMI protocol."""
    
    def __init__(self, device_id: str, device_name: str):
        self.device_id = device_id
        self.device_name = device_name
        self.message_counter = 0
        self.current_temperature = 22.5
        self.heater_enabled = False
    
    def create_message_id(self):
        """Generate unique message ID."""
        self.message_counter += 1
        return f"device_msg_{self.message_counter}"
    
    def send_initial_configuration(self) -> bytes:
        """Send initial device configuration."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        # Device status
        msg.event.event_id = f"evt_{self.message_counter}"
        msg.event.status_update.device_status.device_id = self.device_id
        msg.event.status_update.device_status.device_name = self.device_name
        msg.event.status_update.device_status.state = DEVICE_READY
        msg.event.status_update.device_status.firmware_version = "v1.0.0"
        msg.event.status_update.device_status.uptime_seconds = 0
        
        return msg.SerializeToString()
    
    def send_temperature_display(self) -> bytes:
        """Send temperature display component update."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.event.event_id = f"evt_{self.message_counter}"
        msg.event.component_update.numeric_display.id.id = "current_temp"
        msg.event.component_update.numeric_display.label = "Current Temperature"
        msg.event.component_update.numeric_display.value = self.current_temperature
        msg.event.component_update.numeric_display.unit = "°C"
        msg.event.component_update.numeric_display.decimal_places = 1
        
        return msg.SerializeToString()
    
    def send_heater_switch(self) -> bytes:
        """Send heater switch component update."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.event.event_id = f"evt_{self.message_counter}"
        msg.event.component_update.switch.id.id = "heater_enable"
        msg.event.component_update.switch.label = "Heater Enabled"
        msg.event.component_update.switch.state = self.heater_enabled
        msg.event.component_update.switch.enabled = True
        
        return msg.SerializeToString()
    
    def send_alert(self, level: AlertLevel, message: str, code: str) -> bytes:
        """Send an alert event."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.event.event_id = f"evt_{self.message_counter}"
        msg.event.alert.level = level
        msg.event.alert.message = message
        msg.event.alert.code = code
        msg.event.alert.requires_acknowledgment = (level >= ALERT_WARNING)
        
        return msg.SerializeToString()
    
    def send_telemetry(self) -> bytes:
        """Send telemetry data."""
        msg = Message(
            message_id=self.create_message_id(),
            timestamp=Timestamp(milliseconds=int(time.time() * 1000))
        )
        
        msg.event.event_id = f"evt_{self.message_counter}"
        
        # Add temperature telemetry point
        point = msg.event.telemetry.points.add()
        point.metric_name = "temperature"
        point.value.double_value = self.current_temperature
        point.timestamp.milliseconds = int(time.time() * 1000)
        point.tags["sensor"] = "main"
        point.tags["unit"] = "celsius"
        
        return msg.SerializeToString()
    
    def process_command(self, data: bytes) -> bytes:
        """Process a command and return response event."""
        msg = Message()
        msg.ParseFromString(data)
        
        if msg.HasField('command'):
            cmd = msg.command
            
            if cmd.HasField('button_press'):
                return self.handle_button_press(cmd.button_press, cmd.request_id)
            elif cmd.HasField('slider_change'):
                return self.handle_slider_change(cmd.slider_change, cmd.request_id)
            elif cmd.HasField('switch_toggle'):
                return self.handle_switch_toggle(cmd.switch_toggle, cmd.request_id)
        
        return b""
    
    def handle_button_press(self, button_press, request_id: str) -> bytes:
        """Handle button press command."""
        button_id = button_press.button_id.id
        
        if button_id == "emergency_stop":
            return self.send_alert(
                ALERT_CRITICAL,
                "Emergency stop activated!",
                "ESTOP_001"
            )
        
        return b""
    
    def handle_slider_change(self, slider_change, request_id: str) -> bytes:
        """Handle slider change command."""
        # Process the slider value change
        return self.send_temperature_display()
    
    def handle_switch_toggle(self, switch_toggle, request_id: str) -> bytes:
        """Handle switch toggle command."""
        switch_id = switch_toggle.switch_id.id
        
        if switch_id == "heater_enable":
            self.heater_enabled = switch_toggle.new_state
            return self.send_heater_switch()
        
        return b""


def main():
    """Demonstrate protocol usage."""
    print("HMI Protocol Demo")
    print("=" * 60)
    
    # Create instances
    webapp = HMIWebApp()
    device = HMIDevice("TEMP_CTRL_001", "Temperature Controller")
    
    print("\n1. Device sends initial configuration")
    init_msg = device.send_initial_configuration()
    print(f"   Sent {len(init_msg)} bytes")
    
    # Parse and display
    msg = Message()
    msg.ParseFromString(init_msg)
    print(f"   Device: {msg.event.status_update.device_status.device_name}")
    print(f"   State: {DeviceState.Name(msg.event.status_update.device_status.state)}")
    
    print("\n2. Device sends UI components")
    temp_msg = device.send_temperature_display()
    print(f"   Temperature display: {len(temp_msg)} bytes")
    
    heater_msg = device.send_heater_switch()
    print(f"   Heater switch: {len(heater_msg)} bytes")
    
    print("\n3. Web app toggles heater switch")
    toggle_cmd = webapp.send_switch_toggle("heater_enable", True)
    print(f"   Sent command: {len(toggle_cmd)} bytes")
    
    # Device processes command
    response = device.process_command(toggle_cmd)
    print(f"   Device response: {len(response)} bytes")
    
    # Parse response
    msg = Message()
    msg.ParseFromString(response)
    if msg.event.HasField('component_update'):
        print(f"   Heater state: {msg.event.component_update.switch.state}")
    
    print("\n4. Device sends telemetry")
    telemetry = device.send_telemetry()
    print(f"   Telemetry data: {len(telemetry)} bytes")
    
    msg = Message()
    msg.ParseFromString(telemetry)
    if msg.event.HasField('telemetry'):
        for point in msg.event.telemetry.points:
            print(f"   Metric: {point.metric_name} = {point.value.double_value:.1f}")
    
    print("\n5. Device sends critical alert")
    alert = device.send_alert(
        ALERT_CRITICAL,
        "Temperature exceeded limit!",
        "TEMP_HIGH_001"
    )
    print(f"   Alert: {len(alert)} bytes")
    
    msg = Message()
    msg.ParseFromString(alert)
    if msg.event.HasField('alert'):
        print(f"   Level: {AlertLevel.Name(msg.event.alert.level)}")
        print(f"   Message: {msg.event.alert.message}")
    
    print("\n6. Web app sends heartbeat")
    heartbeat = webapp.send_heartbeat()
    print(f"   Heartbeat: {len(heartbeat)} bytes")
    
    msg = Message()
    msg.ParseFromString(heartbeat)
    if msg.HasField('heartbeat'):
        print(f"   Source: {msg.heartbeat.source}")
        print(f"   Sequence: {msg.heartbeat.sequence_number}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")


if __name__ == "__main__":
    main()
