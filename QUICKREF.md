# Quick Reference Guide

## Message Structure

All messages use the top-level `Message` envelope:

```protobuf
Message {
  message_id: string          // Unique message identifier
  timestamp: Timestamp        // Message creation time
  payload: Command|Event|Heartbeat
}
```

## Commands (Web App → Device)

| Command Type | Purpose | Key Fields |
|-------------|---------|------------|
| `button_press` | Trigger button action | `button_id` |
| `slider_change` | Update slider value | `slider_id`, `new_value` |
| `switch_toggle` | Toggle switch state | `switch_id`, `new_state` |
| `text_input` | Submit text field value | `text_field_id`, `new_value` |
| `selector_change` | Change dropdown selection | `selector_id`, `selected_index` |
| `configuration_update` | Update device configuration | `parameters[]` |
| `get_status` | Request device status | `component_ids[]` |
| `get_configuration` | Request configuration | `keys[]` |

## Events (Device → Web App)

| Event Type | Purpose | Key Fields |
|-----------|---------|------------|
| `status_update` | Device/component status | `device_status`, `component_statuses[]` |
| `alert` | Notification/warning/error | `level`, `message`, `code` |
| `configuration_response` | Config update response | `success`, `parameters[]` |
| `component_update` | UI component update | `button`/`slider`/etc. |
| `telemetry` | Sensor/metric data | `points[]` |
| `error_response` | Error notification | `code`, `message`, `details` |

## UI Widgets

| Widget | Purpose | Key Properties |
|--------|---------|----------------|
| `Button` | Interactive button | `label`, `enabled`, `icon` |
| `Slider` | Numeric range input | `min_value`, `max_value`, `current_value`, `step` |
| `Switch` | Binary toggle | `label`, `state`, `enabled` |
| `TextField` | Text input | `label`, `value`, `placeholder`, `password` |
| `Label` | Text display | `text`, `style` |
| `NumericDisplay` | Formatted number | `value`, `unit`, `decimal_places` |
| `ProgressBar` | Progress indicator | `current`, `max`, `indeterminate` |
| `Selector` | Dropdown menu | `options[]`, `selected_index` |

## Enum Values

### DeviceState
- `DEVICE_OFFLINE` (0)
- `DEVICE_INITIALIZING` (1)
- `DEVICE_READY` (2)
- `DEVICE_RUNNING` (3)
- `DEVICE_ERROR` (4)
- `DEVICE_MAINTENANCE` (5)

### AlertLevel
- `ALERT_INFO` (0)
- `ALERT_WARNING` (1)
- `ALERT_ERROR` (2)
- `ALERT_CRITICAL` (3)

### LabelStyle
- `LABEL_NORMAL` (0)
- `LABEL_HEADING` (1)
- `LABEL_SUBHEADING` (2)
- `LABEL_WARNING` (3)
- `LABEL_ERROR` (4)
- `LABEL_SUCCESS` (5)

### ErrorCode
- `UNKNOWN_ERROR` (0)
- `INVALID_COMPONENT` (1)
- `INVALID_VALUE` (2)
- `COMPONENT_DISABLED` (3)
- `DEVICE_NOT_READY` (4)
- `TIMEOUT` (5)
- `PERMISSION_DENIED` (6)
- `CONFIGURATION_ERROR` (7)

## Common Patterns

### Send Command
```protobuf
Message {
  message_id: "cmd_123"
  timestamp: { milliseconds: <unix_ms> }
  command: {
    request_id: "req_123"  // For correlation
    <command_type>: { ... }
  }
}
```

### Receive Event
```protobuf
Message {
  message_id: "evt_456"
  timestamp: { milliseconds: <unix_ms> }
  event: {
    event_id: "evt_456"
    <event_type>: { ... }
  }
}
```

### Heartbeat
```protobuf
Message {
  message_id: "hb_789"
  timestamp: { milliseconds: <unix_ms> }
  heartbeat: {
    source: "webapp"|"device"
    sequence_number: <number>
  }
}
```

## Value Types

The `Value` message supports multiple data types:
- `bool_value`: Boolean (true/false)
- `int_value`: 32-bit integer
- `double_value`: Double-precision float
- `string_value`: UTF-8 string
- `bytes_value`: Binary data

Example:
```protobuf
Value { int_value: 42 }
Value { bool_value: true }
Value { string_value: "hello" }
```

## Code Generation Commands

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

### C#
```bash
protoc --csharp_out=. hmi_protocol.proto
```

## Minimal Example Workflow

1. **Connection**: Web app connects to device
2. **Initialization**: Device sends initial configuration
3. **Interaction**: User interacts with UI → Command sent
4. **Response**: Device processes → Event sent back
5. **Updates**: Device sends periodic status/telemetry
6. **Heartbeats**: Both sides send periodic heartbeats

## Tips

✓ Always include `request_id` in commands for correlation  
✓ Use timestamps for debugging and ordering  
✓ Send heartbeats every 5-10 seconds  
✓ Validate input values before sending  
✓ Handle error responses gracefully  
✓ Use appropriate alert levels  
✓ Enable/disable components based on state  
✓ Send telemetry at regular intervals  
✓ Implement reconnection logic  
✓ Log all messages for debugging
