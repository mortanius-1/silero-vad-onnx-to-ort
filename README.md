# Silero VAD: onnx to ort automated conversion 

This repository automatically tracks the official [snakers4/silero-vad](https://github.com/snakers4/silero-vad) repository. Every week an automation downloads the latest `silero_vad.onnx` model file, optimises and compiles it into the `.ort` format, and publishes a new release tagged as **`[Origin Tag] ORT Build`** for deployment on Mobile (*arm*) devices.

*Disclaimer: This project is an automated compilation project and is not officially affiliated with the core Silero VAD development team. All credit for the voice activity models belongs to [snakers4](https://github.com/snakers4).*