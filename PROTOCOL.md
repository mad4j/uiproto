# Communication Protocol Documentation

## Overview

This protocol defines a communication interface between an embedded device and a JavaScript HMI (Human-Machine Interface) application using Protocol Buffers (protobuf).

## Supported Communication Scenarios

### 1. Request-Reply (Standard Pattern)

The JavaScript application sends a Request to the embedded device, which processes it and sends back a Reply immediately with the result.

**Flow:**
```
JavaScript HMI  -->  [Request]  -->  Embedded Device
JavaScript HMI  <--  [Reply]    <--  Embedded Device
```

**Example Use Cases:**
- Get parameter values (e.g., temperature, pressure)
- Set simple parameters
- Query device status

**Example:**
```javascript
// JavaScript HMI sends request
{
  type: MESSAGE_TYPE.REQUEST,
  payload: {
    request: {
      request_id: 1,
      command: "get_parameter",
      parameters: [{ name: "temperature", value: null }],
      timestamp: Date.now()
    }
  }
}

// Embedded device sends reply
{
  type: MESSAGE_TYPE.REPLY,
  payload: {
    reply: {
      request_id: 1,
      success: true,
      message: "Parameter retrieved",
      parameters: [{ name: "temperature", value: { float_value: 25.5 } }],
      continuation: false,
      timestamp: Date.now()
    }
  }
}
```

### 2. Notification (One-way Message)

The embedded device sends a Notification to the JavaScript application without expecting a response. This is used for asynchronous events, status changes, or alerts.

**Flow:**
```
JavaScript HMI  <--  [Notification]  <--  Embedded Device
```

**Example Use Cases:**
- Sensor value changed
- Error occurred
- Device status changed
- Alert triggered

**Example:**
```javascript
// Embedded device sends notification
{
  type: MESSAGE_TYPE.NOTIFICATION,
  payload: {
    notification: {
      request_id: 0,  // Not related to any request
      event_type: "parameter_changed",
      parameters: [
        { name: "temperature", value: { float_value: 26.0 } },
        { name: "alarm", value: { bool_value: true } }
      ],
      timestamp: Date.now()
    }
  }
}
```

### 3. Request-Reply with Continuation

The JavaScript application sends a Request to the embedded device. The device acknowledges the request immediately with a Reply (continuation=true), indicating that the work has started but not completed. When the work is actually finished, the device sends a Notification.

**Flow:**
```
JavaScript HMI  -->  [Request]              -->  Embedded Device
JavaScript HMI  <--  [Reply (continuation)] <--  Embedded Device
                     ... work in progress ...
JavaScript HMI  <--  [Notification]         <--  Embedded Device
```

**Example Use Cases:**
- Long-running operations (e.g., calibration, data acquisition)
- File transfers
- Complex calculations
- Operations that require waiting for external events

**Example:**
```javascript
// JavaScript HMI sends request
{
  type: MESSAGE_TYPE.REQUEST,
  payload: {
    request: {
      request_id: 42,
      command: "start_calibration",
      parameters: [{ name: "mode", value: { string_value: "full" } }],
      timestamp: Date.now()
    }
  }
}

// Embedded device sends immediate reply with continuation flag
{
  type: MESSAGE_TYPE.REPLY,
  payload: {
    reply: {
      request_id: 42,
      success: true,
      message: "Calibration started",
      parameters: [],
      continuation: true,  // Indicates that a notification will follow
      timestamp: Date.now()
    }
  }
}

// ... calibration in progress ...

// Embedded device sends notification when work is complete
{
  type: MESSAGE_TYPE.NOTIFICATION,
  payload: {
    notification: {
      request_id: 42,  // References the original request
      event_type: "work_completed",
      parameters: [
        { name: "status", value: { string_value: "success" } },
        { name: "calibration_value", value: { float_value: 1.025 } }
      ],
      timestamp: Date.now()
    }
  }
}
```

## Message Structure

### Message Envelope
All messages are wrapped in a `Message` envelope that identifies the message type and contains the payload.

### Request
- `request_id`: Unique identifier for tracking the request
- `command`: String identifying the operation to perform
- `parameters`: Array of name-value pairs
- `timestamp`: When the request was created

### Reply
- `request_id`: References the original request
- `success`: Boolean indicating success or failure
- `message`: Optional status or error message
- `parameters`: Response data
- `continuation`: Boolean flag indicating if a notification will follow
- `timestamp`: When the reply was created

### Notification
- `request_id`: Optional reference to a related request (0 if not related)
- `event_type`: String describing the type of notification
- `parameters`: Event data
- `timestamp`: When the notification was created

## Parameter Types

The protocol supports multiple parameter value types:
- `int_value`: 32-bit signed integer
- `uint_value`: 32-bit unsigned integer
- `float_value`: 32-bit floating point
- `double_value`: 64-bit floating point
- `bool_value`: Boolean
- `string_value`: String
- `bytes_value`: Binary data

## Implementation Guidelines

### For JavaScript HMI Application:
1. Generate unique `request_id` for each request
2. Handle replies by matching `request_id`
3. When receiving a reply with `continuation=true`, expect a notification with the same `request_id`
4. Listen for notifications continuously
5. Implement timeout mechanisms for requests that may not receive a reply

### For Embedded Device:
1. Process incoming requests and respond with matching `request_id`
2. Set `continuation=true` in replies when the operation will complete asynchronously
3. Send notifications with the original `request_id` when work is complete
4. Send notifications for autonomous events (with `request_id=0`)
5. Include meaningful `event_type` strings for easy filtering

## Error Handling

When an error occurs, the embedded device should send a Reply with:
- `success=false`
- `message` containing error description
- `continuation=false` (unless the error is about starting the work, and notification will still come)

Example:
```javascript
{
  type: MESSAGE_TYPE.REPLY,
  payload: {
    reply: {
      request_id: 99,
      success: false,
      message: "Invalid parameter: temperature out of range",
      parameters: [],
      continuation: false,
      timestamp: Date.now()
    }
  }
}
```

## Building the Protocol

To generate code from the protobuf definition:

### For JavaScript:
```bash
npm install protobufjs
protoc --js_out=import_style=commonjs,binary:. protocol.proto
```

Or using protobufjs:
```bash
pbjs -t static-module -w commonjs -o protocol.js protocol.proto
pbts -o protocol.d.ts protocol.js
```

### For C/C++ (Embedded Device):
```bash
protoc --cpp_out=. protocol.proto
```

### For Python:
```bash
protoc --python_out=. protocol.proto
```

## Transport Layer

This protocol definition is transport-agnostic and can be used over:
- WebSocket
- Serial communication (UART, USB)
- TCP/IP sockets
- Message queues (MQTT, etc.)

The protobuf messages should be serialized to binary format before transmission and deserialized upon reception.
