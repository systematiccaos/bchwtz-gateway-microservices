# Use Cases and Testing
## Binding and releasing of tags
* Should be tested with at least 10 gateways and 10 tags
* Do gateways successfully release tags based on rssi?
* How long do tags stay connected to one gateway at a time if rssi is very similar?
* What unexpected behavior does occur on manual interactions with the tags?
* What happens if a tag was streaming before and is now used for other operation?
* How does the heartbeat influence the tags binding and releasing?

## Restarting of parts of the gateway and crash testing
* What happens if we shut down parts of different gateways?
* What happens if we massively scale up transcoding? Does this influence the api?
