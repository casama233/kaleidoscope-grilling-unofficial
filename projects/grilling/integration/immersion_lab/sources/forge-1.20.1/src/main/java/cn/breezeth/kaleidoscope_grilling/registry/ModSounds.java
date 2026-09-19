package cn.breezeth.kaleidoscope_grilling.registry;

import cn.breezeth.kaleidoscope_grilling.KaleidoscopeGrilling;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
  public static final DeferredRegister<SoundEvent> SOUNDS =
      DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, KaleidoscopeGrilling.MOD_ID);
  public static final RegistryObject<SoundEvent> ACTION_SUCCESS = register("action_success");
  public static final RegistryObject<SoundEvent> GRILL_FLIP = register("grill_flip");
  public static final RegistryObject<SoundEvent> GRILL_LOOP = register("grill_loop");
  public static final RegistryObject<SoundEvent> PICKUP_ITEM = register("pickup_item");
  public static final RegistryObject<SoundEvent> SKEWER_DISASSEMBLE =
      register("skewer_disassemble");
  public static final RegistryObject<SoundEvent> SEASON = register("season");
  public static final RegistryObject<SoundEvent> SHAKE_SEASONING = register("shake_seasoning");
  public static final RegistryObject<SoundEvent> SEASONING_BOTTLE_PLACE =
      register("seasoning_bottle_place");
  public static final RegistryObject<SoundEvent> SEASONING_BOTTLE_STACK =
      register("seasoning_bottle_stack");
  public static final RegistryObject<SoundEvent> ONE_SKEWER_EAT = register("one_skewer_eat");
  public static final RegistryObject<SoundEvent> TWO_SKEWER_EAT = register("two_skewer_eat");
  public static final RegistryObject<SoundEvent> THREE_SKEWER_EAT =
      register("three_skewer_eat");
  public static final RegistryObject<SoundEvent> FOUR_SKEWER_EAT =
      register("four_skewer_eat");

  private static RegistryObject<SoundEvent> register(String name) {
    ResourceLocation id = new ResourceLocation(KaleidoscopeGrilling.MOD_ID, name);
    return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(id));
  }

  private ModSounds() {}
}
