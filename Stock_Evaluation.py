# 1) Gets the current date and creates the filename that today's stocklist
#    will be downloaded as.

# 2) Downloads the list of stocks that have hit an all-time high from
#    www.barcharts.com using function bar_charts_scrape()

# *****You should modify the code to save it where you want*****

# 3) Activate function csv_writer
# 4) csv_writer() points to function make_new_stock_list(), which uses the file
#    downloaded from www.barcharts.com to put all the stocks into a list and
#    return that list.
# 5) csv_writer() points to Last_30_Days() function where the list of the stocks
#    that have made it through the entire screeing process over ther last
#    30 days is accessed and edited to remove entries older than 30 days. It
#    does this by using the days_between() functions. The updated list is
#    returned.
# 6) The New_Stock_List and the 30_Days_List are sent to the function
#    sorting_loop()
# 7) The sorting_loop() starts off by opening and logging into
#    www.investors.com.  Each stock is check for whether it is on the
#    30_Days_List and if its market capitalisation is over $5B. If this these
#    are not the case then the EPS value of the stock is checked using lxml.
#    If it is over 90, the RS value is checked using Selenium. If it is over 90
#    The stock is added to the sorted_list and the 30_day_list. These are both
#    returned to the CSV file.
# 8) The stock type, sector, and industry are scraped off of the morningstart
#    website and added as well
# 9) A new file with all the screened stocks is written and created.


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


# Dowloads latest all-time high list
def bar_charts_scrape():

    path = "/Users/alexschimel/Desktop/Stock_picking"

    # creates a firefox profile so that files are automatically downloaded
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", path)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

    # log in to bar charts and downloads today's list
    browser = webdriver.Firefox(firefox_profile=profile)
    browser.get('https://www.barchart.com/#/login')
    time.sleep(1.32)
    elem = browser.find_element_by_xpath('//*[@id="bc-login-form"]/div[1]/input[1]')
    elem.send_keys("bpoole@pobox.com")
    elem_2 = browser.find_element_by_id("login-form-password")
    elem_2.send_keys("Valence26")
    elem_2 = browser.find_element_by_xpath('//*[@id="bc-login-form"]/div[6]/button').click()
    time.sleep(6.834)
    browser.get('https://www.barchart.com/stocks/highs-lows#/viewName=57401&timeFrame=alltime')
    time.sleep(8.7)
    download = browser.find_element_by_xpath(
        '//*[@id="main-content-column"]/div/div[3]/div[2]/div[2]/a[3]').click()
    time.sleep(10)
    browser.close()


# Creates a list of today's stocks to be sorted
def make_new_stock_list(file_name):
    # Creates a variable with all the data from the CSV file in it
    stock_list = io.open("%s" % file_name, newline='')
    reader = csv.reader(stock_list)

    # Moves the posistion of the reader past the header
    header = next(reader)

    # Creates a list of lists of all the desired data from 'reader'
    data = []
    for row in reader:
        symbol = row[0]
        name = row[1]
        high = float(row[2])
        cap = int(row[3])
        date = datetime.datetime.strptime(row[4], '%m/%d/%y')
        formatted_date = date.strftime('%Y%m%d')
        data.append([symbol, name, high, cap, formatted_date])

    return data


# Calculates the diffrence between two dates in days
def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y%m%d")
    d2 = datetime.datetime.strptime(d2, "%Y%m%d")
    return abs((d2 - d1).days)


# Returns a list of the stocks evaluated over last 30 days.
def Last_30_Days(today):
    Last_Thirty_Days = "30_Day_Tracker.csv"
    tracker = io.open(Last_Thirty_Days, newline='')
    reader_2 = csv.reader(tracker)
    data_2 = []
    for row_2 in reader_2:

        entry_date = row_2[1]
        date_compare = days_between(today, entry_date)
        if date_compare <= 30:
            symbol_2 = row_2[0]
            date_2 = row_2[1]
            data_2.append([symbol_2, date_2])
    return data_2


# checks if a stock is already in the last 30 days list
def symbol_compare(data_2, Symbol):
    for n in range(0, len(data_2)):
        current_row = data_2[n]
        Legacy_Symbol = current_row[0]
        if Symbol == Legacy_Symbol:
            return True
    else:
        return False


