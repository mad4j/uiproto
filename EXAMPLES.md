# Usage Examples

This document provides code examples demonstrating how to use the protocol in different programming languages.

## JavaScript Examples

### Setup
```bash
npm install protobufjs
pbjs -t static-module -w commonjs -o protocol.js protocol.proto
pbts -o protocol.d.ts protocol.js
```

### Example 1: Simple Request-Reply

```javascript
const protobuf = require('protobufjs');

// Load the protocol
const root = protobuf.loadSync('protocol.proto');
const Message = root.lookupType('uiproto.Message');
const MessageType = root.lookupEnum('uiproto.MessageType');

// Create a request
const request = {
  type: MessageType.values.REQUEST,
  request: {
    requestId: 1,
    command: 'get_temperature',
    parameters: [{
      name: 'sensor_id',
      value: { stringValue: 'sensor_1' }
    }],
    timestamp: Date.now()
  }
};

// Encode the message
const errMsg = Message.verify(request);
if (errMsg) throw Error(errMsg);
const buffer = Message.encode(request).finish();

// Send buffer over your transport (WebSocket, Serial, etc.)
// websocket.send(buffer);

// When receiving a reply
const reply = Message.decode(buffer);
console.log('Reply:', reply);
```

### Example 2: Request with Continuation

```javascript
// Create a request for a long-running operation
const calibrationRequest = {
  type: MessageType.values.REQUEST,
  request: {
    requestId: 42,
    command: 'start_calibration',
    parameters: [{
      name: 'mode',
      value: { stringValue: 'full' }
    }],
    timestamp: Date.now()
  }
};

// Send the request
const buffer = Message.encode(calibrationRequest).finish();
websocket.send(buffer);

// Handle the immediate reply
websocket.on('message', (data) => {
  const message = Message.decode(data);
  
  if (message.type === MessageType.values.REPLY) {
    const reply = message.reply;
    
    if (reply.requestId === 42) {
      if (reply.continuation) {
        console.log('Calibration started, waiting for completion...');
        // Keep listening for the notification
      } else {
        console.log('Calibration completed immediately:', reply);
      }
    }
  }
  
  if (message.type === MessageType.values.NOTIFICATION) {
    const notification = message.notification;
    
    if (notification.requestId === 42 && 
        notification.eventType === 'work_completed') {
      console.log('Calibration finished!');
      notification.parameters.forEach(param => {
        console.log(`${param.name}:`, param.value);
      });
    }
  }
});
```

### Example 3: Handling Notifications

```javascript
// Listen for autonomous notifications from the device
websocket.on('message', (data) => {
  const message = Message.decode(data);
  
  if (message.type === MessageType.values.NOTIFICATION) {
    const notification = message.notification;
    
    switch (notification.eventType) {
      case 'parameter_changed':
        console.log('Parameter changed:');
        notification.parameters.forEach(param => {
          console.log(`  ${param.name} = ${JSON.stringify(param.value)}`);
        });
        break;
        
      case 'error':
        console.error('Device error:', notification.parameters);
        break;
        
      case 'alarm':
        console.warn('Alarm triggered:', notification.parameters);
        break;
        
      default:
        console.log('Notification:', notification);
    }
  }
});
```

## C/C++ Examples (Embedded Device)

### Setup
```bash
protoc --cpp_out=. protocol.proto
# Link with -lprotobuf
```

### Example 1: Process Request and Send Reply

```cpp
#include "protocol.pb.h"
#include <iostream>

void handleRequest(const uint8_t* data, size_t length) {
    // Parse incoming message
    uiproto::Message requestMsg;
    if (!requestMsg.ParseFromArray(data, length)) {
        std::cerr << "Failed to parse request" << std::endl;
        return;
    }
    
    if (requestMsg.type() != uiproto::REQUEST) {
        return;
    }
    
    const auto& request = requestMsg.request();
    
    // Create reply
    uiproto::Message replyMsg;
    replyMsg.set_type(uiproto::REPLY);
    
    auto* reply = replyMsg.mutable_reply();
    reply->set_request_id(request.request_id());
    reply->set_continuation(false);
    reply->set_timestamp(getCurrentTimestamp());
    
    // Process the command
    if (request.command() == "get_temperature") {
        reply->set_success(true);
        reply->set_message("Temperature retrieved");
        
        auto* param = reply->add_parameters();
        param->set_name("temperature");
        param->mutable_value()->set_float_value(25.5f);
    } else {
        reply->set_success(false);
        reply->set_message("Unknown command");
    }
    
    // Serialize and send
    std::string buffer;
    replyMsg.SerializeToString(&buffer);
    sendData((const uint8_t*)buffer.data(), buffer.size());
}
```

