# PROMPT BOOK

制作用プロンプト（提携文）のカード集。ブラウザで開き、カードを選んで条件を指定し、コピーして各アプリに貼って使う。

公開URL：https://（ユーザー名）.github.io/prompt-book/

## 使い方

1. カードを選ぶ（色は貼り先のアプリ：Claude／ChatGPT／Photoshop／Illustrator）
2. 条件を選ぶ・入力する
3. 注意を読んで「確認した」→ コピー
4. 指定のアプリに、画像・原稿と一緒に貼る

生成結果は必ず原稿・原本と照合すること。最後は人の目で確認する。

選んだ条件は各自のブラウザに保存される（チームでは共有されない）。

## ファイル構成

| ファイル | 役割 |
| --- | --- |
| index.html | 公開されるカードブック本体（ビルドで生成。直接編集しない） |
| src/build_cardbook.py | カード定義・画面・ビルド処理 |
| src/design_prompt.html | プロンプト本文の共通部品（旧ツール。ビルド時に読み込む） |

## 更新手順

1. src/build_cardbook.py（カード追加・画面）か src/design_prompt.html（共通のプロンプト文）を編集
2. ビルド：`python3 src/build_cardbook.py`（Python 3 のみ。追加ライブラリ不要）
3. index.html をブラウザで開いて確認
4. コミットして push（GitHub Pages に自動反映）

## GitHub Pages の設定（初回のみ）

Settings → Pages → Source：Deploy from a branch → Branch：main ／ (root) → Save
