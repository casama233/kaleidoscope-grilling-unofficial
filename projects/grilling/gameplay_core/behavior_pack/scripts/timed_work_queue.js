/** Stable min-heap, bounded dequeue and keyed replacement without per-tick full sorts. */
export class TimedWorkQueue{
 constructor(){this.heap=[];this.live=new Map();this.serial=0;}
 before(a,b){return a.at<b.at||(a.at===b.at&&a.serial<b.serial);}
 schedule(key,at){const old=this.live.get(key);if(old?.at===at)return;const node={key,at,serial:++this.serial};this.live.set(key,node);this.heap.push(node);let i=this.heap.length-1;while(i){const p=(i-1)>>1;if(!this.before(node,this.heap[p]))break;this.heap[i]=this.heap[p];i=p;}this.heap[i]=node;}
 cancel(key){this.live.delete(key);}
 pop(){const first=this.heap[0],last=this.heap.pop();if(this.heap.length){let i=0;while(i*2+1<this.heap.length){let c=i*2+1;if(c+1<this.heap.length&&this.before(this.heap[c+1],this.heap[c]))c++;if(!this.before(this.heap[c],last))break;this.heap[i]=this.heap[c];i=c;}this.heap[i]=last;}return first;}
 take(now,budget){const out=[];while(this.heap.length&&out.length<budget){const n=this.heap[0];if(this.live.get(n.key)!==n){this.pop();continue;}if(n.at>now)break;this.pop();this.live.delete(n.key);out.push(n.key);}return out;}
 get size(){return this.live.size;}
}
