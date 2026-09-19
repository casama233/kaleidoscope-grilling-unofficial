package cn.breezeth.kaleidoscope_grilling.skewer;

import cn.breezeth.kaleidoscope_grilling.client.SkewerAnimationDebug;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.Player;

public final class EnderPearlEatingAnimation {
  public static final float LENGTH_SECONDS = 5.0F;

  private static final float[] RIGHT_POSITION_TIMES = {
    0.0F, 0.45833F, 0.54167F, 0.58333F, 0.95833F, 1.20833F, 1.75F, 1.83333F,
    1.91667F, 1.95833F, 2.33333F, 2.58333F, 2.875F, 3.125F, 3.41667F,
    3.66667F, 4.04167F, 4.45833F
  };
  private static final float[] RIGHT_POSITION_X = {
    3.0F, 8.0F, 8.0F, 6.31F, 5.0F, 8.0F, 8.0F, 8.0F, 8.0F, 6.31F, 5.0F,
    8.0F, 8.0F, 8.0F, 5.0F, 8.0F, 14.0F, 17.0F
  };
  private static final float[] RIGHT_POSITION_Y = {
    -7.0F, -10.0F, -7.0F, -6.81F, -7.0F, -7.0F, -10.0F, -10.0F, -7.0F,
    -7.0F, -7.0F, -5.0F, -7.0F, -6.0F, -6.0F, -6.0F, -8.0F, -17.0F
  };
  private static final float[] RIGHT_POSITION_Z = {
    -5.0F, -9.0F, -7.0F, -6.06F, -5.0F, -2.0F, -9.0F, -9.0F, -7.0F,
    -6.06F, -5.0F, -2.0F, -7.0F, -9.0F, -9.0F, -9.0F, -9.0F, -5.0F
  };

  private static final float[] RIGHT_ROTATION_TIMES = {
    0.0F, 0.45833F, 0.54167F, 0.95833F, 1.20833F, 1.75F, 1.83333F, 1.91667F,
    2.33333F, 2.58333F, 2.875F, 3.125F, 3.41667F, 3.66667F, 4.04167F,
    4.45833F
  };
  private static final float[] RIGHT_ROTATION_X = {
    83.7983F, 114.0944F, 121.5944F, 127.2944F, 101.5944F, 114.0944F,
    114.0944F, 121.5944F, 127.2944F, 101.0133F, 114.0944F, 120.9509F,
    124.3929F, 120.9509F, 120.9509F, 119.9402F
  };
  private static final float[] RIGHT_ROTATION_Y = {
    9.8513F, -3.7751F, -3.7751F, -3.7751F, -3.7751F, -3.7751F, -3.7751F,
    -3.7751F, -3.7751F, -5.2472F, -3.7751F, -7.6725F, -12.7084F, -7.6725F,
    -7.6725F, -8.674F
  };
  private static final float[] RIGHT_ROTATION_Z = {
    16.6457F, 53.8578F, 53.8578F, 53.8578F, 53.8578F, 53.8578F, 53.8578F,
    53.8578F, 53.8578F, 61.235F, 53.8578F, 60.299F, 69.0801F, 60.299F,
    60.299F, 56.6086F
  };

  private static final float[] LEFT_POSITION_TIMES = {
    2.70833F, 2.875F, 3.125F, 3.41667F, 3.54167F, 3.66667F, 4.20833F,
    4.54167F, 4.91667F
  };
  private static final float[] LEFT_POSITION_X = {
    0.0F, -10.0F, -5.0F, -4.0F, -4.0F, -5.0F, -5.0F, -7.0F, -11.0F
  };
  private static final float[] LEFT_POSITION_Y = {
    -1.0F, -9.0F, -3.0F, -3.0F, -3.0F, -3.0F, -2.0F, -6.0F, -6.0F
  };
  private static final float[] LEFT_POSITION_Z = {
    0.0F, -6.0F, -6.0F, -7.0F, -6.0F, -6.0F, -6.0F, -4.0F, 1.0F
  };

