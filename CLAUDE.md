# pixel-asset-forge

ドット絵アセットを、テキストグリッドから決定的に生成するリポジトリ。

## 原則

- **グリッドが正、PNG は生成物。** `assets/**/*.txt` だけが編集対象。`build/` 以下の PNG は
  いつ消してもよい。PNG を直接編集しない。
- **新規アセットを書く前に、必ず `types/<type>/SPEC.md` と `types/<type>/reference/` を読む。**
  絵柄は散文ではなく reference で揃える。
- **目視の前に `tools/validate.py` を通す。** 行長・未定義文字・パレット外参照は
  機械で落とす。目視はそれを通ってからにする。
- **パレットに色を足したら `tools/check_colors.py` を通す。** 隣り合った色が
  区別できるかを見る。ただし**目視の代替にはならない**（実測で、目視が見つけた
  11件のうちこのチェックが拾えたものは0件）。拾えるのは「別名だが実質同じ色」だけ。
- **`tile` 型は1枚の目視では終わらない。`tools/tilemap.py` で並べて継ぎ目を見る。**
  川の初版は1枚では完璧に見えて、並べると境界に暗い帯が出た。
  `validate.py` も `check_colors.py` も通過する。
- **完成したら `tools/contact_sheet.py` を更新する。** 型をまたいだ絵柄のズレはここで見つかる。

## コマンド

```sh
.venv/bin/python tools/validate.py            # 構造の検査（異常時は非ゼロ終了）
.venv/bin/python tools/check_colors.py        # 隣接色の分離度（助言。hard failure のみ非ゼロ）
.venv/bin/python tools/render.py              # txt -> png（等倍と x8）
.venv/bin/python tools/tilemap.py             # tile を 3x3 で並べる（継ぎ目の確認）
.venv/bin/python tools/contact_sheet.py       # build/contact_sheet.png
.venv/bin/python -m unittest discover -s tests  # tools/ を触ったとき
```

`tilemap.py --layout layouts/example.txt` でマップを組んで接続も確認できる。

初回のみ: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

等倍 PNG は目視には小さすぎる。見るのは `_x8.png` の方。

## グリッドファイル形式

```
# type: face
# size: 32x32
# light: upper-left
# bg: gradient:#1c1834->#323256
# map: o=outline e=hair_hi f=hair_base g=hair_shadow
................................
（size で宣言した行数ぶん続く）
```

- `map` の値は `palette/master.json` のキー。色は必ずここ経由で参照する。
- `.` は背景。`bg` は `transparent` / `#rrggbb` / `gradient:#rrggbb->#rrggbb`。
- `# max_colors: N` を書くと使用色数の上限が検査される（任意）。
- コロンを含まない `#` 行はコメント。コロンを含む行は正しいヘッダでなければ失敗する。

## ミラーで作れるものをコピーで持たない

反転や回転で作れるアセットは、本体を持たない派生ファイルにする（HANDOFF 2.4）。

```
# from: river_ne.txt
# transform: mirror_x
```

変形は `mirror_x` / `mirror_y` / `rotate_180` / `rotate_cw` / `rotate_ccw`。
書かなかったヘッダは由来元から継承する。

**変形は光源を一緒に動かす。** 陰影が変形軸について対称なものにしか使えない。
川は使えるが、顔グラや城には使えない。機械では検査していない。

## 新しい機械チェックを思いついたら、まず偽陽性を数える

案の段階で良さそうに見えたチェックが、**3回とも実測して初めて撤回か下方修正に
なっている**。孤立ピクセル検査と継ぎ目チェックは撤回、`check_colors.py` は
しきい値を ΔE 22 から 10 へ。実装したら必ず既存アセット全件に掛けて
偽陽性を数えること。経緯は README の「深いチェックを試して2回落としている」。

## 勝手に決めないこと

`docs/HANDOFF.md` の「3. 未確定のこと」を参照。

**確定済み:** 解像度は `face` = 32x32、`item` = 16x16、`tile` = 16x16。
`tile` はシームレス（全周に輪郭を回さない）。

**未確定:** 目指す絵柄、アセットあたりの色数上限（`# max_colors:` は実装済みだが
どのアセットでも未使用）、マスターパレットの具体的な色、`face` / `item` / `tile` 以外の
型の一覧、未定義の型の解像度。必要になったら確認を取る。
