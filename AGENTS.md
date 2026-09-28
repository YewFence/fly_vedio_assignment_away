This is a Playwright-based automation tool that automatically watches course videos on SCNU 砺儒云 (Moodle, moodle.scnu.edu.cn).

After changing project code or configuration, run `mise run check` before finishing and make sure the check passes. If the check fails, try `mise run fix` first, then fix any remaining issues manually.

Keep reusable development and CI commands in mise tasks so local and automated workflows use the same entry points.

This project is in early development and does not require backward compatibility yet. When a cleaner long-term design requires an incompatible change, make the change deliberately instead of preserving compatibility through extra complexity.

## Real accounts and credentials

- Several failed logins within a short window lock the SCNU account for one hour. Never retry logins in a loop with real credentials.
- `.env` and `cookies.json` hold plaintext login state. Never commit, share, or paste them.
- The tool only talks to the Moodle site and its login/video services. Do not add requests to other hosts without a strong reason.

## Running locally

Running the tool means driving a real browser session on a real account, so leave it to the user: by default, do not launch `mise run dev`, start or attach to browsers, or modify `.env` and `cookies.json`. Verify changes with `mise run check` and the test suite instead of live runs.

## Platform behavior

The platform reports watch progress in batches of roughly 15 seconds, so its completion bar lags behind actual playback. Completion is judged by the platform's completion flag first, falling back to "played to the end"; if the flag is still missing 30 seconds after playback ends, the tool warns and skips to the next video. Read the workflow section in README.md before changing playback or completion-detection logic.
