# HMI Protocol Architecture

## Protocol Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (Web UI, Device Logic, Business Rules)                      │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────────┐
│                  HMI Protocol Layer                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Commands   │  │    Events    │  │  Heartbeats  │     │
│  │  (Web→Dev)   │  │  (Dev→Web)   │  │ (Bidirect.)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  Message Envelope (ID, Timestamp, Payload)                   │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────────┐
│              Protocol Buffer Serialization                   │
│              (Binary Encoding/Decoding)                      │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────────┐
│                   Transport Layer                            │
│  (WebSocket, HTTP, MQTT, gRPC, TCP/IP)                      │
└─────────────────────────────────────────────────────────────┘
```

## Message Flow

### Initialization Sequence

```
Web App                                Device
   │                                      │
   │◄────── InitialConfiguration ────────│
   │         (Device Status,              │
   │          UI Layout,                  │
   │          Components)                 │
   │                                      │
```

### Command-Response Pattern

```
Web App                                Device
   │                                      │
   │────────── Command ─────────────────►│
   │         (Button Press,               │
   │          Slider Change,              │
   │          etc.)                       │
   │                                      │
   │◄────── Event ───────────────────────│
   │         (Status Update,              │
   │          Component Update,           │
   │          or Error)                   │
   │                                      │
```

### Event Streaming Pattern

```
Web App                                Device
   │                                      │
   │◄──── Status Update ─────────────────│
   │                                      │
   │◄──── Telemetry Data ────────────────│
   │                                      │
   │◄──── Alert ─────────────────────────│
   │                                      │
   │◄──── Component Update ──────────────│
   │                                      │
```

### Heartbeat Pattern

```
Web App                                Device
   │                                      │
   │────────── Heartbeat ────────────────►│
   │         (seq: 1)                     │
   │                                      │
   │◄────── Heartbeat ────────────────────│
   │         (seq: 1)                     │
   │                                      │
   │────────── Heartbeat ────────────────►│
   │         (seq: 2)                     │
   │                                      │
   │◄────── Heartbeat ────────────────────│
   │         (seq: 2)                     │
   │                                      │
```

## Message Structure

```
Message
├── message_id: string
├── timestamp: Timestamp
└── payload: (one of)
    ├── Command
    │   ├── request_id: string
    │   └── command_type: (one of)
    │       ├── button_press
    │       ├── slider_change
    │       ├── switch_toggle
    │       ├── text_input
    │       ├── selector_change
    │       ├── configuration_update
    │       ├── get_status
    │       └── get_configuration
    │
    ├── Event
    │   ├── event_id: string
    │   └── event_type: (one of)
    │       ├── status_update
    │       ├── alert
    │       ├── configuration_response
    │       ├── component_update
    │       ├── telemetry
    │       └── error_response
    │
    └── Heartbeat
        ├── source: string
        └── sequence_number: int64
```

## UI Component Hierarchy

```
UI Widgets
├── Input Widgets
│   ├── Button
│   ├── Slider
│   ├── Switch
│   ├── TextField
│   └── Selector
│
└── Display Widgets
    ├── Label
    ├── NumericDisplay
    └── ProgressBar
```

## State Machine

### Device States

```
                  ┌─────────────┐
                  │   OFFLINE   │
                  └──────┬──────┘
                         │ connect
                         ▼
                  ┌─────────────┐
             ┌────┤INITIALIZING │
             │    └──────┬──────┘
             │           │ ready
             │           ▼
             │    ┌─────────────┐
      error  │    │    READY    │◄─────┐
             │    └──────┬──────┘      │
             │           │ start       │ stop
             │           ▼             │
             │    ┌─────────────┐      │
             └───►│   RUNNING   │──────┘
             │    └──────┬──────┘
             │           │ error
             │           ▼
             │    ┌─────────────┐
             └────┤    ERROR    │
             │    └─────────────┘
             │           │ maintenance
             │           ▼
             │    ┌─────────────┐
             └────┤ MAINTENANCE │
                  └─────────────┘
