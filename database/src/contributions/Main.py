#!python3
#encoding: utf-8
import requests
from bs4 import BeautifulSoup
import dataset
import datetime
import os.path

class Main(object):
    def __init__(self, path_dir_db):
        self.__path_dir_db = path_dir_db
        self.__db = None
        self.__username = None
    """
    ContributionDBの生成と更新を実行する。
    DBが存在しなければDBファイルとテーブルを作成する。
    DBが存在すればレコードを更新する。
    @param {string} usernameは対象ユーザ名。
    """
    def Run(self, username):
        self.__Create(username)
        self.__Insert(self.__GetContributionsSince(self.__GetContributionsSVG(username), self.__GetLastDateFromDB()))
    def __Create(self, username):
        # DB用に空ファイルを作成する
        path_file_db = self.__GetDbFilePath(username)
        if os.path.isfile(path_file_db):
            self.__db = self.__OpenDb(username)
            return
        with open(path_file_db, 'w') as f:
            pass
        # テーブルを作成する
        self.__db = self.__OpenDb(username)
        sql = """
create table "Contributions"(
    "Id"                integer primary key,
    "Date"              text not null,
    "Count"             integer not null check(0 <= "Count")
);
"""
        self.__db.query(sql)
    """
    DBファイルパスを返す。
    @param {str} usernameは対象ユーザ名。
    """
    def __GetDbFilePath(self, username):
        return os.path.join(self.__path_dir_db, 'GitHub.Contributions.{username}.sqlite3'.format(username=username))
    """
    ContributionDBファイルを開く。
    """
    def __OpenDb(self, username):
        path_file_db = self.__GetDbFilePath(username)
        if os.path.isfile(path_file_db):
            return dataset.connect('sqlite:///' + path_file_db)
        else:
            return None
    """
    DBから最終日を取得する。
    @return {soup.find} HTML内のSVG要素。
    """
    def __GetLastDateFromDB(self):
        if None is self.__db:
            return None
        sql = 'select MAX("Date") LastDate from Contributions;'
        return self.__db.query(sql).next()['LastDate']
    """
    GitHub個人ページからSVG要素を取得し返す。
    @param {string} usernameは対象ユーザ名。
    @return {soup.find} HTML内のSVG要素。
    """
    def __GetContributionsSVG(self, username):
        last_date = self.__GetLastDateFromDB()
        if None is last_date or None is not last_date and last_date < "{0:%Y-%m-%d}".format(datetime.datetime.now()):
            print('************************{0}'.format(username))
            url = 'https://github.com/{username}'.format(username=username)
            file_name = '{username}_contributions'.format(username=username)
            r = requests.get(url)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser') # html.parser, lxml
            return soup.find("svg", attrs={"class": "js-calendar-graph-svg"})
        else:
            return None
    """
    指定した日付と同じかそれより未来のみを対象としたContributionsを取得する。
    @param {soup.find} svgはHTML内のSVG要素。
    @param {string} sinceは日付。yyyy-MM-dd書式。Noneや空文字ならすべての日付を対象とする。
    @return {dict} 指定した日付とそれ以降におけるSVGのContributions。
    """
    def __GetContributionsSince(self, svg, since):
        if None is svg:
            return None
        contributions = []
        for rect in svg.find_all('rect'):
            date = rect.get('data-date')
            if not since or (since and since <= date):
                contributions.append({"Date": date, "Count": rect.get('data-count')})
        return contributions
    """
    指定した日付と同じかそれより未来のみを対象としたContributionsを取得する。
    @param {dict} 
    """
    def __Insert(self, contributions):
        if None is contributions:
            return
        self.__db.begin()
        # 指定した日付と同日なら更新する
        self.__db['Contributions'].update(contributions[0], 'Date')
        # 指定した日付以降なら挿入する
        for c in contributions[1:]:
            self.__db['Contributions'].insert(c)
        self.__db.commit()


if __name__ == '__main__':
    username = 'ytyaru'
    path_dir_db = os.path.abspath(os.path.dirname(__file__))
    m = Main(path_dir_db)
    m.Run(username)

