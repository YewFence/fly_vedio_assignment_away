#!/usr/bin/env bash
set -euo pipefail

: "${GH_REPO:?}"
: "${RELEASE_TAG:?}"
: "${RELEASE_COMMIT:?}"
: "${ALLOW_TAG_CREATION:?}"
: "${RELEASE_PRERELEASE:?}"
: "${RELEASE_NOTES_FILE:?}"

if [[ ! "${RELEASE_TAG}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z][0-9A-Za-z.-]*)?$ ]] ||
   [[ ! "${RELEASE_COMMIT}" =~ ^[0-9a-f]{40}$ ]] ||
   [[ ! "${ALLOW_TAG_CREATION}" =~ ^(true|false)$ ]] ||
   [[ ! "${RELEASE_PRERELEASE}" =~ ^(true|false)$ ]]; then
  echo "Invalid release metadata" >&2
  exit 1
fi

if [[ "$(git rev-parse HEAD)" != "${RELEASE_COMMIT}" ]]; then
  echo "Checkout does not match the resolved release commit" >&2
  exit 1
fi
if [[ ! -s "${RELEASE_NOTES_FILE}" ]]; then
  echo "Release notes are missing or empty" >&2
  exit 1
fi

assets=()
if [[ -n "${RELEASE_ASSET_DIR:-}" ]]; then
  shopt -s nullglob
  assets=("${RELEASE_ASSET_DIR}"/*)
  if [[ "${#assets[@]}" -eq 0 ]]; then
    echo "No release assets in ${RELEASE_ASSET_DIR}" >&2
    exit 1
  fi
  for asset in "${assets[@]}"; do
    if [[ ! -f "${asset}" ]]; then
      echo "Release asset is not a file: ${asset}" >&2
      exit 1
    fi
  done
fi

# GraphQL distinguishes missing resources (null) from failed requests.
# shellcheck disable=SC2016 # These are GraphQL variables, not shell variables.
repository_json="$(gh api graphql \
  -f owner="${GH_REPO%/*}" -f name="${GH_REPO#*/}" \
  -f tag="${RELEASE_TAG}" -f ref="refs/tags/${RELEASE_TAG}" \
  -f query='query($owner: String!, $name: String!, $tag: String!, $ref: String!) {
    repository(owner: $owner, name: $name) {
      ref(qualifiedName: $ref) { target { oid } }
      release(tagName: $tag) { isDraft }
    }
  }')"
jq -e '.data.repository | type == "object"' <<< "${repository_json}" >/dev/null

if jq -e '.data.repository.ref != null' <<< "${repository_json}" >/dev/null; then
  # The commits endpoint peels annotated tags as well as lightweight tags.
  tag_commit="$(gh api "repos/${GH_REPO}/commits/refs%2Ftags%2F${RELEASE_TAG}" --jq .sha)"
  if [[ "${tag_commit}" != "${RELEASE_COMMIT}" ]]; then
    echo "Remote tag ${RELEASE_TAG} does not match ${RELEASE_COMMIT}" >&2
    exit 1
  fi
elif [[ "${ALLOW_TAG_CREATION}" != "true" ]]; then
  echo "Remote tag ${RELEASE_TAG} must already exist for this release entrypoint" >&2
  exit 1
fi

if jq -e '.data.repository.release == null' <<< "${repository_json}" >/dev/null; then
  create_args=(
    --repo "${GH_REPO}" --target "${RELEASE_COMMIT}"
    --title "${RELEASE_TAG}" --notes-file "${RELEASE_NOTES_FILE}"
    "--prerelease=${RELEASE_PRERELEASE}"
  )
  if [[ "${ALLOW_TAG_CREATION}" != "true" ]]; then
    create_args+=(--verify-tag)
  fi
  # gh owns temporary drafts, asset uploads, publication, and failure cleanup.
  gh release create "${RELEASE_TAG}" "${assets[@]}" "${create_args[@]}"
  exit 0
fi

if [[ "${#assets[@]}" -gt 0 ]]; then
  gh release upload "${RELEASE_TAG}" "${assets[@]}" --repo "${GH_REPO}" --clobber
fi
edit_args=(
  --repo "${GH_REPO}" --notes-file "${RELEASE_NOTES_FILE}"
  "--prerelease=${RELEASE_PRERELEASE}"
)
if jq -e '.data.repository.release.isDraft' <<< "${repository_json}" >/dev/null; then
  edit_args+=(--draft=false --target "${RELEASE_COMMIT}")
fi
if [[ "${ALLOW_TAG_CREATION}" != "true" ]]; then
  edit_args+=(--verify-tag)
fi
gh release edit "${RELEASE_TAG}" "${edit_args[@]}"
