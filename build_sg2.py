import pandas as pd, numpy as np, json, warnings
warnings.filterwarnings("ignore")
a=pd.read_csv("agg_final.csv",encoding="utf-8-sig")
sm=pd.read_csv("store_meta.csv",encoding="utf-8-sig")
plan1={"즉석밥류","소스류","양념류","장류"}
plan2={"과일","냉동간편식","냉동밥","냉동만두","냉동면","1차축산물(생란,정육)"}
a["안"]=a["소분류"].map(lambda c:1 if c in plan1 else(2 if c in plan2 else 0))
a=a[a["안"]>0].copy()
days=dict(zip(sm["점포코드"],sm["관측일수"]))
a["일회전"]=a["sales"]/a["점포코드"].map(days)          # 관측기간 일평균 판매
a["발생비율"]=a["sold"]/a["점포코드"].map(days)
a["폐기율"]=a["폐기율"].clip(0,0.5)

# 인덱스: (store,prod)->row
bykey={(r["점포코드"],r["상품코드"]):r for _,r in a.iterrows()}
prod_meta=a.groupby("상품코드").agg(상품명=("상품명","first"),소분류=("소분류","first"),
    안=("안","first"),단가=("단가","median"),원가=("원가","median"),폐기율=("폐기율","median")).to_dict("index")

# 유사점포: 면적 최근접 6개
stores=sm.sort_values("매장면적").reset_index(drop=True)
areas=stores["매장면적"].values; codes=stores["점포코드"].values
def similar(code,k=6):
    i=list(codes).index(code)
    order=np.argsort(np.abs(areas-areas[i]))
    return [codes[j] for j in order if codes[j]!=code][:k]

# 점포별 상품별 일회전 lookup
rot={}; carried={}
for _,r in a.iterrows():
    rot[(r["점포코드"],r["상품코드"])]=r["일회전"]; carried.setdefault(r["점포코드"],set()).add(r["상품코드"])

def grade(code,pc):
    if pc not in carried.get(code,()): return "A"
    r=bykey[(code,pc)]["발생비율"]
    return "C" if r>=0.10 else "B"

recs={}
allprods=set(a["상품코드"])
for code in codes:
    sims=similar(code)
    lst=[]
    # 후보: 자점 취급 + 유사점포가 파는 상품
    cand=set(carried.get(code,set()))
    for s in sims: cand|=carried.get(s,set())
    for pc in cand:
        pm=prod_meta.get(pc); 
        if not pm: continue
        simvals=[rot[(s,pc)] for s in sims if (s,pc) in rot]
        simRot=float(np.mean(simvals)) if simvals else 0.0
        self_c = pc in carried.get(code,())
        selfRot=float(rot[(code,pc)]) if self_c else None
        if not self_c and simRot<0.10: continue      # 자점 미취급 & 유사점포도 저조 -> 제외
        # 단가/원가/폐기율: 자점 우선, 없으면 유사평균/상품중앙
        if self_c:
            rr=bykey[(code,pc)]; price=rr["단가"]; cost=rr["원가"]; wr=rr["폐기율"]
        else:
            price=pm["단가"]; cost=pm["원가"]; wr=pm["폐기율"]
        if price<=0 or cost<=0: continue
        lst.append({"code":str(pc),"name":pm["상품명"],"cat":pm["소분류"],"plan":int(pm["안"]),
            "grade":grade(code,pc),"selfRot":round(selfRot,2) if selfRot is not None else None,
            "simRot":round(simRot,2),"price":int(price),"cost":int(cost),"wrate":round(float(wr),3),
            "carried":bool(self_c)})
    lst.sort(key=lambda x:-x["simRot"])
    # 안별 상위 100
    out=[x for x in lst if x["plan"]==1][:100]+[x for x in lst if x["plan"]==2][:100]
    recs[str(code)]=out

stores_js=[{"code":str(r["점포코드"]),"name":r["점포명"],"area":round(float(r["매장면적"]),1),
    "loc":str(r["입지유형"]),"open":str(r["개점일자"]),"days":int(r["관측일수"]),
    "sims":[str(s) for s in similar(r["점포코드"])]} for _,r in stores.iterrows()]

json.dump({"stores":stores_js,"recs":recs},open("sg2_data.json","w"),ensure_ascii=False)
import os
print("stores",len(stores_js),"| json KB",round(os.path.getsize('sg2_data.json')/1024,1))
tot=sum(len(v) for v in recs.values())
print("총 추천엔트리",tot,"| 점포평균",round(tot/len(recs)))
# 샘플: 한 신점
s="55458"  # 수원영통점(신점, 36일)
ex=recs[s]
print(f"\n[예시] 55458 수원영통점 추천 {len(ex)}개, 미취급(A) 도입후보:",sum(1 for x in ex if x['grade']=='A'))
for x in sorted(ex,key=lambda x:-x['simRot'])[:5]:
    print(f"  {x['grade']} {x['name'][:18]:18s} 유사회전 {x['simRot']} 자점 {x['selfRot']} 단가{x['price']} 원가{x['cost']}")
