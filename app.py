from urllib.request import urlopen
import urllib

from bs4 import BeautifulSoup

import csv

import re


class Parser:
    def __init__(self, url_catalog):
        self.url_catalog = url_catalog
        self.splitting = url_catalog.split('/')
        self.file_name = self.splitting[3]
        self.page_url = '?page='
        self.much_pages = 999
        self.initial_url = '{}//{}/'.format(self.splitting[0], self.splitting[2])
        self.href_list = list()

    def check_pages(self):
        for count_page in range(1, self.much_pages):
            try:
                doc_count = urlopen('{}{}{}'.format(self.url_catalog, self.page_url, count_page)).read()
            except urllib.request.HTTPError:
                break
            else:
                html_count = BeautifulSoup(doc_count, 'html.parser')
                categories = self.find_data(html_count, 'a', 'call_to_action _secondary _medium view_details')
                for href in categories:
                    str_href = '{}{}'.format(self.initial_url, href.get('href'))
                    self.href_list.append(str_href)

    def record(self, data_for_recording):
        with open('Data/{}.csv'.format(self.file_name), 'a') as data_file:
            writer = csv.writer(data_file)
            writer.writerow(data_for_recording)

    @staticmethod
    def find_data(html, tag, value):
        return html.findAll(tag, value)

    @staticmethod
    def get_value_info(each):
        pattern = re.compile(r'\s+')
        value = each.get_text().replace(',', ' and')
        value = re.sub(pattern, ' ', value).strip()
        return value

    def collect_info(self, value_f_n, *args, info_i=None):
        try:
            assert info_i
            for (each_i, each_s_n, each_p, each_e, each_c) in zip(info_i, *args):
                value_s_n = self.get_value_info(each_s_n)
                value_p = self.get_value_info(each_p)
                value_i = 'http:{}'.format(each_i['src'])
                value_e = self.get_value_info(each_e)[:-1]
                value_c = self.get_value_info(each_c)
                info = '{} - {}, {}, {}, {}, {}'.format(value_f_n, value_s_n, value_p, value_i, value_e, value_c).split(
                    ',')
                self.record(info)
        except AssertionError:
            for (each_s_n, each_p, each_e, each_c) in zip(*args):
                value_s_n = self.get_value_info(each_s_n)
                value_p = self.get_value_info(each_p)
                value_i = '[ No Image ]'
                value_e = self.get_value_info(each_e)[:-1]
                value_c = self.get_value_info(each_c)
                info = '{} - {}, {}, {}, {}, {}'.format(value_f_n, value_s_n, value_p, value_i, value_e, value_c).split(
                    ',')
                self.record(info)

    def process(self):
        self.check_pages()
        for each_href in self.href_list:
            doc = urlopen(each_href).read()
            html = BeautifulSoup(doc, 'html.parser')
            column_name = ['Name', 'Price', 'Image', 'Estimated', 'Code']
            first_name = self.find_data(html, 'h1', {'id': 'product_family_heading'})
            first_name = first_name[0].get_text().replace(',', ' and')
            sub_name = self.find_data(html, 'span', {'class': 'name'})
            price = self.find_data(html, 'span', {'class': 'price'})
            img = self.find_data(html, 'img', {'style': 'display:none;'})
            estimate = self.find_data(html, 'p', {'class': ['notification_in-stock', 'notification_out-stock']})
            code = self.find_data(html, 'span', {'class': 'item-code'})
            self.record(column_name)
            self.collect_info(first_name, sub_name, price, estimate, code, info_i=img)


CreateParse = Parser(
    'http://www.viovet.co.uk/Pet_Foods_Diets-Dogs-Hills_Pet_Nutrition-Hills_Prescription_Diets/c233_234_2678_93/category.html')
CreateParse.process()
