# Pendant visual concept decisions

## Selected concept

- **Architecture:** current repository v2: nRF5340 BLE, phone relay, onboard NAND flash, onboard motion/audio/haptic hardware. ESP32 and the nRF9160 development kit are excluded from the wearable visual.
- **Envelope:** the exterior explores the Ø34 × 12.5 mm visual target. The corrected exploded study uses an honest Ø34 × 14 mm fallback with the currently specified 10 × 10 × 4 mm LRA. Reaching 12.5 mm likely requires an approximately 8 × 8 × 3.2 mm actuator and final CAD validation.
- **Appearance:** warm-white satin nonconductive enclosure, partial champagne-gold decorative ring, discreet RF window, fine-chain bail.
- **Interaction:** a flush left mechanical button and a right 5 mm scroll crown are presented as a concept because the current v2 input mechanism is still unresolved.
- **Light:** the requested ring is represented as a thin optical light-pipe driven by low-power micro RGB emitters, not a power-hungry ring of 5 × 5 mm SK6812 packages.
- **Storage:** “flash drive” is represented by the specified W25N02KV 256 MB onboard NAND flash IC. The previously bought 64 GB microSD card can remain a bench/prototype medium, but its 31.85 × 25.4 mm breakout board is too large for this 34 mm pendant.
- **Bluetooth:** nRF5340 already contains BLE; the current v2 product does not require a second BLE module. Phone relay is also how private audio reaches earbuds in this architecture.
- **Battery:** the visualization uses the v2 semi-custom Ø30 × 4.7 mm protected LiPo target. It is a requirement, not a confirmed purchased part.
- **Accuracy boundary:** chip and module dimensions come from the repository specification/datasheets. The enclosure, round battery supplier, magnetic pogo part, side controls, acoustics, and final component placement still require mechanical and DFM validation. The generated technical image preserves relative-size intent but is not a CAD file or fabrication drawing.
