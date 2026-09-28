After changing project code or configuration, run `mise run check` before finishing and make sure the check passes. If the check fails, try `mise run fix` first, then fix any remaining issues manually.

Keep reusable development and CI commands in mise tasks so local and automated workflows use the same entry points.

This project is in early development and does not require backward compatibility yet. When a cleaner long-term design requires an incompatible change, make the change deliberately instead of preserving compatibility through extra complexity.
