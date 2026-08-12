# Circuit — desktop (beta)

**A shared board that you and Claude both read and write.** Six surfaces —
Spool (tasks), Sparks (ideas), Margin (notes), Cadence (calendar), Vault
(files) and Canvas — over one board file on your own disk. Claude connects
through an MCP bridge and edits the same board you're looking at; changes
appear live and every one is logged under Claude's name.

This is a **beta for Windows 10/11 (64-bit) and macOS 11+** (Apple Silicon or
Intel). No account, no server, no telemetry — nothing leaves your machine.

## Download

Grab the latest from **[Releases →](../../releases/latest)**:

**Windows** — **`Circuit-…-setup.exe`** (per-user install, no admin prompt)

**macOS** — pick your chip:
- **`Circuit-…-arm64.dmg`** — Apple Silicon (M1/M2/M3/M4)
- **`Circuit-…-x64.dmg`** — Intel
- the matching **`.zip`** is the same app, if you'd rather unzip-and-drag than mount a disk image

**Both** — **`circuit-….mcpb`**, the one-click Claude Desktop extension (optional; see below)

## ⚠️ Your OS will warn you — and it's right to

Neither build is code-signed, so the first launch is stopped on both platforms.
Don't take that on trust — **verify the hash against the Release notes first**,
then allow it.

**Windows** — SmartScreen shows a blue *"Windows protected your PC"* screen.
Click **More info**, then **Run anyway**.

```powershell
Get-FileHash .\Circuit-1.0.0-preview.2-setup.exe
```

**macOS** — Gatekeeper says the app *"can't be opened"* or *"is damaged"*
(because it isn't notarized, not because anything's wrong). **Right-click
Circuit.app → Open → Open** — that records a one-time exception, and every
launch after is a normal double-click. If a downloaded `.dmg` still refuses:

```bash
shasum -a 256 ~/Downloads/Circuit-1.0.0-preview.2-arm64.dmg   # verify
xattr -dr com.apple.quarantine /Applications/Circuit.app       # clear the download quarantine
```

If a hash doesn't match the Release notes, don't run it.

## Connecting Claude

Circuit brings its own MCP server — no Node, no repo, no build.

- **One click:** download the `.mcpb` from the Release and drop it on Claude
  Desktop's **Settings → Extensions**, or just double-click it. It asks for
  your Circuit folder; the default is already correct.
- **By hand / for Claude Code:** open **Settings → Claude** in the app — it
  prints the exact config to paste, with your machine's paths already in it.

Claude then writes to the same board file you're looking at. Restart Claude
after connecting.

## Where your board lives

One plain-JSON file, in the open:

```
Windows   %USERPROFILE%\Documents\Circuit\board.json
macOS     ~/Documents/Circuit/board.json
```

Circuit writes it atomically and keeps a dated snapshot each day in the
`backups` folder beside it. It starts empty — no sample data to clear out.

## Known limits in this beta

- **Unsigned** — hence the gatekeeper warnings above (SmartScreen on Windows,
  Gatekeeper on macOS).
- **No auto-update** — to move to a newer build, download it and install over
  the top. Your board is untouched.
- **One machine** — no sync yet.
- **Reset** clears the board but leaves file attachments on disk; **Export**
  lists your files but doesn't bundle their bytes.

## Feedback

Found a bug or have a thought? Open an **[issue](../../issues/new)** — the more
specific ("I did X, expected Y, got Z"), the more useful.

---

*Circuit is closed-source in this beta; this repo hosts the downloads and issue
tracker only.*
