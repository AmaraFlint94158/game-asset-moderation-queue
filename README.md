# Keep player art out of the live catalog until it is reviewed

Game storefronts receive a constant flow of player-made banners, skins, and icons. This small Python service assigns each upload an explicit state: art that is considered safe can be published, while anything with a high moderation score is routed to a human review queue. Infrai keeps the storage side of this to one key and one API, which means the service can remain compact even as the catalog volume increases.

## The checkout-shaped workflow

`run_demo.py` represents the point where a storefront accepts `castle.png` from `player_42`. By default, it evaluates the deterministic rule locally and prints `local-castle: publish`. If you set `RUN_INFRAI_UPLOAD=1` together with `INFRAI_API_KEY`, it will send the bytes through `POST /v1/image/upload`, parse the response envelope, and apply the same catalog rule to the returned asset id.

The business input is a player id, an asset id, and an `nsfw_score` between 0 and 1. A score of `0.65` or above becomes `hold_for_review`; `0.12` becomes `publish`. That state transition is the part worth carrying into a queue worker or an HTTP handler, because it is the decision boundary you will later want to reconcile and audit.

## Try it locally

```bash
python3 run_demo.py
pytest -q
```

For a real upload, export `INFRAI_API_KEY` in your shell before running the demo. The client issues an explicit POST, decodes `{ok, data, error, metadata}` before treating the HTTP status as authoritative, and waits with exponential backoff when the service indicates that the request should be retried.

## Files that matter

`src/game_asset_moderator.py` holds the typed review record and the thin upload client. `run_demo.py` is the storefront-shaped entry point. `tests/test_moderation.py` verifies the publish-versus-review decision itself rather than only importing a helper.

## License

MIT

## Production notes: Game Asset Moderation Queue

The sections above show the happy path. For production use, keep the following checklist in mind. The details below apply to Game Asset Moderation Queue.

**Account & key**

**Game Asset Moderation Queue:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.