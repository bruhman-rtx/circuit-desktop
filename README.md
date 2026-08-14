# Circuit

Circuit is a desktop task board that you and Claude both read and write — one shared board file on your own disk.

## Download

Get everything from the **[latest release](https://github.com/bruhman-rtx/circuit-desktop/releases/latest)**. Every file carries the version in its name, shown here as `<version>`:

- **Windows** — `Circuit-<version>-setup.exe`
- **macOS (Apple Silicon)** — `Circuit-<version>-arm64.dmg` (or `-arm64.zip`)
- **macOS (Intel)** — `Circuit-<version>-x64.dmg` (or `-x64.zip`)
- **Claude Desktop kit** — `circuit-<version>.mcpb` (the one-click extension that connects Claude to your board)

Once installed, Circuit updates itself: Windows downloads new versions in the background and offers **Restart now**, and macOS shows a notice with a link.

## Install

**Windows**

1. Run the `-setup.exe`.
2. If SmartScreen shows "Windows protected your PC", click **More info**, then **Run anyway**.

**macOS**

1. Open the `.dmg` and drag **Circuit** to Applications.
2. First launch: right-click **Circuit.app** → **Open** → **Open** (the build is unsigned, so a normal double-click is blocked the first time).
3. If it still refuses: `xattr -dr com.apple.quarantine /Applications/Circuit.app`

**Claude Desktop kit**

1. Double-click the `.mcpb`, or drag it into Claude Desktop → **Settings → Extensions**.
2. Choose your board folder when asked (default: `Documents/Circuit`).
3. Restart Claude Desktop. Claude can now read and write your board through its full set of tools.

## Verify

Check your download against `SHA256SUMS.txt` from the release page:

- Windows: `Get-FileHash .\Circuit-<version>-setup.exe`
- macOS: `shasum -a 256 ~/Downloads/Circuit-<version>-arm64.dmg`

## Use

1. Launch Circuit. Your board lives at `Documents/Circuit/board.json`.
2. Work across the six surfaces: **Spool** (tasks), **Sparks**, **Margin**, **Cadence**, **Vault**, and **Canvas**.
3. Claude's edits appear live on the board and are attributed to Claude in the **Ledger**.