  private static final float[] LEFT_ROTATION_TIMES = {
    2.70833F, 2.875F, 3.125F, 3.41667F, 3.54167F, 3.66667F, 4.20833F,
    4.54167F, 4.91667F
  };
  private static final float[] LEFT_ROTATION_X = {
    0.0F, 102.5307F, 112.5307F, 112.2582F, 109.5738F, 94.6483F, 73.7096F,
    118.9719F, 118.9719F
  };
  private static final float[] LEFT_ROTATION_Y = {
    0.0F, -36.835F, -36.835F, -37.8009F, -54.4572F, -31.4733F, -88.9307F,
    -31.664F, -31.664F
  };
  private static final float[] LEFT_ROTATION_Z = {
    0.0F, -7.5897F, -7.5897F, -3.7147F, -1.3876F, 17.4133F, 33.5173F,
    -16.6214F, -16.6214F
  };

  private static final float[] MAIN_ITEM_POSITION_TIMES = {
    0.0F, 2.58333F, 3.41667F, 3.66667F
  };
  private static final float[] MAIN_ITEM_POSITION_Y = {0.0F, 0.0F, -3.0F, -3.0F};
  private static final float[] MAIN_ITEM_ROTATION_TIMES = {
    0.45833F, 0.95833F, 1.20833F, 2.33333F, 2.58333F, 3.41667F, 3.66667F
  };
  private static final float[] MAIN_ITEM_ROTATION_X = {
    0.0F, 12.5F, 0.0F, 12.5F, 0.0F, 37.0F, 37.0F
  };

  private static final float[] SECOND_ITEM_TRANSFORM_TIMES = {0.0F, 3.54167F};
  private static final float[] SECOND_ITEM_POSITION_X = {0.0F, -9.0F};
  private static final float[] SECOND_ITEM_POSITION_Y = {0.0F, -2.0F};
  private static final float[] SECOND_ITEM_POSITION_Z = {0.0F, 5.0F};
  private static final float[] SECOND_ITEM_ROTATION_X = {0.0F, -75.0F};
  private static final float[] SECOND_ITEM_ROTATION_Y = {0.0F, 0.0F};
  private static final float[] SECOND_ITEM_ROTATION_Z = {0.0F, -82.5F};
  private static final float[] SECOND_ITEM_SCALE_TIMES = {3.5F, 3.54167F, 4.16667F, 4.20833F};
  private static final float[] SECOND_ITEM_SCALE = {0.0F, 1.0F, 1.0F, 0.0F};

  private static final float[] ONE_RIGHT_TIMES = {0F, .75F, 1F, 1.16667F, 1.54167F, 1.91667F, 2.5F, 2.70833F, 2.83333F, 3.25F, 3.375F, 3.75F, 4.125F};
  private static final float[] ONE_RIGHT_X = {3F, 8F, 8F, 8.8F, 8F, 8F, 8F, 8F, 6F, 6F, 7F, 8F, 17F};
  private static final float[] ONE_RIGHT_Y = {-7F, -7F, -6F, -5.86F, -6F, -6F, -6F, -6F, -5F, -5F, -5F, -6F, -17F};
  private static final float[] ONE_RIGHT_Z = {-5F, -7F, -9F, -8.15F, -9F, -9F, -15F, -16F, -10F, -10F, -14F, -9F, -5F};
  private static final float[] ONE_RIGHT_ROT_X = {83.7983F,114.0944F,120.9509F,108.7506F,120.9509F,120.9509F,170.9509F,170.9509F,178.4509F,178.4509F,160.9509F,120.9509F,119.9402F};
  private static final float[] ONE_RIGHT_ROT_Y = {9.8513F,-3.7751F,-7.6725F,-16.0773F,-7.6725F,-7.6725F,-7.6725F,-7.6725F,-7.6725F,-7.6725F,-7.6725F,-7.6725F,-8.674F};
  private static final float[] ONE_RIGHT_ROT_Z = {16.6457F,53.8578F,60.299F,73.684F,60.299F,60.299F,60.299F,60.299F,60.299F,60.299F,60.299F,60.299F,56.6086F};
  private static final float[] ONE_LEFT_TIMES = {.58333F,.75F,1F,1.125F,1.16667F,1.20833F,1.54167F,1.75F,2F,2.16667F,2.75F};
  private static final float[] ONE_LEFT_X = {0F,-10F,-5F,-4.24F,-3.24F,-4.24F,-5F,-5F,-5F,-7F,-11F};
  private static final float[] ONE_LEFT_Y = {-1F,-9F,-3F,-2.58F,-2.58F,-2.58F,-3F,-3F,-3F,-3F,-11F};
  private static final float[] ONE_LEFT_Z = {0F,-6F,-6F,-6.46F,-7.46F,-6.46F,-6F,-6F,-6F,-5F,-1F};
  private static final float[] ONE_LEFT_ROT_X = {0F,102.5307F,112.5307F,113.2593F,113.2593F,113.2593F,94.6483F,102.1653F,107.1653F,107.1653F,105.9851F};
  private static final float[] ONE_LEFT_ROT_Y = {0F,-36.835F,-36.835F,-36.358F,-36.358F,-36.358F,-31.4733F,-56.3504F,-56.3504F,-56.3504F,-27.8382F};
  private static final float[] ONE_LEFT_ROT_Z = {0F,-7.5897F,-7.5897F,-6.1189F,-6.1189F,-6.1189F,17.4133F,13.8699F,13.8699F,13.8699F,-5.2621F};

