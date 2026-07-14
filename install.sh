#!/usr/bin/env bash
# gemini-slide-generator skill installer
# Usage: curl -fsSL https://<your-site>/install.sh | bash
set -euo pipefail

REPO="aigisujp-sudo/gemini-slide-generator"
BRANCH="main"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/gemini-slide-generator"

echo "Installing gemini-slide-generator skill..."

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz -C "$TMP_DIR"

SRC_DIR="$(find "$TMP_DIR" -maxdepth 1 -type d -name "gemini-slide-generator-*")/skill"

mkdir -p "$DEST"
cp -r "$SRC_DIR"/. "$DEST"/

echo "Installed to: $DEST"
echo ""
echo "Next steps:"
echo "  1. cd \"$DEST\" && pip install -r requirements.txt"
echo "  2. Set GEMINI_API_KEY (and Google OAuth credentials for Slides/Drive)."
echo "     See: $DEST/references/google_setup.md"
echo ""
echo "Done."