# Does several sorts to get a final list
def Sorting_Loop(data, data_2):
    # Variable to hold new list of stocks that meet sorting criteria
    sorted_list = []
    check_list = data_2
    driver = webdriver.Firefox()
    driver.get("https://myibd.investors.com/secure/signin.aspx?eurl=http%3A%2F%2Fwww.investors.com%2F")
    elem = driver.find_element_by_id("UserName")
    time.sleep(3)
    elem.clear()
    elem.send_keys("bpoole@pobox.com")
    elem_2 = driver.find_element_by_id("Password")
    elem_2.clear()
    time.sleep(3.42)
    elem_2.send_keys("Valence26")
    time.sleep(3.76)
    elem_2 = driver.find_element_by_id("loginButton")
    elem_2.click()
    time.sleep(1.62)
    # This is our sorting loop
    for n in range(0, len(data)):
        this_line = data[n]
        symbol = str(this_line[0])
        date = str(this_line[4])
        checker = symbol_compare(check_list, symbol)
        # This first sort limits stocks that have a market capitalisation
        # of $5B or less (5,000,000 thousand)
        if this_line[3] < 5000000 and checker is False:
            # This data is scraped from the following URL. It is the Earnings Per
            # Share (EPS) growth rating and can be obtained without logging into
            # the website. It is a rating that compares all the stocks in the
            # Investors Business Daily (IBD, www.investors.com) and rates them
            # on a 0-99 scale. I want to pick only the best stocks that have an
            # EPS of 90 or greater.
            url = "http://research.investors.com/stock-quotes/nasdaq-" + symbol + ".htm"
            page = requests.get(url)
            html = lxml.html.fromstring(page.text)
            content_divs = html.xpath('//*[@id="stkQteOver-1"]/div/div[2]/ul[3]/li[2]')
            # sometimes there are symbols that have a '.' inside them like 'HEI.A'.
            # www.investors.com can't handle these and an error is returned. This
            # try code skips over anything that returns an error and moves on to
            # the next one. Sometimes the website just doesn't seem to find the
            # right path even for a propper symbol, so I've set the code up to
            # try to access each symbol twice just in case.
            try:
                EPS = content_divs[0].text_content().strip()
                checker = symbol_compare(check_list, symbol)
            except:
                try:
                    EPS = content_divs[0].text_content().strip()
                    checker = symbol_compare(check_list, symbol)
                except:
                    print "4th didn't work"
                    pass
                else:
                    if int(EPS) >= 90 and checker is False:
                        for x in range(0, 2):
                            driver.get(
                                "http://research.investors.com/stock-quotes/nasdaq-" + symbol + ".htm")
                            RS = driver.find_element_by_xpath(
                                '//*[@id="stkQteOver-1"]/div/div[2]/ul[4]/li[2]').text
                            print RS
                            compared = "?"
                            if RS == compared:
                                time.sleep(5)
                                pass
                            else:
                                if int(RS) >= 90:
                                    this_line.append(EPS)
                                    this_line.append(RS)
                                    sorted_list.append(this_line)
                                    check_list.append([symbol, date])
                                    break
                                else:
                                    break
                    else:
                        pass
            else:
                if int(EPS) >= 90 and checker is False:
                    for x in range(0, 2):
                        driver.get(
                            "http://research.investors.com/stock-quotes/nasdaq-" + symbol + ".htm")
                        RS = driver.find_element_by_xpath(
                            '//*[@id="stkQteOver-1"]/div/div[2]/ul[4]/li[2]').text
                        print RS
                        compared = "?"
                        if RS == compared:
                            time.sleep(5)
                            pass
                        else:
                            if int(RS) >= 90:
                                this_line.append(EPS)
                                this_line.append(RS)
                                sorted_list.append(this_line)
                                check_list.append([symbol, date])
                                break
                            else:
                                break
                else:
                    pass
        else:
            pass

    file = open("30_Day_Tracker.csv", "w")
    writer = csv.writer(file)
    r = 0
    for line in check_list:
        first_line = check_list[r]
        writer.writerow([first_line[0], first_line[1]])
        r += 1
    file.close()
    driver.close()
    return sorted_list


# This is kind of the engine to run the program. It makes the final csv file.
def csv_writer(input_file, time):
    New_Stock_List = make_new_stock_list(input_file)
    Thirty_Days = Last_30_Days(time)
    Sorted_Stocks = Sorting_Loop(New_Stock_List, Thirty_Days)
    formatted_date = dt
    Final_Stocks_Path = "%s_Sorted_Stocks.csv" % str(formatted_date)
    file = open(Final_Stocks_Path, 'w')
    writer = csv.writer(file)
    header = ('Ticker', 'Name', 'High', 'Date', 'EPS', 'RS', 'Type', 'Sector', 'Industry')
    writer.writerow(header)
    r = 0
    morning = webdriver.Firefox()
    for line in Sorted_Stocks:
        each_line = Sorted_Stocks[r]
        morning_site = "http://financials.morningstar.com/company-profile/c.action?t=" + \
            each_line[0]
        print morning_site
        morning.get(morning_site)
        import time
        time.sleep(.5)
        Stock_Type = morning.find_element_by_xpath('//*[@id="PeerInfo2"]/table/tbody/tr/td[1]').text
        try:
            str(Stock_Type)
            each_line.append(Stock_Type)
        except:
            Stock_Type = "unknown"
            each_line.append(Stock_Type)
        Sector = morning.find_element_by_xpath('//*[@id="BasicData"]/table/tbody/tr[6]/td[3]').text
        try:
            str(Sector)
            each_line.append(Sector)
        except:
            Sector = "unknown"
            each_line.append(Sector)
        Industry = morning.find_element_by_xpath(
            '//*[@id="BasicData"]/table/tbody/tr[6]/td[5]').text
        try:
            str(Industry)
            each_line.append(Industry)
        except:
            Sector = "unknown"
            each_line.append(Industry)
        writer.writerow(each_line)
        r += 1
    morning.close()
    file.close()


dt = str(datetime.datetime.now(tz=EST5EDT()))
dt = dt.split(" ")
dt = dt[0]
dt = dt.split('-')
file_name = "all-us-exchanges-all-time-new-highs-%s-%s-%s.csv" % (dt[1], dt[2], dt[0])
dt = dt[0] + dt[1] + dt[2]


bar_charts_scrape()
csv_writer(file_name, dt)
