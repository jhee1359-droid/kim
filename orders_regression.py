# -*- coding: utf-8 -*-
"""
당일 실제발주수량 회귀 예측 - 앙상블 3종 비교 + 최적모델 저장 + 변수중요도
- 목표변수 : 참고_당일실제발주수량
- 사용 피처 : '월' ~ '직전발주후_경과일'
- 전처리 : 결측 대치 + 정규화(StandardScaler) + 범주화(One-Hot / TargetEncoder)
- 분할 : Train 70% / Test 30%
- 모델 : RandomForest / ExtraTrees / HistGradientBoosting
- 튜닝 : GridSearchCV(3-fold, r2)
"""
import warnings, os, numpy as np, pandas as pd, joblib
warnings.filterwarnings("ignore")
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, TargetEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor

RS = 42
DATA = ("/root/.claude/uploads/2cbc08f3-f4f0-5c61-890a-c59003410fb2/"
        "afaad623-________________________.xlsx")
df = pd.read_excel(DATA, sheet_name="6.모델링데이터")

TARGET = "참고_당일실제발주수량"
fc = list(df.columns[df.columns.get_loc("월"):df.columns.get_loc("직전발주후_경과일") + 1])
X, y = df[fc].copy(), df[TARGET].astype(float)

hi = ["상품코드", "상품명"]
lo = ["요일명", "소분류", "날씨유형명"]
num = [c for c in fc if c not in hi + lo]
print(f"[데이터] {len(df):,}행 | 피처 {len(fc)}개 | 타깃 {TARGET}")
print(f"[타깃] 평균 {y.mean():.2f}, 중앙값 {y.median():.0f}, 최대 {y.max():.0f}")

prep = ColumnTransformer([
    ("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), num),
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False), lo),
    ("te", TargetEncoder(random_state=RS), hi)])

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.30, random_state=RS)
print(f"[분할] Train {len(Xtr):,} / Test {len(Xte):,}")

models = {
    "RandomForestRegressor": (RandomForestRegressor(random_state=RS, n_jobs=-1),
        {"model__n_estimators": [150], "model__max_depth": [20],
         "model__min_samples_leaf": [5, 10]}),
    "ExtraTreesRegressor": (ExtraTreesRegressor(random_state=RS, n_jobs=-1),
        {"model__n_estimators": [150], "model__max_depth": [20],
         "model__min_samples_leaf": [5, 10]}),
    "HistGradientBoostingRegressor": (HistGradientBoostingRegressor(random_state=RS),
        {"model__learning_rate": [0.05, 0.1], "model__max_iter": [300],
         "model__max_leaf_nodes": [31, 63]}),
}

res, best = [], {"name": None, "test": -1e9, "pipe": None}
for name, (est, grid) in models.items():
    pipe = Pipeline([("prep", prep), ("model", est)])
    gs = GridSearchCV(pipe, grid, cv=3, scoring="r2", n_jobs=1, refit=True)
    gs.fit(Xtr, ytr)
    e = gs.best_estimator_
    tr, te = r2_score(ytr, e.predict(Xtr)), r2_score(yte, e.predict(Xte))
    res.append((name, tr, te, {k.replace('model__', ''): v for k, v in gs.best_params_.items()}))
    if te > best["test"]:
        best = {"name": name, "test": te, "pipe": e}

print("\n" + "=" * 54)
for name, tr, te, p in res:
    print(f"\n모델 : {name}\ntrain r2_score : {tr:.4f}\ntest  r2_score : {te:.4f}\n  best params : {p}")
print("\n" + "-" * 54)
print(f"[최고 성능 모델] {best['name']} (test R2={best['test']:.4f})")

joblib.dump(best["pipe"], "best_model_orders.pkl", compress=("gzip", 6))
print("[저장] best_model_orders.pkl", round(os.path.getsize("best_model_orders.pkl") / 1e6, 1), "MB")

sub = Xte.sample(n=min(8000, len(Xte)), random_state=RS)
perm = permutation_importance(best["pipe"], sub, yte.loc[sub.index], n_repeats=5,
                              random_state=RS, scoring="r2", n_jobs=-1)
imp = pd.DataFrame({"변수": fc, "중요도": perm.importances_mean}).sort_values(
    "중요도", ascending=False).reset_index(drop=True)
print("\n[변수 중요도]")
for _, r in imp.iterrows():
    print(f"  {r['변수']:20s}: {r['중요도']:.4f}")
imp.to_csv("feature_importance_orders.csv", index=False, encoding="utf-8-sig")
print("[저장] feature_importance_orders.csv")
