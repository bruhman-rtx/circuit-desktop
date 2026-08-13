# Circuit

Circuit is a desktop task board that you and Claude both read and write — one shared board file on your own disk.

## Download

Get everything from the **[v1.0.0-preview.2 release](https://github.com/bruhman-rtx/circuit-desktop/releases/tag/v1.0.0-preview.2)**:

- **Windows** — `Circuit-1.0.0-preview.2-setup.exe`
- **macOS (Apple Silicon)** — `Circuit-1.0.0-preview.2-arm64.dmg` (or `-arm64.zip`)
- **macOS (Intel)** — `Circuit-1.0.0-preview.2-x64.dmg` (or `-x64.zip`)
- **Claude Desktop kit** — `circuit-1.0.0-preview.2.mcpb` (the one-click extension that connects Claude to your board)

## Install

**Windows**

1. Run `Circuit-1.0.0-preview.2-setup.exe`.
2. If SmartScreen shows "Windows protected your PC", click **More info**, then **Run anyway**.

**macOS**

1. Open the `.dmg` and drag **Circuit** to Applications.
2. First launch: right-click **Circuit.app** → **Open** → **Open** (the build is unsigned, so a normal double-click is blocked the first time).
3. If it still refuses: `xattr -dr com.apple.quarantine /Applications/Circuit.app`

**Claude Desktop kit**

1. Double-click `circuit-1.0.0-preview.2.mcpb`, or drag it into Claude Desktop → **Settings → Extensions**.
2. Choose your board folder when asked (default: `Documents/Circuit`).
3. Restart Claude Desktop. Claude can now read and write your board through 55 tools.

## Verify

Check your download against `SHA256SUMS.txt` from the release page:

- Windows: `Get-FileHash .\Circuit-1.0.0-preview.2-setup.exe`
- macOS: `shasum -a 256 ~/Downloads/Circuit-1.0.0-preview.2-arm64.dmg`

## Use

1. Launch Circuit. Your board lives at `Documents/Circuit/board.json`.
2. Work across the six surfaces: **Spool** (tasks), **Sparks**, **Margin**, **Cadence**, **Vault**, and **Canvas**.
3. Claude's edits appear live on the board and are attributed to Claude in the **Ledger**.
