package cn.breezeth.kaleidoscope_grilling.skewer;

import cn.breezeth.kaleidoscope_grilling.registry.ModItems;

import cn.breezeth.kaleidoscope_grilling.mixin.SpriteContentsAccessor;
import com.mojang.blaze3d.platform.NativeImage;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

public final class SkewerColorProvider {
  private static final int GRID_SIZE = 4;
  private static final int CELL_COUNT = GRID_SIZE * GRID_SIZE;
  private static final int FACE_COUNT = 6;
  private static final int SLOT_STRIDE = 128;
  private static final int FALLBACK = 0xB86B45;
  private static final int MAX_RENDER_DEPTH = 3;
  private static final Map<PaletteKey, int[]> CACHE = new ConcurrentHashMap<>();
  private static final Map<ItemStack, RenderData> RENDER_CACHE = new IdentityHashMap<>();
  private static final ThreadLocal<Integer> RENDER_DEPTH = ThreadLocal.withInitial(() -> 0);

  public static int color(ItemStack skewer, int tintIndex) {
    if (tintIndex < 0) return -1;
    if (tintIndex == SkewerOutlineRender.OUTLINE_TINT) return opaque(SkewerOutlineRender.color());
    int slot = tintIndex / SLOT_STRIDE;
    int localIndex = tintIndex % SLOT_STRIDE;
    int face = localIndex / CELL_COUNT;
    int cell = localIndex % CELL_COUNT;
    if (slot >= 3 || face >= FACE_COUNT) return -1;
    RenderData renderData = renderData(skewer);
    if (renderData == null) return opaque(stageColor(skewer, FALLBACK, cell));
    if (slot >= renderData.palettes().size()) return -1;
    int[] palette = renderData.palettes().get(slot);
    int color = shadeForFace(palette[cell], face);
    return opaque(stageColor(skewer, color, cell));
  }

  public static void clearCache() {
    CACHE.clear();
    RENDER_CACHE.clear();
  }

  private static RenderData renderData(ItemStack skewer) {
    int depth = RENDER_DEPTH.get();
    if (depth >= MAX_RENDER_DEPTH) return null;
    RENDER_DEPTH.set(depth + 1);
    try {
      Object ingredientToken =
          skewer.hasTag() ? skewer.getTag().get("SkewerIngredientStacks") : null;
      Object cookedToken = skewer.hasTag() ? skewer.getTag().get("CookedIngredientStacks") : null;
      RenderData cached = RENDER_CACHE.get(skewer);
      if (cached != null
          && cached.ingredientToken() == ingredientToken
          && cached.cookedToken() == cookedToken) return cached;

      List<ItemStack> ingredients = SkeweringHandler.readEffectiveIngredientStacks(skewer);
      if (ingredients.isEmpty()) ingredients = SkewerRecipes.displayIngredients(skewer);
      Minecraft minecraft = Minecraft.getInstance();
      List<int[]> palettes = new ArrayList<>(ingredients.size());
      for (ItemStack ingredient : ingredients) {
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(ingredient.getItem());
        PaletteKey key =
            new PaletteKey(id, ingredient.hasTag() ? ingredient.getTag().hashCode() : 0);
        if (CACHE.size() > 512) CACHE.clear();
        palettes.add(CACHE.computeIfAbsent(key, ignored -> sample(minecraft, ingredient)));
      }
      if (RENDER_CACHE.size() >= 256) RENDER_CACHE.clear();
      RenderData resolved = new RenderData(ingredientToken, cookedToken, List.copyOf(palettes));
      RENDER_CACHE.put(skewer, resolved);
      return resolved;
    } finally {
      RENDER_DEPTH.set(depth);
    }
  }

  private static int[] sample(Minecraft minecraft, ItemStack ingredient) {
    try {
      BakedModel model = minecraft.getItemRenderer().getModel(ingredient, minecraft.level, null, 0);
      TextureAtlasSprite sprite = model.getParticleIcon();
      NativeImage image =
          ((SpriteContentsAccessor) (Object) sprite.contents()).grilling$getOriginalImage();
      int width = sprite.contents().width();
      int height = sprite.contents().height();
      int itemTint = isSkewerLike(ingredient) ? -1 : minecraft.getItemColors().getColor(ingredient, 0);
      return sampleGrid(image, width, height, itemTint);
    } catch (RuntimeException ignored) {
      int[] fallback = new int[CELL_COUNT];
      java.util.Arrays.fill(fallback, FALLBACK);
      return fallback;
    }
  }

