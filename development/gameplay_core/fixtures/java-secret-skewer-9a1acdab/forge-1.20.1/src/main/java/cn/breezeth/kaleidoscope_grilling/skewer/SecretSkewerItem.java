package cn.breezeth.kaleidoscope_grilling.skewer;

import cn.breezeth.kaleidoscope_grilling.food.FoodState;
import cn.breezeth.kaleidoscope_grilling.food.HotFoodConfig;


import cn.breezeth.kaleidoscope_grilling.mixin.FoodDataAccessor;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

public final class SecretSkewerItem extends MultiBiteSkewerItem {
  private static final String COOKED_TAG = "Cooked";
  private static final String CREATOR_TAG = "Creator";
  private static final String CREATOR_NAME_TAG = "CreatorName";
  private static final String CREATOR_UUID_TAG = "CreatorUuid";
  private static final String VISUAL_STAGE_TAG = "ClientVisualStage";

  public SecretSkewerItem(Properties properties) {
    super(properties, null, null, 0, AnimationProfile.THREE_RANDOM);
  }

  @Override
  public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
    ItemStack stack = player.getItemInHand(hand);
    if (SkeweringHandler.ingredientCount(stack) != 3) {
      return InteractionResultHolder.fail(stack);
    }
    return super.use(level, player, hand);
  }

  public static boolean isCooked(ItemStack stack) {
    return stack.hasTag() && stack.getTag().getBoolean(COOKED_TAG);
  }

  public static void setCooked(ItemStack stack, boolean cooked) {
    if (cooked) stack.getOrCreateTag().putBoolean(COOKED_TAG, true);
    else if (stack.hasTag()) stack.getTag().remove(COOKED_TAG);
  }

  public static void setVisualStage(ItemStack stack, int stage) {
    stack.getOrCreateTag().putInt(VISUAL_STAGE_TAG, stage);
  }

  public static int getVisualStage(ItemStack stack) {
    return stack.hasTag() ? stack.getTag().getInt(VISUAL_STAGE_TAG) : 0;
  }

  public static void setCreator(ItemStack stack, Player player) {
    stack.getOrCreateTag().putString(CREATOR_NAME_TAG, player.getScoreboardName());
    stack.getOrCreateTag().putUUID(CREATOR_UUID_TAG, player.getUUID());
  }

  public static String getCreator(ItemStack stack) {
    if (stack.hasTag() && stack.getTag().contains(CREATOR_NAME_TAG)) {
      return stack.getTag().getString(CREATOR_NAME_TAG);
    }
    if (stack.hasTag() && stack.getTag().contains(CREATOR_TAG)) {
      return stack.getTag().getString(CREATOR_TAG);
    }
    return "";
  }

  @Override
  protected ItemStack finishFoodAndEffect(ItemStack stack, Level level, LivingEntity entity) {
    ItemStack consumed = stack.copy();
    List<ItemStack> ingredients = SkeweringHandler.readEffectiveIngredientStacks(consumed);
    ItemStack result = super.finishFoodAndEffect(stack, level, entity);
    if (!level.isClientSide) {
      for (ItemStack ingredient : ingredients) {
        if (ingredient.getItem().getFoodProperties(ingredient, entity) == null) continue;
        FoodSnapshot food = FoodSnapshot.capture(entity);
        ItemStack remainder = ingredient.copyWithCount(1).finishUsingItem(level, entity);
        food.restore(entity);
        if (entity instanceof Player player
            && !remainder.isEmpty()
            && !ItemStack.isSameItemSameTags(remainder, ingredient)) {
          player.getInventory().placeItemBackInInventory(remainder);
        }
      }
    }
    return result;
  }

  @Override
  public FoodProperties getFoodProperties(ItemStack stack, @Nullable LivingEntity entity) {
    List<ItemStack> ingredients = SkeweringHandler.readEffectiveIngredientStacks(stack);
    List<ItemStack> rawIngredients = SkeweringHandler.readIngredientStacks(stack);
    if (ingredients.isEmpty()) {
      return new FoodProperties.Builder().nutrition(1).saturationMod(0).build();
    }

    int totalNutrition = 0;
    float weightedSaturation = 0;
    int count = 0;

    for (ItemStack ingredient : ingredients) {
      FoodProperties fp = ingredient.getItem().getFoodProperties(ingredient, entity);
      if (fp == null) continue;
      int n = fp.getNutrition();
      totalNutrition += n;
      weightedSaturation += n * fp.getSaturationModifier();
      count++;
    }

    if (count == 0 || totalNutrition <= 0) {
      return new FoodProperties.Builder().nutrition(1).saturationMod(0).build();
    }

    float coefficient = 0.6F * (hasDuplicateIngredients(rawIngredients) ? 0.8F : 1.0F);
    int nutrition = Math.max(1, (int) Math.floor(totalNutrition * coefficient));
    float saturation = Math.max(0, weightedSaturation / totalNutrition);
    if (!isCooked(stack)) {
      nutrition = Math.max(1, (int) Math.floor(nutrition * 0.5F));
      saturation *= 0.5F;
    }

    return new FoodProperties.Builder().nutrition(nutrition).saturationMod(saturation).build();
  }

  @Override
  public void appendHoverText(
      ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
    List<ItemStack> ingredients = SkeweringHandler.readIngredientStacks(stack);
    for (ItemStack ingredient : ingredients) {
      tooltip.add(
          Component.literal("- ").append(ingredient.getHoverName()).withStyle(ChatFormatting.GRAY));
    }
    String creator = getCreator(stack);
    tooltip.add(
        Component.translatable(
                "tooltip.kaleidoscope_grilling.secret_skewer.creator_story",
                creator.isEmpty()
                    ? Component.translatable("tooltip.kaleidoscope_grilling.secret_skewer.someone")
                    : Component.literal(creator))
            .withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    if (level == null || !FoodState.isHot(stack, level)) {
      boolean cooked = isCooked(stack);
      tooltip.add(Component.empty());
      tooltip.add(
          Component.translatable(
                  cooked
                      ? "tooltip.kaleidoscope_grilling.secret_skewer.cooked"
                      : "tooltip.kaleidoscope_grilling.secret_skewer.raw")
              .withStyle(cooked ? ChatFormatting.GOLD : ChatFormatting.DARK_GRAY));
    }
    if (hasDuplicateIngredients(ingredients)) {
      tooltip.add(
          Component.translatable("tooltip.kaleidoscope_grilling.secret_skewer.duplicate_penalty")
              .withStyle(ChatFormatting.DARK_GRAY));
    }
  }

  private static boolean hasDuplicateIngredients(List<ItemStack> ingredients) {
    for (int i = 1; i < ingredients.size(); i++) {
      for (int j = 0; j < i; j++) {
        if (ItemStack.isSameItemSameTags(ingredients.get(i), ingredients.get(j))) return true;
      }
    }
    return false;
  }

  private record FoodSnapshot(int food, float saturation, float exhaustion) {
    static FoodSnapshot capture(LivingEntity entity) {
      if (!(entity instanceof Player player)) return new FoodSnapshot(0, 0, 0);
      FoodDataAccessor data = (FoodDataAccessor) player.getFoodData();
      return new FoodSnapshot(
          data.grilling$getFoodLevel(),
          data.grilling$getSaturationLevel(),
          data.grilling$getExhaustionLevel());
    }

    void restore(LivingEntity entity) {
      if (!(entity instanceof Player player)) return;
      FoodDataAccessor data = (FoodDataAccessor) player.getFoodData();
      data.grilling$setFoodLevel(food);
      data.grilling$setSaturationLevel(saturation);
      data.grilling$setExhaustionLevel(exhaustion);
    }
  }
}