### Example 2: Send Notification

```cpp
void sendParameterChangeNotification(const std::string& paramName, float value) {
    uiproto::Message notificationMsg;
    notificationMsg.set_type(uiproto::NOTIFICATION);
    
    auto* notification = notificationMsg.mutable_notification();
    notification->set_request_id(0); // Not related to any request
    notification->set_event_type("parameter_changed");
    notification->set_timestamp(getCurrentTimestamp());
    
    auto* param = notification->add_parameters();
    param->set_name(paramName);
    param->mutable_value()->set_float_value(value);
    
    // Serialize and send
    std::string buffer;
    notificationMsg.SerializeToString(&buffer);
    sendData((const uint8_t*)buffer.data(), buffer.size());
}
```

### Example 3: Handle Long-Running Operation

```cpp
// Global state for tracking ongoing operations
struct PendingOperation {
    uint32_t requestId;
    std::string operation;
};

void handleCalibrationRequest(const uiproto::Request& request) {
    // Send immediate reply with continuation flag
    uiproto::Message replyMsg;
    replyMsg.set_type(uiproto::REPLY);
    
    auto* reply = replyMsg.mutable_reply();
    reply->set_request_id(request.request_id());
    reply->set_success(true);
    reply->set_message("Calibration started");
    reply->set_continuation(true); // Important: signals that work continues
    reply->set_timestamp(getCurrentTimestamp());
    
    std::string buffer;
    replyMsg.SerializeToString(&buffer);
    sendData((const uint8_t*)buffer.data(), buffer.size());
    
    // Start the actual calibration in background
    startCalibrationAsync(request.request_id());
}

void onCalibrationComplete(uint32_t requestId, float calibrationValue) {
    // Send notification when work is complete
    uiproto::Message notificationMsg;
    notificationMsg.set_type(uiproto::NOTIFICATION);
    
    auto* notification = notificationMsg.mutable_notification();
    notification->set_request_id(requestId); // Reference original request
    notification->set_event_type("work_completed");
    notification->set_timestamp(getCurrentTimestamp());
    
    auto* statusParam = notification->add_parameters();
    statusParam->set_name("status");
    statusParam->mutable_value()->set_string_value("success");
    
    auto* valueParam = notification->add_parameters();
    valueParam->set_name("calibration_value");
    valueParam->mutable_value()->set_float_value(calibrationValue);
    
    std::string buffer;
    notificationMsg.SerializeToString(&buffer);
    sendData((const uint8_t*)buffer.data(), buffer.size());
}
```

## Python Examples

### Setup
```bash
protoc --python_out=. protocol.proto
```

### Example: Complete Communication Handler

