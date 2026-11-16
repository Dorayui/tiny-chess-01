import os,json,urllib.request as U
V=[0,100,320,330,500,900,20000]
D={2:(31,33,14,18,-31,-33,-14,-18),3:(15,17,-15,-17),4:(1,16,-1,-16)}
D[5]=D[6]=D[3]+D[4]
T={};K={};N=0
def fen(f):
 b=[0]*128;rows,s,c,e,*_=f.split()
 for r,row in enumerate(rows.split('/')):
  x=0
  for p in row:
   if p.isdigit():x+=int(p)
   else:b[(7-r)*16+x]=' PNBRQK'.index(p.upper())*(1 if p<'a' else -1);x+=1
 return b,1 if s=='w' else -1,c,-1 if e=='-' else ord(e[0])-97+16*(int(e[1])-1)
def hit(b,t,s):
 for d in (-15,-17):
  q=t+d*s
  if not q&136 and b[q]==s:return 1
 for p in D:
  for d in D[p]:
   q=t+d
   while not q&136:
    if b[q]:
     if b[q]==p*s:return 1
     break
    if p in (2,6):break
    q+=d
 return 0
def play(z,m):
 b,s,c,e=z;b=b[:];a,t,p=m;v=b[a];b[a]=0
 if abs(v)==1 and t==e:b[t-16*s]=0
 b[t]=p*s if p else v
 if abs(v)==6 and abs(t-a)==2:
  r=a+3 if t>a else a-4;b[(a+t)//2]=b[r];b[r]=0
 for q,h in ((4,'KQ'),(116,'kq'),(0,'Q'),(7,'K'),(112,'q'),(119,'k')):
  if a==q or t==q:
   for k in h:c=c.replace(k,'')
 return b,-s,c,(a+t)//2 if abs(v)==1 and abs(t-a)==32 else -1
def moves(z,cap=0):
 b,s,c,e=z;o=[];king=b.index(6*s)
 for a in range(128):
  if a&136 or b[a]*s<=0:continue
  p=abs(b[a]);ts=[]
  if p==1:
   t=a+16*s
   if not t&136 and not b[t]:
    ts.append(t)
    if a//16==(1 if s==1 else 6) and not b[t+16*s]:ts.append(t+16*s)
   for d in (15,17):
    t=a+d*s
    if not t&136 and (b[t]*s<0 or t==e):ts.append(t)
  else:
   for d in D[p]:
    t=a+d
    while not t&136:
     if b[t]*s>0:break
     ts.append(t)
     if b[t] or p in (2,6):break
     t+=d
   if p==6 and a in (4,116) and not cap and not hit(b,a,-s):
    for h,d in (('K' if s==1 else 'k',1),('Q' if s==1 else 'q',-1)):
     if h in c and b[a+(3 if d==1 else -4)]==4*s and all(not b[a+i*d] for i in range(1,3 if d==1 else 4)) and not hit(b,a+d,-s):ts.append(a+2*d)
  for t in ts:
   if cap and not b[t] and not (p==1 and t==e):continue
   for pr in ((5,4,3,2) if p==1 and t//16 in (0,7) else (0,)):
    m=(a,t,pr)
    if not hit(play(z,m)[0],t if p==6 else king,-s):o.append(m)
 return o
def val(z):
 b,s,_,_=z;v=0;end=sum(V[abs(p)] for p in b if 1<abs(p)<6)<2400
 for a,p in enumerate(b):
  if p:
   k=abs(p);y=a//16 if p>0 else 7-a//16;c=7-abs(2*(a%16)-7)-abs(2*y-7)
   v+=(1 if p>0 else -1)*(V[k]+(y*7 if k==1 else c*4 if k<5 else c if k==5 else c*5 if end else -c*4-y*8))
 return s*(v+30*((b.count(3)>1)-(b.count(-3)>1)))
def search(z,d,a,b,l=0):
 global N
 N+=1
 if N>50000:raise TimeoutError
 key=(tuple(z[0]),*z[1:]);old=a;tt=T.get(key);best=None
 if d>0 and tt and tt[0]>=d and abs(tt[1])<29000:
  _,v,f,best=tt
  if f==0 or f==1 and v>=b or f==-1 and v<=a:return v
 check=hit(z[0],z[0].index(6*z[1]),-z[1])
 if d<=0 and not check:
  v=val(z)
  if v>=b:return v
  a=max(a,v)
 ms=moves(z,d<=0 and not check)
 if not ms:return -30000+l if check else (0 if d>0 else a)
 ms.sort(key=lambda m:10**6*(m==(tt[3] if tt else None))+10*V[abs(z[0][m[1]])]-abs(z[0][m[0]])+V[m[2]]+90*(m==K.get(l)),reverse=True)
 for m in ms:
  v=-search(play(z,m),d-1,-b,-a,l+1)
  if v>a:a=v;best=m
  if a>=b:K[l]=m;break
 if d>0:
  if len(T)>18000:T.clear()
  T[key]=(d,a,1 if a>=b else -1 if a<=old else 0,best or ms[0])
 return a
def uci(m):
 a,t,p=m;return ''.join(chr(97+q%16)+str(1+q//16) for q in (a,t))+(' pnbrqk'[p] if p else '')
def choose(f,legal):
 global N
 N=0;T.clear();K.clear();best=legal[0]
 try:
  z=fen(f)
  for d in range(1,31):
   search(z,d,-31000,31000);m=uci(T[(tuple(z[0]),*z[1:])][3])
   if m in legal:best=m
 except TimeoutError:pass
 except Exception:return legal[0]
 return best
def main():
 url=os.environ['MAKEFUN_ENV_URL'].rstrip('/')
 def post(p,o):return json.load(U.urlopen(U.Request(url+p,json.dumps(o).encode(),{'Content-Type':'application/json'})))
 while True:
  g=post('/game',{})
  while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
  if g['status']=='done':break
if __name__=='__main__':main()
