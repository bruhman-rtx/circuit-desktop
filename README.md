# Circuit

Circuit is a desktop task board that you and Claude both read and write — one shared board file on your own disk.

> ### 🧪 This is a free public beta — and it stays free, forever.
>
> The build you download here is the open beta of Circuit. It's complete and fully usable, and it will remain **free and publicly available on this page for good** — install it, keep it, use it as long as you like. The beta is released under the [MIT License](LICENSE).
>
> **Circuit v1.0 will be a paid release.** From here on, every new feature, improvement, and fix lands in v1 — this beta is a fixed snapshot, not the ongoing product. Grab it now and the beta is yours for free; everything that comes *next* lives in the paid v1.

## Download

Get everything from the **[latest release](https://github.com/bruhman-rtx/circuit-desktop/releases/latest)**. Every file carries the version in its name, shown here as `<version>`:

- **Windows** — `Circuit-<version>-setup.exe`
- **macOS (Apple Silicon)** — `Circuit-<version>-arm64.dmg` (or `-arm64.zip`)
- **macOS (Intel)** — `Circuit-<version>-x64.dmg` (or `-x64.zip`)
- **Claude Desktop kit** — `circuit-<version>.mcpb` (the one-click extension that connects Claude to your board)

Once installed, Circuit updates itself: Windows downloads new versions in the background and offers **Restart now**, and macOS shows a notice with a link to this page.

## What talks to what

Straight answers, because a desktop app deserves them:

- **Your board stays on your disk.** `Documents/Circuit/board.json` is a local file. Circuit never uploads it.
- **The beta needs a free account.** Signing up, signing in, and password reset talk to Circuit's beta server (`api-production-4657b.up.railway.app`) — that is how beta access is managed. The account carries your sign-in, not your board.
- **Update checks** ask GitHub for the latest release.
- **Bug reports are opt-in and visible.** If you send one, it uploads your description and the screenshot region you cropped yourself — nothing is captured until you press the button.
- **Analytics ship switched off.** The build contains self-hosted analytics code; it is disabled in this beta.

## Verify, then install

The beta builds are **not code-signed** (signing lands with v1), so Windows and macOS both warn on first launch. That warning means *unsigned*, not *unsafe* — but don't take our word for it: check your download against `SHA256SUMS.txt` from the release page first, and only then tell the OS to proceed.

- Windows: `Get-FileHash .\Circuit-<version>-setup.exe`
- macOS: `shasum -a 256 ~/Downloads/Circuit-<version>-arm64.dmg`

**Windows**

1. Run the `-setup.exe`.
2. SmartScreen shows "Windows protected your PC" because the installer is unsigned. If your hash matched above, click **More info**, then **Run anyway**.

**macOS**

1. Open the `.dmg` and drag **Circuit** to Applications.
2. First launch: right-click **Circuit.app** → **Open** → **Open** (unsigned builds are blocked on a normal double-click the first time).
3. If it still refuses: `xattr -dr com.apple.quarantine /Applications/Circuit.app`

**Claude Desktop kit**

1. Double-click the `.mcpb`, or drag it into Claude Desktop → **Settings → Extensions**.
2. Choose your board folder when asked (default: `Documents/Circuit`).
3. Restart Claude Desktop. Claude can now read and write your board through its full set of tools.

## Use

1. Launch Circuit. Your board lives at `Documents/Circuit/board.json`.
2. Work across the six surfaces: **Spool** (tasks), **Sparks**, **Margin**, **Cadence**, **Vault**, and **Canvas**.
3. Claude's edits appear live on the board and are attributed to Claude in the **Ledger**.

## Licence & source

The beta is [MIT-licensed](LICENSE). This repository hosts downloads and release notes; Circuit's application source is private while the beta runs.
