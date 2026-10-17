package cn.breezeth.kaleidoscope_grilling.skewer;

import cn.breezeth.kaleidoscope_grilling.KaleidoscopeGrilling;
import cn.breezeth.kaleidoscope_grilling.registry.ModItems;

import cn.breezeth.kaleidoscope_grilling.food.FoodState;
import cn.breezeth.kaleidoscope_grilling.food.HotFoodConfig;
import cn.breezeth.kaleidoscope_grilling.food.HotFoodGuiBadge;

import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexSorting;
import com.mojang.logging.LogUtils;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.CreativeModeInventoryScreen;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.ForgeHooksClient;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix4f;
import org.slf4j.Logger;

public final class SkewerGuiIconCache {
  private static final float GUI_ITEM_DEPTH = 150.0F;
  private static final Logger LOGGER = LogUtils.getLogger();
  private static final int BASE_SIZE = 32;
  private static final int CACHE_SIZE = 64;
  private static final int MAX_CUSTOM_ICONS = 64;
  private static final int FIXED_BAKES_PER_FRAME = 2;
  private static final int CUSTOM_BAKES_PER_FRAME = 1;
  private static final boolean JVM_DISABLED =
      Boolean.getBoolean("kaleidoscope_grilling.disableGuiIconCache");
  private static final Map<String, ResourceLocation> FIXED_CACHE = new HashMap<>();
  private static final LinkedHashMap<String, ResourceLocation> CUSTOM_CACHE =
      new LinkedHashMap<>(MAX_CUSTOM_ICONS, 0.75F, true);
  private static final Set<String> PENDING_FIXED = new LinkedHashSet<>();
  private static final Set<String> PENDING_CUSTOM = new LinkedHashSet<>();
  private static final Set<String> FAILED = new HashSet<>();
  private static final Map<String, Integer> FAILURE_COUNTS = new HashMap<>();
  private static final Map<ItemStack, IngredientKeyData> INGREDIENT_KEY_CACHE =
      new IdentityHashMap<>();
  private static long customTextureSequence;
  private static long budgetFrame = Long.MIN_VALUE;
  private static int fixedBudget;
  private static int customBudget;