  private static boolean isSkewerLike(ItemStack stack) {
    return stack.is(ModItems.UNFINISHED_SKEWER.get())
        || stack.is(ModItems.SECRET_SKEWER.get())
        || ModItems.RAW_SKEWERS.stream().anyMatch(item -> stack.is(item.get()))
        || ModItems.FIXED_SKEWERS.stream().anyMatch(item -> stack.is(item.get()));
  }

  private static int[] sampleGrid(NativeImage image, int width, int height, int itemTint) {
    int minX = width / 4;
    int maxX = Math.max(minX + 1, width * 3 / 4);
    int minY = height / 4;
    int maxY = Math.max(minY + 1, height * 3 / 4);
    List<Integer> centerColors = collect(image, minX, maxX, minY, maxY, 0);
    if (centerColors.isEmpty()) {
      minX = 0;
      maxX = width;
      minY = 0;
      maxY = height;
      centerColors = collect(image, minX, maxX, minY, maxY, 0);
    }
    int fallback = centerColors.isEmpty() ? FALLBACK : average(centerColors);
    int medianLuminance = medianLuminance(centerColors);
    int darkCutoff = Math.min(36, Math.max(5, Math.round(medianLuminance * 0.24F)));
    Integer[] sampled = new Integer[CELL_COUNT];
    for (int gridZ = 0; gridZ < GRID_SIZE; gridZ++) {
      // Texture Y grows downward, while the food model's visual bottom is low Z.
      int sourceY = GRID_SIZE - 1 - gridZ;
      int fromY = minY + (maxY - minY) * sourceY / GRID_SIZE;
      int toY = Math.max(fromY + 1, minY + (maxY - minY) * (sourceY + 1) / GRID_SIZE);
      for (int gridX = 0; gridX < GRID_SIZE; gridX++) {
        int fromX = minX + (maxX - minX) * gridX / GRID_SIZE;
        int toX = Math.max(fromX + 1, minX + (maxX - minX) * (gridX + 1) / GRID_SIZE);
        List<Integer> block = collect(image, fromX, toX, fromY, toY, darkCutoff);
        if (block.isEmpty()) block = collect(image, fromX, toX, fromY, toY, 0);
        if (!block.isEmpty()) sampled[gridZ * GRID_SIZE + gridX] = average(block);
      }
    }
    fillTransparentCells(sampled, fallback);
    int[] result = new int[CELL_COUNT];
    for (int i = 0; i < CELL_COUNT; i++) {
      result[i] = itemTint < 0 ? sampled[i] : multiply(sampled[i], itemTint);
    }
    result = quantize(result, 8);
    cleanIsolatedCells(result);
    return result;
  }

  private static List<Integer> collect(
      NativeImage image, int minX, int maxX, int minY, int maxY, int darkCutoff) {
    List<Integer> colors = new ArrayList<>();
    for (int y = minY; y < Math.min(maxY, image.getHeight()); y++) {
      for (int x = minX; x < Math.min(maxX, image.getWidth()); x++) {
        int abgr = image.getPixelRGBA(x, y);
        if ((abgr >>> 24) < 48) continue;
        int rgb = (abgr & 0xFF) << 16 | (abgr >>> 8 & 0xFF) << 8 | (abgr >>> 16 & 0xFF);
        if (luminance(rgb) >= darkCutoff) colors.add(rgb);
      }
    }
    return colors;
  }

  private static int average(List<Integer> colors) {
    long red = 0;
    long green = 0;
    long blue = 0;
    for (int color : colors) {
      red += color >>> 16 & 0xFF;
      green += color >>> 8 & 0xFF;
      blue += color & 0xFF;
    }
    int size = Math.max(1, colors.size());
    return (int) (red / size) << 16 | (int) (green / size) << 8 | (int) (blue / size);
  }

  private static int medianLuminance(List<Integer> colors) {
    if (colors.isEmpty()) return luminance(FALLBACK);
    int[] values = colors.stream().mapToInt(SkewerColorProvider::luminance).sorted().toArray();
    return values[values.length / 2];
  }

