# -*- coding: utf-8 -*-
"""
판매량(판매수량) 회귀 예측 - 앙상블 대표 모델 3종 비교

- 목표변수 : 판매량 (판매수량)
- 사용 피처 : '월' ~ '소분류' 범위 컬럼
              (월, 영업팀명, SC명, 점포코드, 점포명, 상품소분류명)
- 전처리    : 정규화(StandardScaler) + 범주화(One-Hot Encoding)
- 분할      : Train 80% / Test 20% (타깃 분포 층화 샘플링)
- 불균형    : 우측으로 크게 치우친 타깃 -> log1p 변환(TransformedTargetRegressor)
              + 타깃 구간 층화(stratified) 분할로 분포 불균형 해소
- 모델      : RandomForest / GradientBoosting / HistGradientBoosting (앙상블 3종)
- 튜닝      : GridSearchCV (5-fold, scoring=r2)
- 출력      : 모델별 Train / Test R2_Score
"""

import warnings
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)

warnings.filterwarnings("ignore")
RANDOM_STATE = 42


# ---------------------------------------------------------------------------
# 고카디널리티 범주형 -> 평균(타깃) 인코딩 변환기
#   - 학습 데이터의 카테고리별 타깃 평균으로 인코딩(원-핫 대비 차원 폭증 방지).
#   - 인코딩 맵은 '학습 데이터'로만 산출 -> 테스트 데이터 누수 없음.
#   - 파이프라인/그리드서치의 각 CV 폴드 내부에서 재적합되어 절차상 안전.
# ---------------------------------------------------------------------------
class MeanTargetEncoder(BaseEstimator, TransformerMixin):
    def fit(self, X, y):
        X = pd.DataFrame(X).reset_index(drop=True)
        y = pd.Series(np.asarray(y).ravel())
        self.columns_ = list(X.columns)
        self.global_ = float(y.mean())
        self.maps_ = {c: y.groupby(X[c].values).mean() for c in self.columns_}
        return self

    def transform(self, X):
        X = pd.DataFrame(X)
        cols = [
            X[c].map(self.maps_[c]).fillna(self.global_).to_numpy().reshape(-1, 1)
            for c in self.columns_
        ]
        return np.hstack(cols)

# ---------------------------------------------------------------------------
# 1. 데이터 로드 + long 포맷 변환 (월별 블록 -> '월' 컬럼)
# ---------------------------------------------------------------------------
SALES_FILE = (
    "/root/.claude/uploads/2cbc08f3-f4f0-5c61-890a-c59003410fb2/"
    "0229fc40-002._____________20260806164347.xlsx"
)


def load_long(path):
    raw = pd.read_excel(path, sheet_name="Sheet1", header=None)
    ids = ["영업팀명", "SC명", "점포코드", "점포명", "상품소분류명"]
    # 각 월 블록의 시작 컬럼 (매출액, 판매수량, 발주수량, 발주매가금액)
    blocks = {5: 5, 6: 9, 7: 13}
    data = raw.iloc[2:].reset_index(drop=True)  # 0,1행은 헤더
    records = []
    for _, r in data.iterrows():
        base = {ids[i]: r[i] for i in range(5)}
        for month, start in blocks.items():
            rec = dict(base)
            rec["월"] = month
            rec["판매수량"] = r[start + 1]
            records.append(rec)
    return pd.DataFrame(records)


df = load_long(SALES_FILE)

# 결측 타깃(해당 월 미판매) -> 0 으로 처리
df["판매수량"] = pd.to_numeric(df["판매수량"], errors="coerce").fillna(0.0)

# ---------------------------------------------------------------------------
# 2. 피처 / 타깃 정의  ('월' ~ '소분류')
# ---------------------------------------------------------------------------
TARGET = "판매수량"
numeric_features = ["월"]
# 저(低)-카디널리티(사실상 단일 점포) -> 원-핫 범주화
lowcard_features = ["영업팀명", "SC명", "점포코드", "점포명"]
# 고(高)-카디널리티(195개 소분류) -> 타깃(평균) 인코딩 범주화
highcard_features = ["상품소분류명"]