  public static boolean render(GuiGraphics graphics, ItemStack stack, int x, int y) {
    if (SkewerItemRenderContext.isCapturing() || SkewerOutlineRender.isActive())
      return false;
    Minecraft minecraft = Minecraft.getInstance();
    if (minecraft.screen instanceof CreativeModeInventoryScreen && minecraft.level != null)
      stack = SkeweringHandler.creativePreviewFrame(stack, minecraft.level.getGameTime());
    boolean custom = isCompletedCustom(minecraft, stack);
    boolean generated = SkewerRecipes.usesGeneratedModel(stack) || isGeneratedKubeSkewer(stack);
    boolean composedCustom =
        !HotFoodConfig.USE_CUSTOM_SKEWER_64X_CACHE.get()
            && (isStartedCustom(minecraft, stack) || generated);
    boolean fixed = isBuiltInFixedSkewer(stack);
    boolean failed =
        stack.is(ModItems.MYSTERIOUS_SKEWER.get()) || stack.is(ModItems.DARK_GRILLING.get());
    if (!custom && !composedCustom && !fixed && !failed) return false;
    ResourceLocation itemId = ForgeRegistries.ITEMS.getKey(stack.getItem());
    if (itemId == null) return false;
    if (failed) {
      if (HotFoodConfig.USE_FIXED_SKEWER_64X_CACHE.get()) return false;
      renderStaticIcon(graphics, failedIcon(stack, minecraft), x, y);
      return true;
    }
    boolean cooked =
        SkewerRecipes.isCookedSkewer(stack)
            || stack.is(ModItems.SECRET_SKEWER.get()) && SecretSkewerItem.isCooked(stack);
    boolean hot = cooked && minecraft.level != null && FoodState.isHot(stack, minecraft.level);
    if (fixed && !HotFoodConfig.USE_FIXED_SKEWER_64X_CACHE.get()) {
      renderStaticIcon(graphics, fixedIcon(itemId, cooked, minecraft), x, y);
      HotFoodGuiBadge.render(graphics, stack, minecraft.level, x, y);
      return true;
    }
    if (composedCustom) {
      if (!isEnabled()) return false;
      String state = cooked ? "cooked" : "raw";
      String key =
          "16/"
              + customKey(minecraft, stack, itemId, state)
              + "/v"
              + CustomSkewerGuiTexture.variantBits(stack);
      ResourceLocation texture = CUSTOM_CACHE.get(key);
      if (texture == null) {
        ResourceLocation textureId =
            new ResourceLocation(
                KaleidoscopeGrilling.MOD_ID, "skewer_gui_cache/custom_" + customTextureSequence++);
        texture = CustomSkewerGuiTexture.bake(stack, textureId);
        if (texture == null) return false;
        CUSTOM_CACHE.put(key, texture);
        trimCustomCache(minecraft);
      }
      renderCachedIcon(graphics, texture, x, y, 16);
      HotFoodGuiBadge.render(graphics, stack, minecraft.level, x, y);
      return true;
    }
    if (custom ? !isEnabled() : !isFixedCacheEnabled()) return false;
    String state = cooked ? hot ? "hot" : "cooked" : "raw";
    if (cooked
        && itemId != null
        && "grilled_slime_skewer".equals(itemId.getPath())
        && minecraft.level != null) {
      state += "_frame_" + (minecraft.level.getGameTime() / 4L % 5L);
    }
    int size = CACHE_SIZE;
    String key = custom ? customKey(minecraft, stack, itemId, state) : itemId + "/" + state;
    if (FAILED.contains(key)) return false;
    Map<String, ResourceLocation> cache = custom ? CUSTOM_CACHE : FIXED_CACHE;
    ResourceLocation texture = cache.get(key);
    if (texture == null) {
      Set<String> pending = custom ? PENDING_CUSTOM : PENDING_FIXED;
      if (pending.add(key)) {
        if (custom) trimPendingCustom();
        return false;
      }
      refreshBudgets(minecraft);
      if (custom ? customBudget <= 0 : fixedBudget <= 0) return false;
      if (custom) customBudget--;
      else fixedBudget--;
      pending.remove(key);
      ResourceLocation textureId =
          custom
              ? new ResourceLocation(
                  KaleidoscopeGrilling.MOD_ID, "skewer_gui_cache/custom_" + customTextureSequence++)
              : new ResourceLocation(
                  KaleidoscopeGrilling.MOD_ID,
                  "skewer_gui_cache/" + itemId.getPath() + "_" + state);
      texture = bake(graphics, stack, itemId, state, textureId, outlineColor(cooked, hot), size);
      if (texture == null) {
        int failures = FAILURE_COUNTS.merge(key, 1, Integer::sum);
        if (failures >= 2) FAILED.add(key);
        return false;
      }
      FAILURE_COUNTS.remove(key);
      cache.put(key, texture);
      if (custom) trimCustomCache(minecraft);
    }
    renderCachedIcon(graphics, texture, x, y, size);
    HotFoodGuiBadge.render(graphics, stack, minecraft.level, x, y);
    return true;
  }

  private static ResourceLocation fixedIcon(
      ResourceLocation itemId, boolean cooked, Minecraft minecraft) {
    String suffix = cooked ? "_cooked" : "_raw";
    if (cooked
        && "grilled_slime_skewer".equals(itemId.getPath())
        && minecraft.level != null) {
      suffix += "_frame_" + (minecraft.level.getGameTime() / 4L % 5L);
    }
    return new ResourceLocation(
        KaleidoscopeGrilling.MOD_ID,
        "textures/item/fixed_skewer_gui_16/" + itemId.getPath() + suffix + ".png");
  }

  private static ResourceLocation failedIcon(ItemStack stack, Minecraft minecraft) {
    String name = "dark_grilling";
    if (stack.is(ModItems.MYSTERIOUS_SKEWER.get())) {
      long gameTime = minecraft.level == null ? 0L : minecraft.level.getGameTime();
      name = "mysterious_skewer_frame_" + (gameTime / 4L % 5L);
    }
    return new ResourceLocation(
        KaleidoscopeGrilling.MOD_ID,
        "textures/item/fixed_skewer_gui_16/" + name + ".png");
  }

  private static void renderStaticIcon(
      GuiGraphics graphics, ResourceLocation texture, int x, int y) {
    graphics.pose().pushPose();
    graphics.pose().translate(0.0F, 0.0F, GUI_ITEM_DEPTH);
    RenderSystem.enableBlend();
    RenderSystem.defaultBlendFunc();
    graphics.blit(texture, x, y, 16, 16, 0.0F, 0.0F, 16, 16, 16, 16);
    RenderSystem.disableBlend();
    graphics.pose().popPose();
  }

