# Taka Register — Deployment & Release Guide

How the apps and this website are built, hosted, and updated.

## Overview

| Piece | Repo | Visibility | Role |
|-------|------|-----------|------|
| Website (this repo) | `skp9699/takaregister.in` | public | GitHub Pages site at `www.takaregister.in` (`CNAME`). Hosts `index.html`, `version.json`, `faq/`. |
| Windows app source | *(private)* | private | Builds `TakaRegister.exe`. |
| Windows downloads | `skp9699/taka-register` | **public** | Release-only host. Serves `TakaRegister.exe` as a release asset. |
| Android app source | `skp9699/takaregister-mobile` | private | Flutter source. Builds `TakaRegister-mobile.apk`. |
| Android downloads | `skp9699/takaregister-android` | **public** *(new)* | Release-only host. Serves `TakaRegister-mobile.apk` as a release asset. |

### Download links (on the website)

`index.html` points the download buttons at the **public** release-host repos using the
`releases/latest/download/<asset>` URL, which always resolves to the newest published release:

- Windows: `https://github.com/skp9699/taka-register/releases/latest/download/TakaRegister.exe`
- Android: `https://github.com/skp9699/takaregister-android/releases/latest/download/TakaRegister-mobile.apk`

> The release-host repo **must be public**, otherwise these URLs return 404 for anonymous visitors.
> The app *source* stays in a separate private repo — only the built binary is published publicly.

### In-app update check

The desktop app polls `https://takaregister.in/version.json` and compares `version` against the
installed build. When a newer version is found it points the user at `download_url`. `faq/faq_version.json`
works the same way for the in-app FAQ. Bump `version.json` here **after** publishing a new release so
existing installs notice the update.

---

## One-time setup: the public Android downloads repo

The session token used by automation cannot create repositories, so create it once by hand.

**Option A — GitHub web UI**
1. New repository → name `takaregister-android`, **Public**, add a README.
2. Done. (No source goes here — it only holds release assets.)

**Option B — gh CLI**
```bash
gh repo create skp9699/takaregister-android --public \
  --description "Public download host for the Taka Register Android app (APK)." \
  --add-readme
```

---

## Publishing a release

### Manual (quickest)

```bash
# Windows EXE
gh release create v1.0.11 ./TakaRegister.exe \
  --repo skp9699/taka-register --title "v1.0.11" --notes "What's new..."

# Android APK  (asset name must stay TakaRegister-mobile.apk to match the website link)
gh release create v1.0.11 ./build/app/outputs/flutter-apk/app-release.apk \
  --repo skp9699/takaregister-android --title "v1.0.11" --notes "What's new..."
# If the built file isn't named TakaRegister-mobile.apk, rename it first:
#   cp app-release.apk TakaRegister-mobile.apk
```

Then bump `version.json` in this repo and push to `main`.

### Automated (recommended)

Let each private *source* repo build its binary and publish the release into the public
download-host repo. A ready-to-use workflow for the Android source repo is in
[`deploy/android-release.yml`](deploy/android-release.yml) — copy it to
`takaregister-mobile/.github/workflows/release.yml`.

It needs one secret in `takaregister-mobile`: a fine-grained PAT named `RELEASE_TOKEN`
with **Contents: read/write** on `takaregister-android`. Trigger a release by pushing a tag:

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
