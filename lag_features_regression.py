# -*- coding: utf-8 -*-
"""
직전 실적(롤링/시차) 피처로 '당일 판매수량' 예측 + case 진단
- 기본 파일(001)에서 상품별로 아래 4개 피처를 계산:
    직전일주일평균발주수량 / 직전일주일평균판매수량 / 직전일주일평균폐기수량 / 전일_판매수량
    · '직전 일주일' = 오늘을 제외한 이전 7일(달력 기준) 평균 (closed='left')
    · '전일'       = 정확히 하루 전(달력) 판매수량, 없으면 0
- 목표변수 : 당일 판매수량
- 전처리 : 정규화(StandardScaler)  (피처 4개 모두 수치형)
- 분할 : Train 70% / Test 30%
- 모델 : RandomForest / ExtraTrees / HistGradientBoosting + GridSearchCV
"""
import warnings, os, numpy as np, pandas as pd, joblib
warnings.filterwarnings("ignore")
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor

RS = 42
F = ("/root/.claude/uploads/2cbc08f3-f4f0-5c61-890a-c59003410fb2/"
     "e3f6d8b7-001._____________20260819_14_30_44.xlsx")
df = pd.read_excel(F, sheet_name="Sheet1")
df["날짜"] = pd.to_datetime(df["기준일자명"], format="%Y년%m월%d일")
P = "04.상품명"
df = df.sort_values([P, "날짜"]).reset_index(drop=True)

# ---- 1) 직전 일주일(오늘 제외) 평균 발주/판매/폐기 ----
di = df.set_index("날짜")
roll = (di.groupby(P)[["발주수량", "판매수량", "폐기수량"]]
          .rolling("7D", closed="left").mean().reset_index()
          .rename(columns={"발주수량": "직전일주일평균발주수량",
                           "판매수량": "직전일주일평균판매수량",
                           "폐기수량": "직전일주일평균폐기수량"}))
df = df.merge(roll, on=[P, "날짜"], how="left")

# ---- 2) 전일(달력 기준 하루 전) 판매수량 ----
prev = df[[P, "날짜", "판매수량"]].copy()
prev["날짜"] = prev["날짜"] + pd.Timedelta(days=1)
prev = prev.rename(columns={"판매수량": "전일_판매수량"})
df = df.merge(prev, on=[P, "날짜"], how="left")

feats = ["직전일주일평균발주수량", "직전일주일평균판매수량",
         "직전일주일평균폐기수량", "전일_판매수량"]
df[feats] = df[feats].fillna(0.0)          # 이력 없음 -> 0
X, y = df[feats].copy(), df["판매수량"].astype(float)

print(f"[데이터] {len(df):,}행 | 상품 {df[P].nunique():,}종 | 피처 {feats}")
print(f"[타깃] 당일판매수량 평균 {y.mean():.2f}, 중앙값 {y.median():.0f}, 최대 {y.max():.0f}")

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.30, random_state=RS)
print(f"[분할] Train {len(Xtr):,} / Test {len(Xte):,} (70/30)")

models = {
    "RandomForestRegressor": (RandomForestRegressor(random_state=RS, n_jobs=-1),
        {"m__n_estimators": [200], "m__max_depth": [8, 14],
         "m__min_samples_leaf": [10, 30]}),
    "ExtraTreesRegressor": (ExtraTreesRegressor(random_state=RS, n_jobs=-1),
        {"m__n_estimators": [200], "m__max_depth": [8, 14],
         "m__min_samples_leaf": [10, 30]}),
    "HistGradientBoostingRegressor": (HistGradientBoostingRegressor(random_state=RS),
        {"m__learning_rate": [0.05, 0.1], "m__max_iter": [300],
         "m__max_leaf_nodes": [15, 31]}),
}

res, best = [], {"name": None, "test": -1e9, "pipe": None}
for name, (est, grid) in models.items():
    pipe = Pipeline([("sc", StandardScaler()), ("m", est)])
    gs = GridSearchCV(pipe, grid, cv=3, scoring="r2", n_jobs=1, refit=True)
    gs.fit(Xtr, ytr)
    e = gs.best_estimator_
    tr, te = r2_score(ytr, e.predict(Xtr)), r2_score(yte, e.predict(Xte))
    res.append((name, tr, te, {k.replace("m__", ""): v for k, v in gs.best_params_.items()}))
    if te > best["test"]:
        best = {"name": name, "test": te, "pipe": e}

print("\n" + "=" * 54)
for name, tr, te, p in res:
    print(f"\n모델 : {name}\ntrain r2_score : {tr:.4f}\ntest  r2_score : {te:.4f}\n  best params : {p}")
print("\n" + "-" * 54)
print(f"[최고] {best['name']} (test R2={best['test']:.4f})")

joblib.dump(best["pipe"], "best_model_lag.pkl", compress=("gzip", 6))
print("[저장] best_model_lag.pkl", round(os.path.getsize("best_model_lag.pkl") / 1e6, 1), "MB")

perm = permutation_importance(best["pipe"], Xte, yte, n_repeats=5, random_state=RS,
                              scoring="r2", n_jobs=-1)
imp = pd.DataFrame({"변수": feats, "중요도": perm.importances_mean}).sort_values(
    "중요도", ascending=False)
print("\n[변수 중요도]")
for _, r in imp.iterrows():
    print(f"  {r['변수']:20s}: {r['중요도']:.4f}")