  private static void renderCachedIcon(
      GuiGraphics graphics, ResourceLocation texture, int x, int y, int size) {
    graphics.pose().pushPose();
    graphics.pose().translate(0.0F, 0.0F, GUI_ITEM_DEPTH);
    graphics.blit(texture, x, y, 16, 16, 0.0F, 0.0F, size, size, size, size);
    graphics.pose().popPose();
  }

  public static boolean hasCachedIcon(ItemStack stack) {
    if (!isEnabled() || SkewerItemRenderContext.isCapturing()) return false;
    Minecraft minecraft = Minecraft.getInstance();
    if (minecraft.screen instanceof CreativeModeInventoryScreen && minecraft.level != null)
      stack = SkeweringHandler.creativePreviewFrame(stack, minecraft.level.getGameTime());
    boolean use64 = HotFoodConfig.USE_CUSTOM_SKEWER_64X_CACHE.get();
    boolean generated = SkewerRecipes.usesGeneratedModel(stack) || isGeneratedKubeSkewer(stack);
    if (use64
        ? !isCompletedCustom(minecraft, stack)
        : !isStartedCustom(minecraft, stack) && !generated) {
      return false;
    }
    ResourceLocation itemId = ForgeRegistries.ITEMS.getKey(stack.getItem());
    boolean cooked =
        SkewerRecipes.isCookedSkewer(stack)
            || stack.is(ModItems.SECRET_SKEWER.get()) && SecretSkewerItem.isCooked(stack);
    boolean hot = cooked && minecraft.level != null && FoodState.isHot(stack, minecraft.level);
    String state = cooked ? "cooked" : "raw";
    String key = customKey(minecraft, stack, itemId, state);
    if (!HotFoodConfig.USE_CUSTOM_SKEWER_64X_CACHE.get()) {
      key = "16/" + key + "/v" + CustomSkewerGuiTexture.variantBits(stack);
    }
    else if (hot) key = customKey(minecraft, stack, itemId, "hot");
    return CUSTOM_CACHE.containsKey(key);
  }

  static ResourceLocation recipeIcon16(ItemStack stack) {
    Minecraft minecraft = Minecraft.getInstance();
    ResourceLocation itemId = ForgeRegistries.ITEMS.getKey(stack.getItem());
    if (itemId == null) return null;
    if ((SkewerRecipes.isRawSkewer(stack) || SkewerRecipes.isCookedSkewer(stack))
        && !HotFoodConfig.USE_FIXED_SKEWER_64X_CACHE.get()) {
      return fixedIcon(itemId, SkewerRecipes.isCookedSkewer(stack), minecraft);
    }
    if (HotFoodConfig.USE_CUSTOM_SKEWER_64X_CACHE.get()
        || !isStartedCustom(minecraft, stack)
        || !isEnabled()) return null;
    String key =
        "16/"
            + customKey(minecraft, stack, itemId, "raw")
            + "/v"
            + CustomSkewerGuiTexture.variantBits(stack);
    ResourceLocation texture = CUSTOM_CACHE.get(key);
    if (texture != null) return texture;
    ResourceLocation textureId =
        new ResourceLocation(
            KaleidoscopeGrilling.MOD_ID, "skewer_gui_cache/custom_" + customTextureSequence++);
    texture = CustomSkewerGuiTexture.bake(stack, textureId);
    if (texture == null) return null;
    CUSTOM_CACHE.put(key, texture);
    trimCustomCache(minecraft);
    return texture;
  }

  /** Returns the authored/composed 16x16 icon without using an active bite animation stage. */
  static ResourceLocation eatingHudIcon16(ItemStack stack) {
    Minecraft minecraft = Minecraft.getInstance();
    ResourceLocation itemId = ForgeRegistries.ITEMS.getKey(stack.getItem());
    if (itemId == null) return null;
    if (stack.is(ModItems.MYSTERIOUS_SKEWER.get()) || stack.is(ModItems.DARK_GRILLING.get()))
      return failedIcon(stack, minecraft);
    if (isBuiltInFixedSkewer(stack))
      return fixedIcon(itemId, SkewerRecipes.isCookedSkewer(stack), minecraft);
    if ((!isStartedCustom(minecraft, stack)
            && !SkewerRecipes.usesGeneratedModel(stack)
            && !isGeneratedKubeSkewer(stack))
        || !isEnabled()) return null;

    boolean cooked = stack.is(ModItems.SECRET_SKEWER.get()) && SecretSkewerItem.isCooked(stack);
    String key =
        "eating_hud/"
            + customKey(minecraft, stack, itemId, cooked ? "cooked" : "raw")
            + "/v"
            + CustomSkewerGuiTexture.variantBits(stack);
    ResourceLocation texture = CUSTOM_CACHE.get(key);
    if (texture != null) return texture;
    ResourceLocation textureId =
        new ResourceLocation(
            KaleidoscopeGrilling.MOD_ID, "skewer_gui_cache/custom_" + customTextureSequence++);
    texture = CustomSkewerGuiTexture.bake(stack, textureId);
    if (texture == null) return null;
    CUSTOM_CACHE.put(key, texture);
    trimCustomCache(minecraft);
    return texture;
  }

