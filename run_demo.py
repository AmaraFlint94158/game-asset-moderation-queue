import os
import struct
import zlib

from src.game_asset_moderator import InfraiClient, review_asset, upload_and_review


def sample_png() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\x32\x70\xa0"))
        + chunk(b"IEND", b"")
    )


def main() -> None:
    player_id = "player_42"
    sample_score = 0.18
    if os.environ.get("RUN_INFRAI_UPLOAD") == "1":
        result = upload_and_review(InfraiClient(), player_id, "castle.png", sample_png(), sample_score)
    else:
        result = review_asset(player_id, "local-castle", sample_score)
    print(f"{result.asset_id}: {result.decision}")


if __name__ == "__main__":
    main()
