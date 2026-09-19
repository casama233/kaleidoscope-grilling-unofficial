package cn.breezeth.kaleidoscope_grilling.seasoning;

import cn.breezeth.kaleidoscope_grilling.oil.AnvilPressAnimationAccess;


import net.minecraft.world.entity.player.Player;

public final class SeasoningAnimation {
  public static final byte EVENT_ID = 69;
  public static final int DURATION_TICKS = 10;

  public static void start(Player player) {
    if (player instanceof AnvilPressAnimationAccess animation) animation.grilling$startSeasoning();
    player.level().broadcastEntityEvent(player, EVENT_ID);
  }

  public static float arc(float progress) {
    return (float) Math.sin(Math.PI * Math.max(0.0F, Math.min(1.0F, progress)));
  }

  private SeasoningAnimation() {}
}