  public static void clear() {
    Minecraft minecraft = Minecraft.getInstance();
    FIXED_CACHE.values().forEach(minecraft.getTextureManager()::release);
    CUSTOM_CACHE.values().forEach(minecraft.getTextureManager()::release);
    FIXED_CACHE.clear();
    CUSTOM_CACHE.clear();
    PENDING_FIXED.clear();
    PENDING_CUSTOM.clear();
    FAILED.clear();
    FAILURE_COUNTS.clear();
    INGREDIENT_KEY_CACHE.clear();
    CustomSkewerGuiTexture.clearTemplates();
    customTextureSequence = 0;
    budgetFrame = Long.MIN_VALUE;
    fixedBudget = 0;
    customBudget = 0;
  }

  private static ResourceLocation bake(
      GuiGraphics current,
      ItemStack stack,
      ResourceLocation itemId,
      String state,
      ResourceLocation textureId,
      int outlineRgb,
      int size) {
    Minecraft minecraft = Minecraft.getInstance();
    RenderTarget main = minecraft.getMainRenderTarget();
    TextureTarget target = null;
    NativeImage blackCapture = null;
    NativeImage whiteCapture = null;
    boolean projectionBackedUp = false;
    try {
      current.flush();
      target = new TextureTarget(size, size, true, Minecraft.ON_OSX);
      RenderSystem.backupProjectionMatrix();
      projectionBackedUp = true;
      RenderSystem.setProjectionMatrix(
          new Matrix4f()
              .setOrtho(0.0F, 16.0F, 16.0F, 0.0F, 1000.0F, ForgeHooksClient.getGuiFarPlane()),
          VertexSorting.ORTHOGRAPHIC_Z);

      blackCapture = capture(minecraft, target, stack, 0.0F);
      whiteCapture = capture(minecraft, target, stack, 1.0F);
      NativeImage transparent = recoverTransparency(blackCapture, whiteCapture, size);
      if (!isValidCapture(transparent, itemId, state)) {
        transparent.close();
        return null;
      }
      NativeImage outlined = outline(transparent, outlineRgb, Math.max(1, size / BASE_SIZE));
      transparent.close();
      blackCapture.close();
      blackCapture = null;
      whiteCapture.close();
      whiteCapture = null;

      DynamicTexture texture = new DynamicTexture(outlined);
      texture.setFilter(true, false);
      minecraft.getTextureManager().register(textureId, texture);
      return textureId;
    } catch (RuntimeException exception) {
      LOGGER.warn("Unable to cache skewer GUI icon {} ({})", itemId, state, exception);
      return null;
    } finally {
      if (blackCapture != null) blackCapture.close();
      if (whiteCapture != null) whiteCapture.close();
      if (projectionBackedUp) RenderSystem.restoreProjectionMatrix();
      if (target != null) target.destroyBuffers();
      main.bindWrite(true);
    }
  }

  private static NativeImage capture(
      Minecraft minecraft, TextureTarget target, ItemStack stack, float background) {
    target.setClearColor(background, background, background, 1.0F);
    target.clear(Minecraft.ON_OSX);
    target.bindWrite(true);
    SkewerItemRenderContext.pushCapture();
    try {
      GuiGraphics offscreen = new GuiGraphics(minecraft, minecraft.renderBuffers().bufferSource());
      offscreen.renderItem(stack, 0, 0);
      offscreen.flush();
    } finally {
      SkewerItemRenderContext.popCapture();
    }
    return Screenshot.takeScreenshot(target);
  }

