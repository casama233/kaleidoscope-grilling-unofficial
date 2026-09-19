package cn.breezeth.kaleidoscope_grilling.client;

import cn.breezeth.kaleidoscope_grilling.registry.ModSounds;
import cn.breezeth.kaleidoscope_grilling.food.HotFoodConfig;

import cn.breezeth.kaleidoscope_grilling.skewer.MultiBiteSkewerItem;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.EntityBoundSoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class ClientSkewerEatingSound {
  private static final Map<Integer, EntityBoundSoundInstance> ACTIVE = new HashMap<>();
  private static final Map<Integer, MultiBiteSkewerItem.AnimationProfile> ACTIVE_PROFILES =
      new HashMap<>();
  private static boolean localWasEating;

  public static void handle(
      int entityId, boolean playing, MultiBiteSkewerItem.AnimationProfile profile) {
    Minecraft minecraft = Minecraft.getInstance();
    EntityBoundSoundInstance previous = ACTIVE.get(entityId);
    if (playing
        && previous != null
        && ACTIVE_PROFILES.get(entityId) == profile
        && minecraft.getSoundManager().isActive(previous)) return;
    ACTIVE.remove(entityId);
    if (previous != null) minecraft.getSoundManager().stop(previous);
    if (!playing) {
      ACTIVE_PROFILES.remove(entityId);
      return;
    }
    ACTIVE_PROFILES.put(entityId, profile);
    if (minecraft.level == null) return;

    Entity entity = minecraft.level.getEntity(entityId);
    if (entity == null) return;
    SoundEvent soundEvent;
    switch (profile) {
      case ONE -> soundEvent = ModSounds.ONE_SKEWER_EAT.get();
      case TWO -> soundEvent = ModSounds.TWO_SKEWER_EAT.get();
      case FOUR -> soundEvent = ModSounds.FOUR_SKEWER_EAT.get();
      default -> soundEvent = ModSounds.THREE_SKEWER_EAT.get();
    }
    EntityBoundSoundInstance sound =
        new EntityBoundSoundInstance(
            soundEvent, SoundSource.PLAYERS, 1.0F, 1.0F, entity, minecraft.level.random.nextLong());
    ACTIVE.put(entityId, sound);
    minecraft.getSoundManager().play(sound);
  }

  /** Client-state fallback so the eater's sound never depends solely on packet delivery. */
  public static void tickLocal() {
    Minecraft minecraft = Minecraft.getInstance();
    var player = minecraft.player;
    if (player == null) {
      ACTIVE.values().forEach(minecraft.getSoundManager()::stop);
      ACTIVE.clear();
      ACTIVE_PROFILES.clear();
      localWasEating = false;
      return;
    }
    boolean eating =
        HotFoodConfig.ENABLE_SKEWER_EATING_ANIMATIONS.get()
            && player.isUsingItem()
            && player.getUseItem().getItem() instanceof MultiBiteSkewerItem;
    if (eating) {
      MultiBiteSkewerItem skewer = (MultiBiteSkewerItem) player.getUseItem().getItem();
      int entityId = player.getId();
      MultiBiteSkewerItem.AnimationProfile profile =
          ACTIVE_PROFILES.getOrDefault(entityId, skewer.animationProfile(player.getUseItem()));
      handle(entityId, true, profile);
    } else if (localWasEating) {
      MultiBiteSkewerItem.AnimationProfile profile =
          ACTIVE_PROFILES.getOrDefault(
              player.getId(), MultiBiteSkewerItem.AnimationProfile.THREE);
      handle(player.getId(), false, profile);
    }
    localWasEating = eating;
  }

  public static MultiBiteSkewerItem.AnimationProfile profile(
      int entityId, MultiBiteSkewerItem.AnimationProfile fallback) {
    return SkewerAnimationDebug.profile(
        entityId, ACTIVE_PROFILES.getOrDefault(entityId, fallback));
  }

  private ClientSkewerEatingSound() {}
}
