# tile 型

マップに敷き詰める地形・建物・調度のタイル。絵柄は本文ではなく既存のタイル
（`assets/tile/`）と `layouts/` のマップで揃えること。以下は機械的な規約のみを書く。

`types/tile/reference/` はまだ無い。当面は `layouts/field.txt`（草原）と
`layouts/castle_interior.txt`（城内）に置かれた既存タイルをお手本とする。

## 確定している規約

| 項目 | 値 |
|---|---|
| 寸法 | `16x16` |
| 光源 | 左上（`# light: upper-left`） |
| 背景 | 使わない。`.` を置かず全セルを塗る（既存65点とも `# bg` を書いていない） |
| 輪郭 | **全周に回さない**（下記） |
| 継ぎ目 | シームレス。同じタイル・隣のタイルと並べて繋がること |

### 輪郭を回さない

`face` と `item` は「全周に `outline` を1pxで回す」が、`tile` にはこの規約を
適用しない。タイルは隣接して敷き詰めるため、輪郭を回すと常に格子が見える。
`tile` の縁は地続きにし、輪郭は城のような**物体のシルエット**にだけ使う。

### ミラー・回転の派生

光の向きが無いもの（平らな地面、川の水路）は `# from:` の派生で持つ。
道の曲がり・T字・横向き、`river_h`、川の曲がり3種、`bridge_v` が派生である。
光の向きがあるもの（城の壁の角 `wall_corner_{nw,ne}` など）は派生にできない。
変形は光源を一緒に動かすため。

`bridge_v` だけは回転の向きに意味がある。デッキの明るい辺は北の行で、
**反時計回り**（`rotate_ccw`）ならそれが西の列に移って `upper-left` のままになる。
時計回りだとハイライトが光源の反対側に行く。

## セット構成

### 草原（45点）

- 地面 `plain` `grass_flowers` `grass_tall` `dirt`
- 道 `path_v` `path_h` `path_cross`、曲がり `path_{ne,nw,se,sw}`、T字 `path_t_{n,s,e,w}`
- 木と岩 `tree` `pine` `forest` `rock` `stump`
- 水 `river_v` `river_h` と曲がり4種 `river_{ne,nw,se,sw}`（`ne` は北と東を繋ぐ）、
  `pond`、橋 `bridge_h`（`river_v` を渡る）/ `bridge_v`（`river_h` を渡る）
- 地形 `mountain` と山岳4種 `mountain_{ne,nw,se,sw}`
- 人の手 `village` `shop` `well` `signpost` `fence_h` `fence_v` `crop_field`
- 城（2x2）`castle_{nw,ne,sw,se}`

### 城内（20点）

- 床 `floor_stone` `floor_worn`
- 絨毯 `carpet_v` `carpet_h` `carpet_cross` `carpet_end_n`
- 壁 `wall_top` `wall_face` `wall_face_{window,torch,banner}` `wall_corner_{nw,ne}`
- 出入口 `door_closed` `stairs_up` `stairs_down`
- 調度 `throne` `pillar` `brazier` `bookshelf`

新しいセットを作ったら、その全点を置いたレイアウトを `layouts/` に足すこと。

## 草原セットの決めごと

**道はどのタイルも四辺の同じ10セル（index 3〜12）を使う。** 直線・曲がり・
十字・T字がこれだけで噛み合う。道の縁の揺らぎは行0・7・8・15には置かない
（隣のタイルが合わせにいく行だから）。

**道に縁取り色は使わない。** 川の均一な1pxの岸が運河に見える原因だったので、
道では不規則な境界そのものに縁の役をさせている。

**川の岸は土2px。** `river_*` `bridge_*` はすべてこの断面（草・土2px・
`water_shadow`・水・`water_shadow`・土2px・草）で端を揃えてある。

**樹冠は `grass_*` で塗らない。** `leaf_hi` の初案は `grass_base` と ΔE 5.9 で、
`check_colors.py` の hard failure だった。地面の緑で木を塗ると地面に沈む。

**地面のテクスチャは全タイルで同じ密度にする。** `grass_flowers` は `plain` の
房の配置をそのまま引き継いで花だけ足し、`dirt` は同じ配置を土の色で置いている。

**敷き詰める地面は、マークの形を揃えず、左右端に半分ずつ房を置く。**
`plain` は周期16pxのままで、これで格子に見えなくなった（3案の比較は
`docs/2026-09-23-findings.md`）。

## 城内セットの決めごと

城の**中**は、フィールドと同じ真上見下ろしの床に、壁だけ正面が見える面を足して作る。

```
wall_top        壁の天面（真上から）
wall_face       その下に置く壁面（正面が見える）
```

南を向いた壁だけがこの2段構成になる。左右の壁は `wall_top` の列だけで、
南側の壁も `wall_top` だけ（面が視点と反対を向くため）。`wall_face` の列
0〜3 と 12〜15 は `wall_face_{window,torch,banner}` と `door_closed` でも
同一にしてあり、壁の並びのどこにでも差し込める。

**角の2枚はミラーで持てない。** `wall_corner_nw` は光を受けて明るく、
`wall_corner_ne` は影に落ちる。

**床パターンはタイルの行0・列0を基準に置いてある。** そのため
`throne` `pillar` `brazier` `bookshelf` `carpet_end_n` のように床の上に物を
置くタイルは、端の数列に `floor_stone` と同じ行を書いておけば、隣に敷いた床と
目地がそのまま繋がる。

## 目視の手順

1枚の `_x8.png` では終わらない。`tools/tilemap.py` で3通り見る。
どれも `validate.py` と `check_colors.py` を通過する欠陥で、機械チェックは無い。

1. `--repeat` で継ぎ目（川の初版は境界に暗い帯が出た）
2. `--repeat` で反復が格子に見えないか（`plain` の初版は壁紙になった）
3. `--layout` で組んだマップで別の物に見えないか（切り株が木箱に見えた）

**目視の締めは必ず `--layout` のマップにすること。**

## 未確定（勝手に決めない）

- **ゲームへの渡し方** — 1枚ずつの PNG か、タイルセットか、マップの完成品か
- **アセットあたりの色数上限** — 未定。既存は3〜12色