  private static NativeImage recoverTransparency(NativeImage black, NativeImage white, int size) {
    NativeImage result = new NativeImage(size, size, true);
    for (int y = 0; y < size; y++) {
      for (int x = 0; x < size; x++) {
        int overBlack = black.getPixelRGBA(x, y);
        int overWhite = white.getPixelRGBA(x, y);
        int red = overBlack & 0xFF;
        int green = overBlack >>> 8 & 0xFF;
        int blue = overBlack >>> 16 & 0xFF;
        int redDifference = clamp((overWhite & 0xFF) - red);
        int greenDifference = clamp((overWhite >>> 8 & 0xFF) - green);
        int blueDifference = clamp((overWhite >>> 16 & 0xFF) - blue);
        int alpha = 255 - Math.max(redDifference, Math.max(greenDifference, blueDifference));
        if (alpha <= 2) {
          result.setPixelRGBA(x, y, 0);
          continue;
        }
        red = clamp((red * 255 + alpha / 2) / alpha);
        green = clamp((green * 255 + alpha / 2) / alpha);
        blue = clamp((blue * 255 + alpha / 2) / alpha);
        result.setPixelRGBA(x, y, alpha << 24 | blue << 16 | green << 8 | red);
      }
    }
    return result;
  }

  private static int clamp(int value) {
    return Math.max(0, Math.min(255, value));
  }

