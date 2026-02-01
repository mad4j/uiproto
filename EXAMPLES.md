# HMI Protocol Examples

This document provides practical examples of using the HMI protocol in various scenarios.

## Example 1: Simple Temperature Controller

This example demonstrates a basic temperature control system with a temperature display, setpoint slider, and enable/disable switch.

### Device Initial Configuration

When the web app connects, the device sends:

```protobuf
Message {
  message_id: "init_001"
  timestamp: { milliseconds: 1706820526000 }
  event: {
    event_id: "evt_init_001"
    status_update: {
      device_status: {
        device_id: "TEMP_CTRL_001"
        device_name: "Temperature Controller"
        state: DEVICE_READY
        firmware_version: "v1.0.0"
        uptime_seconds: 0
      }
    }
  }
}
```

### UI Components Setup

The device sends component updates for each UI element:

```protobuf
// Temperature Display
Message {
  message_id: "comp_001"
  event: {
    event_id: "evt_comp_001"
    component_update: {
      numeric_display: {
        id: { id: "current_temp" }
        label: "Current Temperature"
        value: 22.5
        unit: "°C"
        decimal_places: 1
      }
    }
  }
}

// Setpoint Slider
Message {
  message_id: "comp_002"
  event: {
    event_id: "evt_comp_002"
    component_update: {
      slider: {
        id: { id: "temp_setpoint" }
        label: "Target Temperature"
        min_value: 15.0
        max_value: 30.0
        current_value: 22.0
        step: 0.5
        enabled: true
      }
    }
  }
}

// Enable Switch
Message {
  message_id: "comp_003"
  event: {
    event_id: "evt_comp_003"
    component_update: {
      switch: {
        id: { id: "heater_enable" }
        label: "Heater Enabled"
        state: false
        enabled: true
      }
    }
  }
}
```

### User Changes Setpoint

User drags the slider to 25°C:

```protobuf
Message {
  message_id: "cmd_001"
  timestamp: { milliseconds: 1706820530000 }
  command: {
    request_id: "req_setpoint_001"
    slider_change: {
      slider_id: { id: "temp_setpoint" }
      new_value: 25.0
    }
  }
}
```

Device acknowledges and updates:

```protobuf
Message {
  message_id: "evt_001"
  event: {
    event_id: "evt_ack_001"
    component_update: {
      slider: {
        id: { id: "temp_setpoint" }
        label: "Target Temperature"
        min_value: 15.0
        max_value: 30.0
        current_value: 25.0
        step: 0.5
        enabled: true
      }
    }
  }
}
```

### User Enables Heater

```protobuf
Message {
  message_id: "cmd_002"
  command: {
    request_id: "req_enable_001"
    switch_toggle: {
      switch_id: { id: "heater_enable" }
      new_state: true
    }
  }
}
```

### Device Sends Periodic Temperature Updates

Every second, the device sends updated temperature:

```protobuf
Message {
  message_id: "telem_001"
  event: {
    event_id: "evt_telem_001"
    telemetry: {
      points: [
        {
          metric_name: "temperature"
          value: { double_value: 23.2 }
          timestamp: { milliseconds: 1706820531000 }
          tags: { "sensor": "main", "unit": "celsius" }
        }
      ]
    }
  }
}
```

And updates the display:

```protobuf
Message {
  message_id: "disp_001"
  event: {
    event_id: "evt_disp_001"
    component_update: {
      numeric_display: {
        id: { id: "current_temp" }
        label: "Current Temperature"
        value: 23.2
        unit: "°C"
        decimal_places: 1
      }
    }
  }
}
```

## Example 2: Industrial Process Control

This example shows a more complex industrial control panel with multiple sections.

### UI Layout