  private static void fillTransparentCells(Integer[] colors, int fallback) {
    for (int index = 0; index < colors.length; index++) {
      if (colors[index] != null) continue;
      int x = index % GRID_SIZE;
      int z = index / GRID_SIZE;
      int nearest = -1;
      int nearestDistance = Integer.MAX_VALUE;
      for (int candidate = 0; candidate < colors.length; candidate++) {
        if (colors[candidate] == null) continue;
        int distance = Math.abs(x - candidate % GRID_SIZE) + Math.abs(z - candidate / GRID_SIZE);
        if (distance < nearestDistance) {
          nearest = candidate;
          nearestDistance = distance;
        }
      }
      colors[index] = nearest < 0 ? fallback : colors[nearest];
    }
  }

  private static int[] quantize(int[] colors, int maxColors) {
    List<ColorCluster> clusters = new ArrayList<>();
    for (int color : colors) clusters.add(new ColorCluster(color));
    while (clusters.size() > maxColors) {
      int first = 0;
      int second = 1;
      double nearest = Double.MAX_VALUE;
      for (int i = 0; i < clusters.size(); i++) {
        for (int j = i + 1; j < clusters.size(); j++) {
          double distance =
              labDistanceSquared(clusters.get(i).average(), clusters.get(j).average());
          if (distance < nearest) {
            nearest = distance;
            first = i;
            second = j;
          }
        }
      }
      clusters.get(first).merge(clusters.remove(second));
    }
    int[] result = new int[colors.length];
    for (int index = 0; index < colors.length; index++) {
      int nearestColor = clusters.get(0).average();
      double nearest = labDistanceSquared(colors[index], nearestColor);
      for (int i = 1; i < clusters.size(); i++) {
        int candidate = clusters.get(i).average();
        double distance = labDistanceSquared(colors[index], candidate);
        if (distance < nearest) {
          nearest = distance;
          nearestColor = candidate;
        }
      }
      result[index] = nearestColor;
    }
    return result;
  }

  private static void cleanIsolatedCells(int[] colors) {
    int[] original = colors.clone();
    Map<Integer, Integer> frequencies = new HashMap<>();
    for (int color : original) frequencies.merge(color, 1, Integer::sum);
    for (int index = 0; index < original.length; index++) {
      if (frequencies.getOrDefault(original[index], 0) > 1) continue;
      int x = index % GRID_SIZE;
      int z = index / GRID_SIZE;
      Map<Integer, Integer> neighbors = new HashMap<>();
      if (x > 0) neighbors.merge(original[index - 1], 1, Integer::sum);
      if (x + 1 < GRID_SIZE) neighbors.merge(original[index + 1], 1, Integer::sum);
      if (z > 0) neighbors.merge(original[index - GRID_SIZE], 1, Integer::sum);
      if (z + 1 < GRID_SIZE) neighbors.merge(original[index + GRID_SIZE], 1, Integer::sum);
      int majority = original[index];
      int majorityCount = 0;
      for (Map.Entry<Integer, Integer> entry : neighbors.entrySet()) {
        if (entry.getValue() > majorityCount) {
          majority = entry.getKey();
          majorityCount = entry.getValue();
        }
      }
      if (majorityCount >= 2 && labDistanceSquared(original[index], majority) > 30 * 30) {
        colors[index] = majority;
      }
    }
  }

  private static int shadeForFace(int color, int face) {
    float[] factors = {1.05F, 0.75F, 0.80F, 0.90F, 0.88F, 0.84F};
    float strength = Mth.clamp(luminance(color) / 90.0F, 0.35F, 1.0F);
    return shade(color, (1.0F + (factors[face] - 1.0F) * strength) * 1.06F);
  }

  private static int stageColor(ItemStack stack, int rgb, int cell) {
    int stage = SecretSkewerItem.getVisualStage(stack);
    if (stage == 0
        && ((stack.is(ModItems.SECRET_SKEWER.get()) && SecretSkewerItem.isCooked(stack))
            || SkewerRecipes.isCookedSkewer(stack))) stage = 4;
    if (stage == 0) return rgb;
    if (stage == 1) return blend(rgb, 0xFFD06A, 0.16F, 1.08F);
    int x = cell % GRID_SIZE;
    int z = cell / GRID_SIZE;
    boolean edge = x == 0 || x == GRID_SIZE - 1 || z == 0 || z == GRID_SIZE - 1;
    if (stage == 2) return blend(rgb, 0xB96A32, edge ? 0.27F : 0.18F, edge ? 0.96F : 1.0F);
    if (stage == 3) return blend(rgb, 0x9D4825, edge ? 0.40F : 0.28F, edge ? 0.88F : 0.94F);
    if (stage >= 5) return blend(rgb, 0x17110E, edge ? 0.88F : 0.76F, edge ? 0.42F : 0.52F);
    if (SkeweringHandler.hasCookedIngredientStacks(stack)) {
      int glazed = blend(rgb, 0xC84F3B, edge ? 0.04F : 0.08F, 1.02F);
      return blend(glazed, 0x713A22, edge ? 0.14F : 0.06F, edge ? 0.97F : 1.0F);
    }
    int glazed = blend(rgb, 0xB94A35, edge ? 0.10F : 0.16F, 1.0F);
    return blend(glazed, 0x713A22, edge ? 0.34F : 0.18F, edge ? 0.91F : 0.98F);
  }

