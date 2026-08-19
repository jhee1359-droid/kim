# -*- coding: utf-8 -*-
"""
판매량 예측 기반 '권장 발주량' 산출
- 저장된 판매예측 모델(best_model.pkl, ExtraTrees, test R2 0.68)을 불러와
  각 상품의 예측 판매량을 구하고, 그로부터 권장 발주량을 계산한다.
- 발주는 사람이 최종 판단하되, 이 값을 '참고 기준'으로 제시.

  권장발주 = max(0, round( 예측판매 × (리드타임+1) + 안전재고 − 현재고 ))
    · 리드타임(LEAD_TIME) : 발주 후 입고까지 일수 (기본 1)
    · 안전재고           : 예측판매 × SAFETY_RATIO (기본 0.5)
    · 현재고             : 재고추정_D1 컬럼 사용
  ※ 리드타임·안전재고·현재고는 실제 값이 확보되면 아래 파라미터만 바꾸면 됨.
"""
import numpy as np, pandas as pd, joblib

# ----- 조정 가능한 발주 파라미터 -----
LEAD_TIME = 1        # 발주 후 입고까지 일수
SAFETY_RATIO = 0.5   # 안전재고 = 예측판매 × 이 비율
STOCK_COL = "재고추정_D1"   # 현재고로 사용할 컬럼
# ------------------------------------

DATA = ("/root/.claude/uploads/2cbc08f3-f4f0-5c61-890a-c59003410fb2/"
        "afaad623-________________________.xlsx")
MODEL = "best_model.pkl"

df = pd.read_excel(DATA, sheet_name="6.모델링데이터")
model = joblib.load(MODEL)

# 판매모델이 학습한 피처: '월' ~ '참고_당일실제발주수량'
feat = list(df.columns[df.columns.get_loc("월"):
                       df.columns.get_loc("참고_당일실제발주수량") + 1])

# 1) 예측 판매량
df["예측판매량"] = np.clip(model.predict(df[feat]), 0, None)

# 2) 권장 발주량 계산
#    재고추정_D1 에 음수(오류/미보정 추정)가 많아 그대로 쓰면 발주량이 과대해짐
#    -> 현재고는 0 미만을 0으로 보정해 '수요 기반'으로 계산 (실재고 확보 시 교체)
stock = df[STOCK_COL].clip(lower=0)
cover = df["예측판매량"] * (LEAD_TIME + 1)          # 리드타임+당일 수요
safety = df["예측판매량"] * SAFETY_RATIO             # 안전재고
df["권장발주량"] = np.maximum(0, np.round(cover + safety - stock)).astype(int)
df["예측판매량"] = df["예측판매량"].round(1)

# 3) '현재 시점'(상품별 가장 최근 데이터) 발주 추천표
latest = df.loc[df.groupby("상품코드")["데이터경과일"].idxmax()].copy()
cols = ["상품코드", "상품명", "소분류", "월", "요일명",
        "전일_판매수량", STOCK_COL, "예측판매량", "권장발주량"]
latest = latest[cols].sort_values("권장발주량", ascending=False).reset_index(drop=True)

# 4) 저장 (엑셀: 현재시점 추천 / 전체 상세)
with pd.ExcelWriter("발주추천_결과.xlsx", engine="openpyxl") as w:
    latest.rename(columns={STOCK_COL: "현재고(추정)"}).to_excel(
        w, sheet_name="현재시점_발주추천", index=False)
    df[["상품코드", "상품명", "소분류", "월", "요일명", "데이터경과일",
        "전일_판매수량", STOCK_COL, "타깃_당일판매수량",
        "예측판매량", "권장발주량"]].rename(
        columns={"타깃_당일판매수량": "실제판매량", STOCK_COL: "현재고(추정)"}
    ).to_excel(w, sheet_name="전체상세", index=False)

print(f"[파라미터] 리드타임 {LEAD_TIME}일, 안전재고비율 {SAFETY_RATIO}, 현재고={STOCK_COL}")
print(f"[대상] 상품 {latest['상품코드'].nunique()}종, 전체 {len(df):,}행")
print(f"[산출] 현재시점 총 권장발주량 합계 = {int(latest['권장발주량'].sum()):,}개")
print("\n[현재 시점 발주 추천 상위 15개]")
print(latest.head(15).to_string(index=False))
print("\n[저장] 발주추천_결과.xlsx (시트: 현재시점_발주추천 / 전체상세)")
