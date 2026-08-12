# Image QA

## Final exterior

- File: `outputs/pendant-exterior-white-gold-v1.png`
- Format and size: PNG, 1536 × 1024.
- Visual checks passed: warm-white nonmetallic body; champagne-gold partial trim; continuous diffused LED halo; flush left button; right knurled scroll crown; tiny front mic; lower speaker ports; rear mic; four rear magnetic contacts; fine-chain bail; human-worn scale view; no screen; no exposed circuit board; no ESP32; no USB-C; no logo or watermark.

## Final exploded breakdown

- File: `outputs/pendant-exploded-dimensioned-v2.png`
- Format and size: PNG, 1536 × 1024.
- Visual checks passed: Ø34 enclosure; explicit 14 mm fallback and 12.5 mm stretch note; Ø32 PCB; Ø30 battery as its own full-width layer; 13 mm speaker and 10 × 10 mm LRA together in the upper mechatronic layer; four pogo contacts; side controls; scale bar; dimension gauge; nRF5340, nPM1304, NAND flash, BMI270, microphones, audio amp, haptic driver, BLE antenna, and keep-out callouts; no ESP32, nRF9160 DK, USB-C, microSD breakout, or rectangular hobby battery.
- Engineering caveat: this is a high-fidelity packaging concept, not routed PCB/CAD/thermal/acoustic/RF validation. The 14 mm stack and all lateral clearances must still be rebuilt in parametric CAD before enclosure tooling or PCB release.

## Generation method

- Both base assets were produced with the built-in image-generation tool.
- The technical breakdown received one built-in targeted edit after visual inspection exposed an impossible same-plane placement of the Ø30 mm battery and 10 × 10 mm LRA.
- The original first-pass breakdown is retained as `outputs/pendant-exploded-34mm-draft-v1.png` for traceability and is not the recommended final.