  private EnderPearlEatingAnimation() {}

  public static Pose sample(Player player, float partialTick) {
    return sample(player, partialTick, MultiBiteSkewerItem.AnimationProfile.THREE);
  }

  public static Pose sample(Player player, float partialTick, MultiBiteSkewerItem.AnimationProfile profile) {
    float seconds =
        Mth.clamp(
            (player.getUseItem().getUseDuration()
                    - player.getUseItemRemainingTicks()
                    + partialTick)
                / 20.0F,
            0.0F,
            LENGTH_SECONDS);
    seconds = SkewerAnimationDebug.seconds(player, seconds);
    return profile == MultiBiteSkewerItem.AnimationProfile.ONE ? sampleOne(seconds) : sample(seconds);
  }

  private static Pose sampleOne(float seconds) {
    float time = Mth.clamp(seconds, 0.0F, 4.5F);
    ArmPose activeArm = new ArmPose(
        catmullRom(time, ONE_RIGHT_TIMES, ONE_RIGHT_X), catmullRom(time, ONE_RIGHT_TIMES, ONE_RIGHT_Y), catmullRom(time, ONE_RIGHT_TIMES, ONE_RIGHT_Z),
        catmullRom(time, ONE_RIGHT_TIMES, ONE_RIGHT_ROT_X), catmullRom(time, ONE_RIGHT_TIMES, ONE_RIGHT_ROT_Y), catmullRom(time, ONE_RIGHT_TIMES, ONE_RIGHT_ROT_Z));
    ArmPose helperArm = new ArmPose(
        catmullRom(time, ONE_LEFT_TIMES, ONE_LEFT_X), catmullRom(time, ONE_LEFT_TIMES, ONE_LEFT_Y), catmullRom(time, ONE_LEFT_TIMES, ONE_LEFT_Z),
        catmullRom(time, ONE_LEFT_TIMES, ONE_LEFT_ROT_X), catmullRom(time, ONE_LEFT_TIMES, ONE_LEFT_ROT_Y), catmullRom(time, ONE_LEFT_TIMES, ONE_LEFT_ROT_Z));
    ItemPose mainItem = new ItemPose(0F, catmullRom(time, new float[]{0F,.45833F,1.29167F}, new float[]{0F,0F,-3F}), 0F,
        catmullRom(time, new float[]{.20833F,.45833F,1.29167F}, new float[]{12.5F,0F,29.5F}), 0F, 0F, 1F);
    float secondScale = time >= 1.16667F ? 1F : 0F;
    ItemPose secondItem = new ItemPose(-9F, -2F, 5F, 75F, 0F, -275F, secondScale);
    return new Pose(activeArm, helperArm, mainItem, secondItem);
  }

