import dataset
import os.path
import math
import datetime
from bs4 import BeautifulSoup

class YearContribution:
    def __init__(self, username, year, year_records, year_contribution):
        self.__username = username
        self.__year = year
        self.__year_records = year_records
        self.__year_contribution = year_contribution
        self.__SetThreshold(year_contribution)
        self.__SetColor()

    @property
    def Records(): return self.__year_records
    @property
    def Username(): return self.__username
    @property
    def Contribution(): return self.__year_contribution
    @property
    def Colors(): return self.__colors
    
    # 色を取得する
    def GetColor(self, contribution_value):
        for i, threshold in enumerate(self.__threshold):
            if threshold < contribution_value: continue
            else: return self.__colors[i]
        return self.__colors[-1]
            
    """
    色の閾値を算出する。公式の算出方法が不明。仮に1年間あたりの総貢献数で1日あたりの閾値を決める。
    * 0: 1件未満
    * 1: 最低1 1件以上 * 0.25 1/4 0.75 1.00
    * 2: 最低2 1日平均 * 0.50 2/4 1.25 1.50
    * 3: 最低3 1日平均 * 0.75 3/4 1.75 2.00
    * 4: 最低4 1日平均 * 1.00 4/4 2.25 2.50
    """
    def __SetThreshold(self, year_contribution_count):
        self.__threshold = []
        self.__threshold.append(0)
        if self.__year < datetime.datetime.now().year:
            one_day_average = year_contribution_count / 365
        else:
            one_day_average = year_contribution_count / (datetime.datetime.now() - datetime.datetime(datetime.datetime.now().year, 1, 1)).days
#            print('aaaaaaaaaaaaaaaaaaaaaaaaa:', one_day_average)
#            print('year_contribution_count:', year_contribution_count)
#        rates = [1.00, 1.50, 2.00, 2.5]
#        rates = [1.00, 1.50, 2.50, 4.00]
        rates = [1.00, 2.00, 3.00, 4.00]
        for x in [1, 2, 3, 4]:
#            value = int(one_day_average*(x/4))
            value = round(one_day_average*rates[x-1])
            if x < value: self.__threshold.append(value)
            else: self.__threshold.append(x)
        print(self.__threshold)
        return self.__threshold

    def __SetColor(self):
        self.__colors = ['#eee', '#c6e48b', '#7bc96f', '#239a3b', '#196127']

class ContributionSvg:
    def __init__(self, db, year_records, year):
        self.__db = db
        self.__year_records = year_records
        self.__year = year
    
    """
    SVGファイルを作成する。1ユーザ1年毎に1ファイル。
    """
    def Create(self):
        svg_base = '''<svg width="720" height="114" class="js-calendar-graph-svg">
    <g transform="translate(16, 30)">
    </g>
</svg>'''        
        self.__soup = BeautifulSoup(svg_base, 'html.parser')
        self.__soup.svg.append(BeautifulSoup('<text text-anchor="start" class="YearContribution" dx="0" dy="10">{0}: {1} contributions</text>\n'.format(self.__year, self.__GetOneYearContributionCount()), 'html.parser'))
        
        firstDt, lastDt = (datetime.datetime(self.__year, 1, 1), datetime.datetime(self.__year, 12, 31))
        yc = YearContribution('username', self.__year, self.__year_records, self.__GetOneYearContributionCount())
        with open('ContributionSvg.svg', mode='w', encoding='utf-8') as f:
            g = self.__soup.svg.g            
            first_date = firstDt
            for yearofweek in range(0, 54):
                dom_week, first_date = self.__GetSvgDayofweekContribution(yearofweek, first_date, yc)
                g.append(dom_week)
                if None is first_date: break
                if self.__year < first_date.year: break
            g.append(BeautifulSoup(self.__GetSvgHeaderMonth(), 'html.parser'))
            g.append(BeautifulSoup(self.__GetSvgHeaderDayofweek(), 'html.parser'))
            f.write(str(self.__soup))
        return self.__soup
            
    """
    1週間分のSVGと次の開始日を返す。
    """
    def __GetSvgDayofweekContribution(self, yearofweek, first_date, yc):
        first_date_week = self.__ConvertWeek(first_date.weekday())
        dom_week = BeautifulSoup('<g transform="translate({x}, 0)"></g>'.format(x=13*yearofweek), 'html.parser')
        for dayofweek in range(0, 7):
            if dayofweek < first_date_week: continue
            targetDt = first_date + datetime.timedelta(days=(dayofweek - first_date_week))
