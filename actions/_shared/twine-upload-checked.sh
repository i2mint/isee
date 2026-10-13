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
# Env: ALLOW_SKIP (default "false"), TWINE (default "twine": the command run).
set -uo pipefail

log="$(mktemp)"
trap 'rm -f "$log"' EXIT

${TWINE:-twine} upload "$@" 2>&1 | tee "$log"
status=${PIPESTATUS[0]}
if [ "$status" -ne 0 ]; then
  echo "::error title=PyPI upload failed::twine upload exited with status $status; nothing new may be on PyPI. See the log above."
  exit "$status"
fi

skipped="$(grep -oE 'Skipping [^ ]+ because it appears to already exist' "$log" | awk '{print $2}' | sort -u)"
if [ -z "$skipped" ]; then
  exit 0
fi

files="$(echo "$skipped" | paste -sd ' ' -)"
message="Not published to PyPI: these files already exist there, so twine skipped them: ${files}. The version was not bumped, or this run re-ran an earlier release."
if [ "${ALLOW_SKIP:-false}" = "true" ]; then
  echo "::warning title=Nothing new published to PyPI::${message}"
  level="Warning"
else
  echo "::error title=Nothing new published to PyPI::${message} Bump the version, or pass allow-skip: true if re-uploading is expected."
  level="Error"
fi
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  printf '### %s: nothing new published to PyPI\n\n%s\n' "$level" "$message" >> "$GITHUB_STEP_SUMMARY"
fi
[ "${ALLOW_SKIP:-false}" = "true" ] && exit 0
exit 1
