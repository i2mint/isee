#!/usr/bin/env bash
# Run `twine upload "$@"` and fail when it did not actually publish.
#
# twine exits 0 when --skip-existing skips every file ("Skipping X because it
# appears to already exist"), so a CI run whose version was already on PyPI
# looked green while nothing was published (i2mint/isee#26). This wrapper keeps
# twine's output in the log, and when anything was skipped it:
#   - prints a GitHub error annotation (visible on the run's summary page),
#   - appends the same to the job summary ($GITHUB_STEP_SUMMARY), and
#   - exits 1, unless ALLOW_SKIP=true (then the annotation is a warning).
#
# Env: ALLOW_SKIP ("true" to warn instead of failing; default "false"),
#      ISEE_TWINE_CMD (default "twine": the command run, a seam for tests).
set -uo pipefail
allow_skip="$(echo "${ALLOW_SKIP:-false}" | tr '[:upper:]' '[:lower:]')"

log="$(mktemp)"
trap 'rm -f "$log"' EXIT

# twine logs through rich, which wraps at the terminal width (80 in CI) and
# would split the skip message across lines: give it room, and unbuffer it so
# the log keeps stdout and stderr in order.
COLUMNS=10000 PYTHONUNBUFFERED=1 ${ISEE_TWINE_CMD:-twine} upload "$@" 2>&1 | tee "$log"
status=${PIPESTATUS[0]}
if [ "$status" -ne 0 ]; then
  echo "::error title=PyPI upload failed::twine upload exited with status $status; nothing new may be on PyPI. See the log above."
  exit "$status"
fi

# Colour codes out, and wrapped lines joined back, in case the width was not
# honoured: the message must be found however it was printed.
flat="$(sed 's/\x1b\[[0-9;]*m//g' "$log" | tr '\n' ' ' | tr -s ' ')"
skipped="$(echo "$flat" | grep -oE 'Skipping [^ ]+ because it appears to already exist' | awk '{print $2}' | sort -u)"
if [ -z "$skipped" ]; then
  if echo "$flat" | grep -qE 'Skipping .* appears to already'; then
    skipped="(files twine reported as skipped; see the log above)"
  else
    exit 0
  fi
fi

files="$(echo "$skipped" | paste -sd ' ' -)"
message="Not published to PyPI: these files already exist there, so twine skipped them: ${files}. The version was not bumped, or this run re-ran an earlier release."
if [ "$allow_skip" = "true" ]; then
  echo "::warning title=Nothing new published to PyPI::${message}"
  level="Warning"
else
  echo "::error title=Nothing new published to PyPI::${message} Bump the version, or pass allow-skip: true if re-uploading is expected."
  level="Error"
fi
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  printf '### %s: nothing new published to PyPI\n\n%s\n' "$level" "$message" >> "$GITHUB_STEP_SUMMARY"
fi
[ "$allow_skip" = "true" ] && exit 0
exit 1
