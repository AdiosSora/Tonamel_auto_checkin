# Tonamel_auto_checkin


使用言語(バージョン) : Python(3.12.1)

必要ライブラリ
  下記ライブラリをpip installしてください。
  
  pip install pysimplegui
  pip install opencv-python
  pip install configparser
  pip install urllib
  pip install selenium


本リポジトリクローン後のディレクトにChromeフォルダを作成してください。
Chromeフォルダには下記URLからテスト版のChromeをダウンロードし、入れてください。
https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/
※ダウンロードしたファイルのchrome-win64フォルダ内のファイル全てを作成したchromeフォルダ内にコピーペーストしてください。


設定
config.iniにTwitterのログインIDとパスワードを設定してください。

使い方 ※製造中の為頻繁に変わる可能性があります。
読み取り/自動チェックイン開始
1.start.batを実行
2.読み取り開始ボタンを押下
  2-1.自動でログインがChromeブラウザにて行われます。
      操作を行う必要はありません。

読み取り中止
1.読み取り中止ボタンを押下してください。
  自動でブラウザを閉じ、読み取りを中止します。

システム終了
1.終了ボタンまたはアプリケーションの閉じるボタンを押下してください。
  ※問題ありませんが、読み取り中止を行ってからシステム終了するとより安全です。

