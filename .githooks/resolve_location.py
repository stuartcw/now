#!/usr/bin/env python3
"""Resolve a pasted Google Maps share link into a working /maps/embed?pb=...
URL, in place, for the pre-commit hook.

Google blocks regular share links (maps.app.goo.gl/..., google.com/maps/...)
from loading in an iframe on another site. The only URL format that's
actually embeddable without an API key is the one Google's own "Share >
Embed a map" button generates (/maps/embed?pb=...). This script follows a
pasted share link, pulls the coordinates and place ID out of the resolved
page, and builds that same URL format.

This relies on an undocumented JSON blob (APP_INITIALIZATION_STATE) Google
embeds in the resolved page — not a supported API. If Google changes that
page's structure, this will start failing loudly (non-zero exit) rather
than silently writing a wrong or broken map URL.
"""
import re
import sys
import urllib.request
from urllib.parse import parse_qs, urlparse

URL_RE = re.compile(r"https?://\S+")
MAPS_HOST_RE = re.compile(r"google\.[a-z.]+/maps|goo\.gl/maps|maps\.app\.goo\.gl")
STATE_RE = re.compile(
    r"APP_INITIALIZATION_STATE\s*=\s*\[\[\[([\d.]+),(-?[\d.]+),(-?[\d.]+)\]"
    r",\[0,0,0\],\[1024,768\],([\d.]+)\]"
)


def fail(message):
    print(f"resolve_location.py: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        fail("usage: resolve_location.py <path-to-location-file>")

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        content = f.read()

    stripped = content.strip()
    if not stripped or "/maps/embed" in stripped:
        return  # plain text, or already resolved — nothing to do

    match = URL_RE.search(stripped)
    if not match:
        return  # no URL at all — plain text, leave as-is

    url = match.group(0)
    if not MAPS_HOST_RE.search(url):
        return  # some other URL — leave as plain text

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            final_url = response.geturl()
            body = response.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        fail(f"couldn't fetch {url}: {exc}")

    ftid = parse_qs(urlparse(final_url).query).get("ftid", [None])[0]
    if not ftid:
        fail(f"resolved to {final_url} but found no ftid (place ID) in it")

    state_match = STATE_RE.search(body)
    if not state_match:
        fail(
            "couldn't find coordinates in the resolved page "
            "(Google may have changed its page format)"
        )
    dist, lng, lat, zoom = state_match.groups()

    label_match = re.search(r"Take a look at (.+?) on Google Maps", content)
    label = label_match.group(1) if label_match else "Location"

    place_id = ftid.replace(":", "%3A")
    embed_url = (
        "https://www.google.com/maps/embed?pb="
        f"!1m18!1m12!1m3!1d{dist}!2d{lng}!3d{lat}"
        "!2m3!1f0!2f0!3f0!3m2!1i1024!2i768"
        f"!4f{zoom}!3m3!1m2!1s{place_id}!2s{label}"
        "!5e0!3m2!1sen!2sjp!4v0"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(embed_url + "\n")

    print(f"resolve_location.py: resolved {url} -> embeddable map for {label}")


if __name__ == "__main__":
    main()
