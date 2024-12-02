# Handling roaming locking state
## Gateway-local statemachine
Gateways have to implement a state machine where they store their communication state for each tag. As we cannot connect to a tag that is bound in communication, we have to wait for it to leave the communication to be able to perform roaming actions.
```mermaid
stateDiagram-v2 
    direction TB
    
    [*] --> Unlocked: Initialization
    
    Unlocked --> Locked: Gateway starts communication
    Locked --> Unlocked: Communication lost or ended

    state "Tag" as Tag {
        direction LR
        [*] --> Unlocked
        Unlocked --> Locked: Communication Established
        Locked --> Unlocked: Communication Ended
    }
    
    state "Gateway" as Gateway {
        direction LR
        [*] --> Idle
        Idle --> Communicating: Starts Communication
        Communicating --> Idle: Stops or Loses Communication
    }
    
    Gateway --> Tag: Sends Communication Signal
    Tag --> Gateway: Acknowledges Signal

```

## Platform-managed shadow states
Shadows implement a field where they store their communication state. As we cannot connect to a tag that is bound in communication, we have to wait for it to leave the communication to be able to perform roaming actions.
```mermaid
sequenceDiagram
    autonumber
    participant Gateway
    participant Tag
    participant Platform

    Gateway->>Tag: Start Communication
    Tag->>Gateway: Acknowledge Communication
    Gateway->>Platform: Update Tag Shadow to "Locked" and add CurrentGatewayAdress
    Platform-->>Gateway: Acknowledge Update

    Gateway->>Tag: End Communication
    Tag->>Gateway: Acknowledge End
    Gateway->>Platform: Update Tag Shadow to "Unlocked"
    Platform-->>Gateway: Acknowledge Update

    Gateway->>Tag: Communication Lost/Aborted
    Tag->>Gateway: Timeout or Error Detected
    Gateway->>Platform: Update Tag Shadow to "Unlocked"
    Platform-->>Gateway: Acknowledge Update
```
## Roaming management
Roaming is handled by sorting a list of gateways by their RSSI-values for each tagshadow and storing the one with the highest RSSI to the field NearestGateway.
```mermaid
    sequenceDiagram
    autonumber
    participant Gateway1
    participant Gateway2
    participant Gateway3
    participant Tag
    participant Platform

    Note over Gateway1,Gateway3: Gateways measure RSSI of the Tag
    Gateway1->>Platform: Send RSSI of Tag
    Gateway2->>Platform: Send RSSI of Tag
    Gateway3->>Platform: Send RSSI of Tag

    Platform->>Platform: Evaluate RSSI values
    Platform->>Platform: Select Gateway with strongest RSSI
    Platform->>TagShadow: Update "NearestGateway" in Tag's shadow

    Note over Platform: NearestGateway field updated
    Platform-->>Gateway2: Notify "NearestGateway"

    Note over Platform,Tag: BLE GATT command process starts
    Platform->>Tag: Send BLE GATT command to shadow
    Tag->>Platform: Acknowledge BLE GATT command

    Platform->>Gateway2: Forward GATT command to NearestGateway
    Gateway2->>Tag: Connect to Tag and execute GATT command
    Tag->>Gateway2: Respond to GATT command
    Gateway2->>Platform: Send GATT command response
    Platform->>TagShadow: Update shadow with command result
```