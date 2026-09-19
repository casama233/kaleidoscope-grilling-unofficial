package cn.breezeth.kaleidoscope_grilling.seasoning;

import cn.breezeth.kaleidoscope_grilling.KaleidoscopeGrilling;
import cn.breezeth.kaleidoscope_grilling.registry.ModItems;

import cn.breezeth.kaleidoscope_grilling.oil.AnvilPressAnimationAccess;


import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = KaleidoscopeGrilling.MOD_ID, value = Dist.CLIENT)
public final class SeasoningFirstPersonAnimation {
  @SubscribeEvent
  public static void render(RenderHandEvent event) {
    Minecraft minecraft = Minecraft.getInstance();
    var player = minecraft.player;
    if (!(player instanceof AnvilPressAnimationAccess animation)
        || event.getHand() != InteractionHand.MAIN_HAND) return;
    ItemStack stack = player.getMainHandItem();
    boolean shaking =
        player.isUsingItem()
            && player.getUsedItemHand() == InteractionHand.MAIN_HAND
            && player.getUseItem().is(ModItems.PENDING_SEASONING.get());
    float progress = animation.grilling$getSeasoningProgress(event.getPartialTick());
    if (!shaking && (progress < 0.0F || !stack.is(ModItems.SPECIAL_SEASONING.get()))) return;
    event.setCanceled(true);

    float wave =
        shaking
            ? Mth.sin((player.getTicksUsingItem() + event.getPartialTick()) * 1.8F)
            : Mth.sin(progress * Mth.TWO_PI * 2.0F);
    float arc = shaking ? 1.0F : SeasoningAnimation.arc(progress);
    boolean right = player.getMainArm() == HumanoidArm.RIGHT;
    float side = right ? 1.0F : -1.0F;
    PoseStack pose = event.getPoseStack();
    pose.pushPose();
    pose.translate(side * (0.50F + wave * 0.08F), -0.41F + arc * 0.10F, -0.82F);
    pose.mulPose(Axis.XP.rotationDegrees(-28.0F + arc * 42.0F));
    pose.mulPose(Axis.YP.rotationDegrees(180.0F + side * wave * 18.0F));
    pose.mulPose(Axis.ZP.rotationDegrees(side * (22.0F + wave * 25.0F)));
    if (!shaking) pose.mulPose(Axis.ZP.rotationDegrees(180.0F));
    ItemDisplayContext context =
        right
            ? ItemDisplayContext.FIRST_PERSON_RIGHT_HAND
            : ItemDisplayContext.FIRST_PERSON_LEFT_HAND;
    minecraft
        .getItemRenderer()
        .renderStatic(
            stack,
            context,
            event.getPackedLight(),
            OverlayTexture.NO_OVERLAY,
            pose,
            event.getMultiBufferSource(),
            minecraft.level,
            player.getId());
    pose.popPose();
  }

  private SeasoningFirstPersonAnimation() {}
}
