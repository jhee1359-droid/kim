import pandas as pd, numpy as np, warnings, pickle
warnings.filterwarnings("ignore")
p="sgdata/001.점포_상품 매출 분석(일)_20260902144541.csv"
cols=['점포코드','점포명','매장면적','입지유형','개점일자','기준일자명','03.상품소분류명',
      '04.상품코드','04.상품명','현재매가','기준원가','판매수량','발주수량','폐기수량']
dt={'점포코드':'int32','점포명':'str','매장면적':'float32','입지유형':'str','개점일자':'str',
    '기준일자명':'str','03.상품소분류명':'str','04.상품코드':'str','04.상품명':'str',
    '현재매가':'float32','기준원가':'float32','판매수량':'float32','발주수량':'float32','폐기수량':'float32'}
parts=[]; smeta=[]; rows=0; dates=set()
for ch in pd.read_csv(p,usecols=cols,dtype=dt,chunksize=500000,encoding="utf-8-sig"):
    rows+=len(ch); dates.update(ch['기준일자명'].unique())
    ch['sold']=(ch['판매수량']>0).astype('int32')
    g=ch.groupby(['점포코드','04.상품코드'],observed=True).agg(
        소분류=('03.상품소분류명','first'), 상품명=('04.상품명','first'),
        sales=('판매수량','sum'), sold=('sold','sum'), rows=('판매수량','size'),
        order=('발주수량','sum'), waste=('폐기수량','sum'),
        psum=('현재매가','sum'), csum=('기준원가','sum'))
    parts.append(g.reset_index())
    smeta.append(ch[['점포코드','점포명','매장면적','입지유형','개점일자','기준일자명']])
print("rows",rows,"dates",len(dates),flush=True)
big=pd.concat(parts,ignore_index=True)
final=big.groupby(['점포코드','04.상품코드'],observed=True).agg(
    소분류=('소분류','first'), 상품명=('상품명','first'),
    sales=('sales','sum'), sold=('sold','sum'), rows=('rows','sum'),
    order=('order','sum'), waste=('waste','sum'), psum=('psum','sum'), csum=('csum','sum')).reset_index()
# store meta + 관측일수
sm=pd.concat(smeta,ignore_index=True)
sdays=sm.groupby('점포코드')['기준일자명'].nunique().rename('관측일수')
smeta_df=sm.drop_duplicates('점포코드')[['점포코드','점포명','매장면적','입지유형','개점일자']].merge(sdays,on='점포코드')
# 회전율 등
final['회전율']=final['sales']/final['rows']            # 취급일 평균 판매
final['단가']=(final['psum']/final['rows']).round(0)
final['원가']=(final['csum']/final['rows']).round(0)
final['폐기율']=np.where(final['order']>0, final['waste']/final['order'],0)
final=final.rename(columns={'04.상품코드':'상품코드'})
final.to_csv("agg_final.csv",index=False,encoding="utf-8-sig")
smeta_df.to_csv("store_meta.csv",index=False,encoding="utf-8-sig")
print("store-product",len(final),"stores",len(smeta_df),flush=True)
print(smeta_df.sort_values('매장면적').to_string(index=False),flush=True)