#            if self.__year < targetDt.year: continue
            if datetime.datetime.now() < targetDt: return (dom_week, None) # 未来の場合、次の日をNoneにして中断
            record = self.__db['Contributions'].find_one(Date="{0:%Y-%m-%d}".format(targetDt))
            if None is record:
                record = {}
                record['Date'] = "{0:%Y-%m-%d}".format(targetDt)
                record['Count'] = 0
            dom_day = BeautifulSoup(self.__GetSvgOneDayContribution(record, dayofweek, yc.GetColor(record['Count'])), 'html.parser')
            dom_week.g.append(dom_day)
        return (dom_week, first_date + datetime.timedelta(days=(7 - first_date_week))) # next_date

    """
    day_of_week: 0〜6(日〜土)
    contribution: 0〜4()
    week: 0〜6(日〜土)
    """
    def __GetSvgOneDayContribution(self, record, dayofweek, fill):
        return '<rect class="day" width="10" height="10" x="13" y="{y}" fill="{fill}" data-count="{count}" data-date="{date}"></rect>'.format(y=12*dayofweek, fill=fill, count=record['Count'], date=record['Date'])
    
    # 月曜はじまりを日曜はじまりに変換する
    # datetime.weekday() 0〜6(月〜日)
    # https://docs.python.jp/3/library/datetime.html#datetime.datetime.weekday
    # return 0〜6(日〜土)
    # 0 1 2 3 4 5 6
    # 月火水木金土日
    # 日月火水木金土
    def __ConvertWeek(self, mon_week):
        sun_week = mon_week + 1
        if 7 == sun_week: return 0
        else: return sun_week
    
    # 1年のうち何週目か（日〜土の順で算出）
    def __GetYearofweek(self, dt):
        if isinstance(dt, str): dt = datetime.strptime(dt, '%Y-%m-%d')
        if not isinstance(dt, datetime.datetime): raise Exception('引数dtはdatetime型か%Y-%m-%d形式の文字列を指定してください。')
#        print(dt)
        first_day_of_year = datetime.datetime(dt.year, 1, 1)
#        print(first_day_of_year)
#        span = (dt - first_day_of_year).days
        span = (dt - first_day_of_year).days + self.__ConvertWeek(dt.weekday())
        return math.ceil(span / 7)

    def __GetSvgHeaderMonth(self):
        titles = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#        titles = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
#        titles = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

        # その月の1日が1年の内何週目にあるか(year_of_week)によって位置を算出できる。
        # 日曜日からはじめたときの年何週目かを算出するのはどうやるのか。
        year_of_weeks = self.__GetYearofweeks()
        result = ''
        for i, title in enumerate(titles):
#            result += '            <text x="{x}" y="-10" class="month">{title}</text>\n'.format(title=title, x=(37+(60*i)))
#            result += '            <text x="{x}" y="-4" class="month">{title}</text>\n'.format(title=title, x=(12+(59*i)))
            result += '            <text x="{x}" y="-4" class="month">{title}</text>\n'.format(title=title, x=(13*year_of_weeks[i]))
            
        return result
    
    def __GetYearofweeks(self):
        year_of_weeks = []
        for month in range(1, 13):
            year_of_weeks.append(self.__GetYearofweek(datetime.datetime(self.__year, month, 1)))
        print(year_of_weeks)
        return year_of_weeks
    
    def __GetSvgHeaderDayofweek(self):
        titles = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
#        titles = ['日', '月', '火', '水', '木', '金', '土']
        result = ''
        for i, title in enumerate(titles):
            if 0 == (i % 2):
                result += '        <text text-anchor="start" class="wday" dx="-14" dy="{dy}" style="display: none;">{title}</text>\n'.format(dy=(8+(12*i)), title=title)
            else:
                result += '        <text text-anchor="start" class="wday" dx="-14" dy="{dy}">{title}</text>\n'.format(dy=(8+(12*i)), title=title)
        return result
    
    """
    1年間あたりの貢献数。
    db: DB
    year: 対象の年(西暦)
    """
    def __GetOneYearContributionCount(self):
        records = self.__db.query('select SUM("Count") YearCount from "Contributions" where "Date" like "{year}-%"'.format(year=self.__year))
        return records.next()['YearCount']


# テスト実行
if __name__ == '__main__':
    username = 'ytyaru'
    path_dir_db = '/tmp/GitHub.Uploader.Issue.201706210940/database/res/db/'
    path_file_db = 'GitHub.Contributions.{0}.sqlite3'.format(username)
    print(os.path.join(path_dir_db, path_file_db))
    db = dataset.connect('sqlite:///' + os.path.join(path_dir_db, path_file_db))
    s = ContributionSvg(db, path_dir_db, 2016)
    s.Create()
