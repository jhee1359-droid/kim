import json
D=json.load(open("sg3_data.json"))
DATA_JS=json.dumps(D,ensure_ascii=False,separators=(',',':'))
CSS=r'''
:root{--bg:#eef1ef;--surface:#fff;--surface-2:#f4f7f5;--surface-3:#e9efec;
--ink:#15201b;--ink-soft:#556158;--ink-faint:#879189;--line:#dde4df;--line-strong:#c7d0ca;
--accent:#0f766e;--accent-soft:#dcefec;--accent-ink:#0b574f;--p1:#0f766e;--p1-soft:#dcefec;--p2:#b45309;--p2-soft:#f7ead5;
--gA:#2563eb;--gA-bg:#e5edfb;--gB:#c2790a;--gB-bg:#fbeed6;--gC:#15864a;--gC-bg:#e4f3e9;--pos:#15864a;--neg:#cc3b3b;
--shadow:0 1px 2px rgba(20,40,35,.06),0 8px 22px rgba(20,40,35,.06);}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;
--bg:#0d1210;--surface:#141b17;--surface-2:#1a221d;--surface-3:#202a24;--ink:#e6ede8;--ink-soft:#98a29b;--ink-faint:#6b746d;--line:#27312b;--line-strong:#354139;
--accent:#2dd4bf;--accent-soft:#123430;--accent-ink:#7ff0e2;--p1:#2dd4bf;--p1-soft:#123430;--p2:#f0a83a;--p2-soft:#3a2a10;
--gA:#7db3f0;--gA-bg:#16263c;--gB:#f0b429;--gB-bg:#332708;--gC:#4ade80;--gC-bg:#123020;--pos:#4ade80;--neg:#f87171;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.4);}}
[data-theme="dark"]{color-scheme:dark;--bg:#0d1210;--surface:#141b17;--surface-2:#1a221d;--surface-3:#202a24;--ink:#e6ede8;--ink-soft:#98a29b;--ink-faint:#6b746d;--line:#27312b;--line-strong:#354139;
--accent:#2dd4bf;--accent-soft:#123430;--accent-ink:#7ff0e2;--p1:#2dd4bf;--p1-soft:#123430;--p2:#f0a83a;--p2-soft:#3a2a10;
--gA:#7db3f0;--gA-bg:#16263c;--gB:#f0b429;--gB-bg:#332708;--gC:#4ade80;--gC-bg:#123020;--pos:#4ade80;--neg:#f87171;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.4);}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",system-ui,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1000px;margin:0 auto;padding:22px 16px 64px}
h1{font-family:"Gothic A1",sans-serif;margin:0;font-size:25px;font-weight:800;letter-spacing:-.01em}
.mono{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.eyebrow{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent-ink);font-weight:600}
.htop{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.sub{color:var(--ink-soft);font-size:13.5px;margin:5px 0 0;max-width:62ch}
.themebtn{border:1px solid var(--line-strong);background:var(--surface);color:var(--ink-soft);border-radius:9px;padding:8px 12px;font:inherit;font-size:13px;cursor:pointer}
.modes{display:flex;gap:8px;margin:16px 0 0;background:var(--surface-3);padding:5px;border-radius:12px;width:fit-content}
.mode{border:0;background:transparent;color:var(--ink-soft);border-radius:9px;padding:9px 18px;font:inherit;font-size:14px;font-weight:600;cursor:pointer;font-family:"Gothic A1",sans-serif}
.mode[aria-selected=true]{background:var(--surface);color:var(--accent-ink);box-shadow:var(--shadow)}
.pick{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;margin:14px 0;box-shadow:var(--shadow)}
.pickrow{display:flex;gap:16px;align-items:flex-end;flex-wrap:wrap}
.fld{display:flex;flex-direction:column;gap:6px}
.fld label{font-size:12px;color:var(--ink-soft);font-weight:600}
.fld input,.fld select{font:inherit;font-size:16px;font-weight:600;padding:10px 12px;border:1px solid var(--line-strong);border-radius:10px;background:var(--surface-2);color:var(--ink)}
.fld input{width:120px}.fld select{min-width:120px}
.fld input:focus,.fld select:focus{outline:2px solid var(--accent);outline-offset:1px}
.matched{margin-top:12px;font-size:12.5px;color:var(--ink-faint);line-height:1.6;border-top:1px dashed var(--line);padding-top:10px}
.matched b{color:var(--accent-ink);font-weight:600}
.storeinfo{font-size:13px;color:var(--ink-soft);line-height:1.7}.storeinfo b{color:var(--ink);font-weight:600}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;margin-left:6px}
.tag.new{background:var(--gA-bg);color:var(--gA)}.tag.old{background:var(--surface-3);color:var(--ink-faint)}
.tabs{display:flex;gap:8px;margin:14px 0}
.tab{flex:1;border:1px solid var(--line-strong);background:var(--surface);border-radius:12px;padding:11px 14px;cursor:pointer;text-align:left}
.tab .t1{font-family:"Gothic A1",sans-serif;font-weight:700;font-size:14.5px}.tab .t2{font-size:11px;color:var(--ink-faint);margin-top:2px}
.tab[data-p="1"][aria-selected=true]{border-color:var(--p1);box-shadow:inset 0 0 0 1px var(--p1);background:var(--p1-soft)}
.tab[data-p="2"][aria-selected=true]{border-color:var(--p2);box-shadow:inset 0 0 0 1px var(--p2);background:var(--p2-soft)}
.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.scard{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:13px 14px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.scard .strip{position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent)}.scard.g .strip{background:var(--gC)}.scard.pos .strip{background:var(--pos)}.scard.pos .val{color:var(--pos)}
.scard .lab{font-size:11.5px;color:var(--ink-soft);font-weight:500}.scard .val{font-size:22px;font-weight:600;margin-top:5px;line-height:1}.scard .val small{font-size:12px;color:var(--ink-faint);margin-left:2px;font-weight:500}
.bar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line-strong);background:var(--surface);color:var(--ink-soft);border-radius:999px;padding:6px 12px;font-size:12.5px;cursor:pointer;font-weight:500;display:flex;align-items:center;gap:6px}
.chip[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:#fff}
[data-theme="dark"] .chip[aria-pressed=true],:root:not([data-theme="light"]) .chip[aria-pressed=true]{color:#04110e}
.chip .dot{width:8px;height:8px;border-radius:50%}.chip.gA .dot{background:var(--gA)}.chip.gB .dot{background:var(--gB)}.chip.gC .dot{background:var(--gC)}
.bar select,.bar input{font:inherit;font-size:13px;padding:7px 10px;border:1px solid var(--line-strong);border-radius:9px;background:var(--surface);color:var(--ink)}
.bar input[type=search]{flex:1;min-width:130px}
details.params{background:var(--surface);border:1px solid var(--line);border-radius:12px;margin-bottom:14px;box-shadow:var(--shadow)}
details.params summary{cursor:pointer;padding:12px 16px;font-size:13px;font-weight:600;color:var(--ink-soft);list-style:none;display:flex;gap:8px}
details.params summary::-webkit-details-marker{display:none}details.params summary::before{content:"⚙"}
.pgrid{padding:2px 16px 16px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px 22px}
.pctl label{display:flex;justify-content:space-between;font-size:12.5px;color:var(--ink-soft);margin-bottom:6px}.pctl label b{color:var(--accent-ink);font-weight:600}
.pctl input[type=range]{width:100%;accent-color:var(--accent)}
.pnote{font-size:11.5px;color:var(--ink-faint);grid-column:1/-1;border-top:1px dashed var(--line);padding-top:9px}
.count{font-size:12.5px;color:var(--ink-faint);margin:0 2px 12px}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.card{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--line-strong);border-radius:14px;padding:15px 16px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:11px}
.card.gA{border-left-color:var(--gA)}.card.gB{border-left-color:var(--gB)}.card.gC{border-left-color:var(--gC)}
.card .top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.card .nm{font-weight:600;font-size:14.5px;line-height:1.3}.card .ct{font-size:11.5px;color:var(--ink-faint);margin-top:2px}
.grade{flex-shrink:0;padding:5px 10px;border-radius:10px;font-weight:700;font-size:12px;font-family:"Gothic A1",sans-serif;white-space:nowrap}
.grade.gA{background:var(--gA-bg);color:var(--gA)}.grade.gB{background:var(--gB-bg);color:var(--gB)}.grade.gC{background:var(--gC-bg);color:var(--gC)}
.evi{font-size:12.5px;color:var(--ink-soft);background:var(--surface-2);border-radius:9px;padding:9px 11px;line-height:1.5}.evi b{color:var(--ink);font-weight:600}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.metric{background:var(--surface-2);border-radius:9px;padding:8px 10px}.metric .k{font-size:10.5px;color:var(--ink-faint);font-weight:500}
.metric .v{font-size:16px;font-weight:600;margin-top:3px;font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;line-height:1.1}.metric .v small{font-size:10px;color:var(--ink-faint);margin-left:1px;font-weight:500}
.metric.profit .v.pos{color:var(--pos)}.metric.profit .v.neg{color:var(--neg)}
.empty{padding:36px;text-align:center;color:var(--ink-faint);grid-column:1/-1}
footer{margin-top:24px;font-size:11.5px;color:var(--ink-faint);line-height:1.75;border-top:1px solid var(--line);padding-top:14px}footer b{color:var(--ink-soft);font-weight:600}
@media (max-width:680px){.summary{grid-template-columns:repeat(2,1fr)}.cards{grid-template-columns:1fr}.pgrid{grid-template-columns:1fr 1fr}}
'''
HTML=r'''<title>SG 개점 상품 진단</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@500;700;800&family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>__CSS__</style>
<div class="wrap">
  <div class="htop">
    <div><div class="eyebrow">현장부서 AI · 2권역 · SG 이식</div><h1>SG 개점 상품 진단</h1>
    <p class="sub">유사점포(면적·입지 근접)의 실제 회전율을 근거로 1안·2안 <b>추천상품·적정수량·폐기예상·손익</b>을 산출합니다.</p></div>
    <button class="themebtn" id="theme">◐ 테마</button>
  </div>
  <div class="modes" id="modes">
    <button class="mode" data-m="new" aria-selected="true">신규 개점</button>
    <button class="mode" data-m="exist" aria-selected="false">기존점 진단</button>
  </div>

  <div class="pick">
    <div id="newpick">
      <div class="pickrow">
        <div class="fld"><label>매장면적(㎡)</label><input id="area" type="number" value="150" min="80" max="320" step="1"></div>
        <div class="fld"><label>입지유형</label><select id="loc"></select></div>
        <div class="fld" style="flex:1"><label>&nbsp;</label><div class="storeinfo">신규 개점 예정 점포 조건을 입력하면, 유사한 기존점들이 실제로 파는 상품으로 <b>초도 발주안</b>을 제안합니다.</div></div>
      </div>
      <div class="matched" id="matchednew"></div>
    </div>
    <div id="existpick" hidden>
      <div class="pickrow">
        <div class="fld"><label>점포 선택</label><select id="store"></select></div>
        <div class="fld" style="flex:1"><label>&nbsp;</label><div class="storeinfo" id="storeinfo"></div></div>
      </div>
      <div class="matched" id="matchedex"></div>
    </div>
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
    <div class="pnote">단가·원가·폐기율은 셀프BI 실제값. 적정수량=올림(주간회전×(1+예상발주량조정)÷진열단위)×진열단위. 유사점포=면적·입지 근접 6개점.</div>
  </div></details>
  <div class="bar"><div class="chips" id="chips"></div>
    <select id="sort"><option value="profit">주간손익순</option><option value="rot">회전율순</option><option value="name">이름순</option></select>
    <input type="search" id="q" placeholder="상품명 검색…"></div>
  <div class="count" id="count"></div>
  <div class="cards" id="cards"></div>
  <footer>
    <div id="footgrade"></div>
    <div style="margin-top:5px"><b>산출</b> · 주간회전=일회전×7 · 적정수량=올림(주간회전×(1+예상발주량조정)÷진열단위)×진열단위 · 폐기예상=적정수량×실제폐기율 · 주간손익=판매이익−폐기손실 <span id="foot2"></span></div>
    <div style="margin-top:5px">데이터: 2권역 19개 점포(기존 13·신점 6)·123일 셀프BI 실적.</div>
  </footer>
</div>
<script>
const D=__DATA__;const $=s=>document.querySelector(s);const won=n=>Math.round(n).toLocaleString();
const S=D.stores,PR=D.prods;
const rotBy=S.map(()=>({}));D.links.forEach(([s,p,r])=>{rotBy[s][p]=r;});
let P={mode:"new",plan:1,g:"all",sort:"profit",q:"",adj:20,unitq:1,invest:30,area:150,loc:"",store:0};

// init selects
$("#loc").innerHTML='<option value="">전체 입지</option>'+[...new Set(S.map(s=>s.loc))].sort().map(l=>`<option value="${l}">입지 ${l}</option>`).join("");
$("#store").innerHTML=S.map((s,i)=>`<option value="${i}">${s.code} · ${s.name} (${s.area}㎡)</option>`).join("");
function isNew(s){return String(s.open)>="20260101";}

function simStores(area,loc,exclude){
  let pool=S.map((s,i)=>({i,s})).filter(x=>x.i!==exclude);
  let wl=loc?pool.filter(x=>x.s.loc===loc):pool;
  let base=wl.length>=3?wl:pool;
  base.sort((a,b)=>Math.abs(a.s.area-area)-Math.abs(b.s.area-area));
  return base.slice(0,6).map(x=>x.i);
}
function factor(){return 1+P.adj/100;}
function build(sims,selfIdx){
  // selfIdx: 기존점 index (null이면 신규)
  const rows=[];
  for(let p=0;p<PR.length;p++){
    if(PR[p].plan!==P.plan)continue;
    const carriers=sims.filter(s=>rotBy[s][p]!=null);
    const simRot=carriers.length?carriers.reduce((a,s)=>a+rotBy[s][p],0)/carriers.length:0;
    const self=selfIdx!=null?rotBy[selfIdx][p]:null;
    let grade,rot;
    if(selfIdx==null){                     // 신규: 전 품목 도입 대상
      if(simRot<0.1)continue; rot=simRot;
      grade=simRot>=1.0?["강력추천","gC","S"]:simRot>=0.3?["추천","gA","R"]:["검토","gB","V"];
    }else{                                 // 기존점
      const carried=self!=null;
      if(!carried&&simRot<0.1)continue;
      rot=carried?self:simRot;
      grade=!carried?["도입후보","gA","A"]:(self>=0.1?["정상","gC","C"]:["취급·저조","gB","B"]);
    }
    const pr=PR[p],w=rot*7,u=P.unitq;
    const qty=Math.max(u,Math.ceil(w*factor()/u)*u);
    const wasteQ=qty*pr.wrate, net=w*(pr.price-pr.cost)-wasteQ*pr.cost;
    rows.push({p,name:pr.name,cat:pr.cat,price:pr.price,simRot:+simRot.toFixed(2),self:self!=null?+self.toFixed(2):null,
      rot,qty:Math.round(qty),wasteQ,net,grade:grade[0],gcls:grade[1],gkey:grade[2],carriers:carriers.length});
  }
  return rows;
}
const CHIPS={new:[["all","전체",""],["S","강력추천","gC"],["R","추천","gA"],["V","검토","gB"]],
             exist:[["all","전체",""],["A","도입후보","gA"],["C","정상","gC"],["B","취급·저조","gB"]]};
function renderChips(){$("#chips").innerHTML=CHIPS[P.mode].map(([k,l,c])=>
  `<button class="chip ${c}" data-g="${k}" aria-pressed="${P.g===k}">${c?'<span class="dot"></span>':''}${l}</button>`).join("");}

function reason(r){
  const ns=r.carriers;
  if(P.mode==="new") return `유사점포 <b>${ns}개</b>가 하루 평균 <b>${r.simRot}개</b> 판매. 개점 초도 <b>${r.qty}개</b> 발주 시 주간손익 <b>${won(r.net)}원</b> — ${r.grade}.`;
  if(r.gkey==="A") return `자점 <b>미취급</b>이나 유사점포 ${ns}개는 하루 <b>${r.simRot}개</b> 판매. 도입 시 주간 <b>${r.qty}개</b>, 손익 <b>${won(r.net)}원</b>.`;
  return `자점 하루 <b>${r.self}개</b> 회전. 주간 적정 <b>${r.qty}개</b>, 손익 <b>${won(r.net)}원</b>, 폐기예상 ${r.wasteQ.toFixed(1)}개.`;
}
function render(){
  let sims,selfIdx=null,head="";
  if(P.mode==="new"){
    P.area=+$("#area").value||150; P.loc=$("#loc").value;
    sims=simStores(P.area,P.loc,null);
    $("#matchednew").innerHTML=`유사 기존점 <b>${sims.length}개</b> (면적 ${P.area}㎡·입지 ${P.loc||'전체'} 근접): `+sims.map(i=>`${S[i].name}(${S[i].area}㎡)`).join(" · ");
  }else{
    selfIdx=P.store; const s=S[selfIdx];
    sims=simStores(s.area,s.loc,selfIdx);
    $("#storeinfo").innerHTML=`<b>${s.name}</b> (${s.code}) <span class="tag ${isNew(s)?'new':'old'}">${isNew(s)?'신점':'기존점'}</span> · ${s.area}㎡ · 입지 ${s.loc} · 개점 ${String(s.open).replace(/(\d{4})(\d{2})(\d{2})/,'$1.$2.$3')}`;
    $("#matchedex").innerHTML=`유사점포 <b>${sims.length}개</b>: `+sims.map(i=>`${S[i].name}(${S[i].area}㎡)`).join(" · ");
  }
  const list=build(sims,selfIdx);
  const net=list.reduce((a,r)=>a+r.net,0);
  const depr=P.plan===2?P.invest*10000/156:0, payback=(P.plan===2&&net>0)?P.invest*10000/net:0;
  const hi=P.mode==="new"?list.filter(r=>r.gkey==="S").length:list.filter(r=>r.gkey==="A").length;
  const totQty=list.reduce((a,r)=>a+r.qty,0);
  const c4=P.mode==="new"
    ?[["추천 품목","",`${list.length}<small>종</small>`],["강력추천","g",`${hi}<small>종</small>`],["초도 총발주","",`${won(totQty)}<small>개</small>`],
      P.plan===2?["집기 투자회수",payback>0?"pos":"",payback>0?`${payback.toFixed(0)}<small>주</small>`:"—"]:["주간 예상손익",net>=0?"pos":"",`${won(net)}<small>원</small>`]]
    :[["추천 품목","",`${list.length}<small>종</small>`],["도입후보(A)","g",`${hi}<small>종</small>`],["주간 예상손익",net>=0?"pos":"",`${won(net)}<small>원</small>`],
      P.plan===2?["집기 투자회수",payback>0?"pos":"",payback>0?`${payback.toFixed(0)}<small>주</small>`:"—"]:["유사점포","",`${sims.length}<small>개</small>`]];
  $("#summary").innerHTML=c4.map(([l,c,v])=>`<div class="scard ${c}"><div class="strip"></div><div class="lab">${l}</div><div class="val mono">${v}</div></div>`).join("");
  $("#foot2").innerHTML=P.plan===2?`· 2안 순손익=Σ손익−주간감가(${won(depr)}원)`:"";
  $("#footgrade").innerHTML=P.mode==="new"
    ?'<b>추천강도</b> · <span style="color:var(--gC)">강력추천</span> 유사점포 하루1개+ · <span style="color:var(--gA)">추천</span> 0.3~1 · <span style="color:var(--gB)">검토</span> 0.1~0.3'
    :'<b>등급</b> · <span style="color:var(--gA)">도입후보</span> 자점 미취급·유사점포 판매 · <span style="color:var(--gC)">정상</span> 자점 회전 양호 · <span style="color:var(--gB)">취급·저조</span> 자점 회전 낮음';

  let f=list.filter(r=>(P.g==="all"||r.gkey===P.g)&&(!P.q||r.name.toLowerCase().includes(P.q.toLowerCase())));
  f.sort((a,b)=>P.sort==="name"?a.name.localeCompare(b.name,"ko"):P.sort==="rot"?b.rot-a.rot:b.net-a.net);
  $("#count").textContent=`${f.length}개 · ${P.plan}안 ${P.plan===1?'비축형·무투자':'모듈형·투자'} · ${P.mode==="new"?'신규 개점 초도발주':'기존점 발주진단'}`;
  const wrap=$("#cards");
  if(!f.length){wrap.innerHTML='<div class="empty">해당 조건의 추천 상품이 없습니다.</div>';return;}
  const fr=document.createDocumentFragment();
  f.forEach(r=>{const el=document.createElement("div");el.className="card "+r.gcls;
    el.innerHTML=`<div class="top"><div><div class="nm">${esc(r.name)}</div><div class="ct">${esc(r.cat)} · 단가 ${won(r.price)}원</div></div><div class="grade ${r.gcls}">${r.grade}</div></div>`+
    `<div class="evi">${reason(r)}</div><div class="metrics">`+
    `<div class="metric"><div class="k">${P.mode==="new"?"초도발주/주":"적정수량/주"}</div><div class="v">${r.qty}<small>개</small></div></div>`+
    `<div class="metric"><div class="k">폐기예상</div><div class="v">${r.wasteQ.toFixed(1)}<small>개</small></div></div>`+
    `<div class="metric profit"><div class="k">주간손익</div><div class="v ${r.net>=0?'pos':'neg'}">${won(r.net)}<small>원</small></div></div></div>`;
    fr.appendChild(el);});
  wrap.innerHTML="";wrap.appendChild(fr);
}
function esc(s){return s.replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));}
$("#modes").onclick=e=>{const b=e.target.closest(".mode");if(!b)return;P.mode=b.dataset.m;P.g="all";
  [...e.currentTarget.children].forEach(c=>c.setAttribute("aria-selected",c===b));
  $("#newpick").hidden=P.mode!=="new";$("#existpick").hidden=P.mode==="new";renderChips();render();};
$("#tabs").onclick=e=>{const t=e.target.closest(".tab");if(!t)return;P.plan=+t.dataset.p;
  [...e.currentTarget.children].forEach(c=>c.setAttribute("aria-selected",c===t));$("#investwrap").style.display=P.plan===2?"":"none";render();};
$("#investwrap").style.display="none";
$("#chips").onclick=e=>{const b=e.target.closest(".chip");if(!b)return;P.g=b.dataset.g;
  [...e.currentTarget.children].forEach(c=>c.setAttribute("aria-pressed",c===b));render();};
$("#area").oninput=render;$("#loc").onchange=render;$("#store").onchange=e=>{P.store=+e.target.value;render();};
const bind=(id,k,f)=>{$("#"+id).oninput=e=>{P[k]=+e.target.value;$("#v-"+id).textContent=f?f(P[k]):P[k];render();};};
bind("adj","adj",v=>(v>=0?"+":"")+v+"%");bind("unitq","unitq");bind("invest","invest");
$("#sort").onchange=e=>{P.sort=e.target.value;render();};$("#q").oninput=e=>{P.q=e.target.value;render();};
const root=document.documentElement;$("#theme").onclick=()=>{const c=root.getAttribute("data-theme")||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");root.setAttribute("data-theme",c==="dark"?"light":"dark");};
renderChips();render();
</script>'''
out=HTML.replace("__CSS__",CSS).replace("__DATA__",DATA_JS)
open("SG_개점진단_tool.html","w").write(out)
print("written",round(len(out)/1024,1),"KB")
