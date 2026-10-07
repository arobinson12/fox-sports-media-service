# Fox Sports Media Service - CodeMender CI/CD & IDE Integration

This repository demonstrates the end-to-end **Google CodeMender (CM)** developer lifecycle for **Fox Sports Broadcast & Digital Media**.

It pairs **local ambient on-save IDE security scans** with an **automated GitHub Actions CI/CD deployment guardrail** powered by **Gemini 3.8 Flash** via Google Cloud Workload Identity Federation (WIF).

---

## 🏈 Architecture Overview

```
                      +------------------------------------------+
                      |         Fox Sports Developer             |
                      |          (VS Code on macOS)              |
                      +--------------------+---------------------+
                                           |
                    Cmd + S (Save)         | Local git push
                           v               v
            +--------------------+   +------------------------------------+
            | cm find on save    |   | GitHub Pull Request                |
            | (gemini-3.8-flash) |   +-----------------+------------------+
            +----------+---------+                     |
                       |                               v
                       v             +------------------------------------+
            +--------------------+   | GitHub Actions CI Guardrail        |
            | .sarif Diagnostics |   | - Keyless WIF (GCP)                |
            | Inline Squiggles   |   | - cm find --diff (Delta Scan)      |
            | Problems Panel     |   | - Security Gate (--fail-on)        |
            +--------------------+   +-----------------+------------------+
                                                       |
                                           Blocked or Approved?
                                          /                    \
                               (Vulnerabilities Found)    (Clean / Fixed)
                                        v                        v
                            ❌ Block Pull Request Merge    ✅ Approved to Merge
```

---

## 🔍 The Highlight Service Code

Located in `src/fox_sports_highlights.py`:
* **`export_game_clip()`**: Clips live broadcast streams using `ffmpeg` for on-air replays.
  * *Vulnerability:* **OS Command Injection (CWE-78)** via unsanitized clip parameters.
* **`get_highlights_by_player()`**: Queries highlight metadata for the Fox Sports app.
  * *Vulnerability:* **SQL Injection (CWE-89)** via raw string formatting.

---

## 🛠️ Local Developer Experience (VS Code)

1. Open this repository in VS Code:
   ```bash
   code /Users/ahmadrobinson/Documents/fox-sports-media-service
   ```
2. Open `src/fox_sports_highlights.py`.
3. Press **`Cmd + S`** (`Ctrl + S`):
   * CodeMender automatically triggers in the background using `gemini-3.8-flash`.
   * Findings populate the **Problems Panel** (`Cmd + Shift + M`) and display red squiggles directly inline.
4. Autonomous Fix with `cm fix`:
   ```bash
   cm fix <finding-id>
   ```
   CodeMender synthesizes a validated, idiomatic patch and offers an interactive `git diff` for approval.

---

## 🚀 GitHub Actions CI/CD Guardrail

The workflow at `.github/workflows/codemender-gate.yml` implements enterprise best practices from `codemenderandgh.md`:
* **Keyless Authentication:** Workload Identity Federation (WIF) with zero service account keys.
* **Dynamic CLI Caching:** Restores cached `cm` binary in seconds instead of vendoring large binaries in git.
* **Delta PR Auditing:** Uses `cm find --diff origin/main` to only audit modified lines and 1-hop callers, keeping PR reviews blazing fast.
* **Hard Enforcement:** Blocks PR merge with a non-zero exit code if `CRITICAL` or `HIGH` vulnerabilities are found.
* **Rich GitHub Surfaces:** Uploads SARIF results directly to GitHub's **Security -> Code Scanning** tab and writes a dashboard summary to `$GITHUB_STEP_SUMMARY`.