  public static Pose sample(float seconds) {
    float time = Mth.clamp(seconds, 0.0F, LENGTH_SECONDS);
    ArmPose activeArm =
        new ArmPose(
            catmullRom(time, RIGHT_POSITION_TIMES, RIGHT_POSITION_X),
            catmullRom(time, RIGHT_POSITION_TIMES, RIGHT_POSITION_Y),
            catmullRom(time, RIGHT_POSITION_TIMES, RIGHT_POSITION_Z),
            catmullRom(time, RIGHT_ROTATION_TIMES, RIGHT_ROTATION_X),
            catmullRom(time, RIGHT_ROTATION_TIMES, RIGHT_ROTATION_Y),
            catmullRom(time, RIGHT_ROTATION_TIMES, RIGHT_ROTATION_Z));
    ArmPose helperArm =
        new ArmPose(
            catmullRom(time, LEFT_POSITION_TIMES, LEFT_POSITION_X),
            catmullRom(time, LEFT_POSITION_TIMES, LEFT_POSITION_Y),
            catmullRom(time, LEFT_POSITION_TIMES, LEFT_POSITION_Z),
            catmullRom(time, LEFT_ROTATION_TIMES, LEFT_ROTATION_X),
            catmullRom(time, LEFT_ROTATION_TIMES, LEFT_ROTATION_Y),
            catmullRom(time, LEFT_ROTATION_TIMES, LEFT_ROTATION_Z));
    ItemPose mainItem =
        new ItemPose(
            0.0F,
            catmullRom(time, MAIN_ITEM_POSITION_TIMES, MAIN_ITEM_POSITION_Y),
            0.0F,
            catmullRom(time, MAIN_ITEM_ROTATION_TIMES, MAIN_ITEM_ROTATION_X),
            0.0F,
            0.0F,
            1.0F);
    ItemPose secondItem =
        new ItemPose(
            catmullRom(time, SECOND_ITEM_TRANSFORM_TIMES, SECOND_ITEM_POSITION_X),
            catmullRom(time, SECOND_ITEM_TRANSFORM_TIMES, SECOND_ITEM_POSITION_Y),
            catmullRom(time, SECOND_ITEM_TRANSFORM_TIMES, SECOND_ITEM_POSITION_Z),
            catmullRom(time, SECOND_ITEM_TRANSFORM_TIMES, SECOND_ITEM_ROTATION_X),
            catmullRom(time, SECOND_ITEM_TRANSFORM_TIMES, SECOND_ITEM_ROTATION_Y),
            catmullRom(time, SECOND_ITEM_TRANSFORM_TIMES, SECOND_ITEM_ROTATION_Z),
            Mth.clamp(catmullRom(time, SECOND_ITEM_SCALE_TIMES, SECOND_ITEM_SCALE), 0.0F, 1.0F));
    return new Pose(activeArm, helperArm, mainItem, secondItem);
  }

  public static void applyActiveArm(
      ModelPart arm,
      HumanoidArm actualSide,
      ArmPose pose,
      MultiBiteSkewerItem.AnimationProfile profile) {
    applyArm(arm, actualSide, true, pose);
    if (profile == MultiBiteSkewerItem.AnimationProfile.ONE) {
      arm.y += 3.8F;
      arm.zRot -= (actualSide == HumanoidArm.RIGHT ? 1.0F : -1.0F) * 7.5F * Mth.DEG_TO_RAD;
      moveTowardHand(arm, 1.0F);
    }
  }

  public static void applyHelperArm(
      ModelPart arm,
      HumanoidArm actualSide,
      ArmPose pose,
      MultiBiteSkewerItem.AnimationProfile profile) {
    applyArm(arm, actualSide, false, pose);
    if (profile == MultiBiteSkewerItem.AnimationProfile.ONE) {
      arm.y += 3.8F;
    }
  }

  private static void moveTowardHand(ModelPart arm, float distance) {
    float sinX = Mth.sin(arm.xRot);
    float cosX = Mth.cos(arm.xRot);
    float sinY = Mth.sin(arm.yRot);
    float cosY = Mth.cos(arm.yRot);
    float sinZ = Mth.sin(arm.zRot);
    float cosZ = Mth.cos(arm.zRot);
    arm.x += distance * (cosZ * sinY * sinX - sinZ * cosX);
    arm.y += distance * (sinZ * sinY * sinX + cosZ * cosX);
    arm.z += distance * cosY * sinX;
  }

  public static void transformMainItem(
      PoseStack poseStack, HumanoidArm actualSide, ItemPose pose) {
    float side = actualSide == HumanoidArm.RIGHT ? 1.0F : -1.0F;
    translateChildFromAuthoredArm(
        poseStack, actualSide, true, 1.975F, -8.925F, -7.575F, pose);
    poseStack.mulPose(Axis.XP.rotationDegrees(180.0F + pose.rotationX()));
    poseStack.mulPose(Axis.YP.rotationDegrees(side * pose.rotationY()));
    poseStack.mulPose(Axis.ZP.rotationDegrees(side * pose.rotationZ()));
    poseStack.translate(0.0F, 7.0F / 16.0F, 2.0F / 16.0F);
  }

