#!/usr/bin/env python3
"""Add the MarufYT Phase 2 strings to all 16 localization tables (idempotent).

Values for the player buttons keep the upstream product name, which the
runtime rebrands to MarufYT (see MarufYTBrandedString).
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'Resources/YTKACE.bundle'
LANGS = ['en', 'ar', 'ckb', 'de', 'es', 'fr', 'it', 'ja', 'ko', 'pl', 'pt-BR', 'ru', 'tr', 'vi', 'zh-Hans', 'zh-Hant']

T = {
    'ALERTS': ['ALERTS', 'التنبيهات', 'ئاگادارکردنەوەکان', 'HINWEISE', 'AVISOS', 'ALERTES', 'AVVISI', '通知', '알림',
               'POWIADOMIENIA', 'ALERTAS', 'УВЕДОМЛЕНИЯ', 'UYARILAR', 'THÔNG BÁO', '提示', '提示'],
    'SKIPPING': ['SKIPPING', 'التخطي', 'تێپەڕاندن', 'ÜBERSPRINGEN', 'OMISIÓN', 'SAUT', 'SALTO', 'スキップ', '건너뛰기',
                 'POMIJANIE', 'PULAR', 'ПРОПУСК', 'ATLAMA', 'BỎ QUA', '跳过', '略過'],
    'SEGMENT COLORS': ['SEGMENT COLORS', 'ألوان المقاطع', 'ڕەنگی بەشەکان', 'SEGMENTFARBEN', 'COLORES DE SEGMENTOS',
                       'COULEURS DES SEGMENTS', 'COLORI DEI SEGMENTI', 'セグメントの色', '구간 색상', 'KOLORY SEGMENTÓW',
                       'CORES DOS SEGMENTOS', 'ЦВЕТА СЕГМЕНТОВ', 'SEGMENT RENKLERİ', 'MÀU PHÂN ĐOẠN', '片段颜色', '片段顏色'],
    'Repository': ['Repository', 'المستودع', 'کۆگا', 'Repository', 'Repositorio', 'Dépôt', 'Repository', 'リポジトリ',
                   '저장소', 'Repozytorium', 'Repositório', 'Репозиторий', 'Depo', 'Kho mã nguồn', '代码库', '程式碼庫'],
    'Version': ['Version', 'الإصدار', 'وەشان', 'Version', 'Versión', 'Version', 'Versione', 'バージョン', '버전',
                'Wersja', 'Versão', 'Версия', 'Sürüm', 'Phiên bản', '版本', '版本'],
    'Package': ['Package', 'الحزمة', 'پاکێج', 'Paket', 'Paquete', 'Paquet', 'Pacchetto', 'パッケージ', '패키지',
                'Pakiet', 'Pacote', 'Пакет', 'Paket', 'Gói', '软件包', '套件'],
    'Floating Tab Bar Depth': [
        'Floating Tab Bar Depth', 'عمق شريط التبويب العائم', 'قووڵی شریتی تابی سەرئاو',
        'Tiefe der schwebenden Tab-Leiste', 'Profundidad de la barra de pestañas flotante',
        'Profondeur de la barre d’onglets flottante', 'Profondità della barra delle schede fluttuante',
        'フローティングタブバーの奥行き', '떠 있는 탭 바 깊이', 'Głębia pływającego paska kart',
        'Profundidade da barra de abas flutuante', 'Глубина плавающей панели вкладок',
        'Yüzen Sekme Çubuğu Derinliği', 'Độ sâu thanh tab nổi', '浮动标签栏立体感', '浮動標籤列立體感'],
    'Soft shadow under the floating glass tab bar.': [
        'Soft shadow under the floating glass tab bar.', 'ظل ناعم أسفل شريط التبويب الزجاجي العائم.',
        'سێبەرێکی نەرم لە ژێر شریتی تابی شووشەیی سەرئاو.',
        'Weicher Schatten unter der schwebenden Glas-Tab-Leiste.',
        'Sombra suave bajo la barra de pestañas de cristal flotante.',
        'Ombre douce sous la barre d’onglets en verre flottante.',
        'Ombra morbida sotto la barra delle schede in vetro fluttuante.',
        'フローティングのガラスタブバーの下にやわらかい影を表示します。',
        '떠 있는 글래스 탭 바 아래에 부드러운 그림자를 표시합니다.',
        'Delikatny cień pod pływającym szklanym paskiem kart.',
        'Sombra suave sob a barra de abas de vidro flutuante.',
        'Мягкая тень под плавающей стеклянной панелью вкладок.',
        'Yüzen cam sekme çubuğunun altında yumuşak gölge.',
        'Bóng mờ nhẹ bên dưới thanh tab kính nổi.',
        '在浮动玻璃标签栏下方显示柔和阴影。', '在浮動玻璃標籤列下方顯示柔和陰影。'],
    'YTKACE Sleep Timer': [
        'YTKACE Sleep Timer', 'مؤقت النوم YTKACE', 'کاتژمێری خەوی YTKACE', 'YTKACE-Schlaftimer',
        'YTKACE: temporizador', 'Minuterie de veille YTKACE', 'Timer di spegnimento YTKACE',
        'YTKACE スリープタイマー', 'YTKACE 취침 타이머', 'YTKACE: wyłącznik czasowy',
        'Timer de suspensão do YTKACE', 'YTKACE: таймер сна', 'YTKACE Uyku Zamanlayıcısı',
        'Hẹn giờ ngủ YTKACE', 'YTKACE 睡眠定时器', 'YTKACE 睡眠計時器'],
    'YTKACE SponsorBlock': [
        'YTKACE SponsorBlock', 'SponsorBlock في YTKACE', 'SponsorBlockی YTKACE', 'YTKACE-SponsorBlock',
        'YTKACE: SponsorBlock', 'SponsorBlock YTKACE', 'SponsorBlock YTKACE', 'YTKACE SponsorBlock',
        'YTKACE SponsorBlock', 'YTKACE: SponsorBlock', 'SponsorBlock do YTKACE', 'YTKACE: SponsorBlock',
        'YTKACE SponsorBlock', 'SponsorBlock YTKACE', 'YTKACE SponsorBlock', 'YTKACE SponsorBlock'],
    'YTKACE Transcript': [
        'YTKACE Transcript', 'نص الفيديو YTKACE', 'دەقی ڤیدیۆی YTKACE', 'YTKACE-Transkript',
        'YTKACE: transcripción', 'Transcription YTKACE', 'Trascrizione YTKACE', 'YTKACE 文字起こし',
        'YTKACE 스크립트', 'YTKACE: transkrypcja', 'Transcrição do YTKACE', 'YTKACE: расшифровка',
        'YTKACE Transkript', 'Bản chép lời YTKACE', 'YTKACE 文字记录', 'YTKACE 文字記錄'],
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
            block = newline + '/* MarufYT */' + newline + newline.join(lines) + newline
            path.write_bytes((raw.rstrip('\r\n') + block).encode('utf-8'))
            added += len(lines)
            print(f'{lang}: +{len(lines)}')
    print(f'added {added} strings')


if __name__ == '__main__':
    main()
