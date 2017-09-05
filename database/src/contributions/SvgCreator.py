import dataset
import os.path
import ContributionSvg
class SvgCreator:
    def __init__(self, path_dir_db, usernames=None):
        self.__SetPathDirDb(path_dir_db)
        self.__SetUsernames(usernames)

    """
    SVGファイルを作成する。1ユーザ1年毎に1ファイル。
    """    
    def Create(self):
        print(self.__path_dir_db)
        print(self.__usernames)
        for username in self.__usernames:
            db = self.__GetDb(username)
            for records, year in self.__GetOneYearRecords(db):
                file_name = self.__GetSvgFilename(username, year)
#                print(year, records)
#                print(year, records, file_name)
                if os.path.isfile(file_name): continue
                print(year, records)
                with open(file_name, mode='w', encoding='utf-8') as f:
                    f.write(str(ContributionSvg.ContributionSvg(db, records, year).Create()))
    
    def __SetUsernames(self, usernames):
        if None is usernames:
            path_db_account = os.path.join(self.__path_dir_db, 'GitHub.Accounts.sqlite3')
            if not os.path.isfile(path_db_account): raise Exception('DBファイルが存在しません。:', path_db_account)
            db = dataset.connect('sqlite:///' + path_db_account)
            self.__usernames = []
            for record in db['Accounts'].find(): self.__usernames.append(record['Username'])
        elif isinstance(usernames, str): self.__usernames = [usernames]
        elif isinstance(usernames, (list, tuple)): self.__usernames = usernames
        else: raise Exception('引数usernamesはstr,list,tupleのいずれかの型にしてください。')
    def __SetPathDirDb(self, path_dir_db):
        if path_dir_db.endswith('/'): self.__path_dir_db = path_dir_db[:-1]
        else: self.__path_dir_db = path_dir_db
        if not os.path.isdir(path_dir_db): raise Exception('引数path_dir_dbはDBが存在するディレクトリパスを指定してください。: {0}'.format(self.__path_dir_db))
    def __GetDbFilename(self, username): return "GitHub.Contributions.{0}.sqlite3".format(username)
    def __GetSvgFilename(self, username, year): return "GitHub.Contributions.{0}.{1}.svg".format(username, year)
    def __GetDb(self, username):
        path = os.path.join(self.__path_dir_db, self.__GetDbFilename(username))
        try: return dataset.connect('sqlite:///' + path)
        except: print('DBファイルを開けませんでした。:', path); raise;

    # 最古年と最新年を取得する
    def __GetYearFirstAndLast(self, db):
        count = db['Contributions'].count()
        if 0 == count: raise Exception('レコードが1件も存在しません。')
        elif 1 == count: return int(db['Contributions'].find().next()['Date'][:first_cont.index('-')])
        else:
            min_date = db.query('select MIN("Date") MinDate from "Contributions"').next()['MinDate']
            max_date = db.query('select MAX("Date") MaxDate from "Contributions"').next()['MaxDate']
            return (int(min_date[:min_date.index('-')]), int(max_date[:max_date.index('-')])) # yyyy-MM-dd

    # 1年毎のDBレコード配列を返す(1月1日〜12月31日迄)
    def __GetOneYearRecords(self, db):
        years = self.__GetYearFirstAndLast(db)
        if isinstance(years, tuple):
            for target_year in range(years[0], (years[1] + 1)):
                yield (db.query('select * from "Contributions" where "Date" like "{year}-%" order by Date asc'.format(year=target_year)), target_year)
        else:
            return (db['Contributions'].find(order_by='Date'), first_year)


# テスト実行
if __name__ == '__main__':
    s = SvgCreator('/tmp/GitHub.Uploader.Issue.201706210940/database/res/db/')
    s.Create()