  private static NativeImage outline(NativeImage source, int rgb, int radius) {
    int width = source.getWidth();
    int height = source.getHeight();
    NativeImage result = new NativeImage(width, height, true);
    result.copyFrom(source);
    int abgr = 0xFF000000 | (rgb & 0xFF) << 16 | (rgb & 0xFF00) | (rgb >>> 16 & 0xFF);
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        if (alpha(source, x, y) > 16) continue;
        if (hasVisibleNeighbor(source, x, y, radius)) {
          result.setPixelRGBA(x, y, abgr);
        }
      }
    }
    return result;
  }

  private static boolean hasVisibleNeighbor(NativeImage image, int x, int y, int radius) {
    for (int offsetY = -radius; offsetY <= radius; offsetY++) {
      for (int offsetX = -radius; offsetX <= radius; offsetX++) {
        if (Math.abs(offsetX) + Math.abs(offsetY) > radius) continue;
        if (alpha(image, x + offsetX, y + offsetY) > 16) return true;
      }
    }
    return false;
  }

  private static int alpha(NativeImage image, int x, int y) {
    if (x < 0 || y < 0 || x >= image.getWidth() || y >= image.getHeight()) return 0;
    return image.getPixelRGBA(x, y) >>> 24;
  }

  private static boolean isValidCapture(
      NativeImage image, ResourceLocation itemId, String state) {
    int width = image.getWidth();
    int height = image.getHeight();
    int visible = 0;
    int minX = width;
    int minY = height;
    int maxX = -1;
    int maxY = -1;
    for (int y = 0; y < image.getHeight(); y++) {
      for (int x = 0; x < image.getWidth(); x++) {
        if (alpha(image, x, y) <= 16) continue;
        visible++;
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }
    int boundsWidth = maxX < minX ? 0 : maxX - minX + 1;
    int boundsHeight = maxY < minY ? 0 : maxY - minY + 1;
    int cornerSize = Math.max(2, width / 16);
    boolean pollutedCorner =
        countVisiblePixels(image, 0, 0, cornerSize, cornerSize) > cornerSize * cornerSize / 2
            || countVisiblePixels(
                    image,
                    width - cornerSize,
                    height - cornerSize,
                    width,
                    height)
                > cornerSize * cornerSize / 2;
    boolean valid =
        visible >= width
            && visible <= width * height * 3 / 4
            && boundsWidth >= width / 4
            && boundsHeight >= height / 4
            && !pollutedCorner;
    if (!valid) {
      LOGGER.warn(
          "Rejected invalid skewer GUI cache for {} ({}): visible={}, bounds={}x{}, corner={}",
          itemId,
          state,
          visible,
          boundsWidth,
          boundsHeight,
          pollutedCorner);
    }
    return valid;
  }

  private static int countVisiblePixels(
      NativeImage image, int minX, int minY, int maxX, int maxY) {
    int count = 0;
    for (int y = minY; y < maxY; y++) {
      for (int x = minX; x < maxX; x++) {
        if (alpha(image, x, y) > 16) count++;
      }
    }
    return count;
  }

  private static int outlineColor(boolean cooked, boolean hot) {
    return hot ? 0xFF3B30 : cooked ? 0xFFFF33 : 0xFFFFFF;
  }

  private static String customKey(
      Minecraft minecraft, ItemStack stack, ResourceLocation itemId, String state) {
    StringBuilder key =
        new StringBuilder(itemId.toString())
            .append('/')
            .append(state)
            .append('/')
            .append(SkeweringHandler.modelState(stack))
            .append('/')
            .append(SecretSkewerItem.getVisualStage(stack));
    return key.append(ingredientKey(minecraft, stack)).toString();
  }

  private static String ingredientKey(Minecraft minecraft, ItemStack stack) {
    Object ingredientToken =
        stack.hasTag() ? stack.getTag().get("SkewerIngredientStacks") : null;
    Object cookedToken = stack.hasTag() ? stack.getTag().get("CookedIngredientStacks") : null;
    IngredientKeyData cached = INGREDIENT_KEY_CACHE.get(stack);
    if (cached != null
        && cached.ingredientToken() == ingredientToken
        && cached.cookedToken() == cookedToken) return cached.key();

    StringBuilder key = new StringBuilder();
    List<ItemStack> ingredients =
        minecraft.level == null
            ? SkewerRecipes.displayIngredients(stack)
            : SkeweringHandler.readEffectiveIngredientStacks(stack);
    for (ItemStack ingredient : ingredients) {
      key.append('|')
          .append(ForgeRegistries.ITEMS.getKey(ingredient.getItem()))
          .append('@')
          .append(ingredient.hasTag() ? ingredient.getTag().hashCode() : 0);
    }
    if (INGREDIENT_KEY_CACHE.size() >= 256) INGREDIENT_KEY_CACHE.clear();
    String resolved = key.toString();
    INGREDIENT_KEY_CACHE.put(
        stack, new IngredientKeyData(ingredientToken, cookedToken, resolved));
    return resolved;
  }

  private static void trimCustomCache(Minecraft minecraft) {
    while (CUSTOM_CACHE.size() > MAX_CUSTOM_ICONS) {
      Map.Entry<String, ResourceLocation> eldest = CUSTOM_CACHE.entrySet().iterator().next();
      CUSTOM_CACHE.remove(eldest.getKey());
      minecraft.getTextureManager().release(eldest.getValue());
    }
  }

  private static boolean isCompletedCustom(Minecraft minecraft, ItemStack stack) {
    return stack.is(ModItems.SECRET_SKEWER.get())
        && minecraft.level != null
        && SkeweringHandler.ingredientCount(stack) >= 3;
  }

  private static boolean isStartedCustom(Minecraft minecraft, ItemStack stack) {
    return (stack.is(ModItems.UNFINISHED_SKEWER.get())
            || stack.is(ModItems.SECRET_SKEWER.get()))
        && minecraft.level != null
        && SkeweringHandler.ingredientCount(stack) > 0;
  }

  private static boolean isBuiltInFixedSkewer(ItemStack stack) {
    return ModItems.RAW_SKEWERS.stream().anyMatch(item -> stack.is(item.get()))
        || ModItems.FIXED_SKEWERS.stream().anyMatch(item -> stack.is(item.get()));
  }

  private static boolean isGeneratedKubeSkewer(ItemStack stack) {
    Object item = stack.getItem();
    if (!item.getClass().getName().equals(
        "cn.breezeth.kaleidoscope_grilling.kubejs.KubeSkewerItem")) return false;
    try {
      return Boolean.TRUE.equals(item.getClass().getMethod("usesGeneratedModel").invoke(item));
    } catch (ReflectiveOperationException ignored) {
      return false;
    }
  }

  private static void refreshBudgets(Minecraft minecraft) {
    long frame = minecraft.getFrameTimeNs();
    if (frame == budgetFrame) return;
    budgetFrame = frame;
    fixedBudget = FIXED_BAKES_PER_FRAME;
    customBudget = CUSTOM_BAKES_PER_FRAME;
  }

  private static void trimPendingCustom() {
    while (PENDING_CUSTOM.size() > MAX_CUSTOM_ICONS) {
      PENDING_CUSTOM.remove(PENDING_CUSTOM.iterator().next());
    }
  }

  private static boolean isEnabled() {
    return !JVM_DISABLED && HotFoodConfig.ENABLE_SKEWER_GUI_CACHE.get();
  }

  private static boolean isFixedCacheEnabled() {
    return !JVM_DISABLED && HotFoodConfig.USE_FIXED_SKEWER_64X_CACHE.get();
  }

  private record IngredientKeyData(Object ingredientToken, Object cookedToken, String key) {}

  private SkewerGuiIconCache() {}
}
