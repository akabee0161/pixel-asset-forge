# pixel-asset-forge

ゲーム用ドット絵アセットを、テキストグリッドから決定的に生成するリポジトリ。
対象は Ankardo（子供向けゲーム）。

PNG を直接生成せず、1文字＝1ピクセルの文字グリッドを git 管理し、`tools/render.py` が
PNG に変換する。差分が「1行＝1ピクセル行」になって修正箇所が追えること、再生成が
決定的であること、パレット差し替えが一括で効くことがこの方式の理由。

## セットアップ

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 使い方

```sh
.venv/bin/python tools/validate.py       # 機械チェック。異常時は非ゼロ終了
.venv/bin/python tools/render.py         # assets/**/*.txt -> build/**/*.png（等倍 + x8）
.venv/bin/python tools/contact_sheet.py  # 全アセットを1枚に並べる
```

各ツールとも、引数にファイルやディレクトリを渡せば対象を絞れる。
`--help` に詳細がある。

ツール自体のテスト:

```sh
.venv/bin/python -m unittest discover -s tests
```

## 構成

```
CLAUDE.md                  作業時の規約（短く保つ）
palette/master.json        色名 -> RGB。色は必ずここ経由で参照する
types/<type>/SPEC.md       寸法・構成要素などの機械的な規約
types/<type>/reference/    合格済みアセット＝お手本。絵柄はここで揃える
assets/<type>/<name>.txt   生成物のソース（これが正）
tools/                     render / validate / contact_sheet
tests/                     tools/ のテスト
build/                     PNG 出力（git 管理外）
docs/HANDOFF.md            設計の経緯と、確定／未確定の区別
seed/face32.py             リポジトリ化前の原型。分解済みで、もう実行経路にない
```

## ワークフロー

```
types/<type>/SPEC.md と reference/ を読む
  -> assets/<type>/<name>.txt を書く
  -> validate.py -> render.py
  -> build/<type>/<name>_x8.png を目視
  -> 修正 or 提出
```

目視の前に機械チェックを挟むのが要点。パレット外の色、行の長さ、寸法、使用色数は
安価に落とせる。

## 現状

- `face` 型: reference 1点（`types/face/reference/knight`）。32x32 / 14色
- `item` 型: 1点目 `assets/item/chest.txt`（木製の宝箱）。16x16 / 8色 / 背景透過

### 収束回数の実測（item 1点目）

**5周。** 各周で直した内容は以下。

| 周 | 直したこと |
|---|---|
| 1 | 蓋が斜めに切り落とした台形で宝箱に見えない。金具帯が柱に見える。錠前が読めない |
| 2 | 蓋の肩を丸め、金具帯を外側へ出して蓋と本体を縦に貫かせ、錠前を4x3に拡大 |
| 3 | 左帯が `metal_hi` べた塗りで右帯と別素材に見える。境界線が黒帯。底が潰れている |
| 4 | 帯を `metal_base` に統一、境界線と底の明度を上げる |
| 5 | 左端1px列のハイライトが面の照りでなく縁の光に見える。帯の右側の面へ移動 |

内訳としては、1〜2周目がシルエットと構成要素の配置、3〜5周目が明度配分。
機械チェックで落ちた回数は0で、5周はすべて目視由来。

`types/item/SPEC.md` はまだ書いていない（HANDOFF 手順4）。1点だけでは
どこまでが `item` 型の規約でどこからがこのアセット固有かを分離できないため。

解像度は型ごとに決める。確定しているのは `face` = 32x32、`item` = 16x16 の2つだけ。

残る未確定の項目（目指す絵柄、アセットあたりの色数上限、マスターパレットの具体的な色、
顔グラ以外の型の一覧）は `docs/HANDOFF.md` の 3 節にまとめてある。
勝手に確定させないこと。