  private static int luminance(int rgb) {
    return Math.round(
        ((rgb >>> 16) & 0xFF) * 0.2126F + ((rgb >>> 8) & 0xFF) * 0.7152F + (rgb & 0xFF) * 0.0722F);
  }

  private static double labDistanceSquared(int first, int second) {
    double[] a = toLab(first);
    double[] b = toLab(second);
    double dl = a[0] - b[0];
    double da = a[1] - b[1];
    double db = a[2] - b[2];
    return dl * dl + da * da + db * db;
  }

  private static double[] toLab(int rgb) {
    double r = linear((rgb >>> 16 & 0xFF) / 255.0);
    double g = linear((rgb >>> 8 & 0xFF) / 255.0);
    double b = linear((rgb & 0xFF) / 255.0);
    double x = pivotLab((r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047);
    double y = pivotLab(r * 0.2126729 + g * 0.7151522 + b * 0.0721750);
    double z = pivotLab((r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883);
    return new double[] {116 * y - 16, 500 * (x - y), 200 * (y - z)};
  }

  private static double linear(double value) {
    return value <= 0.04045 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
  }

  private static double pivotLab(double value) {
    return value > 0.008856 ? Math.cbrt(value) : 7.787 * value + 16.0 / 116.0;
  }

  private static int blend(int rgb, int target, float amount, float brightness) {
    int r =
        Mth.clamp(
            Math.round(
                (((rgb >>> 16) & 0xFF) * (1 - amount) + ((target >>> 16) & 0xFF) * amount)
                    * brightness),
            0,
            255);
    int g =
        Mth.clamp(
            Math.round(
                (((rgb >>> 8) & 0xFF) * (1 - amount) + ((target >>> 8) & 0xFF) * amount)
                    * brightness),
            0,
            255);
    int b =
        Mth.clamp(
            Math.round(((rgb & 0xFF) * (1 - amount) + (target & 0xFF) * amount) * brightness),
            0,
            255);
    return r << 16 | g << 8 | b;
  }

  private static int multiply(int first, int second) {
    return (((first >>> 16) & 0xFF) * ((second >>> 16) & 0xFF) / 255) << 16
        | (((first >>> 8) & 0xFF) * ((second >>> 8) & 0xFF) / 255) << 8
        | (first & 0xFF) * (second & 0xFF) / 255;
  }

  private static int shade(int rgb, float factor) {
    int r = Mth.clamp(Math.round(((rgb >>> 16) & 0xFF) * factor), 0, 255);
    int g = Mth.clamp(Math.round(((rgb >>> 8) & 0xFF) * factor), 0, 255);
    int b = Mth.clamp(Math.round((rgb & 0xFF) * factor), 0, 255);
    return r << 16 | g << 8 | b;
  }

  private static int opaque(int rgb) {
    return 0xFF000000 | rgb;
  }

  private record PaletteKey(ResourceLocation item, int tagHash) {}

  private record RenderData(
      Object ingredientToken, Object cookedToken, List<int[]> palettes) {}

  private static final class ColorCluster {
    private int count;
    private long red;
    private long green;
    private long blue;

    private ColorCluster(int color) {
      add(color);
    }

    private void add(int color) {
      count++;
      red += (color >>> 16) & 0xFF;
      green += (color >>> 8) & 0xFF;
      blue += color & 0xFF;
    }

    private void merge(ColorCluster other) {
      count += other.count;
      red += other.red;
      green += other.green;
      blue += other.blue;
    }

    private int average() {
      return (int) (red / count) << 16 | (int) (green / count) << 8 | (int) (blue / count);
    }
  }

  private SkewerColorProvider() {}
}
