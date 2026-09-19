# pixel-asset-forge

ドット絵アセットを、テキストグリッドから決定的に生成するリポジトリ。

## 原則

- **グリッドが正、PNG は生成物。** `assets/**/*.txt` だけが編集対象。`build/` 以下の PNG は
  いつ消してもよい。PNG を直接編集しない。
- **新規アセットを書く前に、必ず `types/<type>/SPEC.md` と `types/<type>/reference/` を読む。**
  絵柄は散文ではなく reference で揃える。
- **目視の前に `tools/validate.py` を通す。** 行長・未定義文字・パレット外参照は
  機械で落とす。目視はそれを通ってからにする。
- **完成したら `tools/contact_sheet.py` を更新する。** 型をまたいだ絵柄のズレはここで見つかる。

## コマンド

```sh
.venv/bin/python tools/validate.py            # 機械チェック（異常時は非ゼロ終了）
.venv/bin/python tools/render.py              # txt -> png（等倍と x8）
.venv/bin/python tools/contact_sheet.py       # build/contact_sheet.png
.venv/bin/python -m unittest discover -s tests  # tools/ を触ったとき
```

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

## 勝手に決めないこと

`docs/HANDOFF.md` の「3. 未確定のこと」を参照。目指す絵柄、型ごとの解像度、
アセットあたりの色数上限、マスターパレットの具体的な色はいずれも未確定。
必要になったら確認を取る。