feature_cols = numeric_features + lowcard_features + highcard_features
X = df[feature_cols].copy()
y = df[TARGET].astype(float)

print(f"[데이터] 표본 수: {len(df)}  |  피처: {feature_cols}")
print(f"[타깃] 판매량 분포 -> 평균 {y.mean():.1f}, 중앙값 {y.median():.1f}, "
      f"최대 {y.max():.0f}, 왜도(skew) {y.skew():.2f}")

# ---------------------------------------------------------------------------
# 3. 전처리 : 정규화(수치) + 범주화(원-핫 / 타깃 인코딩)
#    - 월           : StandardScaler 정규화
#    - 저카디널리티 : OneHotEncoder 범주화
#    - 소분류(195개): 평균 타깃 인코딩으로 범주화
#      -> 고카디널리티 변수의 권장 인코딩. 원-핫(195차원) 대비 차원/과적합을
#         줄이고, 소분류별 판매 수준을 1개 연속형 피처로 압축.
# ---------------------------------------------------------------------------
preprocess = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         lowcard_features),
        ("te", MeanTargetEncoder(), highcard_features),
    ]
)

# ---------------------------------------------------------------------------
# 4. 불균형 해소용 층화 분할 (타깃을 분위수 구간으로 나눠 stratify)
# ---------------------------------------------------------------------------
strata = pd.qcut(y.rank(method="first"), q=5, labels=False)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=strata
)
print(f"[분할] Train {len(X_train)}  /  Test {len(X_test)}  (80% / 20%, 타깃 층화)")

# ---------------------------------------------------------------------------
# 5. 앙상블 대표 모델 3종 + 하이퍼파라미터 그리드
#    (치우친 타깃은 log1p 변환으로 학습 -> expm1 역변환)
# ---------------------------------------------------------------------------
models = {
    "RandomForestRegressor": (
        RandomForestRegressor(random_state=RANDOM_STATE),
        {
            "reg__regressor__n_estimators": [300, 500],
            "reg__regressor__max_depth": [None, 12],
            "reg__regressor__min_samples_leaf": [1, 2],
        },
    ),
    "GradientBoostingRegressor": (
        GradientBoostingRegressor(random_state=RANDOM_STATE),
        {
            "reg__regressor__n_estimators": [300, 500],
            "reg__regressor__learning_rate": [0.05, 0.1],
            "reg__regressor__max_depth": [2, 3],
        },
    ),
    "HistGradientBoostingRegressor": (
        HistGradientBoostingRegressor(random_state=RANDOM_STATE),
        {
            "reg__regressor__max_iter": [300, 500],
            "reg__regressor__learning_rate": [0.05, 0.1],
            "reg__regressor__max_leaf_nodes": [15, 31],
        },
    ),
}

results = []
for name, (estimator, grid) in models.items():
    # log1p 타깃 변환으로 불균형(왜도) 완화
    reg = TransformedTargetRegressor(
        regressor=estimator, func=np.log1p, inverse_func=np.expm1
    )
    pipe = Pipeline([("prep", preprocess), ("reg", reg)])

    search = GridSearchCV(
        pipe, grid, cv=5, scoring="r2", n_jobs=-1, refit=True
    )
    search.fit(X_train, y_train)
    best = search.best_estimator_

    train_r2 = r2_score(y_train, best.predict(X_train))
    test_r2 = r2_score(y_test, best.predict(X_test))
    results.append((name, train_r2, test_r2, search.best_params_))

# ---------------------------------------------------------------------------
# 6. 결과 출력
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("           앙상블 모델별 R2_Score 비교 결과")
print("=" * 60)
for name, tr, te, params in results:
    flag = "O (통과)" if te > 0.7 else "X (미달)"
    print(f"\n모델 : {name}")
    print(f"train r2_score : {tr:.4f}")
    print(f"test  r2_score : {te:.4f}")
    print(f"* test r2_score가 0.7이 넘는가? -> {flag}")

print("\n" + "-" * 60)
print("[최적 하이퍼파라미터]")
for name, _, _, params in results:
    clean = {k.replace('reg__regressor__', ''): v for k, v in params.items()}
    print(f"  - {name}: {clean}")
