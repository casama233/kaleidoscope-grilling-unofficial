"""Observe pinned Java quality code with data-only adapters, outside Minecraft.

Supply the five original .java files in forge-1.20.1/ and neoforge-1.21.1/.
Original sources and compiler output stay outside Git; only the numeric fixture
is maintained here. JDK Random/Collections and unchanged author methods execute.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import shutil
import subprocess

HASHES={
 'forge-1.20.1/QualityEvaluator.java':'d7d8b53950b3c3ae6dc405dbd1e7b67b6adaba9a7b8e0ece7c6586c51c969d7b',
 'forge-1.20.1/Quality.java':'97fb5e5105906745e717e1179c56828b36f82acdc3d1fef1831f72a64758e39c',
 'neoforge-1.21.1/QualityEvaluator.java':'d7d8b53950b3c3ae6dc405dbd1e7b67b6adaba9a7b8e0ece7c6586c51c969d7b',
 'neoforge-1.21.1/Quality.java':'c7c36f8e541c45c264180c7c1eacb7cf89331244c85742fa20f16648e0044e01',
 'neoforge-1.21.1/QualityUtils.java':'d696f1d1887e220beb789f94c79834b3e7e3fdfc8d9fcbd4da00aed513370efb',
}
PKG='com/github/ysbbbbbb/kaleidoscopecookery/item/quality/'
STUBS={
 'com/google/common/collect/Lists.java':'package com.google.common.collect; public final class Lists {public static <T> java.util.ArrayList<T> newArrayList(){return new java.util.ArrayList<>();}}',
 'it/unimi/dsi/fastutil/Pair.java':'package it.unimi.dsi.fastutil; public record Pair<L,R>(L left,R right){public static <L,R> Pair<L,R> of(L l,R r){return new Pair<>(l,r);}}',
 'it/unimi/dsi/fastutil/ints/IntList.java':'package it.unimi.dsi.fastutil.ints; public interface IntList extends java.util.List<Integer>{default int getInt(int i){return get(i);}}',
 'it/unimi/dsi/fastutil/ints/IntArrayList.java':'package it.unimi.dsi.fastutil.ints; public class IntArrayList extends java.util.ArrayList<Integer> implements IntList{public IntArrayList(int n){super(n);}}',
 # The two-field hash bridge was checked against both official acq/akr methods.
 'net/minecraft/resources/ResourceLocation.java':"package net.minecraft.resources; public final class ResourceLocation {private final String namespace,path; public ResourceLocation(String id){int i=id.indexOf(':');namespace=id.substring(0,i);path=id.substring(i+1);} @Override public int hashCode(){return 31*namespace.hashCode()+path.hashCode();}}",
 'net/minecraft/util/Mth.java':'package net.minecraft.util; public final class Mth{public static double clamp(double x,double a,double b){return Math.max(a,Math.min(b,x));}}',
 'net/minecraft/world/item/ItemStack.java':'package net.minecraft.world.item; public final class ItemStack {public final String id;private final java.util.Map<Object,Object> data=new java.util.HashMap<>(); public ItemStack(String id){this.id=id;} public <T> void set(Object key,T value){data.put(key,value);} @SuppressWarnings("unchecked") public <T> T get(Object key){return (T)data.get(key);} public boolean has(Object key){return data.containsKey(key);}}',
 'net/minecraft/world/item/crafting/Ingredient.java':'package net.minecraft.world.item.crafting; import net.minecraft.world.item.ItemStack; public final class Ingredient {private final java.util.Set<String> ids;public Ingredient(String... ids){this.ids=java.util.Set.of(ids);}public boolean isEmpty(){return ids.isEmpty();}public boolean test(ItemStack stack){return isEmpty()?stack.id.isEmpty():ids.contains(stack.id);}}',
 'org/jetbrains/annotations/NotNull.java':'package org.jetbrains.annotations; @java.lang.annotation.Target({java.lang.annotation.ElementType.TYPE_USE,java.lang.annotation.ElementType.METHOD}) public @interface NotNull{}',
 'net/minecraft/ChatFormatting.java':'package net.minecraft;public enum ChatFormatting{GOLD,GREEN,WHITE,DARK_GRAY}',
 'net/minecraft/network/chat/Component.java':'package net.minecraft.network.chat;public class Component{public static MutableComponent translatable(String key){return new MutableComponent();}}',
 'net/minecraft/network/chat/MutableComponent.java':'package net.minecraft.network.chat;public final class MutableComponent extends Component{public MutableComponent withStyle(net.minecraft.ChatFormatting style){return this;}}',
 'net/minecraft/util/ByIdMap.java':'package net.minecraft.util;public final class ByIdMap{public enum OutOfBoundsStrategy{ZERO}public static <T> java.util.function.IntFunction<T> continuous(java.util.function.ToIntFunction<T> id,T[] values,OutOfBoundsStrategy strategy){return i->values[i>=0&&i<values.length?i:0];}}',
 'net/minecraft/util/StringRepresentable.java':'package net.minecraft.util;public interface StringRepresentable{String getSerializedName();static <T extends Enum<T> & StringRepresentable> com.mojang.serialization.Codec<T> fromEnum(java.util.function.Supplier<T[]> supplier){return new com.mojang.serialization.Codec<>();}}',
 'com/mojang/serialization/Codec.java':'package com.mojang.serialization;public class Codec<T>{}',
 'io/netty/buffer/ByteBuf.java':'package io.netty.buffer;public class ByteBuf{}',
 'net/minecraft/network/codec/StreamCodec.java':'package net.minecraft.network.codec;public class StreamCodec<B,T>{}',
 'net/minecraft/network/codec/ByteBufCodecs.java':'package net.minecraft.network.codec;public class ByteBufCodecs{public static <T> StreamCodec<io.netty.buffer.ByteBuf,T> idMapper(java.util.function.IntFunction<T> from,java.util.function.ToIntFunction<T> to){return new StreamCodec<>();}}',
 'com/github/ysbbbbbb/kaleidoscopecookery/init/ModDataComponents.java':'package com.github.ysbbbbbb.kaleidoscopecookery.init;public final class ModDataComponents{public static final Object QUALITY=new Object();}',
 'net/minecraft/world/effect/MobEffectInstance.java':'package net.minecraft.world.effect;public final class MobEffectInstance{private final Object effect;private final int duration,amplifier;public MobEffectInstance(Object e,int d,int a){effect=e;duration=d;amplifier=a;}public Object getEffect(){return effect;}public int getDuration(){return duration;}public int getAmplifier(){return amplifier;}}',
 'net/minecraft/world/food/FoodProperties.java':'package net.minecraft.world.food;import net.minecraft.world.item.ItemStack;import net.minecraft.world.effect.MobEffectInstance;public record FoodProperties(int nutrition,float saturation,boolean canAlwaysEat,float eatSeconds,java.util.Optional<ItemStack> usingConvertsTo,java.util.List<PossibleEffect> effects){public record PossibleEffect(java.util.function.Supplier<MobEffectInstance> supplier,float probability){public MobEffectInstance effect(){return supplier.get();}}}',
}
DRIVER=r'''import java.io.*;import java.util.*;import java.lang.reflect.*;
import net.minecraft.resources.ResourceLocation;import net.minecraft.world.item.ItemStack;import net.minecraft.world.item.crafting.Ingredient;
import com.github.ysbbbbbb.kaleidoscopecookery.item.quality.*;
public class QualityOracle {
 public static void main(String[] args)throws Exception{
  Method vector=QualityEvaluator.class.getDeclaredMethod("randomVector",List.class,ResourceLocation.class,long.class);vector.setAccessible(true);
  BufferedReader in=new BufferedReader(new InputStreamReader(System.in));String line;
  while((line=in.readLine())!=null){
   String[] row=line.split("\t",-1);long seed=Long.parseLong(row[0]);ResourceLocation id=new ResourceLocation(row[1]);
   List<Ingredient> ingredients=new ArrayList<>();for(String slot:row[2].split(";"))ingredients.add(new Ingredient(slot.split(",")));
   List<Ingredient> padded=new ArrayList<>(ingredients);while(padded.size()<9)padded.add(new Ingredient());
   List<ItemStack> inputs=new ArrayList<>();for(String item:row[3].split(",",-1))inputs.add(new ItemStack(item));
   Quality quality=QualityEvaluator.evaluate(inputs,padded,id,seed);
   List<?> v=(List<?>)vector.invoke(null,ingredients,id,seed);List<Integer> ratios=new ArrayList<>();
   for(Object pair:v)ratios.add((Integer)pair.getClass().getMethod("right").invoke(pair));
   System.out.println("{\"quality\":"+quality.getId()+",\"hash\":"+id.hashCode()+",\"seed\":\""+(seed*31+id.hashCode())+"\",\"ratios\":"+ratios+"}");
  }
 }
}'''
NUTRITION_DRIVER=r'''import java.util.*;import net.minecraft.world.food.FoodProperties;
import com.github.ysbbbbbb.kaleidoscopecookery.item.quality.*;
public class NutritionOracle{public static void main(String[] args){
 int[] ns={9,8,10};float[] ss={0.7F,0.6F,0.8F};
 for(int i=0;i<ns.length;i++)for(Quality q:Quality.values()){
  // Official 1.21.1 FoodConstants.saturationByModifier bytecode: i2f,fmul,2,fmul.
  FoodProperties raw=new FoodProperties(ns[i],ns[i]*ss[i]*2F,false,1.6F,Optional.empty(),List.of());
  FoodProperties result=QualityUtils.modifyFoodProperties(raw,q);
  System.out.println("{\"dish\":"+i+",\"quality\":"+q.getId()+",\"nutrition\":"+result.nutrition()+",\"saturationGain\":"+(double)result.saturation()+"}");
 }
}}'''
SEEDS=['-9223372036854775808','-9223372036854775807','-9007199254740993','-1','0','1','9007199254740993','9223372036854775807']
RECIPES=[
 ('houttuynia_stir_fried_pork',[['kaleidoscope_grilling:houttuynia'],['minecraft:porkchop']]),
 ('green_pepper_squid_tentacles',[['kaleidoscope_cookery:green_chili'],['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:onion']]),
 ('braised_chicken_wings',[['kaleidoscope_grilling:chicken_wing'],['minecraft:sugar']]),
]

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--source-dir',required=True,type=Path);ap.add_argument('--output-dir',required=True,type=Path)
 ap.add_argument('--java',default='java');ap.add_argument('--fixture',required=True,type=Path);args=ap.parse_args()
 root=args.source_dir.resolve();out=args.output_dir.resolve()
 repo=Path(__file__).resolve().parents[1]
 if out==repo or repo in out.parents:raise SystemExit('Compiler/source output must stay outside the public worktree')
 out.mkdir(parents=True,exist_ok=False);src=out/'src';src.mkdir()
 for name,digest in HASHES.items():
  if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise SystemExit('Unreviewed original source: '+name)
 for relative,text in STUBS.items():
  p=src/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text+'\n')
 (src/'QualityOracle.java').write_text(DRIVER+'\n')
 cases=[];lines=[]
 for name,ingredients in RECIPES:
  for seed in SEEDS:
   for counts in itertools.product(range(1,9),repeat=len(ingredients)):
    if sum(counts)>9:continue
    inputs=[slot[0] for slot,n in zip(ingredients,counts) for _ in range(n)]+['']*(9-sum(counts))
    cases.append((name,seed,counts));lines.append('\t'.join([seed,'kaleidoscope_grilling:flex_pot/'+name,';'.join(','.join(s) for s in ingredients),','.join(inputs)]))
 def compile_to(classes):
  classes.mkdir(exist_ok=True)
  subprocess.run([args.java,'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-d',str(classes),*[str(p) for p in src.rglob('*.java')]],check=True)
 observations={}
 for branch in ['forge-1.20.1','neoforge-1.21.1']:
  for name in ['QualityEvaluator.java','Quality.java']:
   dst=src/PKG/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/branch/name,dst)
  classes=out/branch;compile_to(classes)
  result=subprocess.run([args.java,'-cp',str(classes),'QualityOracle'],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
  observations[branch]=[json.loads(line) for line in result.stdout.splitlines()]
 assert observations['forge-1.20.1']==observations['neoforge-1.21.1']
 values=observations['neoforge-1.21.1'];assert len(values)==len(cases)==1248
 shutil.copyfile(root/'neoforge-1.21.1/QualityUtils.java',src/PKG/'QualityUtils.java')
 (src/'NutritionOracle.java').write_text(NUTRITION_DRIVER+'\n');compile_to(classes)
 result=subprocess.run([args.java,'-cp',str(classes),'NutritionOracle'],capture_output=True,text=True,check=True)
 nutrition=[json.loads(line) for line in result.stdout.splitlines()]
 groups=[]
 for name,ingredients in RECIPES:
  for seed in SEEDS:
   selected=[(c,v) for c,v in zip(cases,values) if c[:2]==(name,seed)];first=selected[0][1]
   assert all(v['ratios']==first['ratios'] and v['seed']==first['seed'] and v['hash']==first['hash'] for _,v in selected)
   groups.append({'recipeId':'kaleidoscope_grilling:flex_pot/'+name,'worldSeed':seed,'ingredients':ingredients,'javaResourceHash':first['hash'],'javaRecipeSeed':first['seed'],'ratios':first['ratios'],'observations':[[*c[2],v['quality']] for c,v in selected]})
 fixture={'schema':1,'scope':'Unchanged pinned Java QualityEvaluator/Quality with data-only dependency adapters; no Minecraft, player, recipe lifecycle or client execution.',
  'java_cookery':{'forge_1_20_1':'2f4e386ce23f49a385ddf003c67fc6415c55417a','neoforge_1_21_1':'4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c'},
  'grilling':'9a1acdab27698457bec16c9362678e574895a28c','source_sha256':HASHES,
  'adapters':['ItemStack item ID only','Ingredient alternatives and empty slots','Lists/IntList/Pair backed by JDK collections','ResourceLocation hash independently checked against both official JAR methods','Mth clamp','unused enum tooltip/codec/data-component bindings','FoodProperties/MobEffectInstance value carriers'],
  'real_jdk':['signed long overflow','java.util.Random','Collections.shuffle','String.hashCode','Math.sqrt/pow/round','float conversion/multiplication'],
  'fixed_input_slots':9,'branches_equal':True,'quality_observations':len(cases),'cases':groups,
  'neoforge_nutrition':[{**n,'baseId':'kaleidoscope_grilling:'+RECIPES[n['dish']][0]} for n in nutrition],
  'limitations':{'full_author_jar_executed':False,'minecraft':False,'player_simulation':False,'native_bedrock_nutrition':False,'client':False},
  'observation_columns':'ingredient counts in source order, then observed quality ID; input list padded to nine slots'}
 args.fixture.write_text(json.dumps(fixture,ensure_ascii=False,separators=(',',':'))+'\n')
 print(json.dumps({'fixture':str(args.fixture),'quality_observations':len(cases),'nutrition_observations':len(nutrition),'branches_equal':True,'native':False,'client':False}))

if __name__=='__main__':main()
