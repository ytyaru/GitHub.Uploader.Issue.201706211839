# このソフトウェアについて

GitHubアップローダ整理。不要なファイル(クラス)を削除、統合した。

# 前回

* https://github.com/ytyaru/GitHub.Uploader.Issue.201706191032
* https://github.com/ytyaru/GitHub.Uploader.AddFunction.Contributions.DateCheck.201705141658

# 開発環境

* Linux Mint 17.3 MATE 32bit
* [Python 3.4.3](https://www.python.org/downloads/release/python-343/)
* [SQLite](https://www.sqlite.org/) 3.8.2

## WebService

* [GitHub](https://github.com/)
    * [アカウント](https://github.com/join?source=header-home)
    * [AccessToken](https://github.com/settings/tokens)
    * [Two-Factor認証](https://github.com/settings/two_factor_authentication/intro)
    * [API v3](https://developer.github.com/v3/)

# コマンド引数

メッセージを付与することで、コミットメッセージとIssue登録を同時に行う。

```sh
$ python3 GitHubUploader.py ... -m "コミットメッセージとIssueで兼用のメッセージ。"
```

commitメッセージのほうは`fix #Issue番号 指定メッセージ`のようになる。

## 複数行も可能

```sh
$ python3 GitHubUploader.py ... -m "1行目" -m "" -m "3行目。" -m "4行目。"
```

2行目が空行なのは、gitメッセージの書式である。1行目が概要、2行目が空行、3行目以降が詳細。なお、2行目の空白を忘れてしまってもうまく動作するようにしてある。

## Markdownも書ける

```sh
python3 GitHubUploader.py ... -m "タイトル" -m '' -m '# 本文のタイトル' -m '' -m '* リスト項目1' -m '* リスト項目2'
```

Issueの本文ではMarkdownを解釈したHTMLとして表示される。ただし、git logで見えるコミットメッセージはMarkdownソーステキストそのままで表示される。

# ライセンス

このソフトウェアはCC0ライセンスである。

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

Library|License|Copyright
-------|-------|---------
[requests](http://requests-docs-ja.readthedocs.io/en/latest/)|[Apache-2.0](https://opensource.org/licenses/Apache-2.0)|[Copyright 2012 Kenneth Reitz](http://requests-docs-ja.readthedocs.io/en/latest/user/intro/#requests)
[dataset](https://dataset.readthedocs.io/en/latest/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2013, Open Knowledge Foundation, Friedrich Lindenberg, Gregor Aisch](https://github.com/pudo/dataset/blob/master/LICENSE.txt)
[bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright © 1996-2011 Leonard Richardson](https://pypi.python.org/pypi/beautifulsoup4),[参考](http://tdoc.info/beautifulsoup/)
[pytz](https://github.com/newvem/pytz)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2003-2005 Stuart Bishop <stuart@stuartbishop.net>](https://github.com/newvem/pytz/blob/master/LICENSE.txt)
[furl](https://github.com/gruns/furl)|[Unlicense](http://unlicense.org/)|[gruns/furl](https://github.com/gruns/furl/blob/master/LICENSE.md)
[PyYAML](https://github.com/yaml/pyyaml)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2006 Kirill Simonov](https://github.com/yaml/pyyaml/blob/master/LICENSE)

