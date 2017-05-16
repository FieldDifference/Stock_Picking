"""
 Gets the current date and creates the filename that today's stocklist
   will be downloaded as.

2) Downloads the list of stocks that have hit an all-time high from
   www.barcharts.com using function bar_charts_scrape()

*****You should modify the code to save it where you want*****

3) Activate function csv_writer
4) csv_writer() points to function make_new_stock_list(), which uses the file
   downloaded from www.barcharts.com to put all the stocks into a list and
   return that list.
5) csv_writer() points to Last_30_Days() function where the list of the
   stocks that have made it through the entire screeing process over ther last
   30 days is accessed and edited to remove entries older than 30 days. It
   does this by using the days_between() functions. The updated list is
   returned.
6) The New_Stock_List and the 30_Days_List are sent to the function
   sorting_loop()
7) The sorting_loop() starts off by opening and logging into
   www.investors.com.  Each stock is check for whether it is on the
   30_Days_List and if its market capitalisation is over $5B. If this these
   are not the case then the EPS value of the stock is checked using lxml.
   If it is over 90, the RS value is checked using Selenium. If it is over 90
   The stock is added to the sorted_list and the 30_day_list. These are both
   returned to the CSV file.
8) The stock type, sector, and industry are scraped off of the morningstart
   website and added as well
9) A new file with all the screened stocks is written and created.
"""

import csv
import io
import datetime
import requests
import lxml.html
from selenium import webdriver
import time


