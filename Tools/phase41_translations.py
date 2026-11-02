#!/usr/bin/env python3
"""Add the Phase 4.1 strings to all 16 localization tables (idempotent).

The translations are machine-assisted and have not been reviewed by native
speakers; they follow the wording of the existing tables.
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'Resources/YTKACE.bundle'
LANGS = ['en', 'ar', 'ckb', 'de', 'es', 'fr', 'it', 'ja', 'ko', 'pl', 'pt-BR', 'ru', 'tr', 'vi', 'zh-Hans', 'zh-Hant']

T = {
    'Private Lookup': ['Private Lookup', 'بحث خاص', 'گەڕانی تایبەت', 'Privater Abruf', 'Consulta privada', 'Recherche privée',
                       'Ricerca privata', 'プライベート検索', '비공개 조회', 'Prywatne wyszukiwanie',
                       'Consulta privada', 'Приватный запрос', 'Gizli Sorgu', 'Tra cứu riêng tư', '隐私查询', '隱私查詢'],
    'Sends only a short hash prefix of the video ID instead of the full ID. Replies are larger.': [
        'Sends only a short hash prefix of the video ID instead of the full ID. Replies are larger.',
        'يرسل بادئة تجزئة قصيرة فقط من معرّف الفيديو بدلاً من المعرّف الكامل. الردود أكبر.',
        'تەنها پێشگری هاشێکی کورتی ناسنامەی ڤیدیۆ دەنێرێت نەک ناسنامە تەواوەکە. وەڵامەکان گەورەترن.',
        'Sendet nur ein kurzes Hash-Präfix der Video-ID statt der vollständigen ID. Antworten sind größer.',
        'Envía solo un prefijo hash corto del ID del vídeo en lugar del ID completo. Las respuestas son más grandes.',
        'N’envoie qu’un court préfixe de hachage de l’identifiant de la vidéo au lieu de l’identifiant complet. Les réponses sont plus volumineuses.',
        'Invia solo un breve prefisso hash dell’ID del video invece dell’ID completo. Le risposte sono più grandi.',
        '動画IDの全体ではなく、短いハッシュの先頭部分のみを送信します。応答は大きくなります。',
        '전체 동영상 ID 대신 짧은 해시 접두사만 전송합니다. 응답이 더 큽니다.',
        'Wysyła tylko krótki prefiks skrótu identyfikatora filmu zamiast pełnego identyfikatora. Odpowiedzi są większe.',
        'Envia apenas um prefixo de hash curto do ID do vídeo em vez do ID completo. As respostas são maiores.',
        'Отправляет только короткий префикс хеша идентификатора видео вместо полного идентификатора. Ответы больше.',
        'Tam kimlik yerine video kimliğinin yalnızca kısa bir karma önekini gönderir. Yanıtlar daha büyüktür.',
        'Chỉ gửi một tiền tố băm ngắn của ID video thay vì ID đầy đủ. Phản hồi lớn hơn.',
        '仅发送视频 ID 的简短哈希前缀，而不是完整 ID。响应会更大。',
        '僅傳送影片 ID 的簡短雜湊前綴，而非完整 ID。回應會較大。'],
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
            block = newline + '/* MarufYT Phase 4.1 */' + newline + newline.join(lines) + newline
            path.write_bytes((raw.rstrip('\r\n') + block).encode('utf-8'))
            added += len(lines)
    print(f'added {added} strings')


if __name__ == '__main__':
    main()
