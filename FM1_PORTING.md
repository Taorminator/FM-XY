# FM-XY firmware porting plan

The current browser demo at `docs/try/index.html` is a JavaScript/Web Audio simulator; it **cannot** be installed on the FM1. The user interface and music logic must be ported to the actual firmware.

1. Fork [Felucca](https://github.com/hugelton/Felucca) as the genuine C/firmware starting point, preserving its history, license, bundled notices, build scripts and tests.
2. Reproduce the unmodified Felucca build with the supported JieLi pi32v2 toolchain and required AC79 SDK files. See [BUILDING.md](https://github.com/hugelton/Felucca/blob/main/BUILDING.md).
3. Build Felucca's WASM browser emulator from the C sources; test baseline latency, voice scheduling, memory limits and sample behavior.
4. Port FM-XY's 240x240 screen drawing, consistent track/preset header, theme selection, and physical button/encoder mappings. Keep rendering bounded.
5. Port chord suggestion/voicings, four-track workflow, 16-step pattern logic, automation and conservative eight-voice limits. Prefer existing Felucca audio/DSP and step scheduler rather than replicating independent Web Audio approximations.
6. For 808/909 kits, DX7 SysEx and future iPhone sampling, trace each actual source file and license. Sampling via [ELI7VH/Felucca](https://github.com/ELI7VH/felucca) is a V2 investigation, not present in V1.
7. Run upstream regression tests, host sanitizer tests, latency/CPU/memory tests and physical FM1 long-duration playback/recording tests. Validate complete device backup and recovery on test hardware.
8. Only then build a verified `.fwsc` release, publish its SHA-256 and activate a real webinstaller based on Felucca's tested mechanisms.

No firmware is currently available. The install page must remain disabled until hardware testing is completed.
