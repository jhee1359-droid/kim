# 상권별 엑셀 생성기

원본 엑셀의 **C열(상권구분)** 값에 따라 상권별로 엑셀 파일을 각각 생성해 주는 도구입니다.

예) C열에 `대학가`, `오피스가` 두 종류가 있으면 →
`상권_대학가.xlsx`, `상권_오피스가.xlsx` 두 개의 파일이 만들어집니다.

각 결과 파일에는 **1행(머리글/제목)** 이 그대로 포함됩니다.

---

## 📁 구성 파일

| 파일 | 설명 |
|------|------|
| `상권별_엑셀생성.bat` | **더블클릭 실행파일** (Windows) |
| `split_by_district.ps1` | 실제 분리를 수행하는 PowerShell 스크립트 (Excel 사용) |
| `split_by_district.py` | Python 대체 버전 (openpyxl 사용) |

> `상권별_엑셀생성.bat` 와 `split_by_district.ps1` 은 **같은 폴더**에 함께 있어야 합니다.

---

## ▶ 사용 방법 (권장 · Windows + Excel)

1. `상권별_엑셀생성.bat`, `split_by_district.ps1`, 그리고 **원본 엑셀 파일**을
   같은 폴더에 둡니다.
2. 아래 둘 중 한 가지 방법으로 실행합니다.
   - **방법 A:** `상권별_엑셀생성.bat` 를 **더블클릭**
     → 같은 폴더의 `.xlsx` 파일을 자동으로 찾아 처리합니다.
   - **방법 B:** 원본 엑셀 파일을 `상권별_엑셀생성.bat` **위로 끌어다 놓기**(드래그 앤 드롭)
3. 같은 폴더에 **`상권별_결과`** 폴더가 생기고, 그 안에 상권별 엑셀 파일이 저장됩니다.

> 이 방식은 PC에 **Microsoft Excel** 이 설치되어 있어야 합니다.
> (별도 프로그램 설치가 필요 없습니다.)

### ⚠️ "이 앱이 차단되었습니다" 또는 실행 정책 경고가 뜰 때
`.bat` 파일이 이미 `-ExecutionPolicy Bypass` 로 실행하므로 대부분 그대로 동작합니다.
만약 SmartScreen 경고가 나오면 **추가 정보 → 실행**을 선택하세요.

---

## ▶ 사용 방법 (대안 · Python)

Excel 이 없거나 Mac/Linux 에서 쓰려면 Python 버전을 사용하세요.

```bash
pip install openpyxl
python split_by_district.py 원본엑셀.xlsx
```

인자를 생략하면 스크립트와 같은 폴더의 `.xlsx` 파일을 자동으로 찾습니다.

---

## ⚙ 설정 변경

다른 열을 기준으로 나누고 싶다면 스크립트 상단의 값을 바꾸면 됩니다.

- PowerShell(`split_by_district.ps1`): `$keyCol = 3`  (A=1, B=2, C=3 …)
- Python(`split_by_district.py`): `KEY_COL = 3`

머리글이 여러 줄이거나 다른 행에 있으면 `$headerRow` / `HEADER_ROW` 값을 조정하세요.
