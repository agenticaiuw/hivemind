# Orchestrator log
- Copied pptx to source.pptx, unzipped to src/ (33 slides, 16:9 12192000x6858000 EMU).
- Exported reference.pdf via PowerPoint AppleScript; rasterized to reference/slide-NN.png (80dpi).
- Delegated build + parity verification to slides_builder (frontend-gpt-sol).
- slides_builder on frontend-gpt-sol failed (model_not_found); relaunched as general-purpose/opus.
- slides_builder2 cut off by proxy error (ERR_PROXY_TUNNEL) mid-build; resumed via SendMessage on user's 'try again'.
- Owner stopped slides_builder2 (deck good). Orchestrator applied dark bg, white text, Inter; backup at deck.before-dark.html. Committed deck + assets + converter.
- Fixed 7 clipped text boxes (s3,8,11,14,15,16,18; Inter wider than Aptos) with JS autofit; all 17 images verified loading. Published to OneDrive: 'AAI Hardware Team Meeting.html' + '_files/' next to the pptx.