```python
import protocol_pb2
from datetime import datetime

class ProtocolHandler:
    def __init__(self, transport):
        self.transport = transport
        self.pending_requests = {}
        
    def send_request(self, request_id, command, parameters):
        """Send a request to the embedded device"""
        msg = protocol_pb2.Message()
        msg.type = protocol_pb2.REQUEST
        
        request = msg.request
        request.request_id = request_id
        request.command = command
        request.timestamp = int(datetime.now().timestamp() * 1000)
        
        for name, value in parameters.items():
            param = request.parameters.add()
            param.name = name
            if isinstance(value, int):
                param.value.int_value = value
            elif isinstance(value, float):
                param.value.float_value = value
            elif isinstance(value, str):
                param.value.string_value = value
            elif isinstance(value, bool):
                param.value.bool_value = value
        
        # Send serialized message
        data = msg.SerializeToString()
        self.transport.send(data)
        
        # Track if continuation is expected
        self.pending_requests[request_id] = {'command': command}
        
    def handle_message(self, data):
        """Handle incoming message from embedded device"""
        msg = protocol_pb2.Message()
        msg.ParseFromString(data)
        
        if msg.type == protocol_pb2.REPLY:
            self.handle_reply(msg.reply)
        elif msg.type == protocol_pb2.NOTIFICATION:
            self.handle_notification(msg.notification)
            
    def handle_reply(self, reply):
        """Handle reply message"""
        request_id = reply.request_id
        
        if reply.success:
            print(f"Request {request_id} succeeded: {reply.message}")
            
            if reply.continuation:
                print(f"  Waiting for completion notification...")
                self.pending_requests[request_id]['waiting'] = True
            else:
                # Request completed immediately
                del self.pending_requests[request_id]
                
            # Process reply parameters
            for param in reply.parameters:
                print(f"  {param.name}: {self.get_param_value(param)}")
        else:
            print(f"Request {request_id} failed: {reply.message}")
            del self.pending_requests[request_id]
            
    def handle_notification(self, notification):
        """Handle notification message"""
        print(f"Notification: {notification.event_type}")
        
        if notification.request_id != 0:
            # Notification related to a previous request
            print(f"  Related to request {notification.request_id}")
            if notification.request_id in self.pending_requests:
                del self.pending_requests[notification.request_id]
        
        # Process notification parameters
        for param in notification.parameters:
            print(f"  {param.name}: {self.get_param_value(param)}")
            
    @staticmethod
    def get_param_value(param):
        """Extract value from parameter based on type"""
        which = param.value.WhichOneof('value')
        if which:
            return getattr(param.value, which)
        return None

# Usage example
if __name__ == '__main__':
    # Assuming you have a transport layer (e.g., serial, websocket)
    handler = ProtocolHandler(your_transport)
    
    # Send a request
    handler.send_request(1, 'get_temperature', {'sensor_id': 'sensor_1'})
    
    # Handle incoming data
    data = your_transport.receive()
    handler.handle_message(data)
```

## Transport Layer Examples

### WebSocket (JavaScript)

```javascript
const WebSocket = require('ws');
const protobuf = require('protobufjs');

const root = protobuf.loadSync('protocol.proto');
const Message = root.lookupType('uiproto.Message');

// Connect to embedded device
const ws = new WebSocket('ws://192.168.1.100:8080');

ws.on('open', () => {
  console.log('Connected to device');
  
  // Send a request
  const request = {
    type: 1, // REQUEST
    request: {
      requestId: 1,
      command: 'get_status',
      parameters: [],
      timestamp: Date.now()
    }
  };
  
  const buffer = Message.encode(request).finish();
  ws.send(buffer);
});

ws.on('message', (data) => {
  const message = Message.decode(new Uint8Array(data));
  console.log('Received:', message.toJSON());
});
```

### Serial Communication (Python with pySerial)

```python
import serial
import protocol_pb2

# Open serial port
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Send request
msg = protocol_pb2.Message()
msg.type = protocol_pb2.REQUEST
msg.request.request_id = 1
msg.request.command = "get_status"
msg.request.timestamp = int(time.time() * 1000)

data = msg.SerializeToString()
# Prefix with length for framing (example protocol)
length = len(data)
ser.write(length.to_bytes(4, 'little'))
ser.write(data)

# Read response
length_bytes = ser.read(4)
length = int.from_bytes(length_bytes, 'little')
data = ser.read(length)

reply_msg = protocol_pb2.Message()
reply_msg.ParseFromString(data)
print(f"Received: {reply_msg}")
```

## Best Practices

1. **Request ID Management**: Use unique, monotonically increasing request IDs
2. **Timeout Handling**: Implement timeouts for requests that may not receive replies
3. **Continuation Tracking**: Keep track of requests with continuation flag to match with later notifications
4. **Event Type Naming**: Use consistent, descriptive names for notification event types
5. **Error Handling**: Always check serialization/deserialization success
6. **Transport Framing**: Add length prefixes or delimiters for stream-based transports
7. **Timestamp Units**: Use milliseconds since epoch for consistency
8. **Parameter Naming**: Use clear, consistent parameter names across your system
