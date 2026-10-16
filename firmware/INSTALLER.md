# FM-XY installer

Use **Felucca's original package builder, Web MIDI installer, backup and recovery code**. Do not replace its flash protocol.

CI stages a self-contained installer from the compiled package using `web/make_site.py`, but does **not** upload or deploy any firmware.

Before release:

1. Full upstream + FM-XY tests pass, including UI/layout, editor compatibility and CPU budgets.
2. Complete ROOT/TYPE keyboard behavior is implemented and tested in **native C**.
3. Real FM1 tests pass: playback latency, 8-voice load, save/restore, USB interruption, upgrade and recovery.
4. Release includes an independently checked SHA-256, original licences, clear warning, backup instructions and a tested return-to-stock path.

Only after all four gates, publish an FM-XY firmware package and enable the installer. Until then, [the website's installer stays disabled](https://taorminator.github.io/FM-XY/installer/).