```

## Data Flow Patterns

### Real-time Monitoring

```
┌──────────┐                          ┌──────────┐
│  Sensor  │                          │ Web UI   │
└────┬─────┘                          └────▲─────┘
     │                                     │
     │ Read Value                          │
     ▼                                     │
┌──────────────┐                           │
│    Device    │───── Telemetry Event ─────┤
│    Logic     │                           │
└──────────────┘                           │
     │                                     │
     │ Update Component                    │
     ▼                                     │
┌──────────────┐                           │
│  Component   │─── Component Update ──────┘
│    State     │
└──────────────┘
```

### User Interaction

```
┌──────────┐                          ┌──────────┐
│ Web UI   │                          │  Device  │
└────┬─────┘                          └────▲─────┘
     │                                     │
     │ User Action                         │
     ▼                                     │
┌──────────────┐                           │
│   Command    │────────────────────►┌─────┴──────┐
│   Message    │                     │  Process   │
└──────────────┘                     │  Command   │
                                     └─────┬──────┘
                                           │
                                           ▼
                                     ┌──────────────┐
                                     │  Update HW   │
                                     └─────┬────────┘
                                           │
     ┌─────────────────────────────────────┘
     │
     ▼
┌──────────────┐                     ┌──────────────┐
│    Event     │◄────────────────────│  Send Event  │
│   Message    │                     └──────────────┘
└──────────────┘
     │
     ▼
┌──────────┐
│ Update   │
│ Web UI   │
└──────────┘
```

## Component Lifecycle

```
Component Creation
       │
       ▼
┌──────────────┐
│  Definition  │ (ID, Type, Properties)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Registration │ (Device sends ComponentUpdate)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Active     │◄─────┐
│   State      │      │ Updates
└──────┬───────┘      │
       │              │
       ▼              │
┌──────────────┐      │
│ User/Device  │──────┘
│  Interaction │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Removal    │
└──────────────┘
```

## Error Handling Flow

```
                    ┌────────────┐
                    │  Command   │
                    │  Received  │
                    └─────┬──────┘
                          │
                    ┌─────▼──────┐
                    │  Validate  │
                    │  Command   │
                    └─────┬──────┘
                          │
                    ┌─────▼─────┐
                    │  Valid?   │
                    └─────┬─────┘
                          │
              ┌───────────┴───────────┐
              │                       │
          Yes │                       │ No
              ▼                       ▼
       ┌──────────────┐        ┌──────────────┐
       │   Execute    │        │     Send     │
       │   Command    │        │    Error     │
       └──────┬───────┘        │   Response   │
              │                └──────────────┘
       ┌──────▼───────┐
       │  Success?    │
       └──────┬───────┘
              │
    ┌─────────┴─────────┐
    │                   │
Yes │                   │ No
    ▼                   ▼
┌─────────┐       ┌──────────────┐
│  Send   │       │     Send     │
│  Event  │       │    Error     │
└─────────┘       │   Response   │
                  └──────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────┐
│         Application Security Layer              │
│  - Input validation                             │
│  - Business logic validation                    │
│  - Rate limiting                                │
└─────────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────────┐
│       Authentication & Authorization            │
│  - User authentication                          │
│  - Component access control                     │
│  - Command authorization                        │
└─────────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────────┐
│            HMI Protocol Layer                   │
│  - Message structure validation                 │
│  - Type safety                                  │
└─────────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────────┐
│          Transport Security Layer               │
│  - TLS/SSL encryption                           │
│  - Certificate validation                       │
└─────────────────────────────────────────────────┘
```

## Deployment Scenarios

### Scenario 1: WebSocket Communication
```
┌──────────────┐         WebSocket          ┌──────────────┐
│  Web Browser │◄──────────────────────────►│    Device    │
│  JavaScript  │   (Binary Protobuf msgs)   │  Embedded SW │
└──────────────┘                            └──────────────┘
```

### Scenario 2: HTTP REST API
```
┌──────────────┐      HTTP POST/GET         ┌──────────────┐
│  Web/Mobile  │◄──────────────────────────►│   Gateway    │
│     App      │   (Protobuf in body)       │   Server     │
└──────────────┘                            └──────┬───────┘
                                                   │
                                                   │ Internal
                                                   │ Protocol
                                                   ▼
                                            ┌──────────────┐
                                            │   Devices    │
                                            └──────────────┘
