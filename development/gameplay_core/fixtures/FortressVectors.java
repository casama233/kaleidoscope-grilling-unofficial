/** Independent Java-long oracle for the author 1.1.1 fortress coordinate hash. */
class FortressVectors {
  static boolean first=true;
  static void point(int x,int y,int z) {
    long value=x*341873128712L ^ z*132897987541L ^ y*42317861L;
    value^=value>>>33;value*=0xff51afd7ed558ccdL;value^=value>>>33;
    if(!first)System.out.print(",\n");first=false;
    System.out.print("  {\"x\":"+x+",\"y\":"+y+",\"z\":"+z+",\"mod\":"+Math.floorMod(value,100)+"}");
  }
  public static void main(String[] args) {
    System.out.println("[");
    for(int x=0;x<16;x++)point(x,64,0);
    point(0,0,0);point(-1,64,-1);point(30000000,127,-30000000);
    point(-30000000,0,30000000);point(Integer.MIN_VALUE,127,Integer.MAX_VALUE);
    java.util.Random random=new java.util.Random(0x20261003L);
    for(int i=0;i<256;i++)point(random.nextInt(60000001)-30000000,random.nextInt(128),random.nextInt(60000001)-30000000);
    System.out.println("\n]");
  }
}
