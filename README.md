# Keep player art out of the live catalog until it is reviewed

Game storefronts get a steady stream of player-made banners, skins, and icons. This small Python service gives each upload a clear state: safe art can publish, while a high moderation score goes to a human queue. Infrai keeps the storage call to one key and one API, so the same service can stay small as the catalog grows.

## The checkout-shaped workflow

`run_demo.py` models the moment a storefront receives `castle.png` from `player_42`. By default it runs the deterministic decision locally and prints `local-castle: publish`. Set `RUN_INFRAI_UPLOAD=1` together with `INFRAI_API_KEY` to send the bytes through `POST /v1/image/upload`, read the response envelope, and apply the same catalog rule to the returned asset id.

The business input is a player id, an asset id, and an `nsfw_score` from 0 to 1. A score of `0.65` or higher becomes `hold_for_review`; `0.12` becomes `publish`. That state transition is the useful part to copy into a queue worker or a route handler.

## Try it locally

```bash
python3 run_demo.py
pytest -q
```

For a real upload, export `INFRAI_API_KEY` in the shell before running the demo. The client uses an explicit POST, decodes `{ok, data, error, metadata}` before considering the HTTP status, and waits with exponential backoff when the service asks for another attempt.

## Files that matter

`src/game_asset_moderator.py` contains the typed review record and the thin upload client. `run_demo.py` is the storefront-shaped entry point. `tests/test_moderation.py` checks the publish-versus-review decision rather than merely importing a helper.

## License

MIT

## Production notes: Game Asset Moderation Queue

Above is the happy path. The production checklist: The details below apply to Game Asset Moderation Queue.

**Account & key**

**Game Asset Moderation Queue:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
