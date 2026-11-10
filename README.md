# partypuzl-packs

The premium question packs for the PartyPuzl Android app, served as static JSON by GitHub Pages:

    https://logang-bot.github.io/partypuzl-packs/v1/packs.json

The app downloads this file, caches it on the device, and keeps using the cached copy when the
site is unreachable. Official (free) packs are not here; they ship inside the app.

> This file is public. Anyone with the URL can read it. It keeps the premium text out of the APK
> and lets packs change without an app release, but it is not access control. The upgrade path to
> purchase-verified downloads is in the app repo's `docs/pack-bank-cloudflare.md`.

## Format (`schemaVersion` 1)

```json
{
  "schemaVersion": 1,
  "contentVersion": 3,
  "packs": {
    "<packId>": {
      "<language>": {
        "truths": ["..."],
        "dares": ["..."],
        "sticky": [{ "text": "...", "presentContinuous": "...", "durationSeconds": 180 }],
        "trivia": [{ "question": "...", "optionA": "...", "optionB": "...", "correct": "A" }]
      }
    }
  }
}
```

- **`packId`** must match a premium pack id in the app's `QuestionPackCatalog`
  (`premium_movie_night`, `premium_spicy`, `premium_nsfw`). An id the app doesn't know is ignored.
  Adding a brand-new pack still needs an app release that defines it.
- **`language`** is a language code (`en`, `es`). The app uses the user's language and falls back
  to `en`, so every pack needs an `en` entry.
- Every list is optional. Use only the ones the pack's game mode needs:
  - Truth or Dare needs **both** `truths` and `dares`.
  - Sticky dares need `sticky`. `text` is the dare, `presentContinuous` is how it reads while it's
    running ("holding eye contact with…"), and the duration label is built by the app from
    `durationSeconds`.
  - Quiz needs `trivia`. `correct` is `"A"` or `"B"`.
- A malformed entry (missing field, wrong type) is skipped, not fatal.
- **`schemaVersion`**: only change it together with an app release that understands the new
  format. An app that sees an unknown version keeps its cached copy.
- **`contentVersion`**: bump it on every content change. It's informational, but it makes it easy
  to see which version a device has.

## Publishing a change

1. Edit `v1/packs.json` and validate it: `python3 -m json.tool v1/packs.json > /dev/null`.
2. Commit and push to `main`. Pages redeploys in about a minute.
3. Devices pick it up the next time the app comes to the foreground, at most every 12 hours per
   app session, or immediately on a cold start.

Don't remove a pack or empty a language that devices already rely on. A device that downloads the
smaller file loses those prompts.

## Files

- `v1/packs.json`: the content.
- `tools/export_from_strings.py`: one-off script that produced the first version from the app's
  old `strings.xml` arrays.
- `.nojekyll`: serve the files as-is.