  public static void transformSecondItem(
      PoseStack poseStack,
      HumanoidArm actualSide,
      ItemPose pose,
      MultiBiteSkewerItem.AnimationProfile profile) {
    float side = actualSide == HumanoidArm.RIGHT ? 1.0F : -1.0F;
    translateChildFromAuthoredArm(
        poseStack, actualSide, false, 10.0F, -8.875F, -5.75F, pose);
    poseStack.mulPose(Axis.ZP.rotationDegrees(pose.rotationZ()));
    poseStack.mulPose(Axis.YP.rotationDegrees(side * pose.rotationY()));
    poseStack.mulPose(Axis.XP.rotationDegrees(-pose.rotationX()));
    if (profile == MultiBiteSkewerItem.AnimationProfile.ONE) {
      poseStack.mulPose(Axis.XP.rotationDegrees(180.0F));
    }
    poseStack.mulPose(Axis.ZP.rotationDegrees(95.0F));
    poseStack.scale(pose.scale(), pose.scale(), pose.scale());
  }

  private static void translateChildFromAuthoredArm(
      PoseStack poseStack,
      HumanoidArm actualSide,
      boolean authoredRight,
      float authoredX,
      float authoredY,
      float authoredZ,
      ItemPose pose) {
    float actualSign = actualSide == HumanoidArm.RIGHT ? 1.0F : -1.0F;
    float authoredSign = authoredRight ? 1.0F : -1.0F;
    float mirror = actualSign * authoredSign;
    poseStack.translate(
        (-mirror * (authoredX + pose.positionX()) + actualSign) / 16.0F,
        (-authoredY - pose.positionY()) / 16.0F,
        (authoredZ + pose.positionZ()) / 16.0F);
  }

  private static void applyArm(
      ModelPart arm, HumanoidArm actualSide, boolean authoredRight, ArmPose pose) {
    float actualSign = actualSide == HumanoidArm.RIGHT ? 1.0F : -1.0F;
    float authoredSign = authoredRight ? 1.0F : -1.0F;
    float xRot = -pose.rotationX() * Mth.DEG_TO_RAD;
    float yRot = actualSign * pose.rotationY() * Mth.DEG_TO_RAD;
    float zRot = pose.rotationZ() * Mth.DEG_TO_RAD;

    float pivotDifference = -actualSign;
    float cosY = Mth.cos(yRot);
    float sinY = Mth.sin(yRot);
    float cosZ = Mth.cos(zRot);
    float sinZ = Mth.sin(zRot);
    float correctionX = pivotDifference * cosZ * cosY;
    float correctionY = pivotDifference * sinZ * cosY;
    float correctionZ = pivotDifference * -sinY;

    arm.x = -actualSign * (4.0F + authoredSign * pose.positionX()) + correctionX;
    arm.y = 2.0F - pose.positionY() + correctionY;
    arm.z = pose.positionZ() + correctionZ;
    arm.xRot = xRot;
    arm.yRot = yRot;
    arm.zRot = zRot;
  }

  private static float catmullRom(float time, float[] times, float[] values) {
    if (time <= times[0]) return values[0];
    int last = times.length - 1;
    if (time >= times[last]) return values[last];

    int right = 1;
    while (time > times[right]) right++;
    int left = right - 1;
    int before = Math.max(0, left - 1);
    int after = Math.min(last, right + 1);
    float progress = (time - times[left]) / (times[right] - times[left]);
    float progress2 = progress * progress;
    float progress3 = progress2 * progress;
    float p0 = values[before];
    float p1 = values[left];
    float p2 = values[right];
    float p3 = values[after];
    return 0.5F
        * ((2.0F * p1)
            + (-p0 + p2) * progress
            + (2.0F * p0 - 5.0F * p1 + 4.0F * p2 - p3) * progress2
            + (-p0 + 3.0F * p1 - 3.0F * p2 + p3) * progress3);
  }

  public record Pose(ArmPose activeArm, ArmPose helperArm, ItemPose mainItem, ItemPose secondItem) {}

  public record ArmPose(
      float positionX,
      float positionY,
      float positionZ,
      float rotationX,
      float rotationY,
      float rotationZ) {}

  public record ItemPose(
      float positionX,
      float positionY,
      float positionZ,
      float rotationX,
      float rotationY,
      float rotationZ,
      float scale) {}
}
