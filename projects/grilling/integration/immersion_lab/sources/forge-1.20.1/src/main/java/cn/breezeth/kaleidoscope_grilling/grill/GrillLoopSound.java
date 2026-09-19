package cn.breezeth.kaleidoscope_grilling.grill;

import cn.breezeth.kaleidoscope_grilling.registry.ModSounds;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;

public final class GrillLoopSound extends AbstractTickableSoundInstance {
  private static final Map<BlockPos, GrillLoopSound> ACTIVE = new HashMap<>();
  private final BlockPos pos;

  private GrillLoopSound(BlockPos pos) {
    super(ModSounds.GRILL_LOOP.get(), SoundSource.BLOCKS, RandomSource.create());
    this.pos = pos.immutable();
    this.x = pos.getX() + 0.5;
    this.y = pos.getY() + 0.35;
    this.z = pos.getZ() + 0.5;
    this.volume = 0.65F;
    this.looping = true;
    this.delay = 0;
  }

  public static void ensure(GrillBlockEntity grill) {
    if (!grill.getBlockState().getValue(GrillBlock.LIT) || grill.isEmpty()) return;
    ACTIVE.computeIfAbsent(
        grill.getBlockPos(),
        pos -> {
          GrillLoopSound sound = new GrillLoopSound(pos);
          Minecraft.getInstance().getSoundManager().play(sound);
          return sound;
        });
  }

  @Override
  public void tick() {
    var level = Minecraft.getInstance().level;
    if (level == null
        || !(level.getBlockEntity(pos) instanceof GrillBlockEntity grill)
        || !grill.getBlockState().getValue(GrillBlock.LIT)
        || grill.isEmpty()) {
      stop();
      ACTIVE.remove(pos, this);
    }
  }
}
