# uiproto
Communication protocol for responsive UI

## Overview

This repository defines a Protocol Buffers (protobuf) based communication protocol between embedded devices and JavaScript HMI (Human-Machine Interface) applications.

## Features

The protocol supports three communication patterns:

1. **Request-Reply**: Standard synchronous request-response pattern
2. **Notification**: Asynchronous one-way messages from device to UI
3. **Request-Reply with Continuation**: Immediate acknowledgment with deferred completion notification

## Files

- `protocol.proto` - Protocol Buffers schema definition
- `PROTOCOL.md` - Comprehensive protocol documentation with examples

## Quick Start

### View the Protocol Definition
See `protocol.proto` for the complete protobuf schema.

### Read the Documentation
See `PROTOCOL.md` for detailed documentation including:
- Communication scenarios with flow diagrams
- Message structure explanations
- Usage examples for all three patterns
- Implementation guidelines
- Error handling
- Code generation instructions

## Communication Scenarios

### 1. Request-Reply
```
JavaScript HMI  -->  [Request]  -->  Embedded Device
JavaScript HMI  <--  [Reply]    <--  Embedded Device
```

### 2. Notification
```
JavaScript HMI  <--  [Notification]  <--  Embedded Device
```

### 3. Request-Reply with Continuation
```
JavaScript HMI  -->  [Request]              -->  Embedded Device
JavaScript HMI  <--  [Reply (continuation)] <--  Embedded Device
                     ... work in progress ...
JavaScript HMI  <--  [Notification]         <--  Embedded Device
```

## Generate Code

### For JavaScript
```bash
npm install protobufjs
pbjs -t static-module -w commonjs -o protocol.js protocol.proto
pbts -o protocol.d.ts protocol.js
```

### For C/C++ (Embedded)
```bash
protoc --cpp_out=. protocol.proto
```

### For Python
```bash
protoc --python_out=. protocol.proto
```

## License

See LICENSE file for details.
