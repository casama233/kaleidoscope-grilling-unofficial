#!/usr/bin/env python3
"""Export the canonical runtime. Runtime transforms and artifact selection retired.

The established command remains usable, but flags that used to patch a private
edition are rejected. Update canonical source, its release version and baseline.
"""
from pathlib import Path
import argparse,shutil
from baseline_gate import check,read
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path,nargs='?',default=ROOT/'build/server-edition');args=p.parse_args()
 config=read(ROOT/'baseline.json');check(config,release=True);out=args.output.resolve()
 if out==ROOT or out in ROOT.parents or any((ROOT/v).resolve()==out or (ROOT/v).resolve() in out.parents or out in (ROOT/v).resolve().parents for v in config['runtime'].values()):raise SystemExit('Output overlaps repository/runtime')
 if out.exists():raise SystemExit('Output already exists; choose a new empty path')
 out.mkdir(parents=True)
 for side,rel in config['runtime'].items():shutil.copytree(ROOT/rel,out/('behavior_pack' if side=='BP' else 'resource_pack'))
 print('Canonical runtime copied exactly; no private gameplay patches')
if __name__=='__main__':main()
