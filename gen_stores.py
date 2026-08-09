#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
점포별 경영계획 엑셀 → data/stores.json 생성기.

입력 엑셀(점포별)의 1행 머리글은 아래 순서를 가정합니다:
  0 영업부명 / 1 영업팀명 / 2 SC명 / 3 점포코드 / 4 점포명 / 5 주소1 / 6 주소2
  7 월누계_경영계획_일반매출(V1) / 8 월누계_경영계획_매출영업일수(V1)
  9 경영계획 일매출 / 10 일반상품매출액(V3) / 11 영업일수(V3)
  12 일매출 실적 / 13 총매출 달성률 / 14 일매출 달성률

사용법:
    pip install openpyxl
    python gen_stores.py 점포별엑셀.xlsx
"""
import json
import os
import re
import sys

try:
    import openpyxl
except ImportError:
    raise SystemExit('[오류] openpyxl 필요:  pip install openpyxl')


def num(x):
    return float(x) if isinstance(x, (int, float)) else 0.0


def parse_addr(addr):
    """주소1 → 시/구/동(법정동)/리. 주소는 지번주소(법정동) 기준."""
    out = {"city": None, "gu": None, "dong": None, "eupmyeon": None, "ri": None}
    if not addr:
        return out
    for t in str(addr).replace('경기도', '경기').split():
        if t.endswith('시') or t.endswith('군'):
            out["city"] = t
        elif t.endswith('구'):
            out["gu"] = t
        elif t.endswith('읍') or t.endswith('면'):
            out["eupmyeon"] = t
        elif t.endswith('동') or t.endswith('가'):
            if out["dong"] is None:
                out["dong"] = t
        elif t.endswith('리'):
            out["ri"] = t
    out["adm"] = out["dong"] or out["eupmyeon"]  # 대표 동(법정동/읍면)
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit('사용법: python gen_stores.py 점포별엑셀.xlsx')
    src = os.path.abspath(sys.argv[1])
    wb = openpyxl.load_workbook(src, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))[1:]

    stores = []
    for r in rows:
        r = list(r) + [None] * (15 - len(r))
        p = parse_addr(r[5])
        v1s, v1d, v3s, v3d = num(r[7]), num(r[8]), num(r[10]), num(r[11])
        stores.append({
            "team": r[1], "sc": r[2], "code": str(r[3]) if r[3] is not None else "",
            "name": r[4], "addr1": r[5], "addr2": r[6],
            "city": p.get("city"), "gu": p.get("gu"), "adm": p.get("adm"), "ri": p.get("ri"),
            "planSales": round(v1s), "planDays": round(v1d, 4),
            "actSales": round(v3s), "actDays": round(v3d, 4),
            "totRate": round(v3s / v1s, 6) if v1s else None,
            "dayRate": round((v3s / v3d) / (v1s / v1d), 6) if v1d and v3d and v1s else None,
        })

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'stores.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            "meta": {"source": "경영계획 점포별", "count": len(stores),
                     "fields": "team,sc,code,name,addr1,addr2,city,gu,adm,ri,"
                               "planSales,planDays,actSales,actDays,totRate,dayRate"},
            "stores": stores,
        }, f, ensure_ascii=False, separators=(',', ':'))
    print('생성 완료: data/stores.json  (%d개 점포)' % len(stores))
    print('이어서  python build_map.py  실행 → index.html 갱신')


if __name__ == '__main__':
    main()
