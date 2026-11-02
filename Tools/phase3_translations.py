#!/usr/bin/env python3
"""Add the Phase 3 strings to all 16 localization tables (idempotent).

The translations are machine-assisted and have not been reviewed by native
speakers; they follow the wording of the existing tables.
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'Resources/YTKACE.bundle'
LANGS = ['en', 'ar', 'ckb', 'de', 'es', 'fr', 'it', 'ja', 'ko', 'pl', 'pt-BR', 'ru', 'tr', 'vi', 'zh-Hans', 'zh-Hant']

T = {
    'Simple': ['Simple', 'بسيط', 'سادە', 'Einfach', 'Sencillo', 'Simple', 'Semplice', 'シンプル', '심플', 'Prosty',
               'Simples', 'Простой', 'Basit', 'Đơn giản', '简洁', '簡潔'],
    "Simple uses YouTube's classic docked tab bar. YouTube and MarufYT are optional Liquid Glass bars.": [
        "Simple uses YouTube's classic docked tab bar. YouTube and MarufYT are optional Liquid Glass bars.",
        'الوضع البسيط يستخدم شريط التبويب الكلاسيكي المثبّت في YouTube. وضعا YouTube وMarufYT شريطان اختياريان بتأثير Liquid Glass.',
        'سادە شریتی تابی کلاسیکی جێگیری YouTube بەکاردەهێنێت. YouTube و MarufYT شریتی Liquid Glassی هەڵبژاردەنین.',
        '„Einfach“ nutzt die klassische, angedockte Tab-Leiste von YouTube. YouTube und MarufYT sind optionale Liquid-Glass-Leisten.',
        '«Sencillo» usa la barra de pestañas clásica anclada de YouTube. YouTube y MarufYT son barras opcionales con Liquid Glass.',
        '« Simple » utilise la barre d’onglets classique ancrée de YouTube. YouTube et MarufYT sont des barres Liquid Glass facultatives.',
        '«Semplice» usa la classica barra delle schede ancorata di YouTube. YouTube e MarufYT sono barre Liquid Glass facoltative.',
        '「シンプル」はYouTubeの従来の固定タブバーを使用します。YouTubeとMarufYTは任意のLiquid Glassバーです。',
        '‘심플’은 YouTube의 기본 고정 탭 바를 사용합니다. YouTube와 MarufYT는 선택형 Liquid Glass 바입니다.',
        '„Prosty” używa klasycznego, zadokowanego paska kart YouTube. YouTube i MarufYT to opcjonalne paski Liquid Glass.',
        '“Simples” usa a barra de abas clássica e ancorada do YouTube. YouTube e MarufYT são barras Liquid Glass opcionais.',
        '«Простой» использует классическую закреплённую панель вкладок YouTube. YouTube и MarufYT — необязательные панели Liquid Glass.',
        '“Basit”, YouTube’un klasik sabit sekme çubuğunu kullanır. YouTube ve MarufYT isteğe bağlı Liquid Glass çubuklarıdır.',
        '“Đơn giản” dùng thanh tab cố định cổ điển của YouTube. YouTube và MarufYT là các thanh Liquid Glass tùy chọn.',
        '“简洁”使用 YouTube 经典的固定标签栏。YouTube 和 MarufYT 为可选的 Liquid Glass 标签栏。',
        '「簡潔」使用 YouTube 經典的固定標籤列。YouTube 與 MarufYT 為選用的 Liquid Glass 標籤列。'],
}


def escape(value):
    return value.replace('\\', '\\\\').replace('"', '\\"')


def main():
    added = 0
    for i, lang in enumerate(LANGS):
        path = ROOT / f'{lang}.lproj/Localizable.strings'
        raw = path.read_bytes().decode('utf-8')
        newline = '\r\n' if '\r\n' in raw else '\n'
        lines = []
        for key, values in T.items():
            assert len(values) == len(LANGS), key
            if f'\n"{escape(key)}" = ' in raw or raw.startswith(f'"{escape(key)}" = '):
                continue
            lines.append(f'"{escape(key)}" = "{escape(values[i])}";')
        if lines:
            block = newline + '/* MarufYT Phase 3 */' + newline + newline.join(lines) + newline
            path.write_bytes((raw.rstrip('\r\n') + block).encode('utf-8'))
            added += len(lines)
    print(f'added {added} strings')


if __name__ == '__main__':
    main()
