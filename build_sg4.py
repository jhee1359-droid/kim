import json
D=json.load(open("sg3_data.json"))
DATA_JS=json.dumps(D,ensure_ascii=False,separators=(',',':'))
CSS=open("_css_tmp.css").read() if False else None
# reuse CSS from build_sg3 by importing its string
import importlib.util,types
src=open("build_sg3.py").read()
CSS=src.split("CSS=r'''",1)[1].split("'''",1)[0]

HTML=r'''<title>SG 신규 개점 추천</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@500;700;800&family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>__CSS__</style>
<div class="wrap">
  <div class="htop">
    <div><div class="eyebrow">현장부서 AI · 2권역 · SG 신규 개점</div><h1>SG 신규 개점 추천</h1>
    <p class="sub"><b>매장면적·입지유형</b>만 입력하면, 면적·입지가 비슷한 기존점들이 실제로 파는 상품으로 1안·2안 <b>초도 발주안(무엇을·몇 개·왜)</b>을 제안합니다.</p></div>
    <button class="themebtn" id="theme">◐ 테마</button>
  </div>

  <div class="pick">
    <div class="pickrow">
      <div class="fld"><label>매장면적(㎡)</label><input id="area" type="number" value="150" min="80" max="320" step="1"></div>
      <div class="fld"><label>입지유형</label><select id="loc"></select></div>
      <div class="fld" style="flex:1"><label>&nbsp;</label><div class="storeinfo">예정 점포 조건 입력 → 유사 기존점 6곳의 실제 회전율로 초도 발주량을 산출합니다.</div></div>
    </div>
    <div class="matched" id="matched"></div>
  </div>

  <div class="tabs" id="tabs">
    <button class="tab" data-p="1" aria-selected="true"><div class="t1">1안 · 비축형</div><div class="t2">무투자 · 상온즉석식·조미소스 · 유통기한 6개월+</div></button>
    <button class="tab" data-p="2" aria-selected="false"><div class="t1">2안 · 모듈형</div><div class="t2">투자 · 과일·계란·냉동즉석식 · 집기 회수 반영</div></button>
  </div>
  <div class="summary" id="summary"></div>
  <details class="params"><summary>담당자 계산 파라미터</summary><div class="pgrid">
    <div class="pctl"><label>예상 발주량 조정 <b><span id="v-adj">+20%</span></b></label><input type="range" id="adj" min="-20" max="100" step="5" value="20"></div>
    <div class="pctl"><label>진열 최소단위 <b><span id="v-unitq">1</span>개</b></label><input type="range" id="unitq" min="1" max="12" step="1" value="1"></div>
    <div class="pctl" id="investwrap"><label>2안 집기 투자액 <b><span id="v-invest">30</span>만원</b></label><input type="range" id="invest" min="0" max="200" step="10" value="30"></div>
    <div class="pnote">단가·원가·폐기율은 셀프BI 실제값. 초도발주=올림(주간회전×(1+예상발주량조정)÷진열단위)×진열단위. 유사점포=면적·입지 근접 6개점.</div>
  </div></details>
  <div class="bar"><div class="chips" id="chips"></div>
    <select id="sort"><option value="profit">주간손익순</option><option value="rot">회전율순</option><option value="name">이름순</option></select>
    <input type="search" id="q" placeholder="상품명 검색…"></div>
  <div class="count" id="count"></div>
  <div class="cards" id="cards"></div>
  <footer>
    <div><b>추천강도</b> · <span style="color:var(--gC)">강력추천</span> 유사점포 하루 1개+ · <span style="color:var(--gA)">추천</span> 0.3~1개 · <span style="color:var(--gB)">검토</span> 0.1~0.3개</div>
    <div style="margin-top:5px"><b>산출</b> · 주간회전=유사점포 일평균×7 · 초도발주=올림(주간회전×(1+예상발주량조정)÷진열단위)×진열단위 · 폐기예상=초도발주×실제폐기율 · 주간손익=판매이익−폐기손실 <span id="foot2"></span></div>
    <div style="margin-top:5px">데이터: 2권역 19개 기존점·123일 셀프BI 실적 · 대상상품 605종.</div>
  </footer>
</div>
<script>
const D=__DATA__;const $=s=>document.querySelector(s);const won=n=>Math.round(n).toLocaleString();
const S=D.stores,PR=D.prods;
const rotBy=S.map(()=>({}));D.links.forEach(([s,p,r])=>{rotBy[s][p]=r;});
let P={plan:1,g:"all",sort:"profit",q:"",adj:20,unitq:1,invest:30,area:150,loc:""};
$("#loc").innerHTML='<option value="">전체 입지</option>'+[...new Set(S.map(s=>s.loc))].sort().map(l=>`<option value="${l}">입지 ${l}</option>`).join("");

function simStores(area,loc){
  let pool=S.map((s,i)=>({i,s}));
  let wl=loc?pool.filter(x=>x.s.loc===loc):pool;
  let base=wl.length>=3?wl:pool;
  base.sort((a,b)=>Math.abs(a.s.area-area)-Math.abs(b.s.area-area));
  return base.slice(0,6).map(x=>x.i);
}
const GR=[[1.0,"강력추천","gC","S"],[0.3,"추천","gA","R"],[0.1,"검토","gB","V"]];
function grade(r){for(const g of GR)if(r>=g[0])return g;return null;}
function build(sims){
  const rows=[];
  for(let p=0;p<PR.length;p++){
    if(PR[p].plan!==P.plan)continue;
    const cs=sims.filter(s=>rotBy[s][p]!=null);
    if(!cs.length)continue;
    const simRot=cs.reduce((a,s)=>a+rotBy[s][p],0)/cs.length;
    if(simRot<0.1)continue;
    const g=grade(simRot),pr=PR[p],w=simRot*7,u=P.unitq;
    const qty=Math.max(u,Math.ceil(w*(1+P.adj/100)/u)*u);
    const wasteQ=qty*pr.wrate, net=w*(pr.price-pr.cost)-wasteQ*pr.cost;
    rows.push({name:pr.name,cat:pr.cat,price:pr.price,simRot:+simRot.toFixed(2),rot:simRot,
      qty:Math.round(qty),wasteQ,net,grade:g[1],gcls:g[2],gkey:g[3],carriers:cs.length});
  }
  return rows;
}
const CHIPS=[["all","전체",""],["S","강력추천","gC"],["R","추천","gA"],["V","검토","gB"]];
$("#chips").innerHTML=CHIPS.map(([k,l,c])=>`<button class="chip ${c}" data-g="${k}" aria-pressed="${P.g===k}">${c?'<span class="dot"></span>':''}${l}</button>`).join("");

function render(){
  P.area=+$("#area").value||150;P.loc=$("#loc").value;
  const sims=simStores(P.area,P.loc);
  $("#matched").innerHTML=`유사 기존점 <b>${sims.length}개</b> (면적 ${P.area}㎡·입지 ${P.loc||'전체'} 근접): `+sims.map(i=>`${S[i].name}(${S[i].area}㎡·입지${S[i].loc})`).join(" · ");
  const list=build(sims);
  const net=list.reduce((a,r)=>a+r.net,0), totQty=list.reduce((a,r)=>a+r.qty,0);
  const hi=list.filter(r=>r.gkey==="S").length;
  const depr=P.plan===2?P.invest*10000/156:0, payback=(P.plan===2&&net>0)?P.invest*10000/net:0;
  const c4=[["추천 품목","",`${list.length}<small>종</small>`],["강력추천","g",`${hi}<small>종</small>`],
    ["초도 총발주","",`${won(totQty)}<small>개</small>`],
    P.plan===2?["집기 투자회수",payback>0?"pos":"",payback>0?`${payback.toFixed(0)}<small>주</small>`:"—"]:["주간 예상손익",net>=0?"pos":"",`${won(net)}<small>원</small>`]];
  $("#summary").innerHTML=c4.map(([l,c,v])=>`<div class="scard ${c}"><div class="strip"></div><div class="lab">${l}</div><div class="val mono">${v}</div></div>`).join("");
  $("#foot2").innerHTML=P.plan===2?`· 2안 순손익=Σ손익−주간감가(${won(depr)}원)`:"";
  let f=list.filter(r=>(P.g==="all"||r.gkey===P.g)&&(!P.q||r.name.toLowerCase().includes(P.q.toLowerCase())));
  f.sort((a,b)=>P.sort==="name"?a.name.localeCompare(b.name,"ko"):P.sort==="rot"?b.rot-a.rot:b.net-a.net);
  $("#count").textContent=`${f.length}개 · ${P.plan}안 ${P.plan===1?'비축형·무투자':'모듈형·투자'} · 신규 개점 초도발주`;
  const wrap=$("#cards");
  if(!f.length){wrap.innerHTML='<div class="empty">해당 조건의 추천 상품이 없습니다.</div>';return;}
  const fr=document.createDocumentFragment();
  f.forEach(r=>{const el=document.createElement("div");el.className="card "+r.gcls;
    el.innerHTML=`<div class="top"><div><div class="nm">${esc(r.name)}</div><div class="ct">${esc(r.cat)} · 단가 ${won(r.price)}원</div></div><div class="grade ${r.gcls}">${r.grade}</div></div>`+
    `<div class="evi">유사점포 <b>${r.carriers}개</b>가 하루 평균 <b>${r.simRot}개</b> 판매. 개점 초도 <b>${r.qty}개</b> 발주 시 주간손익 <b>${won(r.net)}원</b>.</div>`+
    `<div class="metrics"><div class="metric"><div class="k">초도발주/주</div><div class="v">${r.qty}<small>개</small></div></div>`+
    `<div class="metric"><div class="k">폐기예상</div><div class="v">${r.wasteQ.toFixed(1)}<small>개</small></div></div>`+
    `<div class="metric profit"><div class="k">주간손익</div><div class="v ${r.net>=0?'pos':'neg'}">${won(r.net)}<small>원</small></div></div></div>`;
    fr.appendChild(el);});
  wrap.innerHTML="";wrap.appendChild(fr);
}
function esc(s){return s.replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));}
$("#tabs").onclick=e=>{const t=e.target.closest(".tab");if(!t)return;P.plan=+t.dataset.p;
  [...e.currentTarget.children].forEach(c=>c.setAttribute("aria-selected",c===t));$("#investwrap").style.display=P.plan===2?"":"none";render();};
$("#investwrap").style.display="none";
$("#chips").onclick=e=>{const b=e.target.closest(".chip");if(!b)return;P.g=b.dataset.g;
  [...e.currentTarget.children].forEach(c=>c.setAttribute("aria-pressed",c===b));render();};
$("#area").oninput=render;$("#loc").onchange=render;
const bind=(id,k,f)=>{$("#"+id).oninput=e=>{P[k]=+e.target.value;$("#v-"+id).textContent=f?f(P[k]):P[k];render();};};
bind("adj","adj",v=>(v>=0?"+":"")+v+"%");bind("unitq","unitq");bind("invest","invest");
$("#sort").onchange=e=>{P.sort=e.target.value;render();};$("#q").oninput=e=>{P.q=e.target.value;render();};
const root=document.documentElement;$("#theme").onclick=()=>{const c=root.getAttribute("data-theme")||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");root.setAttribute("data-theme",c==="dark"?"light":"dark");};
render();
</script>'''
out=HTML.replace("__CSS__",CSS).replace("__DATA__",DATA_JS)
open("SG_신규개점_tool.html","w").write(out)
print("written",round(len(out)/1024,1),"KB")
