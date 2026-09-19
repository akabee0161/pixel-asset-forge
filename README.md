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
- `item` 型: **未着手**

次にやることは `item` 型で小物を1点作り、何周で収束するかを実測すること。
`types/item/SPEC.md` はその実物ができてから書く。小物が主戦場であり、
まだ1点も検証していない。

未確定の項目（目指す絵柄、型ごとの解像度、色数上限、マスターパレットの具体的な色）は
`docs/HANDOFF.md` の 3 節にまとめてある。勝手に確定させないこと。
