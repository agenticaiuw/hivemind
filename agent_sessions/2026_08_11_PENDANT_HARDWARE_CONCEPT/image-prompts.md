# Final image-generation prompts

## 1. Exterior / product outlook

Use case: product-mockup

Asset type: premium wearable industrial-design concept board

Primary request: Create a photorealistic product-design render of a tiny AI pendant/gadget based on a 34 mm diameter × 12.5 mm thick round enclosure. It should look like real jewelry rather than a development board. Show one large macro three-quarter front view, one smaller rear/side view, and a tasteful inset of an adult model wearing it on a fine chain so the scale is unmistakable.

Subject and geometry: a gently domed circular pendant with a compact integrated top bail, approximately the diameter of a small watch face. Warm-white satin ceramic-like PA12/polycarbonate body. A very thin champagne-gold PVD trim ring wraps most of the rim but stops at a subtle nonconductive RF window near the upper-right antenna sector. A precise diffused LED halo is integrated into a narrow front light-pipe channel, glowing softly in a cool cyan-to-violet gradient; it must look like a continuous optical halo, not exposed individual LEDs. One flush low-profile mechanical button on the left edge. One small tactile knurled champagne-gold scroll wheel/crown on the right edge. Tiny microphone aperture on the front, a discreet row of micro speaker perforations on the lower edge, no display. Rear view has four tiny flush gold magnetic charging contacts and one rear microphone mesh.

Style/medium: high-end photorealistic industrial-design visualization, manufacturable consumer-electronics detail, jewelry product photography, accurate material response.

Composition/framing: landscape design board, uncluttered; the main pendant fills about 60 percent of the canvas, the rear view and on-model inset are clearly secondary. Preserve the small 34 mm scale on the model.

Scene/backdrop: warm ivory-to-light-gray seamless studio background with a faint grounded shadow; the on-model inset uses neutral clothing and keeps the pendant unobstructed.

Lighting/mood: soft luxury studio lighting, controlled specular highlights on gold, gentle diffuse reflection on warm-white polymer, crisp silhouette.

Constraints: no screen; no logo; no text; no watermark. The case must be mostly nonmetallic so Bluetooth can radiate. Keep the front elegant and simple. The side controls must be ergonomically believable and low profile. Do not show internal electronics in this image.

Avoid: ESP32 boards, nRF development kits, USB-C jack, thumb-drive stick, exposed circuit board, large battery, smartwatch face, AirPods case, giant hockey-puck proportions, gemstones, ornate filigree, a continuous all-metal enclosure, exposed LED bulbs, Apple branding, extra buttons.

## 2. Dimension-aware exploded component breakdown

Use case: infographic-diagram

Asset type: landscape industrial-design exploded-view concept sheet

Primary request: Create a clean, technically credible 3D isometric exploded view of the same round AI pendant, separating the layers vertically along one axis while preserving true relative scale. It is a conceptual package study, not a manufactured CAD release. The housing envelope is 34 mm outer diameter × 12.5 mm nominal thickness; maximum fallback envelope is 36 mm × 14 mm. Use crisp leader lines, millimeter dimension arrows, a small 10 mm scale bar, and highly legible labels.

Exploded stack, front to rear: 1.0 mm warm-white PA12/PC front cap with thin champagne-gold partial trim and a translucent circular LED light-pipe; 13 mm diameter × 2.8 mm micro speaker in a molded acoustic cup; 32 mm diameter × 0.8 mm four-layer circular green PCB; a 30 mm diameter × 4.7 mm round protected LiPo battery; a 10 × 10 × 4.0 mm rectangular LRA haptic actuator in a lateral recessed pocket rather than stacked on the battery; 1.0 mm rear cap with four gold magnetic pogo charging contacts. Show a left-edge low-profile button mechanism and a right-edge 5 mm micro scroll encoder/crown integrated into the midframe.

