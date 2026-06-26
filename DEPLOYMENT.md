# Taka Register — Deployment & Release Guide

How the apps and this website are built, hosted, and updated.

## Overview

A single **public** repo hosts the downloadable binaries for every platform as release assets.
App *source* lives in separate private repos; only the built binaries are published publicly.

| Piece | Repo | Visibility | Role |
|-------|------|-----------|------|
| Website (this repo) | `skp9699/takaregister.in` | public | GitHub Pages site at `www.takaregister.in` (`CNAME`). Hosts `index.html`, `version.json`, `faq/`. |
| Windows app source | *(private)* | private | Builds `TakaRegister.exe`. |
| Android app source | `skp9699/takaregister-mobile` | private | Flutter source. Builds `TakaRegister-mobile.apk`. |
| **Downloads (all platforms)** | `skp9699/takaregister-downloads` | **public** | Release-only host. Each `vX.Y.Z` release carries both `TakaRegister.exe` and `TakaRegister-mobile.apk`. |

> Replaces the older per-platform host repo `taka-register` (EXE only), which can be deleted
> once `takaregister-downloads` is publishing.

### Download links (on the website)

`index.html` points both download buttons at the public downloads repo using the
`releases/latest/download/<asset>` URL, which always resolves to the newest published release:

- Windows: `https://github.com/skp9699/takaregister-downloads/releases/latest/download/TakaRegister.exe`
- Android: `https://github.com/skp9699/takaregister-downloads/releases/latest/download/TakaRegister-mobile.apk`

> The downloads repo **must be public**, otherwise these URLs return 404 for anonymous visitors.

### In-app update check

The desktop app polls `https://takaregister.in/version.json` and compares `version` against the
installed build. When a newer version is found it points the user at `download_url`. `faq/faq_version.json`
works the same way for the in-app FAQ. Bump `version.json` here **after** publishing a new release so
existing installs notice the update.

---

## One-time setup: the public downloads repo

The session token used by automation cannot create or delete repositories, so do this by hand once.

**Create it** (web UI: New repository → `takaregister-downloads`, **Public**, add a README), or:

```bash
gh repo create skp9699/takaregister-downloads --public \
  --description "Public download host for Taka Register (Windows EXE + Android APK)." \
  --add-readme
```

**Retire the old repo** once the first combined release is live and the site change is merged:

```bash
gh repo delete skp9699/taka-register   # optional; or archive it instead
```

---

## Publishing a release

One release tag per version carries **both** assets. Asset filenames must stay exactly
`TakaRegister.exe` and `TakaRegister-mobile.apk` to match the website links.

### Manual

```bash
# Create the release for this version (first asset creates it)...
gh release create v1.0.11 ./TakaRegister.exe \
  --repo skp9699/takaregister-downloads --title v1.0.11 --notes "What's new..."

# ...then attach the other platform's asset to the same release.
gh release upload v1.0.11 ./TakaRegister-mobile.apk --repo skp9699/takaregister-downloads
```

Then bump `version.json` in this repo and push to `main`.

### Automated (recommended)

Each private source repo builds its binary on a tag push and publishes it into
`takaregister-downloads`. Whichever job runs first creates the release for the tag; the other
attaches its asset. Ready-to-use workflows are in [`deploy/`](deploy/):

- [`deploy/android-release.yml`](deploy/android-release.yml) → `takaregister-mobile/.github/workflows/release.yml`
- [`deploy/windows-release.yml`](deploy/windows-release.yml) → the Windows source repo (adjust the build step to your toolchain)

Both need a secret `RELEASE_TOKEN` in the source repo: a fine-grained PAT with
**Contents: read/write** on `takaregister-downloads`. Cut a release with:

```bash
git tag v1.0.11 && git push origin v1.0.11
```

---

## Branch / release conventions

- `main` — production. The website's GitHub Pages deploys from `main`; merging here goes live.
- Release version is tracked by git **tags** (`vX.Y.Z`) in the source repos, not long-lived branches.
  `releases/latest/download/...` always follows the most recent published (non-prerelease) release.
- For a public beta channel, publish the release with `--prerelease`; `latest` keeps pointing at the
  last stable release while testers grab the prerelease from the repo's Releases page.
