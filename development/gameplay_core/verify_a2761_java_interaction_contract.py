from __future__ import annotations

import hashlib
import urllib.request

BASE = "https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/"
FILES = {
    "seasoning_block": (
        "forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/SeasoningBottleBlock.java",
        "1088a0eed827be3c773ea5aeca37d5c284e4cb8e",
        (
            "InteractionHand hand,",
            "ItemStack held = player.getItemInHand(hand);",
            "pickupOne(level, pos, player, hand, bottle);",
            "player.setItemInHand(hand, result);",
            "if (!player.getAbilities().instabuild) held.shrink(1);",
        ),
    ),
    "skewering_handler": (
        "forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkeweringHandler.java",
        "88bf552aeebed54e284264f38a6151488c8cb9ed",
        (
            "public static void onRightClickItem(PlayerInteractEvent.RightClickItem event)",
            "if (event.getHand() != InteractionHand.MAIN_HAND) return;",
            "ItemStack offhand = event.getEntity().getOffhandItem();",
            "disassemble(offhand, event.getEntity(), InteractionHand.OFF_HAND)",
        ),
    ),
    "grill_block": (
        "forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/grill/GrillBlock.java",
        "b3f4784635d631a239a471642770b105977ee2d6",
        (
            "InteractionHand hand,",
            "ItemStack held = player.getItemInHand(hand);",
            "held.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));",
            "player.setItemInHand(hand, result.heldReplacement());",
        ),
    ),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main() -> None:
    for name, (path, expected, tokens) in FILES.items():
        req = urllib.request.Request(BASE + path, headers={"User-Agent": "Grilling-A2.7.61-contract/1"})
        with urllib.request.urlopen(req, timeout=90) as response:
            data = response.read()
        actual = git_blob(data)
        assert actual == expected, (name, actual, expected)
        text = data.decode("utf-8")
        for token in tokens:
            assert token in text, (name, token)
    print("A2.7.61 pinned Java interaction-hand contract: PASS")


if __name__ == "__main__":
    main()
