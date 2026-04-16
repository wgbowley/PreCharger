# LT-SPICE
- Simulation does not currently work because the gate driver SPICE model has hidden references to net 0. Hence when the VSSS can't floating up with the mosfet source.

### Improvements needed
- Replace the gate driver model with one that doesn't have hidden assumptions or you a different topology like a high side MOSFET.