```protobuf
InitialConfiguration {
  device_status: {
    device_id: "PROCESS_001"
    device_name: "Chemical Process Controller"
    state: DEVICE_RUNNING
    firmware_version: "v3.2.1"
    uptime_seconds: 432000
  }
  ui_layout: {
    layout_id: "main_layout"
    name: "Process Control Panel"
    sections: [
      {
        section_id: "status"
        title: "System Status"
        components: [
          { component_id: { id: "process_state" }, row: 0, column: 0, width: 2, height: 1 },
          { component_id: { id: "uptime" }, row: 1, column: 0, width: 2, height: 1 }
        ]
      },
      {
        section_id: "controls"
        title: "Process Controls"
        components: [
          { component_id: { id: "start_btn" }, row: 0, column: 0, width: 1, height: 1 },
          { component_id: { id: "stop_btn" }, row: 0, column: 1, width: 1, height: 1 },
          { component_id: { id: "emergency_stop" }, row: 0, column: 2, width: 1, height: 1 }
        ]
      },
      {
        section_id: "parameters"
        title: "Process Parameters"
        components: [
          { component_id: { id: "flow_rate" }, row: 0, column: 0, width: 2, height: 1 },
          { component_id: { id: "pressure" }, row: 1, column: 0, width: 2, height: 1 },
          { component_id: { id: "temperature" }, row: 2, column: 0, width: 2, height: 1 }
        ]
      },
      {
        section_id: "setpoints"
        title: "Setpoints"
        components: [
          { component_id: { id: "flow_setpoint" }, row: 0, column: 0, width: 2, height: 1 },
          { component_id: { id: "pressure_setpoint" }, row: 1, column: 0, width: 2, height: 1 }
        ]
      }
    ]
  }
}
```

### Emergency Stop Button Press

```protobuf
Message {
  message_id: "cmd_emergency"
  timestamp: { milliseconds: 1706820600000 }
  command: {
    request_id: "req_emerg_001"
    button_press: {
      button_id: { id: "emergency_stop" }
    }
  }
}
```

Device responds immediately:

```protobuf
// Update device state
Message {
  message_id: "evt_emergency_001"
  event: {
    event_id: "evt_emerg_001"
    status_update: {
      device_status: {
        device_id: "PROCESS_001"
        state: DEVICE_ERROR
        firmware_version: "v3.2.1"
        uptime_seconds: 432010
      }
    }
  }
}

// Send critical alert
Message {
  message_id: "evt_emergency_002"
  event: {
    event_id: "evt_emerg_002"
    alert: {
      level: ALERT_CRITICAL
      message: "EMERGENCY STOP ACTIVATED"
      code: "ESTOP_001"
      related_component: { id: "emergency_stop" }
      requires_acknowledgment: true
    }
  }
}

// Disable all controls
Message {
  message_id: "evt_emergency_003"
  event: {
    event_id: "evt_emerg_003"
    component_update: {
      slider: {
        id: { id: "flow_setpoint" }
        label: "Flow Rate Setpoint"
        min_value: 0
        max_value: 100
        current_value: 50
        step: 1
        enabled: false  // Disabled during emergency stop
      }
    }
  }
}
```

## Example 3: Configuration Management

### Request Current Configuration

```protobuf
Message {
  message_id: "cmd_getconfig"
  command: {
    request_id: "req_config_001"
    get_configuration: {
      keys: []  // Empty array = get all configuration
    }
  }
}
```

### Device Sends Configuration

```protobuf
Message {
  message_id: "evt_config_001"
  event: {
    event_id: "evt_cfg_001"
    configuration_response: {
      request_id: "req_config_001"
      success: true
      parameters: [
        { key: "sampling_rate_hz", value: { int_value: 100 } },
        { key: "enable_logging", value: { bool_value: true } },
        { key: "log_path", value: { string_value: "/var/log/hmi/" } },
        { key: "max_temperature", value: { double_value: 85.5 } },
        { key: "alert_email", value: { string_value: "admin@example.com" } }
      ]
      error_message: ""
    }
  }
}
```

### Update Configuration

```protobuf
Message {
  message_id: "cmd_updateconfig"
  command: {
    request_id: "req_config_002"
    configuration_update: {
      parameters: [
        { key: "sampling_rate_hz", value: { int_value: 200 } },
        { key: "max_temperature", value: { double_value: 90.0 } }
      ]
    }
  }
}
```

