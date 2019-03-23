from lxml import html
import requests
import sqlite3 as lite
import os


def request_site(link):
    try_number = 100
    for i in range(0, try_number):
        try:
            start_page = requests.get(link)
            tree = html.fromstring(start_page.text)
            del start_page
            return tree
        except:
            pass


class Myket:

    def __init__(self, database_path):
        if os.path.isfile(database_path):
            try:
                self.con = lite.connect(database_path)
            except:
                print("error to connect to database ....")
                input()
                exit(0)
        else:
            print("database was not found...............................")
            input()
            exit(0)

        self.cur = self.con.cursor()
        self.url = "https://myket.ir/app/"

    def __get_app_detail__(self, tree):
        try:
            try:
                self.app_name = tree.xpath(
                    '/html/body/myket-app-root/div/myket-main/div/div/myket-app-page/div/div[1]/div/div[1]/div[2]/h1/text()')[
                    0].strip()
            except:
                self.app_name = " "
            try:
                self.logo = tree.xpath(
                    '/html/body/myket-app-root/div/myket-main/div/div/myket-app-page/div/div[1]/div/div[1]/div[1]/img/@src')[
                    0].strip()
            except:
                self.logo = " "
            try:
                self.category = tree.xpath(
                    '/html/body/myket-app-root/div/myket-main/div/div/myket-app-page/div/div[1]/div/div[2]/a[1]/myket-app-circle-category/myket-app-badge/div/div[2]/text()')[
                    0].strip()
            except:
                self.category = " "

            try:
                self.description_temp = tree.xpath(
                    '//div[@class="wrapper"]/*//div[@class="md-padding"]/text()')
                self.description = ""
                for i in self.description_temp:
                    self.description += i.strip() + " "
            except:
                self.description = ""

                # if not self.__search_package_name__(package_name):
            return True

        except:
            return False

    def crawl_link(self, package_name):
        """
        if package_name is -1 that mean crawl whole site

        :param package_name:
        :return:
        """
        self.get_link_from_page(package_name)
        while True:

            self.cur.execute("SELECT * FROM myket WHERE check_crawled=? LIMIT ?  ", ("0", 10))
            rows = self.cur.fetchall()
            if len(rows) == 0:
                break
            for row in rows:
                print(row[1])
                self.get_link_from_page(row[1])

    def get_link_from_page(self, package_name):
        """
        this methode crawl the site and save all link app in database
        :param package_name:
        :return:
        """

        url = self.url + package_name
        tree = request_site(url)
        links_temp = tree.xpath(
            '//div[@class="layout-row layout-align-center"]/a/@href'
        )[1:]
        print("Pakcage Name =>", package_name)

        if self.__get_app_detail__(tree) and package_name != "":
            self.update_db(self.app_name, self.logo, self.description, self.category, package_name)
        for link in links_temp:
            if not self.____search_package_name___in_url__(link.split('/')[2]):
                self.__insert_link_into_database__(link.split('/')[2])

        self.cur.execute("UPDATE myket SET check_crawled=1  WHERE package_name=?", [package_name])
        self.con.commit()

    def __insert_link_into_database__(self, package_name):
        self.cur.execute(
            "INSERT INTO myket (package_name) VALUES(?)", [package_name])
        self.con.commit()
        print("inserted Pakcage Name ---------------->", package_name)

    def __search_package_name__(self, package_name):
        self.cur.execute("SELECT * FROM myket WHERE package_name=?", (package_name,))
        rows = self.cur.fetchall()
        if rows:
            return True
        return False

    def ____search_package_name___in_url__(self, package_name):
        self.cur.execute("SELECT * FROM myket WHERE package_name=?", (package_name,))
        rows = self.cur.fetchall()
        if rows:
            return True
        return False

    def update_db(self, app_name, logo, description, category, package_name):
        self.cur.execute("UPDATE myket SET name=? , logo=?,description=?,category=?  WHERE package_name=?",
                         [app_name, logo, description, category, package_name])
        self.con.commit()
        print("updated ----------------> ", package_name)


my = Myket("db.db")
my.crawl_link("")
