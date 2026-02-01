# HMI Protocol Documentation

## Overview

This Protocol Buffer (protobuf) schema defines a bidirectional communication protocol between a web application and a device for Human-Machine Interface (HMI) management. The protocol supports real-time UI updates, device control, status monitoring, and configuration management.

## Architecture

The protocol follows a client-server model where:
- **Web Application (Client)**: Sends commands and receives events/updates
- **Device (Server)**: Processes commands, sends status updates and events

### Communication Flow

```
Web Application              Device
      |                        |
      |--- Command ----------->|
      |                        |
      |<------- Event ---------|
      |                        |
      |--- Heartbeat --------->|
      |<------ Heartbeat ------|
```

## Core Concepts

### 1. Message Envelope

All communication uses the `Message` wrapper which contains:
- `message_id`: Unique identifier for tracking
- `timestamp`: Message creation time
- `payload`: Either a Command, Event, or Heartbeat

### 2. Commands (Web App → Device)

Commands are actions initiated by the web application:

#### Button Press
```protobuf
Command {
  request_id: "req_001"
  button_press: {
    button_id: { id: "emergency_stop" }
  }
}
```

#### Slider Change
```protobuf
Command {
  request_id: "req_002"
  slider_change: {
    slider_id: { id: "temperature_setpoint" }
    new_value: 75.5
  }
}
```

#### Switch Toggle
```protobuf
Command {
  request_id: "req_003"
  switch_toggle: {
    switch_id: { id: "pump_enabled" }
    new_state: true
  }
}
```

#### Text Input
```protobuf
Command {
  request_id: "req_004"
  text_input: {
    text_field_id: { id: "operator_name" }
    new_value: "John Doe"
  }
}
```

#### Configuration Update
```protobuf
Command {
  request_id: "req_005"
  configuration_update: {
    parameters: [
      { key: "sampling_rate_hz", value: { int_value: 100 } },
      { key: "enable_logging", value: { bool_value: true } }
    ]
  }
}
```

#### Get Status
```protobuf
Command {
  request_id: "req_006"
  get_status: {
    component_ids: [] // Empty = get all
  }
}
```

### 3. Events (Device → Web App)

Events are notifications sent by the device:

#### Status Update
```protobuf
Event {
  event_id: "evt_001"
  status_update: {
    device_status: {
      device_id: "HMI_001"
      device_name: "Production Line Controller"
      state: DEVICE_RUNNING
      firmware_version: "v2.1.3"
      uptime_seconds: 86400.0
    }
    component_statuses: [
      {
        component_id: { id: "temperature_sensor" }
        current_value: { double_value: 72.3 }
        enabled: true
        status_text: "Normal"
      }
    ]
  }
}
```

#### Alert
```protobuf
Event {
  event_id: "evt_002"
  alert: {
    level: ALERT_WARNING
    message: "Temperature approaching upper limit"
    code: "TEMP_HIGH_001"
    related_component: { id: "temperature_sensor" }
    requires_acknowledgment: true
  }
}
```

#### Component Update
```protobuf
Event {
  event_id: "evt_003"
  component_update: {
    slider: {
      id: { id: "speed_control" }
      label: "Motor Speed"
      min_value: 0
      max_value: 100
      current_value: 75
      step: 1
      enabled: true
    }
  }
}
```

#### Telemetry Data
```protobuf
Event {
  event_id: "evt_004"
  telemetry: {
    points: [
      {
        metric_name: "cpu_usage"
        value: { double_value: 45.2 }
        timestamp: { milliseconds: 1706820526000 }
        tags: { "host": "device_001", "location": "factory_a" }
      }
    ]
  }
}
```

#### Error Response
```protobuf
Event {
  event_id: "evt_005"
  error_response: {
    request_id: "req_001"
    code: COMPONENT_DISABLED
    message: "Cannot press button: component is disabled"
    details: "Button 'emergency_stop' is in maintenance mode"
  }
}
```

## UI Widgets

The protocol supports various UI widget types:

### Button
Interactive button with label and optional icon
```protobuf
Button {
  id: { id: "start_button" }
  label: "Start Process"
  enabled: true
  icon: "play"
}
```

### Slider
Numeric input with range constraints
```protobuf
Slider {
  id: { id: "volume" }
  label: "Volume Level"
  min_value: 0
  max_value: 100
  current_value: 50
  step: 5
  enabled: true
}
```

### Switch
Binary toggle control
```protobuf
Switch {
  id: { id: "power" }
  label: "Power On/Off"
  state: true
  enabled: true
}
```

### TextField
Text input field
```protobuf
TextField {
  id: { id: "user_input" }
  label: "Enter Name"
  value: ""
  placeholder: "Type here..."
  enabled: true
  password: false
}
```

### Label
Display-only text with styling
```protobuf
Label {
  id: { id: "status_label" }
  text: "System Ready"
  style: LABEL_SUCCESS
}
```

### NumericDisplay
Formatted numeric value with units
```protobuf
NumericDisplay {
  id: { id: "pressure_reading" }
  label: "Pressure"
  value: 101.325
  unit: "kPa"
  decimal_places: 2
}
```

### ProgressBar
Progress indicator
```protobuf
ProgressBar {
  id: { id: "download_progress" }
  label: "Downloading..."
  current: 75
  max: 100
  indeterminate: false
}
```

