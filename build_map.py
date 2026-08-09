#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index.html 재생성 스크립트.

data/app_template.html 의 자리표시자에 아래를 주입해 단일 파일 index.html 을 만듭니다.
  __LEAFLET_CSS__  ← data/leaflet.css
  __LEAFLET_JS__   ← data/leaflet.js
  __STORE_DATA__   ← data/stores.json  (window.STORE_DATA = {...};)

사용법:
    python build_map.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, 'data')


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def main():
    tpl = read(os.path.join(D, 'app_template.html'))
    css = read(os.path.join(D, 'leaflet.css'))
    js = read(os.path.join(D, 'leaflet.js'))
    data = read(os.path.join(D, 'stores.json'))

    # 행정동 경계(있으면) 내장 → 열면 바로 지도 표시. 없으면 드래그&드롭으로 로드.
    bpath = os.path.join(D, 'boundary.geojson')
    if os.path.exists(bpath):
        boundary = 'window.BOUNDARY_GEOJSON=' + read(bpath) + ';'
    else:
        boundary = 'window.BOUNDARY_GEOJSON=null;'

    out = (tpl
           .replace('__LEAFLET_CSS__', css)
           .replace('__LEAFLET_JS__', js)
           .replace('__STORE_DATA__', 'window.STORE_DATA=' + data + ';')
           .replace('__BOUNDARY_DATA__', boundary))

    for ph in ('__LEAFLET_CSS__', '__LEAFLET_JS__', '__STORE_DATA__', '__BOUNDARY_DATA__'):
        if ph in out:
            raise SystemExit('자리표시자 미치환: ' + ph)

    out_path = os.path.join(HERE, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)
    print('생성 완료: index.html  (%d bytes)' % len(out.encode('utf-8')))


if __name__ == '__main__':
    main()
