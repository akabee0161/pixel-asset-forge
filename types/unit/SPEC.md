# unit 型

タイル上を動くキャラクターのスプライトシート。
[character-tactics](https://github.com/akabee0161/character-tactics) のマップスプライトに
差し込む前提。絵柄は本文ではなく `reference/` で揃えること。以下は機械的な規約のみを書く。

設計の経緯は `docs/2026-09-20-unit-sprite-sheet-spec.md`、
ロラン1体で測った実測は `docs/2026-09-23-findings.md`。

## 確定している規約

| 項目 | 値 |
|---|---|
| 解像度 | 32x32（ゲーム側 `frame = 32` に合わせる） |
| 背景 | `bg: transparent` |
| 光源 | `# light: upper-left`（タイルと同じ） |
| 構図 | **足元 y=30、左右中央、背丈 24〜26px** |
| 絵柄 | `face` の流儀（全周1pxの輪郭・髪4階調）は**持ち込まない**。全身32pxでは顔が3〜4pxしか取れない |
| 並び | 12行 = 3状態 × 4方向。行 0-3 `idle` / 4-7 `walk` / 8-11 `attack`、各ブロック内は down, up, left, right。ゲーム側が `row = state_index * 4 + direction_index` で読むので、順番は変えられない |
| コマ | `idle` 2 / `walk` 4 / `attack` 3。列数は最大コマ数に揃え、余りは透明 |
| 構成 | `walk` は `[base, walk_a, base, walk_b]`、`attack` は `[atk_wind, atk_hit, base]`。中間と戻りは `base` の流用 |
| 色 | `palette/master.json` を使う。色を足すときは描く前に `probe_colors.py` で草・道・床の色に対して測る |

## ファイル配置

```
assets/unit/<unit>/<frame>.txt    コマの本体
sheets/<unit>.txt                 シート定義（どのコマをどこに置くか）
build/sheets/<unit>.png           ゲームに渡すシート
build/sheets/<unit>_preview.png   目視用のプレビュー
```

**シート定義を `assets/` の下に置いてはいけない。** `validate.py` と `render.py` は
`assets/` 以下の `*.txt` を全部 `rglob` するので、定義をグリッドとして解釈して落ちる。
`layouts/` がトップレベルにあるのと同じ理由である（この穴は実際に踏んだ）。

右向きは左向きからの `mirror_x` 派生にしてよい。**光源と盾の腕も一緒に反転する**が、
依頼者の判断で採用している（ロラン）。

## 目視の手順

1コマの `_x8.png` だけでは終わらない。

1. `tools/sheet.py sheets/<unit>.txt` のプレビュー。コマ境界線・**赤い足元ライン(y=30)**・
   青い中心線が重ねてある。アニメで一番出る欠陥は「コマ間で足元や体の中心が1pxずれて
   絵がガタつく」で、1コマの拡大画像を見ても分からない
2. **ゲームに入れて動かす。** character-tactics は canvas を 0.796倍で描いた実績があり、
   1〜2px の線は丸ごと消える（振りかぶりの剣が消えた）。整数倍で表示される保証は無い

`sheet.py` が出す足元・中心の実測表は助言のみ。`atk_hit` は剣を振り出すので
中心がずれて `off` と出るのが仕様どおりである。

## 未確定（勝手に決めない）

- **許す最小の線幅** — 0.796倍表示で1pxの刃が消えた。`unit` を増やす前に決めたい
- **フレームサイズ** — `garum` はゲーム側で `frame=48`。32px 固定のままでよいか再検討が要る
- **アセットあたりの色数上限** — 未定。ロランは15〜17色
