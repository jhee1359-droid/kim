# -*- coding: utf-8 -*-
"""
당일 판매수량 회귀 예측 - 앙상블 대표 모델 3종 비교 + 최적모델 저장 + 변수중요도

- 목표변수 : 타깃_당일판매수량
- 사용 피처 : '월' ~ '참고_당일실제발주수량' (원본 0~24번 컬럼 전체)
- 전처리    : 결측 대치 + 정규화(StandardScaler) + 범주화(One-Hot / 평균타깃인코딩)
- 분할      : Train 70% / Test 30%
- 모델      : RandomForest / ExtraTrees / HistGradientBoosting (앙상블 3종)
- 튜닝      : GridSearchCV (3-fold, scoring=r2)
- 산출물    : ① 모델별 train/test R2  ② 최고 test R2 모델 .pkl 저장
              ③ 입력 변수(원본 컬럼)별 변수 중요도(순열 중요도)
"""

import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, TargetEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
)

warnings.filterwarnings("ignore")
RANDOM_STATE = 42
DATA = ("/root/.claude/uploads/2cbc08f3-f4f0-5c61-890a-c59003410fb2/"
        "afaad623-________________________.xlsx")


# ---------------------------------------------------------------------------
# 1. 데이터 로드 및 피처/타깃 정의
# ---------------------------------------------------------------------------
df = pd.read_excel(DATA, sheet_name="6.모델링데이터")

TARGET = "타깃_당일판매수량"
feature_cols = list(df.columns[df.columns.get_loc("월"):
                                df.columns.get_loc("참고_당일실제발주수량") + 1])

X = df[feature_cols].copy()
y = df[TARGET].astype(float)

# 범주형 구분
highcard_cat = ["상품코드", "상품명"]                 # 951종 -> 평균타깃인코딩
lowcard_cat = ["요일명", "소분류", "날씨유형명"]        # 7/49/5종 -> 원-핫
numeric_cols = [c for c in feature_cols
                if c not in highcard_cat + lowcard_cat]  # 나머지 수치형 -> 대치+정규화

print(f"[데이터] 표본 {len(df):,}행  |  피처 {len(feature_cols)}개")
print(f"[타깃] 평균 {y.mean():.2f}, 중앙값 {y.median():.0f}, 최대 {y.max():.0f}, 왜도 {y.skew():.1f}")
print(f"[범주화] 원-핫: {lowcard_cat}  |  평균타깃인코딩: {highcard_cat}")

# ---------------------------------------------------------------------------
# 2. 전처리 : 결측 대치 + 정규화 + 범주화
# ---------------------------------------------------------------------------
preprocess = ColumnTransformer(transformers=[
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), numeric_cols),
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False), lowcard_cat),
    # 고카디널리티(상품코드·상품명 각 951종) -> 타깃 인코딩(내부 교차적합으로 누수 방지)
    ("te", TargetEncoder(random_state=RANDOM_STATE), highcard_cat),
])

# ---------------------------------------------------------------------------
# 3. Train 70% / Test 30% 분할
# ---------------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=RANDOM_STATE)
print(f"[분할] Train {len(X_train):,} / Test {len(X_test):,} (70% / 30%)")

# ---------------------------------------------------------------------------
# 4. 앙상블 3종 + 하이퍼파라미터 그리드
# ---------------------------------------------------------------------------
models = {
    "RandomForestRegressor": (
        RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1),
        {"model__n_estimators": [150],
         "model__max_depth": [20],
         "model__min_samples_leaf": [5, 10]},
    ),
    "ExtraTreesRegressor": (
        ExtraTreesRegressor(random_state=RANDOM_STATE, n_jobs=1),
        {"model__n_estimators": [150],
         "model__max_depth": [20],
         "model__min_samples_leaf": [5, 10]},
    ),
    "HistGradientBoostingRegressor": (
        HistGradientBoostingRegressor(random_state=RANDOM_STATE),
        {"model__learning_rate": [0.05, 0.1],
         "model__max_iter": [300, 500],
         "model__max_leaf_nodes": [31, 63]},
    ),
}

results, best = [], {"name": None, "test": -np.inf, "pipe": None}
for name, (estimator, grid) in models.items():
    pipe = Pipeline([("prep", preprocess), ("model", estimator)])
    search = GridSearchCV(pipe, grid, cv=3, scoring="r2", n_jobs=-1, refit=True)
    search.fit(X_train, y_train)
    est = search.best_estimator_

    tr = r2_score(y_train, est.predict(X_train))
    te = r2_score(y_test, est.predict(X_test))
    clean = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    results.append((name, tr, te, clean))
    if te > best["test"]:
        best = {"name": name, "test": te, "pipe": est}

# ---------------------------------------------------------------------------
# 5. 결과 출력
# ---------------------------------------------------------------------------
print("\n" + "=" * 58)
print("            앙상블 모델별 R2_Score 비교")
print("=" * 58)
for name, tr, te, params in results:
    print(f"\n모델 : {name}")
    print(f"train r2_score : {tr:.4f}")
    print(f"test  r2_score : {te:.4f}")
    print(f"  best params : {params}")

print("\n" + "-" * 58)
print(f"[최고 성능 모델] {best['name']}  (test R2 = {best['test']:.4f})")

# ---------------------------------------------------------------------------
# 6. 최적 모델 저장 (.pkl)
# ---------------------------------------------------------------------------
pkl_path = "best_model.pkl"
joblib.dump(best["pipe"], pkl_path, compress=("gzip", 6))
print(f"[모델 저장] '{pkl_path}' 에 최적 파이프라인 저장 완료")

# ---------------------------------------------------------------------------
# 7. 입력 변수(원본 컬럼)별 변수 중요도 - 순열 중요도(permutation importance)
#    원본 컬럼 단위로 섞어 성능 하락폭을 측정 -> 모델 종류와 무관하게 해석 가능
# ---------------------------------------------------------------------------
sub = X_test.sample(n=min(8000, len(X_test)), random_state=RANDOM_STATE)
ysub = y_test.loc[sub.index]
perm = permutation_importance(best["pipe"], sub, ysub, n_repeats=5,
                              random_state=RANDOM_STATE, scoring="r2", n_jobs=-1)
imp = (pd.DataFrame({"변수": feature_cols,
                     "중요도": perm.importances_mean,
                     "표준편차": perm.importances_std})
       .sort_values("중요도", ascending=False).reset_index(drop=True))

print("\n" + "=" * 58)
print(f"      입력 변수 중요도 (순열 중요도, 기준모델: {best['name']})")
print("=" * 58)
for _, r in imp.iterrows():
    print(f"  {r['변수']:20s} : {r['중요도']:.4f}  (±{r['표준편차']:.4f})")
imp.to_csv("feature_importance.csv", index=False, encoding="utf-8-sig")
print("\n[중요도 저장] 'feature_importance.csv'")
