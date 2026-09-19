package cn.breezeth.kaleidoscope_grilling.mixin;

import cn.breezeth.kaleidoscope_grilling.skewer.EnderPearlEatingAnimation;
import cn.breezeth.kaleidoscope_grilling.client.ClientSkewerEatingSound;
import cn.breezeth.kaleidoscope_grilling.skewer.MultiBiteSkewerItem;
import cn.breezeth.kaleidoscope_grilling.skewer.SkewerEatingAnimation;
import cn.breezeth.kaleidoscope_grilling.skewer.SkewerEatingPiece;
import cn.breezeth.kaleidoscope_grilling.skewer.SkewerRecipes;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ItemInHandRenderer.class)
public abstract class ItemInHandSkewerEatingMixin {
  @Inject(method = "renderArmWithItem", at = @At("HEAD"), cancellable = true)
  private void grilling$renderSkewerEating(
      AbstractClientPlayer player,
      float partialTick,
      float pitch,
      InteractionHand hand,
      float swingProgress,
      ItemStack stack,
      float equippedProgress,
      PoseStack pose,
      MultiBufferSource buffers,
      int packedLight,
      CallbackInfo ci) {
    if (!player.isUsingItem()) return;
    MultiBiteSkewerItem.AnimationProfile configured =
        SkewerRecipes.animationProfile(player.getUseItem());
    if (configured == null) return;
    MultiBiteSkewerItem.AnimationProfile profile =
        ClientSkewerEatingSound.profile(player.getId(), configured);
    if (profile == MultiBiteSkewerItem.AnimationProfile.THREE
        || profile == MultiBiteSkewerItem.AnimationProfile.ONE) {
      grilling$renderEnderPearlEating(
          player, partialTick, hand, pose, buffers, packedLight, profile);
      ci.cancel();
      return;
    }
    if (player.getUsedItemHand() != hand) {
      // These authored animations only render the active hand unless they explicitly add a helper.
      ci.cancel();
      return;
    }
    if (!SkewerRecipes.usesCustomEating(stack)) return;

    HumanoidArm arm =
        hand == InteractionHand.MAIN_HAND ? player.getMainArm() : player.getMainArm().getOpposite();
    SkewerEatingAnimation.ArmPose animation =
        SkewerEatingAnimation.sample(player, partialTick, profile);
    PlayerRenderer playerRenderer =
        (PlayerRenderer) Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(player);
    PlayerModel<AbstractClientPlayer> model = playerRenderer.getModel();
    ModelPart armPart = arm == HumanoidArm.RIGHT ? model.rightArm : model.leftArm;
    ModelPart sleevePart = arm == HumanoidArm.RIGHT ? model.rightSleeve : model.leftSleeve;
    SkewerEatingAnimation.applyToArm(armPart, arm, animation, profile);
    sleevePart.copyFrom(armPart);
    armPart.visible = true;
    sleevePart.visible = true;

    pose.pushPose();
    pose.translate(0.0F, -player.getEyeHeight(), 0.0F);
    pose.scale(-1.0F, -1.0F, 1.0F);
    pose.translate(0.0F, -1.501F, 0.0F);

    if (!player.isInvisible()) {
      armPart.render(
          pose,
          buffers.getBuffer(RenderType.entitySolid(player.getSkinTextureLocation())),
          packedLight,
          OverlayTexture.NO_OVERLAY);
      sleevePart.render(
          pose,
          buffers.getBuffer(RenderType.entityTranslucent(player.getSkinTextureLocation())),
          packedLight,
          OverlayTexture.NO_OVERLAY);
    }

    pose.pushPose();
    model.translateToHand(arm, pose);
    SkewerEatingAnimation.transformItem(pose, arm, animation);
    Minecraft.getInstance()
        .getItemRenderer()
        .renderStatic(
            player,
            stack,
            ItemDisplayContext.NONE,
            arm == HumanoidArm.LEFT,
            pose,
            buffers,
            player.level(),
            packedLight,
            OverlayTexture.NO_OVERLAY,
            player.getId());
    pose.popPose();
    pose.popPose();
    ci.cancel();
  }

