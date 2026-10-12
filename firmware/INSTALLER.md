# FM-XY installation workflow (not yet released)

FM-XY uses **Felucca's own installer architecture and package tooling**. No replacement flash protocol is being developed.

Upstream: [Felucca BUILDING.md](https://github.com/hugelton/Felucca/blob/main/BUILDING.md) · [web/make_site.py](https://github.com/hugelton/Felucca/blob/main/web/make_site.py) · [fm1pkg_make.py](https://github.com/hugelton/Felucca/blob/main/tools/fm1pkg_make.py).

## Build and staging (future)
1. Apply the approved FM-XY changes in a history-preserving Felucca fork and build it using the pinned, verified JieLi toolchain and AC79 SDK dependencies.
2. Run the complete upstream tests, budget checks and UI-render lint. Compare audio and timing with the original Felucca build.
3. Produce the application, OTA loader and firmware package with Felucca's normal build script. Confirm product/loader markers, app size, hash and release licenses.
4. Use Felucca's `web/make_site.py` to stage a self-contained installer with its backup and restoration UI.
5. Adapt brand/metadata only after source testing; display firmware identity, exact SHA-256 and explicit user consent. Reuse upstream source and license notices.
6. Test disconnected USB, mismatched device, power loss, partial write, corrupted firmware file and recovery on sacrificial FM1 test hardware.
7. Publish the verified firmware as a GitHub Release, alongside checksums, attribution, flashing instructions and backup/recovery instructions.
8. Only then replace the disabled status page at `docs/installer/index.html` with the verified installer.

## Safety rules
- Never use another firmware's binary renamed to FM-XY.
- The prototype HTML is not firmware and is not suitable for flashing.
- Never flash hardware without a validated recovery plan and tested backup.
- The present draft PR intentionally contains neither an installable `.fwsc` nor an enabled Web MIDI flash button.