Place these parts on the PCB at plausible relative sizes and label them exactly: "nRF5340 BLE SoC — 7 × 7 mm"; "nPM1304 PMIC — 5 × 5 mm"; "W25N02KV 256 MB flash — 8 × 6 mm"; "BMI270 IMU — 2.5 × 3.0 × 0.83 mm"; "2× PDM mics — 3.5 × 2.65 × 0.98 mm"; "MAX98357A amp — 3 × 3 × 0.75 mm"; "DRV2605L haptic driver — 3 × 3 mm"; "BLE antenna — 3.2 × 1.6 × 1.3 mm"; "antenna keep-out — 6.5 × 6.5 mm"; "round LiPo — Ø30 × 4.7 mm, ~330 mAh — supplier TBD"; "LRA — 10 × 10 × 4.0 mm"; "micro speaker — Ø13 × 2.8 mm"; "PCB — Ø32 × 0.8 mm"; "enclosure — Ø34 × 12.5 mm nominal"; "magnetic pogo charging — MPN TBD"; "button + scroll input — concept / TBD"; and "Tight conceptual stack — mechanical/DFM validation required".

Style/medium: premium engineering cutaway visualization, realistic 3D CAD-rendered parts with a restrained technical infographic overlay, white background, high contrast, clear hierarchy.

Composition/framing: landscape, exploded object centered slightly left; component callouts arranged in two clean columns without crossing; small side-profile stack gauge at lower right showing the 12.5 mm nominal thickness. All parts fit within the 34 mm round silhouette when projected together. The 30 mm battery is visibly almost as wide as the 32 mm PCB. Tiny ICs must look tiny relative to the board. The speaker and LRA occupy lateral pockets and do not unrealistically stack full-depth over the battery.

Materials/colors: warm-white shell, champagne-gold trim and pogo contacts, green PCB with gold pads, silver/black IC packages, silver-black battery pouch, dark micro speaker, translucent pale-cyan LED light-pipe.

Constraints: technically plausible relative sizes; readable millimeter labels; no logo; no watermark. Show the BLE antenna at the board edge with a visibly clear keep-out region, away from the battery, speaker magnet, LRA, and gold trim. The LED ring is an optical diffuser/light-pipe, not a ring of large addressable LEDs. The flash is an onboard IC, not a USB thumb drive.

Avoid: ESP32, nRF9160 development kit, separate bulky Bluetooth breakout, USB-C, microSD breakout board, literal USB flash drive, rectangular hobby LiPo, 18 mm speaker, SK6812/NeoPixel packages, all-metal RF enclosure, overlapping components, false scale, extra unlabeled boards, illegible decorative text.

## 2a. Mechanical correction applied to the exploded view

Use case: precise-object-edit

Asset type: corrected dimension-aware industrial-design exploded-view concept sheet

Input image: the first generated exploded view is the edit target.

Primary request: Preserve the overall graphic style, white background, isometric exploded presentation, warm-white/champagne-gold housing, circular PCB, all PCB parts and their exact labels, leader-line clarity, and technical polish. Correct only the mechanical stack so it no longer falsely places the 10 × 10 × 4.0 mm LRA beside the Ø30 mm battery inside the same nearly 31 mm cavity.

Required geometry change: make the Ø30 × 4.7 mm round LiPo its own full-width layer centered below the PCB. Move the 10 × 10 × 4.0 mm rectangular LRA upward into the front mechatronic/acoustic layer, side-by-side with the Ø13 × 2.8 mm speaker and above the PCB. The speaker and LRA must both fit within the projected Ø32 mm PCB circle and must not overlap each other or the BLE antenna keep-out.

Required overall dimension change: update the enclosure callout and side-profile gauge to "Ø34 × 14 mm fallback with current 10 × 10 × 4 mm LRA". Add a concise secondary note: "12.5 mm target requires smaller ~8 × 8 × 3.2 mm LRA + final CAD validation". Keep the 34 mm outer diameter. Keep "Tight conceptual stack — mechanical/DFM validation required".

Constraints: change only the LRA layer, related midframe pocket, total-thickness callouts, and the necessary vertical spacing. Keep the battery diameter visibly almost equal to the PCB diameter. Do not add ESP32, nRF9160, USB-C, a microSD breakout, a literal thumb drive, rectangular battery, or extra boards. No watermark.
