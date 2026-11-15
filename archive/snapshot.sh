#!/bin/zsh
# SNAPSHOT-RITUAL v85.126: after every green commit, tag the proven state and tarball the load-bearing files, so any future hand can stand on exactly this stone
set -e
cd ~/CV_Tool
V="${1:?usage: ./archive/snapshot.sh v85.NNN}"
SHA=$(git rev-parse --short HEAD)
git tag -f "proven-$V" "$SHA"
tar -czf "archive/snapshots/$V-$SHA.tgz" butler.py briefing.py wa.py ship.sh archive/patchlib.py archive/snapshot.sh CONVENTIONS.md ARCHITECTURE.md DEVELOPERS.md notes/DEVLOG.md notes/DASHBOARD.md
echo "📦 snapshot: proven-$V @ $SHA -> archive/snapshots/$V-$SHA.tgz (tag local; mirror commit is the remote proof)"