# Gets current Eastern Standard Time (EST)
class EST5EDT(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def dst(self, dt):
        d = datetime.datetime(dt.year, 3, 8)  # 2nd Sunday in March
        self.dston = d + datetime.timedelta(days=6 - d.weekday())
        d = datetime.datetime(dt.year, 11, 1)  # 1st Sunday in Nov
        self.dstoff = d + datetime.timedelta(days=6 - d.weekday())
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(0)

    def tzname(self, dt):
        return 'EST5EDT'


class DateWork(object):
    def __init__(self):
        self.TodaysDate = str(datetime.datetime.now(tz=EST5EDT()))
        self.CurrentDate = self.TodaysDate.split(" ")
        self.CurrentDate = self.CurrentDate[0]
        self.CurrentDate = self.CurrentDate.split('-')

    def file_name(self):
        FileName = (
            "all-us-exchanges-all-time-new-highs-%s-%s-%s.csv"
            % (self.CurrentDate[1], self.CurrentDate[2], self.CurrentDate[0]))
        return FileName

    def formatted_date(self):
        CurrentDate = (self.CurrentDate[0]
                       + self.CurrentDate[1]
                       + self.CurrentDate[2])
        return CurrentDate


class MorningScrape(object):

    def __init__(self, Symbol):
        self.Symbol = Symbol
        self.Morning = webdriver.Firefox()

    def open_site(self):
        MorningSite = (
            "http://financials.morningstar.com/"
            "company-profile/c.action?t=" +
            self.Symbol)
        print MorningSite
        self.Morning.get(MorningSite)
        time.sleep(.5)

    def close_site(self):
        self.Morning.close()

    def get(self, Path):
        Descript = self.Morning.find_element_by_xpath(Path).text
        try:
            return str(Descript)
        except:
            return "unknown"


# Dowloads latest all-time high list
def bar_charts_scrape():

    Path = "/Users/newwave/lpthw"

    # creates a firefox profile so that files are automatically downloaded
    Profile = webdriver.FirefoxProfile()
    Profile.set_preference("browser.download.folderList", 2)
    Profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    Profile.set_preference("browser.download.manager.showWhenStarting", False)
    Profile.set_preference("browser.download.dir", Path)
    Profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", "text/csv")

    # log in to bar charts and downloads today's list
    Browser = webdriver.Firefox(firefox_profile=Profile)
    Browser.get('https://www.barchart.com/#/login')
    time.sleep(1.32)
    Elem = Browser.find_element_by_xpath(
        '//*[@id="bc-login-form"]/div[1]/input[1]')
    Elem.send_keys("bpoole@pobox.com")
    Elem_2 = Browser.find_element_by_id("login-form-password")
    Elem_2.send_keys("Valence26")
    Elem_2 = Browser.find_element_by_xpath(
        '//*[@id="bc-login-form"]/div[6]/button').click()
    time.sleep(6.834)
    Browser.get(
        'https://www.barchart.com/stocks/highs-lows#'
        '/viewName=57401&timeFrame=alltime')
    time.sleep(8.7)
    Browser.find_element_by_xpath(
        '//*[@id="main-content-column"]/div/div[3]/div[2]/div[2]/a[3]').click()
    time.sleep(10)
    Browser.close()


# Creates a list of today's stocks to be sorted
def make_new_stock_list(FileName):
    # Creates a variable with all the data from the CSV file in it
    StockList = io.open("%s" % FileName, newline='')
    Reader = csv.reader(StockList)

    # Moves the posistion of the reader past the header
    next(Reader)

    # Creates a list of lists of all the desired data from 'reader'
    Data = []
    for Row in Reader:
        Symbol = Row[0]
        Name = Row[1]
        High = float(Row[2])
        Cap = int(Row[3])
        print Row[4]
        try:
            Date = datetime.datetime.strptime(Row[4], '%m/%d/%y')
            FormattedDate = Date.strftime('%Y%m%d')
        except:
            Date = DateWork()
            FormattedDate = Date.formatted_date()
        Data.append([Symbol, Name, High, Cap, FormattedDate])

    StockList.close()
    return Data


# Calculates the diffrence between two dates in days
def days_between(D1, D2):
    D1 = datetime.datetime.strptime(D1, "%Y%m%d")
    print D1
    D2 = datetime.datetime.strptime(D2, "%Y%m%d")
    print D2
    Delta = abs((D2 - D1).days)
    print Delta
    return Delta


# Returns a list of the stocks evaluated over last 30 days.
def last_30_days(today):
    LastThirtyDays = "30_Day_Tracker.csv"
    Tracker = io.open(LastThirtyDays, newline='')
    Reader2 = csv.reader(Tracker)

    Data2 = []
    for Row2 in Reader2:

        EntryDate = Row2[1]
        DateCompare = days_between(today, EntryDate)
        if DateCompare <= 30:
            Symbol2 = Row2[0]
            Date2 = Row2[1]
            Data2.append([Symbol2, Date2])

    Tracker.close()
    return Data2


# checks if a stock is already in the last 30 days list
def symbol_compare(Data2, Symbol):
    for n in range(0, len(Data2)):
        CurrentRow = Data2[n]
        LegacySymbol = CurrentRow[0]
        if Symbol == LegacySymbol:
            return True
    else:
        return False


# Get the EPS value if available
def eps_value(Symbol):
    Url = (
        "http://research.investors.com/stock-quotes/nasdaq-"
        + Symbol + ".htm")
    Page = requests.get(Url)
    HTML = lxml.html.fromstring(Page.text)
    ContentDivs = HTML.xpath(
        '//*[@id="stkQteOver-1"]'
        '/div/div[2]/ul[3]/li[2]')

    # Skips symbols that aren't in Investor's Databases
    # Tries to find symbol twice before passing
    try:
        EPS = ContentDivs[0].text_content().strip()
        int(EPS)
    except:
        try:
            EPS = ContentDivs[0].text_content().strip()
            int(EPS)
        except:
            print "Can't get EPS value."
            return "pass"
        return EPS
    else:
        return EPS


# Open and Log Into Investors.com
def investors_login():
    Driver = webdriver.Firefox()
    Driver.get(
        "https://myibd.investors.com/secure/signin"
        ".aspx?eurl=http%3A%2F%2Fwww.investors.com%2F")
    Elem = Driver.find_element_by_id("UserName")
    time.sleep(3)
    Elem.clear()
    Elem.send_keys("bpoole@pobox.com")
    Elem2 = Driver.find_element_by_id("Password")
    Elem2.clear()
    time.sleep(3.42)
    Elem2.send_keys("Valence26")
    time.sleep(3.76)
    Elem2 = Driver.find_element_by_id("loginButton")
    Elem2.click()
    time.sleep(1.62)
    return Driver


# Goes to Investors.com to get RS Value
def get_rs(Driver, Symbol):
    for x in range(0, 4):
        Driver.get(
            "http://research.investors.com/"
            "stock-quotes/nasdaq-" + Symbol + ".htm")
        RS = Driver.find_element_by_xpath(
            '//*[@id="stkQteOver-1"]/div/'
            'div[2]/ul[4]/li[2]'
        ).text
        print RS
        Compared = "?"
        if RS == Compared:
            time.sleep(5)
            pass
        else:
            break
    return RS


# Does several sorts to get a final list
def sorting_loop(Data, Data2):
    # Variable to hold new list of stocks that meet sorting criteria
    CheckList = Data2
    SortedList = []
    Driver = investors_login()
    # This is our sorting loop
    for n in range(0, len(Data)):
        ThisLine = Data[n]
        Symbol = str(ThisLine[0])
        Date = str(ThisLine[4])
        Checker = symbol_compare(CheckList, Symbol)
        print Symbol
        EPS = eps_value(Symbol)
        # This first sort limits stocks that have a market capitalisation
        # of $5B or less (5,000,000 thousand)
        if EPS is 'pass':
            pass
        elif ThisLine[3] < 5000000 and Checker is False and int(EPS) >= 90:
            RS = get_rs(Driver, Symbol)
            if int(RS) >= 90:
                ThisLine.append(EPS)
                ThisLine.append(RS)
                SortedList.append(ThisLine)
                CheckList.append([Symbol, Date])
            else:
                pass
        else:
            pass

    File = open("30_Day_Tracker.csv", "w")
    Writer = csv.writer(File)
    r = 0
    for Line in CheckList:
        FirstLine = CheckList[r]
        Writer.writerow([FirstLine[0], FirstLine[1]])
        r += 1
    File.close()
    Driver.close()
    return SortedList


def append_morning(SortedStocks):
    TypeXPath = '//*[@id="PeerInfo2"]''/table/tbody/tr/td[1]'
    SectorXPath = '//*[@id="BasicData"]/table/tbody/tr[6]/td[3]'
    IndustryXPath = '//*[@id="BasicData"]/table/tbody/tr[6]/td[5]'

    R = 0
    for line in SortedStocks:
        EachLine = SortedStocks[R]

        St = MorningScrape(EachLine[0])
        St.open_site()

        Stock_Type = St.get(TypeXPath)
        Sector = St.get(SectorXPath)
        Industry = St.get(IndustryXPath)

        St.close_site()

        EachLine.append(Stock_Type)
        EachLine.append(Sector)
        EachLine.append(Industry)

        R += 1

    return SortedStocks


def cvs_writer(SortedStocks):
    date = DateWork()
    FormattedDate = date.formatted_date()
    FinalStocksPath = "%s_Sorted_Stocks.csv" % str(FormattedDate)
    File = open(FinalStocksPath, 'w')
    Writer = csv.writer(File)
    header = (
        'Ticker', 'Name', 'High', 'Date', 'EPS',
        'RS', 'Type', 'Sector', 'Industry'
    )

    Writer.writerow(header)

    R = 0
    for line in SortedStocks:
        EachLine = SortedStocks[R]
        Writer.writerow(EachLine)
        R += 1

    File.close()


# This is kind of the engine to run the program. It makes the final csv file.
def engine():
    bar_charts_scrape()
    Date = DateWork()
    InputFile = Date.file_name()
    Time = Date.formatted_date()
    NewStockList = make_new_stock_list(InputFile)
    ThirtyDays = last_30_days(Time)
    SortedStocks = sorting_loop(NewStockList, ThirtyDays)
    SortedStocks = append_morning(SortedStocks)
    cvs_writer(SortedStocks)


engine()
