#!/bin/sh

DIFF=""
which gdiff >/dev/null 2>/dev/null && DIFF=gdiff
which diff >/dev/null 2>/dev/null && DIFF=diff

git ls-files -- src | while read FILE ; do
  DEST="$(echo "$FILE" | cut -b 4-)"
  DESTDIR="$(dirname "$DEST")"
  if [ ! -e "$DESTDIR" ]; then
    echo creating "$DESTDIR"
    mkdir "$DESTDIR"
  fi
  if [ ! -n "$DIFF" ] || [ ! -e "$DEST"  ] || ! "$DIFF" -q "$FILE" "$DEST" >/dev/null ; then
    echo updating "\"$DEST\""
    cp "$FILE" "$DEST"
  fi
done