### Configuration Update Response

Success:
```protobuf
Message {
  message_id: "evt_config_002"
  event: {
    event_id: "evt_cfg_002"
    configuration_response: {
      request_id: "req_config_002"
      success: true
      parameters: [
        { key: "sampling_rate_hz", value: { int_value: 200 } },
        { key: "max_temperature", value: { double_value: 90.0 } }
      ]
      error_message: ""
    }
  }
}
```

Failure:
```protobuf
Message {
  message_id: "evt_config_003"
  event: {
    event_id: "evt_cfg_003"
    configuration_response: {
      request_id: "req_config_002"
      success: false
      parameters: []
      error_message: "Invalid sampling rate: must be between 1 and 1000 Hz"
    }
  }
}
```

## Example 4: Multi-Level Alerts

### Information Alert

```protobuf
Message {
  message_id: "evt_info_001"
  event: {
    event_id: "evt_alert_001"
    alert: {
      level: ALERT_INFO
      message: "Calibration cycle completed successfully"
      code: "INFO_CAL_001"
      requires_acknowledgment: false
    }
  }
}
```

### Warning Alert

```protobuf
Message {
  message_id: "evt_warn_001"
  event: {
    event_id: "evt_alert_002"
    alert: {
      level: ALERT_WARNING
      message: "Temperature approaching upper threshold (85°C)"
      code: "WARN_TEMP_001"
      related_component: { id: "temp_sensor_1" }
      requires_acknowledgment: true
    }
  }
}
```

### Error Alert

```protobuf
Message {
  message_id: "evt_err_001"
  event: {
    event_id: "evt_alert_003"
    alert: {
      level: ALERT_ERROR
      message: "Sensor communication failure"
      code: "ERR_COMM_001"
      related_component: { id: "pressure_sensor" }
      requires_acknowledgment: true
    }
  }
}
```

### Critical Alert

```protobuf
Message {
  message_id: "evt_crit_001"
  event: {
    event_id: "evt_alert_004"
    alert: {
      level: ALERT_CRITICAL
      message: "Temperature exceeded critical threshold (>95°C) - System shutdown initiated"
      code: "CRIT_TEMP_001"
      related_component: { id: "temp_sensor_1" }
      requires_acknowledgment: true
    }
  }
}
```

## Example 5: Progress Bar for Long Operations

### Start Long Operation

User initiates firmware update:

```protobuf
Message {
  message_id: "cmd_update"
  command: {
    request_id: "req_update_001"
    button_press: {
      button_id: { id: "start_update_btn" }
    }
  }
}
```

### Device Shows Progress Bar

```protobuf
// Initial progress bar
Message {
  message_id: "evt_prog_001"
  event: {
    event_id: "evt_upd_001"
    component_update: {
      progress_bar: {
        id: { id: "update_progress" }
        label: "Downloading firmware..."
        current: 0
        max: 100
        indeterminate: false
      }
    }
  }
}

// Progress update
Message {
  message_id: "evt_prog_002"
  event: {
    event_id: "evt_upd_002"
    component_update: {
      progress_bar: {
        id: { id: "update_progress" }
        label: "Downloading firmware..."
        current: 45
        max: 100
        indeterminate: false
      }
    }
  }
}

// Completion
Message {
  message_id: "evt_prog_003"
  event: {
    event_id: "evt_upd_003"
    component_update: {
      progress_bar: {
        id: { id: "update_progress" }
        label: "Update complete!"
        current: 100
        max: 100
        indeterminate: false
      }
    }
  }
}
```

## Example 6: Form with Multiple Inputs

### User Login Form

