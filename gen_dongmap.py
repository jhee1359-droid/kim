#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
법정동 → 행정동 연계표(data/dong_map.json) 생성기.

점포 주소는 법정동, 경계 파일은 행정동일 때 둘을 잇는 표를 만듭니다.
이름으로 매칭되지 않는 법정동만 골라 좌표로 지오코딩(OSM Nominatim)한 뒤,
행정동 폴리곤에 point-in-polygon 판정으로 소속 행정동을 확정합니다.
(임의 추정 없이, 주어진 경계 파일의 실제 폴리곤에 배치합니다.)

사용법:
    pip install shapely
    python gen_dongmap.py 행정동경계.geojson
결과: data/dong_map.json  (build_map.py 실행 시 index.html에 내장됨)

주의: Nominatim 정책상 1초 간격으로 호출합니다. 미매칭 법정동 수만큼 시간이 걸립니다.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict

try:
    from shapely.geometry import shape, Point
except ImportError:
    raise SystemExit('[오류] shapely 필요:  pip install shapely')

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = {'수원시', '화성시', '군포시', '의왕시'}


def norm(s):
    return str(s).split()[-1] if s else s


def base(s):
    return re.sub(r'([가-힣])\d+(동|가|로|리)$', r'\1\2', norm(s)) if s else s


def city_of(sgg, adm):
    m = re.search(r'[가-힣]+?[시군]', sgg or adm or '')
    return m.group(0) if m else ''


def geocode(q):
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
        {'format': 'json', 'limit': 1, 'countrycodes': 'kr', 'q': q})
    req = urllib.request.Request(url, headers={'User-Agent': 'suwon-exec-map/1.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.load(r)
    return (float(d[0]['lat']), float(d[0]['lon'])) if d else None


def main():
    if len(sys.argv) < 2:
        raise SystemExit('사용법: python gen_dongmap.py 행정동경계.geojson')
    gj = json.load(open(sys.argv[1], encoding='utf-8'))
    stores = json.load(open(os.path.join(HERE, 'data', 'stores.json'), encoding='utf-8'))['stores']

    polys, hjdbase = [], defaultdict(set)
    for ft in gj['features']:
        p = ft.get('properties', {})
        c = city_of(p.get('sggnm', ''), p.get('adm_nm', ''))
        if c not in TARGET:
            continue
        dn = norm(p.get('adm_nm', ''))
        try:
            polys.append((c, dn, shape(ft['geometry'])))
        except Exception:
            continue
        hjdbase[c].add(base(dn))

    need = {}
    for s in stores:
        c, a = s['city'], s['adm']
        if c in TARGET and a and base(a) not in hjdbase[c]:
            need[(c, s['gu'] or '', a)] = True

    def assign(city, pt):
        P = Point(pt[1], pt[0])
        cand = [(dn, g) for (c, dn, g) in polys if c == city]
        for dn, g in cand:
            if g.contains(P):
                return dn
        best, bd = None, 1e9
        for dn, g in cand:
            d = g.distance(P)
            if d < bd:
                bd, best = d, dn
        return best

    gu_key, bare = defaultdict(list), defaultdict(set)
    fails = []
    for (c, gu, a) in sorted(need):
        pt = None
        for q in ('경기도 %s %s%s' % (c, gu + ' ' if gu else '', a), '경기도 %s %s' % (c, a)):
            try:
                pt = geocode(q)
            except Exception:
                pt = None
            if pt:
                break
            time.sleep(1.05)
        time.sleep(1.05)
        if not pt:
            fails.append((c, gu, a))
            continue
        hj = assign(c, pt)
        if hj:
            key = (gu + '|' + a) if gu else a
            if hj not in gu_key[key]:
                gu_key[key].append(hj)
            bare[a].add(hj)
            print('  %s %s %s -> %s' % (c, gu, a, hj))

    alias = dict(gu_key)
    for b, s in bare.items():
        if len(s) == 1:
            alias.setdefault(b, list(s))
    alias = {k: alias[k] for k in sorted(alias)}

    out = os.path.join(HERE, 'data', 'dong_map.json')
    json.dump(alias, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('\n생성: data/dong_map.json  (%d 항목)' % len(alias))
    if fails:
        print('지오코딩 실패(수동 보정 필요):', fails)
    print('이어서  python build_map.py  실행 → index.html에 연계표 내장')


if __name__ == '__main__':
    main()