```

### Scenario 3: MQTT Pub/Sub
```
┌──────────────┐                            ┌──────────────┐
│  Web App     │─────┐                 ┌────│   Device 1   │
└──────────────┘     │                 │    └──────────────┘
                     │    Subscribe    │
┌──────────────┐     ▼     Publish     ▼    ┌──────────────┐
│  Mobile App  │──►┌──────────────┐◄────────│   Device 2   │
└──────────────┘   │ MQTT Broker  │         └──────────────┘
                   │  (Topics)    │
┌──────────────┐   └──────────────┘         ┌──────────────┐
│   Monitor    │─────┘                 └────│   Device N   │
└──────────────┘                            └──────────────┘
```

### Scenario 4: gRPC Streaming
```
┌──────────────┐     gRPC Bidir Stream      ┌──────────────┐
│    Client    │◄══════════════════════════►│  gRPC Server │
│              │  (Protobuf messages)       │  + Device    │
│  - React UI  │                            │   Manager    │
│  - Mobile    │                            │              │
└──────────────┘                            └──────────────┘
```

## Performance Characteristics

### Message Size (typical)

```
Simple Command (Button Press):     50-60 bytes
Slider Update:                     55-65 bytes
Status Update:                     85-150 bytes
Telemetry Point:                   100-120 bytes
Component Update:                  70-90 bytes
Alert Message:                     80-100 bytes
Heartbeat:                         35-40 bytes
```

### Throughput Estimates

```
Transport      │ Messages/sec │ Latency   │ Use Case
───────────────┼──────────────┼───────────┼──────────────────
WebSocket      │ 1000-5000    │ 1-10ms    │ Real-time HMI
HTTP REST      │ 100-500      │ 10-100ms  │ Status polling
MQTT           │ 1000-10000   │ 5-50ms    │ IoT sensors
gRPC           │ 5000-50000   │ 1-5ms     │ High performance
```

## Integration Patterns

### Pattern 1: Direct Integration
```
Web App ◄──► Device
```

### Pattern 2: Gateway Pattern
```
Web App ◄──► Gateway ◄──► Multiple Devices
```

### Pattern 3: Cloud Pattern
```
Web App ◄──► Cloud Service ◄──► Edge Gateway ◄──► Devices
```

### Pattern 4: Hybrid Pattern
```
Web App ◄──► Local Gateway ◄──► Devices
    │                │
    └────────────────┴──────► Cloud (Optional Backup/Analytics)
```

## Extensibility Points

1. **New Command Types**: Add to `Command.command_type` oneof
2. **New Event Types**: Add to `Event.event_type` oneof
3. **New Widget Types**: Add to `ComponentUpdate.component` oneof
4. **New Value Types**: Add to `Value.value_type` oneof
5. **Custom Fields**: Use protobuf extensions or map fields
6. **Versioning**: Add version field to Message envelope

## Best Practices Summary

1. **Always** include request_id for correlation
2. **Always** include timestamps
3. **Send** heartbeats every 5-10 seconds
4. **Validate** input on both sides
5. **Handle** errors gracefully
6. **Use** appropriate alert levels
7. **Enable/disable** components based on state
8. **Buffer** messages during disconnections
9. **Log** all critical operations
10. **Version** your protocol implementations
