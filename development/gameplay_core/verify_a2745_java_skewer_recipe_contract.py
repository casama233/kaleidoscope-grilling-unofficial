from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'recipe_provider':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/compat/jade/SkewerRecipeProvider.java',
  'b7e215c8100cdd81e317c0b4ed127376fc2b07e1',
  (
   'SkewerRecipeBlockEntity recipe',
   'SkewerRecipeBookItem.readRecipeStack(recipe.recipeBook())',
   '"jade.kaleidoscope_grilling.skewer_recipe.record"',
   '"jade.kaleidoscope_grilling.skewer_recipe.ingredients"',
   'SkewerRecipes.getIngredients(recipe.recipeResult())',
   '"tooltip.kaleidoscope_grilling.recipe_book.wall_usage"',
  )
 ),
 'recipe_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerRecipeBlockEntity.java',
  '3b0ea57caa94eb139421cb7e9c14165eebe76d57',
  (
   'private String recipeResult = "";',
   'private ItemStack recipeBook = ItemStack.EMPTY;',
   'public String recipeResult()',
   'public ItemStack recipeBook()',
   'public void setRecipeBook(ItemStack book)',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.45-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.45 pinned Java Skewer Recipe HUD contract: PASS')

if __name__=='__main__':main()