  private static void grilling$renderEnderPearlEating(
      AbstractClientPlayer player,
      float partialTick,
      InteractionHand renderedHand,
      PoseStack pose,
      MultiBufferSource buffers,
      int packedLight,
      MultiBiteSkewerItem.AnimationProfile profile) {
    HumanoidArm renderedArm =
        renderedHand == InteractionHand.MAIN_HAND
            ? player.getMainArm()
            : player.getMainArm().getOpposite();
    HumanoidArm activeArm =
        player.getUsedItemHand() == InteractionHand.MAIN_HAND
            ? player.getMainArm()
            : player.getMainArm().getOpposite();
    boolean active = renderedArm == activeArm;
    EnderPearlEatingAnimation.Pose animation =
        EnderPearlEatingAnimation.sample(player, partialTick, profile);

    PlayerRenderer playerRenderer =
        (PlayerRenderer) Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(player);
    PlayerModel<AbstractClientPlayer> model = playerRenderer.getModel();
    ModelPart armPart = renderedArm == HumanoidArm.RIGHT ? model.rightArm : model.leftArm;
    ModelPart sleevePart =
        renderedArm == HumanoidArm.RIGHT ? model.rightSleeve : model.leftSleeve;
    if (active) {
      EnderPearlEatingAnimation.applyActiveArm(
          armPart, renderedArm, animation.activeArm(), profile);
    } else {
      EnderPearlEatingAnimation.applyHelperArm(
          armPart, renderedArm, animation.helperArm(), profile);
    }
    sleevePart.copyFrom(armPart);
    armPart.visible = true;
    sleevePart.visible = true;

    pose.pushPose();
    pose.translate(0.0F, -player.getEyeHeight(), 0.0F);
    pose.scale(-1.0F, -1.0F, 1.0F);
    pose.translate(0.0F, -1.501F, 0.0F);
    if (!player.isInvisible()) {
      armPart.render(
          pose,
          buffers.getBuffer(RenderType.entitySolid(player.getSkinTextureLocation())),
          packedLight,
          OverlayTexture.NO_OVERLAY);
      sleevePart.render(
          pose,
          buffers.getBuffer(RenderType.entityTranslucent(player.getSkinTextureLocation())),
          packedLight,
          OverlayTexture.NO_OVERLAY);
    }

    if (active) {
      pose.pushPose();
      model.translateToHand(renderedArm, pose);
      EnderPearlEatingAnimation.transformMainItem(
          pose, renderedArm, animation.mainItem());
      Minecraft.getInstance()
          .getItemRenderer()
          .renderStatic(
              player,
              player.getUseItem(),
              ItemDisplayContext.NONE,
              renderedArm == HumanoidArm.LEFT,
              pose,
              buffers,
              player.level(),
              packedLight,
              OverlayTexture.NO_OVERLAY,
              player.getId());
      pose.popPose();
    } else if (animation.secondItem().scale() > 0.001F) {
      pose.pushPose();
      model.translateToHand(renderedArm, pose);
      EnderPearlEatingAnimation.transformSecondItem(
          pose, renderedArm, animation.secondItem(), profile);
      BakedModel piece = SkewerEatingPiece.fixedModel(player.getUseItem(), profile);
      ItemStack ingredient = SkewerEatingPiece.ingredient(player.getUseItem(), profile);
      if (piece != null) {
        Minecraft.getInstance().getItemRenderer().render(
            player.getUseItem(), ItemDisplayContext.NONE, renderedArm == HumanoidArm.LEFT,
            pose, buffers, packedLight, OverlayTexture.NO_OVERLAY, piece);
      } else if (!ingredient.isEmpty()) {
        Minecraft.getInstance().getItemRenderer().renderStatic(
            player, ingredient, ItemDisplayContext.NONE, renderedArm == HumanoidArm.LEFT,
            pose, buffers, player.level(), packedLight, OverlayTexture.NO_OVERLAY, player.getId());
      }
      pose.popPose();
    }
    pose.popPose();
  }
}
