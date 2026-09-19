package cn.breezeth.kaleidoscope_grilling.grill;

import cn.breezeth.kaleidoscope_grilling.registry.ModItems;

import cn.breezeth.kaleidoscope_grilling.skewer.SecretSkewerItem;
import cn.breezeth.kaleidoscope_grilling.skewer.SkewerRecipes;


import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

public final class GrillRenderer implements BlockEntityRenderer<GrillBlockEntity> {
  public GrillRenderer(BlockEntityRendererProvider.Context context) {}

  @Override
  public void render(
      GrillBlockEntity grill,
      float partial,
      PoseStack pose,
      MultiBufferSource buffers,
      int light,
      int overlay) {
    GrillLoopSound.ensure(grill);
    int facingRotation =
        switch (grill.getBlockState().getValue(GrillBlock.FACING)) {
          case EAST -> 90;
          case SOUTH -> 180;
          case WEST -> 270;
          default -> 0;
        };
    pose.pushPose();
    pose.translate(0.5, 0, 0.5);
    pose.mulPose(Axis.YP.rotationDegrees(-facingRotation));
    pose.translate(-0.5, 0, -0.5);
    GrillBlockEntity.FlipAnimationData animation = grill.flipAnimationData;
    int flips = grill.getFlips();
    long now = System.currentTimeMillis();
    if (animation.observedFlips < 0) {
      animation.observedFlips = flips;
    } else if (animation.observedFlips != flips) {
      animation.observedFlips = flips;
      animation.timestamp = now;
      RandomSource random =
          RandomSource.create(grill.getBlockPos().asLong() ^ ((long) flips * 341873128712L));
      for (int i = 0; i < animation.heights.length; i++)
        animation.heights[i] = 0.28F + random.nextFloat() * 0.10F;
    }
    float progress =
        animation.timestamp < 0 ? 1F : Mth.clamp((now - animation.timestamp) / 700F, 0F, 1F);
    boolean animating = flips > 0 && progress < 1F;
    for (int i = 0; i < grill.getContainerSize(); i++) {
      ItemStack stack = grill.getItem(i);
      if (stack.isEmpty()) continue;
      if (stack.is(ModItems.SECRET_SKEWER.get())) {
        stack = stack.copy();
        int stage =
            grill.getPhase() == 0
                ? 0
                : grill.getPhase() == 1
                    ? Math.min(4, 1 + grill.getFlips())
                    : grill.getPhase() == 2 ? 4 : 5;
        SecretSkewerItem.setVisualStage(stack, stage);
      } else if (SkewerRecipes.isRawSkewer(stack)) {
        if (grill.getPhase() == 2) {
          ItemStack cooked = SkewerRecipes.cookedResult(stack);
          if (!cooked.isEmpty()) stack = cooked;
        } else {
          stack = stack.copy();
          int stage =
              grill.getPhase() == 0
                  ? 0
                  : grill.getPhase() == 1 ? Math.min(4, 1 + grill.getFlips()) : 5;
          SecretSkewerItem.setVisualStage(stack, stage);
        }
      }
      float lift = animating ? animation.heights[i] * Mth.sin(Mth.PI * progress) : 0F;
      float rotation = (animating ? flips - 1 + progress : flips) * 180F;
      pose.pushPose();
      if (stack.is(ModItems.SECRET_SKEWER.get())
          || SkewerRecipes.isRawSkewer(stack)
          || SkewerRecipes.isCookedSkewer(stack)) {
        pose.translate((3F + i * 5F) / 16F, 5F / 16F + lift, 6.25F / 16F);
        pose.mulPose(Axis.ZP.rotationDegrees(rotation));
        pose.translate(0, 7F / 16F, 1.75F / 16F);
        Minecraft.getInstance()
            .getItemRenderer()
            .renderStatic(
                stack, ItemDisplayContext.NONE, light, overlay, pose, buffers, grill.getLevel(), i);
      } else {
        pose.translate((3F + i * 5F) / 16F, 0.30F + lift, 0.50F);
        pose.mulPose(Axis.XP.rotationDegrees(90));
        pose.mulPose(Axis.YP.rotationDegrees(rotation));
        Minecraft.getInstance()
            .getItemRenderer()
            .renderStatic(
                stack,
                ItemDisplayContext.FIXED,
                light,
                overlay,
                pose,
                buffers,
                grill.getLevel(),
                i);
      }
      pose.popPose();
    }
    pose.popPose();
  }
}