### Selector
Dropdown selection
```protobuf
Selector {
  id: { id: "mode_select" }
  label: "Operation Mode"
  options: ["Manual", "Auto", "Semi-Auto"]
  selected_index: 1
  enabled: true
}
```

## Device States

The device can be in one of the following states:

- `DEVICE_OFFLINE`: Device is not connected
- `DEVICE_INITIALIZING`: Device is starting up
- `DEVICE_READY`: Device is ready but not actively running
- `DEVICE_RUNNING`: Device is operating normally
- `DEVICE_ERROR`: Device encountered an error
- `DEVICE_MAINTENANCE`: Device is in maintenance mode

## Alert Levels

Alerts can have different severity levels:

- `ALERT_INFO`: Informational message
- `ALERT_WARNING`: Warning that requires attention
- `ALERT_ERROR`: Error condition
- `ALERT_CRITICAL`: Critical condition requiring immediate action

## Error Codes

Standard error codes for error handling:

- `UNKNOWN_ERROR`: Unspecified error
- `INVALID_COMPONENT`: Referenced component doesn't exist
- `INVALID_VALUE`: Value outside acceptable range
- `COMPONENT_DISABLED`: Operation attempted on disabled component
- `DEVICE_NOT_READY`: Device not in appropriate state
- `TIMEOUT`: Operation timed out
- `PERMISSION_DENIED`: Insufficient permissions
- `CONFIGURATION_ERROR`: Configuration parameter invalid

## Initial Setup

When a web application connects to a device, the device should send an `InitialConfiguration` message containing:

```protobuf
InitialConfiguration {
  device_status: { /* device info */ }
  ui_layout: {
    layout_id: "main_layout"
    name: "Main Control Panel"
    sections: [
      {
        section_id: "controls"
        title: "Controls"
        components: [
          { component_id: { id: "start_button" }, row: 0, column: 0, width: 1, height: 1 }
        ]
      }
    ]
  }
  components: [ /* all UI components */ ]
  configuration: [ /* current configuration */ ]
}
```

## Heartbeat Mechanism

Both sides should send periodic heartbeat messages to detect disconnections:

```protobuf
Message {
  message_id: "hb_001"
  timestamp: { milliseconds: 1706820526000 }
  heartbeat: {
    source: "webapp"
    sequence_number: 42
  }
}
```

## Best Practices

1. **Request IDs**: Always include unique `request_id` in commands for correlation with responses
2. **Timestamps**: Include timestamps in all messages for debugging and audit trails
3. **Error Handling**: Check for `ErrorResponse` events corresponding to sent commands
4. **Status Updates**: Request periodic status updates or subscribe to push notifications
5. **Component IDs**: Use consistent, descriptive component IDs across the system
6. **Validation**: Validate values client-side before sending to reduce round-trips
7. **Buffering**: Implement message buffering for unreliable network connections
8. **Version Control**: Include firmware/protocol version in device status for compatibility checks

## Usage Example

### Complete Interaction Flow

1. **Connection Established**
   - Device sends `InitialConfiguration` with all UI components and current status

2. **User Interaction**
   - User presses a button in web app
   - Web app sends `ButtonPress` command
   - Device processes command
   - Device sends `StatusUpdate` event with new state

3. **Device Event**
   - Sensor detects anomaly
   - Device sends `Alert` event
   - Web app displays alert to user
   - User acknowledges (sends command)

4. **Configuration Change**
   - User modifies settings
   - Web app sends `ConfigurationUpdate` command
   - Device validates and applies changes
   - Device sends `ConfigurationResponse` event confirming success

5. **Periodic Updates**
   - Device sends `TelemetryData` events at regular intervals
   - Device sends heartbeat messages
   - Web app sends heartbeat messages

## Transport Layer

This protocol is transport-agnostic and can be used with:

- **WebSocket**: For real-time bidirectional communication
- **HTTP/REST**: For request-response patterns
- **MQTT**: For publish-subscribe patterns
- **gRPC**: For efficient binary communication

The protobuf serialization ensures compact binary encoding for efficient transmission.

## Code Generation

To generate code from this proto file:

### Python
```bash
protoc --python_out=. hmi_protocol.proto
```

### JavaScript
```bash
protoc --js_out=import_style=commonjs,binary:. hmi_protocol.proto
```

### Java
```bash
protoc --java_out=. hmi_protocol.proto
```

### C++
```bash
protoc --cpp_out=. hmi_protocol.proto
```

### Go
```bash
protoc --go_out=. hmi_protocol.proto
```

## Security Considerations

1. **Authentication**: Implement authentication layer on top of this protocol
2. **Encryption**: Use TLS/SSL for transport encryption
3. **Authorization**: Validate user permissions before executing commands
4. **Input Validation**: Sanitize all input values before processing
5. **Rate Limiting**: Implement rate limiting to prevent abuse
6. **Audit Logging**: Log all commands and critical events

## Extensibility

The protocol is designed to be extensible:

- Use `oneof` fields to add new command/event types
- Add new widget types by extending `ComponentUpdate`
- Add custom fields using protobuf's extension mechanism
- Version your messages for backward compatibility
