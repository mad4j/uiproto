# UIProto - HMI Communication Protocol

A comprehensive Protocol Buffer (protobuf) based communication protocol for Human-Machine Interface (HMI) systems, enabling bidirectional communication between web applications and devices.

## Overview

This protocol defines a standardized way for web applications to interact with devices for HMI management, supporting:

- **UI Widgets**: Buttons, sliders, switches, text fields, labels, numeric displays, progress bars, and selectors
- **Bidirectional Communication**: Commands from web app to device, events from device to web app
- **Real-time Updates**: Status monitoring, telemetry data, and component state changes
- **Configuration Management**: Dynamic device configuration and parameter updates
- **Alert System**: Multi-level alerts (Info, Warning, Error, Critical)
- **Error Handling**: Comprehensive error codes and responses
- **Heartbeat Mechanism**: Connection monitoring for both sides

## Quick Start

### Protocol Definition

The protocol is defined in `hmi_protocol.proto` using Protocol Buffers syntax v3.

### Key Message Types

- **Message**: Top-level envelope for all communication
- **Command**: Actions from web app to device (button presses, value changes, configuration updates)
- **Event**: Notifications from device to web app (status updates, alerts, telemetry)
- **Heartbeat**: Keep-alive messages for connection monitoring

### Supported UI Widgets

- Button - Interactive buttons with labels and icons
- Slider - Numeric input with range constraints
- Switch - Binary toggle controls
- TextField - Text input fields (including password fields)
- Label - Display-only text with styling options
- NumericDisplay - Formatted numeric values with units
- ProgressBar - Progress indicators for long operations
- Selector - Dropdown selection widgets

## Documentation

- **[PROTOCOL.md](PROTOCOL.md)** - Complete protocol specification and usage guide
- **[EXAMPLES.md](EXAMPLES.md)** - Practical examples for common scenarios
- **[hmi_protocol.proto](hmi_protocol.proto)** - Protocol Buffer schema definition

## Usage

### Generate Code

Use the Protocol Buffer compiler to generate code for your target language:

```bash
# Python
protoc --python_out=. hmi_protocol.proto

# JavaScript
protoc --js_out=import_style=commonjs,binary:. hmi_protocol.proto

# Java
protoc --java_out=. hmi_protocol.proto

# C++
protoc --cpp_out=. hmi_protocol.proto

# Go
protoc --go_out=. hmi_protocol.proto
```

### Basic Example

```protobuf
// Send a button press command
Message {
  message_id: "cmd_001"
  timestamp: { milliseconds: 1706820526000 }
  command: {
    request_id: "req_001"
    button_press: {
      button_id: { id: "start_button" }
    }
  }
}

// Receive a status update event
Message {
  message_id: "evt_001"
  timestamp: { milliseconds: 1706820527000 }
  event: {
    event_id: "evt_001"
    status_update: {
      device_status: {
        device_id: "HMI_001"
        state: RUNNING
        firmware_version: "v1.0.0"
      }
    }
  }
}
```

## Features

### Device Management
- Device identification and versioning
- Device state tracking (Offline, Initializing, Ready, Running, Error, Maintenance)
- Uptime monitoring

### UI Layout System
- Hierarchical layout with sections
- Grid-based component positioning
- Dynamic component updates

### Configuration System
- Key-value configuration parameters
- Support for multiple data types (bool, int, double, string, bytes)
- Configuration validation and error reporting

### Telemetry System
- Time-series data collection
- Metric tagging for categorization
- Multiple simultaneous metrics

### Alert System
- Four severity levels (Info, Warning, Error, Critical)
- Optional acknowledgment requirement
- Component correlation for context

## Transport Options

This protocol is transport-agnostic and works with:

- **WebSocket** - Real-time bidirectional communication
- **HTTP/REST** - Request-response patterns
- **MQTT** - Publish-subscribe messaging
- **gRPC** - Efficient RPC framework

## Security

The protocol focuses on data structure and should be secured at the transport layer:

- Use TLS/SSL for encryption
- Implement authentication/authorization
- Validate and sanitize all inputs
- Apply rate limiting
- Enable audit logging

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! This protocol is designed to be extensible:

- Add new widget types by extending ComponentUpdate
- Add new command types using oneof fields
- Add new event types for specialized use cases
- Maintain backward compatibility with versioning

## Use Cases

- Industrial control panels
- Building automation systems
- Laboratory equipment interfaces
- Medical device monitoring
- IoT device management
- Process control systems
- Smart home interfaces
- Vehicle dashboards
