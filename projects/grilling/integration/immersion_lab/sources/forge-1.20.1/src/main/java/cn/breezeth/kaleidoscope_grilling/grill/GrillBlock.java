package cn.breezeth.kaleidoscope_grilling.grill;

import cn.breezeth.kaleidoscope_grilling.GrillAutomationApi;
import cn.breezeth.kaleidoscope_grilling.registry.ModAdvancements;
import cn.breezeth.kaleidoscope_grilling.registry.ModBlockEntities;
import cn.breezeth.kaleidoscope_grilling.registry.ModItems;
import cn.breezeth.kaleidoscope_grilling.registry.ModSounds;

import cn.breezeth.kaleidoscope_grilling.oil.OilBrushAnimation;
import cn.breezeth.kaleidoscope_grilling.oil.OilPotCompat;
import cn.breezeth.kaleidoscope_grilling.seasoning.SeasoningAnimation;


import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

public final class GrillBlock extends BaseEntityBlock {
  public static final BooleanProperty LEGGED = BooleanProperty.create("legged");
  public static final BooleanProperty LIT = BooleanProperty.create("lit");
  public static final net.minecraft.world.level.block.state.properties.DirectionProperty FACING =
      HorizontalDirectionalBlock.FACING;
  private static final TagKey<Item> EXTINGUISH_TOOLS =
      TagKey.create(
          Registries.ITEM, new ResourceLocation("kaleidoscope_cookery", "extinguish_stove"));
  private static final VoxelShape FLAT_Z = Block.box(0, 0, 2, 16, 4, 14);
  private static final VoxelShape FLAT_X = Block.box(2, 0, 0, 14, 4, 16);
  private static final VoxelShape LEGS_Z =
      Shapes.or(
          FLAT_Z,
          Block.box(0, 0, 2, 2, 4, 4),
          Block.box(14, 0, 2, 16, 4, 4),
          Block.box(0, 0, 12, 2, 4, 14),
          Block.box(14, 0, 12, 16, 4, 14));
  private static final VoxelShape LEGS_X =
      Shapes.or(
          FLAT_X,
          Block.box(2, 0, 0, 4, 4, 2),
          Block.box(12, 0, 0, 14, 4, 2),
          Block.box(2, 0, 14, 4, 4, 16),
          Block.box(12, 0, 14, 14, 4, 16));

  public GrillBlock(Properties properties) {
    super(properties);
    registerDefaultState(
        stateDefinition
            .any()
            .setValue(LEGGED, false)
            .setValue(LIT, false)
            .setValue(FACING, Direction.NORTH));
  }