```protobuf
// Username field
Message {
  event: {
    component_update: {
      text_field: {
        id: { id: "username" }
        label: "Username"
        value: ""
        placeholder: "Enter username"
        enabled: true
        password: false
      }
    }
  }
}

// Password field
Message {
  event: {
    component_update: {
      text_field: {
        id: { id: "password" }
        label: "Password"
        value: ""
        placeholder: "Enter password"
        enabled: true
        password: true
      }
    }
  }
}

// Role selector
Message {
  event: {
    component_update: {
      selector: {
        id: { id: "role" }
        label: "Role"
        options: ["Operator", "Supervisor", "Administrator"]
        selected_index: 0
        enabled: true
      }
    }
  }
}

// Login button
Message {
  event: {
    component_update: {
      button: {
        id: { id: "login_btn" }
        label: "Login"
        enabled: true
        icon: "login"
      }
    }
  }
}
```

### User Submits Form

```protobuf
// Username input
Message {
  command: {
    request_id: "req_login_001"
    text_input: {
      text_field_id: { id: "username" }
      new_value: "john.doe"
    }
  }
}

// Password input
Message {
  command: {
    request_id: "req_login_002"
    text_input: {
      text_field_id: { id: "password" }
      new_value: "securepassword123"
    }
  }
}

// Role selection
Message {
  command: {
    request_id: "req_login_003"
    selector_change: {
      selector_id: { id: "role" }
      selected_index: 1  // Supervisor
    }
  }
}

// Submit button press
Message {
  command: {
    request_id: "req_login_004"
    button_press: {
      button_id: { id: "login_btn" }
    }
  }
}
```

### Authentication Response

Success:
```protobuf
Message {
  event: {
    event_id: "evt_login_001"
    alert: {
      level: ALERT_INFO
      message: "Login successful. Welcome, John Doe!"
      code: "AUTH_SUCCESS"
      requires_acknowledgment: false
    }
  }
}
```

Failure:
```protobuf
Message {
  event: {
    event_id: "evt_login_002"
    error_response: {
      request_id: "req_login_004"
      code: PERMISSION_DENIED
      message: "Invalid credentials"
      details: "Username or password is incorrect"
    }
  }
}
```

## Example 7: Heartbeat Exchange

### Web App Heartbeat

```protobuf
Message {
  message_id: "hb_webapp_001"
  timestamp: { milliseconds: 1706820600000 }
  heartbeat: {
    source: "webapp"
    sequence_number: 1
  }
}

Message {
  message_id: "hb_webapp_002"
  timestamp: { milliseconds: 1706820605000 }
  heartbeat: {
    source: "webapp"
    sequence_number: 2
  }
}
```

### Device Heartbeat

```protobuf
Message {
  message_id: "hb_device_001"
  timestamp: { milliseconds: 1706820601000 }
  heartbeat: {
    source: "device"
    sequence_number: 1
  }
}

Message {
  message_id: "hb_device_002"
  timestamp: { milliseconds: 1706820606000 }
  heartbeat: {
    source: "device"
    sequence_number: 2
  }
}
```

## Best Practices from Examples

1. **Always include request_id** in commands for correlation with responses
2. **Use appropriate alert levels** to indicate severity
3. **Disable components** when they shouldn't be interactable
4. **Send periodic updates** for real-time values using telemetry
5. **Use progress bars** for long-running operations
6. **Group related components** using UI sections
7. **Validate input** on both client and server sides
8. **Send heartbeats regularly** to detect connection issues
9. **Acknowledge critical alerts** to ensure they were seen
10. **Use descriptive component IDs** for easier debugging

## Testing Scenarios

To test this protocol implementation:

1. **Connection Test**: Verify initial configuration is sent correctly
2. **Command Test**: Send each command type and verify response
3. **Event Test**: Trigger each event type and verify receipt
4. **Error Handling**: Test invalid values and component IDs
5. **Concurrent Operations**: Send multiple commands simultaneously
6. **Disconnection**: Test reconnection and state synchronization
7. **Heartbeat**: Verify both sides detect missing heartbeats
8. **Large Data**: Test with many components (stress test)
9. **Rapid Updates**: High-frequency telemetry data
10. **Alert Acknowledgment**: Verify critical alert workflow
