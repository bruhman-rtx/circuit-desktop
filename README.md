# Loom — desktop (beta)

**A shared board that you and Claude both read and write.** Six surfaces —
Spool (tasks), Sparks (ideas), Margin (notes), Cadence (calendar), Vault
(files) and Canvas — over one board file on your own disk. Claude connects
through an MCP bridge and edits the same board you're looking at; changes
appear live and every one is logged under Claude's name.

This is a **beta for Windows 10/11 (64-bit)**. No account, no server, no
telemetry — nothing leaves your machine.

## Download

Grab the latest from **[Releases →](../../releases/latest)**:

- **`Loom-…-setup.exe`** — the app (per-user install, no admin prompt)
- **`loom-….mcpb`** — the one-click Claude Desktop extension (optional; see below)

## ⚠️ Windows will warn you — and it's right to

The installer is **not code-signed**, so SmartScreen shows a blue *"Windows
protected your PC"* screen. To continue: click **More info**, then **Run
anyway**.

Don't take that on trust — **verify the hash first**. In PowerShell:

```powershell
Get-FileHash .\Loom-1.0.0-preview.1-setup.exe
```

It must match the SHA-256 in the Release notes. If it doesn't, don't run it.

## Connecting Claude

Loom brings its own MCP server — no Node, no repo, no build.

- **One click:** download the `.mcpb` from the Release and drop it on Claude
  Desktop's **Settings → Extensions**, or just double-click it. It asks for
  your Loom folder; the default is already correct.
- **By hand / for Claude Code:** open **Settings → Claude** in the app — it
  prints the exact config to paste, with your machine's paths already in it.

Claude then writes to the same board file you're looking at. Restart Claude
after connecting.

## Where your board lives

One plain-JSON file, in the open:

```
%USERPROFILE%\Documents\Loom\board.json
```

Loom writes it atomically and keeps a dated snapshot each day in
`Documents\Loom\backups`. It starts empty — no sample data to clear out.

## Known limits in this beta

- **Unsigned** — hence the SmartScreen warning above.
- **No auto-update** — to move to a newer build, download it and install over
  the top. Your board is untouched.
- **One machine** — no sync yet.
- **Reset** clears the board but leaves file attachments on disk; **Export**
  lists your files but doesn't bundle their bytes.

## Feedback

Found a bug or have a thought? Open an **[issue](../../issues/new)** — the more
specific ("I did X, expected Y, got Z"), the more useful.

---

*Loom is closed-source in this beta; this repo hosts the downloads and issue
tracker only.*
