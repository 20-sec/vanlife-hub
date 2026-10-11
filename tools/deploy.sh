#!/bin/bash
# Baut die Site, committet ins Entwicklungs-Repo und ins Produktions-Repo (FTP-Deploy per GitHub Actions),
# wartet optional, bis eine URL live ist.
# Aufruf: bash tools/deploy.sh "Commit-Nachricht" [pfad-der-live-sein-muss.html]
set -e
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEP=/tmp/vankompass-deploy
MSG="${1:-Update}"
WAIT="${2:-}"
TRAILER="Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"

cd "$SRC"
python3 build.py | tail -1

git add -A
git diff --cached --quiet || git commit -q -m "$MSG" -m "$TRAILER"
git push -q origin main
echo "dev: $(git log --oneline -1)"

[ -d "$DEP/.git" ] || git clone -q https://github.com/rc-com-domains/vankompass.de.git "$DEP"
cd "$DEP" && git pull -q origin main && cd "$SRC"

GEN="$(python3 -c "from build import BEREICH_ORDER, SITE; print(' '.join(f'{s}.html' for s in BEREICH_ORDER), SITE['indexnow_key'] + '.txt')")"
cp index.html magazin.html bereiche.html camper.html silo-strom.html magazin-strom.html impressum.html datenschutz.html \
   portal.css vanlife-styles.css vanlife-config-v2.js favicon.svg sitemap.xml robots.txt $GEN camper-*.html magazin-*.html "$DEP/"
mkdir -p "$DEP/js" "$DEP/img"
cp js/*.js "$DEP/js/"
cp img/*.svg "$DEP/img/"

cd "$DEP"
git add -A
git diff --cached --quiet || git commit -q -m "$MSG" -m "$TRAILER"
git push -q origin main
echo "prod: $(git log --oneline -1)"

BUILD="$(grep -o 'name="build" content="[^"]*"' "$SRC/index.html" | sed 's/.*content="//;s/"$//')"
if [ -n "$WAIT" ]; then
  echo "warte auf https://vankompass.de/$WAIT (Build $BUILD) ..."
  for i in $(seq 1 60); do
    if curl -s "https://vankompass.de/$WAIT" | grep -q "content=\"$BUILD\""; then
      echo "live: https://vankompass.de/$WAIT"; exit 0
    fi
    sleep 15
  done
  echo "Deploy noch nicht sichtbar, bitte spaeter pruefen: https://vankompass.de/$WAIT"; exit 2
fi
