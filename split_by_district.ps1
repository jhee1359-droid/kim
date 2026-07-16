param([string]$InputPath)

# =====================================================================
#  상권별 엑셀 분리 스크립트 (Excel COM 사용)
#  - 원본 엑셀의 C열(상권구분) 값에 따라 개별 엑셀 파일을 생성합니다.
#  - 1행은 머리글(제목행)으로 간주하여 모든 결과 파일에 포함됩니다.
#  - Microsoft Excel 이 설치되어 있어야 합니다.
# =====================================================================

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# 상권구분이 들어있는 열 번호 (A=1, B=2, C=3 ...)
$keyCol   = 3
# 머리글(제목)이 있는 행 번호
$headerRow = 1

Write-Host '====================================================='
Write-Host '  상권별 엑셀 생성기'
Write-Host '====================================================='

# ---------------------------------------------------------------
# 1) 입력 파일 결정
# ---------------------------------------------------------------
if (-not $InputPath -or $InputPath.Trim() -eq '') {
    $here  = $PSScriptRoot
    if (-not $here) { $here = (Get-Location).Path }
    $cands = Get-ChildItem -Path $here -Filter *.xlsx -File |
             Where-Object { $_.Name -notlike '상권_*' -and $_.Name -notlike '~$*' }

    if (@($cands).Count -eq 0) {
        Write-Host ''
        Write-Host '[오류] 처리할 .xlsx 파일을 찾을 수 없습니다.'
        Write-Host '       원본 엑셀 파일을 이 스크립트와 같은 폴더에 두거나,'
        Write-Host '       배치 파일 위로 끌어다 놓아 주세요.'
        exit 1
    }
    if (@($cands).Count -gt 1) {
        Write-Host ''
        Write-Host '[안내] 폴더에 여러 개의 .xlsx 파일이 있습니다. 아래 파일을 사용합니다:'
    }
    $InputPath = $cands[0].FullName
}

if (-not (Test-Path -LiteralPath $InputPath)) {
    Write-Host ('[오류] 파일을 찾을 수 없습니다: ' + $InputPath)
    exit 1
}
$InputPath = (Resolve-Path -LiteralPath $InputPath).Path
Write-Host ('원본 파일 : ' + $InputPath)

# 결과 폴더 준비
$srcDir = Split-Path -Parent $InputPath
$outDir = Join-Path $srcDir '상권별_결과'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
Write-Host ('결과 폴더 : ' + $outDir)
Write-Host ''

# ---------------------------------------------------------------
# 2) Excel 실행
# ---------------------------------------------------------------
$excel = $null
try {
    $excel = New-Object -ComObject Excel.Application
} catch {
    Write-Host '[오류] Microsoft Excel 을 실행할 수 없습니다. Excel 설치 여부를 확인해 주세요.'
    exit 1
}
$excel.Visible = $false
$excel.DisplayAlerts = $false

$made = 0
try {
    $wb = $excel.Workbooks.Open($InputPath, $false, $true)   # ReadOnly
    $ws = $wb.Worksheets.Item(1)
    $used = $ws.UsedRange
    $rowCount = $used.Rows.Count
    $colCount = $used.Columns.Count

    if ($rowCount -lt ($headerRow + 1)) {
        Write-Host '[오류] 데이터 행이 없습니다.'
        $wb.Close($false)
        exit 1
    }

    # 전체 값을 한 번에 배열로 읽기 (1-based [행,열])
    $data = $used.Value2

    # 상권구분(C열) 값별로 행 번호를 그룹화 (등장 순서 유지)
    $groups = New-Object System.Collections.Specialized.OrderedDictionary
    for ($r = $headerRow + 1; $r -le $rowCount; $r++) {
        $key = $data[$r, $keyCol]
        if ($null -eq $key -or ("$key").Trim() -eq '') { $key = '(미분류)' }
        $key = "$key"
        if (-not $groups.Contains($key)) {
            $groups[$key] = New-Object System.Collections.ArrayList
        }
        [void]$groups[$key].Add($r)
    }

    Write-Host ('상권 종류 : ' + $groups.Count + '개')
    Write-Host '-----------------------------------------------------'

    foreach ($key in $groups.Keys) {
        $rows = $groups[$key]
        $n = $rows.Count + 1   # 머리글 1행 포함

        # 새 워크북에 넣을 2차원 배열 구성 (0-based)
        $arr = New-Object 'object[,]' $n, $colCount
        for ($c = 1; $c -le $colCount; $c++) { $arr[0, $c - 1] = $data[$headerRow, $c] }
        $i = 1
        foreach ($r in $rows) {
            for ($c = 1; $c -le $colCount; $c++) { $arr[$i, $c - 1] = $data[$r, $c] }
            $i++
        }

        $nwb = $excel.Workbooks.Add()
        $nws = $nwb.Worksheets.Item(1)
        $range = $nws.Range($nws.Cells.Item(1, 1), $nws.Cells.Item($n, $colCount))
        $range.Value2 = $arr
        # 머리글 굵게 + 열 너비 자동
        $nws.Rows.Item(1).Font.Bold = $true
        [void]$nws.Columns.AutoFit()

        # 파일명에 사용할 수 없는 문자 치환
        $safe = ($key -replace '[\\/:*?"<>|]', '_').Trim()
        $outPath = Join-Path $outDir ('상권_' + $safe + '.xlsx')

        $nwb.SaveAs($outPath, 51)   # 51 = xlOpenXMLWorkbook (.xlsx)
        $nwb.Close($false)
        $made++
        Write-Host ('  생성됨 : ' + (Split-Path -Leaf $outPath) + '   (' + $rows.Count + '행)')
    }

    $wb.Close($false)
}
finally {
    if ($excel) {
        $excel.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

Write-Host '-----------------------------------------------------'
Write-Host ('완료! 총 ' + $made + '개의 엑셀 파일을 생성했습니다.')
Write-Host ('결과 위치: ' + $outDir)