  @Override
  protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
    b.add(LEGGED, LIT, FACING);
  }

  @Override
  public BlockState getStateForPlacement(BlockPlaceContext c) {
    BlockPos below = c.getClickedPos().below();
    return defaultBlockState()
        .setValue(
            LEGGED,
            !c.getLevel().getBlockState(below).isFaceSturdy(c.getLevel(), below, Direction.UP))
        .setValue(LIT, false)
        .setValue(FACING, c.getHorizontalDirection().getOpposite());
  }

  @Override
  public BlockState updateShape(
      BlockState state,
      Direction direction,
      BlockState neighborState,
      LevelAccessor level,
      BlockPos pos,
      BlockPos neighborPos) {
    if (direction == Direction.DOWN)
      return state.setValue(LEGGED, !neighborState.isFaceSturdy(level, neighborPos, Direction.UP));
    return super.updateShape(state, direction, neighborState, level, pos, neighborPos);
  }

  @Override
  public VoxelShape getShape(
      BlockState s, net.minecraft.world.level.BlockGetter l, BlockPos p, CollisionContext c) {
    boolean x = s.getValue(FACING).getAxis() == Direction.Axis.X;
    return s.getValue(LEGGED) ? (x ? LEGS_X : LEGS_Z) : (x ? FLAT_X : FLAT_Z);
  }

  @Override
  public RenderShape getRenderShape(BlockState state) {
    return RenderShape.MODEL;
  }

  @Override
  public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
    return new GrillBlockEntity(pos, state);
  }

  @Nullable
  @Override
  public <T extends BlockEntity> BlockEntityTicker<T> getTicker(
      Level level, BlockState state, BlockEntityType<T> type) {
    return level.isClientSide
        ? null
        : createTickerHelper(type, ModBlockEntities.GRILL.get(), GrillBlockEntity::tick);
  }

  @Override
  public InteractionResult use(
      BlockState state,
      Level level,
      BlockPos pos,
      Player player,
      InteractionHand hand,
      BlockHitResult hit) {
    if (!(level.getBlockEntity(pos) instanceof GrillBlockEntity grill))
      return InteractionResult.PASS;
    ItemStack held = player.getItemInHand(hand);
    if (held.is(Items.FLINT_AND_STEEL)) {
      if (!state.getValue(LIT)) {
        if (!level.isClientSide) {
          level.setBlock(pos, state.setValue(LIT, true), Block.UPDATE_ALL);
          level.playSound(
              null,
              pos,
              SoundEvents.FLINTANDSTEEL_USE,
              SoundSource.BLOCKS,
              1.0F,
              level.random.nextFloat() * 0.4F + 0.8F);
          held.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
      }
      return InteractionResult.CONSUME;
    }
    if (held.is(EXTINGUISH_TOOLS) && state.getValue(LIT)) {
      if (!level.isClientSide) {
        if (player.isShiftKeyDown()) GrillAutomationApi.forceUnlock(level, pos);
        level.setBlock(pos, state.setValue(LIT, false), Block.UPDATE_ALL);
        level.playSound(
            null,
            pos,
            SoundEvents.FIRE_EXTINGUISH,
            SoundSource.BLOCKS,
            0.5F,
            2.6F + (level.random.nextFloat() - level.random.nextFloat()) * 0.8F);
      }
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    if (OilPotCompat.isOilPot(held)) {
      GrillAutomationApi.Result preview = GrillAutomationApi.brushOil(level, pos, held, true);
      if (preview.success() && !level.isClientSide) {
        String oilType = OilPotCompat.getType(held);
        GrillAutomationApi.Result result = GrillAutomationApi.brushOil(level, pos, held, false);
        if (result.success()) {
          OilBrushAnimation.start(player, hand, oilType);
          ModAdvancements.oiled(player);
          level.playSound(null, pos, ModSounds.GRILL_FLIP.get(), SoundSource.BLOCKS, 0.75F, 1.0F);
          player.displayClientMessage(
              Component.translatable("message.kaleidoscope_grilling.oiled", result.affected()),
              true);
        }
      } else if (!level.isClientSide)
        player.displayClientMessage(
            Component.translatable(
                preview.status() == GrillAutomationApi.Status.INSUFFICIENT_RESOURCE
                    ? "message.kaleidoscope_grilling.not_enough_oil"
                    : "message.kaleidoscope_grilling.no_brushable_skewers"),
            true);
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    if (held.is(ModItems.SPECIAL_SEASONING.get())) {
      GrillAutomationApi.Result preview = GrillAutomationApi.season(level, pos, held, true);
      if (preview.success() && !level.isClientSide) {
        GrillAutomationApi.Result result = GrillAutomationApi.season(level, pos, held, false);
        if (result.success()) {
          SeasoningAnimation.start(player);
          level.playSound(null, pos, ModSounds.SEASON.get(), SoundSource.BLOCKS, 0.85F, 1.0F);
          player.displayClientMessage(
              Component.translatable("message.kaleidoscope_grilling.grill_ready_to_take")
                  .withStyle(ChatFormatting.RED),
              true);
          if (result.shouldReplaceHeld()) player.setItemInHand(hand, result.heldReplacement());
        }
      } else if (!level.isClientSide)
        player.displayClientMessage(
            Component.translatable(
                preview.status() == GrillAutomationApi.Status.INSUFFICIENT_RESOURCE
                    ? "message.kaleidoscope_grilling.not_enough_seasoning"
                    : "message.kaleidoscope_grilling.no_seasonable_skewers"),
            true);
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    if (!held.isEmpty()) {
      GrillAutomationApi.Result preview =
          GrillAutomationApi.insertSkewer(
              level, pos, held, true, !player.getAbilities().instabuild);
      if (preview.status() == GrillAutomationApi.Status.NOT_LIT) {
        if (!level.isClientSide)
          player.displayClientMessage(
              Component.translatable("message.kaleidoscope_grilling.grill_need_heat"), true);
        return InteractionResult.sidedSuccess(level.isClientSide);
      }
      if (preview.success()) {
        if (!level.isClientSide
            && GrillAutomationApi.insertSkewer(
                    level, pos, held, false, !player.getAbilities().instabuild)
                .success())
          level.playSound(
              null, pos, ModSounds.ACTION_SUCCESS.get(), SoundSource.BLOCKS, 0.65F, 1.0F);
        return InteractionResult.sidedSuccess(level.isClientSide);
      }
    }
    if (held.isEmpty() && GrillAutomationApi.flip(level, pos, true).success()) {
      if (!level.isClientSide && GrillAutomationApi.flip(level, pos, false).success()) {
        level.playSound(null, pos, ModSounds.GRILL_FLIP.get(), SoundSource.BLOCKS, 0.75F, 1.0F);
        player.displayClientMessage(
            Component.translatable(
                "message.kaleidoscope_grilling.grill_wait_flip", grill.getFlips(), 4),
            true);
      }
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    if (held.isEmpty() && grill.getPhase() == 0 && !grill.isEmpty()) {
      if (!level.isClientSide)
        player.displayClientMessage(
            Component.translatable("message.kaleidoscope_grilling.grill_need_oil"), true);
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    if (held.isEmpty() && grill.getPhase() == 2 && !grill.isSeasoned()) {
      if (!level.isClientSide)
        player.displayClientMessage(
            Component.translatable("message.kaleidoscope_grilling.grill_need_seasoning"), true);
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    if (held.isEmpty() && grill.canExtract()) {
      if (!level.isClientSide) {
        int extracted = 0;
        do {
          GrillAutomationApi.Result result = GrillAutomationApi.extract(level, pos, false);
          if (!result.success()) break;
          player.getInventory().placeItemBackInInventory(result.output());
          extracted++;
        } while (player.isShiftKeyDown());
        if (extracted > 0)
          level.playSound(null, pos, ModSounds.PICKUP_ITEM.get(), SoundSource.BLOCKS, 0.8F, 1.0F);
      }
      return InteractionResult.sidedSuccess(level.isClientSide);
    }
    return InteractionResult.PASS;
  }

  @Override
  public void animateTick(BlockState s, Level l, BlockPos p, RandomSource r) {
    if (!s.getValue(LIT)) return;
    if (r.nextInt(3) == 0)
      l.addParticle(
          ParticleTypes.SMOKE,
          p.getX() + 0.25 + r.nextDouble() * 0.5,
          p.getY() + 0.22,
          p.getZ() + 0.25 + r.nextDouble() * 0.5,
          0,
          0.02,
          0);
    if (r.nextInt(8) == 0)
      l.addParticle(
          ParticleTypes.FLAME,
          p.getX() + 0.3 + r.nextDouble() * 0.4,
          p.getY() + 0.18,
          p.getZ() + 0.3 + r.nextDouble() * 0.4,
          0,
          0.01,
          0);
  }

  @Override
  public void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean moving) {
    if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof GrillBlockEntity grill)
      grill.dropForBreak();
    super.onRemove(s, l, p, n, moving);
  }
}
