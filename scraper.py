import urllib2
from bs4 import BeautifulSoup

from db import models
from app import db
# site = urllib2.urlopen('http://www.moneycontrol.com/mutualfundindia/').read()
# site = site.split('\n')
# site = [line.strip() for line in site if line.find('/mutual-funds/nav/') >= 0]
# for line in site:
#     soup = BeautifulSoup(line)
#     print soup.a['href'], '#####', soup.a['title'], '#####', soup.a.get_text()
def get_all_category_urls():
    fund_category_urls = set([])
    print 'getting category url'
    site = urllib2.urlopen('http://www.moneycontrol.com/mutual-funds/performance-tracker/returns/large-cap.html').read().split('\n')
    site = [line.strip()  for line in site if line.find('<li>') > -1 and line.find('performance-tracker/returns') > -1]
    for line in site:
        soup = BeautifulSoup(line)
        ls = soup.find_all('li')
        for item in ls:
            url = item.a['href']
            if url.startswith('/mutual-funds/performance-tracker/returns/'):
                fund_category_urls.add('http://www.moneycontrol.com'+url)
    return fund_category_urls

def get_all_funds_for_category(category_url):
    funds = {} # key = fund ID, value = {} value['url'], value['name']
    print 'getting category page'
    site = urllib2.urlopen(category_url)
    site = [line.strip() for line in site if line.find('/mutual-funds/nav/') > -1]
    for line in site:
        soup = BeautifulSoup(line)
        url = soup.td.a['href']
        name = soup.td.a.get_text()
        fund_id = url.split('/')[-1]
        funds[fund_id] = {}
        funds[fund_id]['url'] = 'http://www.moneycontrol.com'+url
        funds[fund_id]['name'] = name
        url_keywords = set([kw.lower() for kw in url.split('/')[-2].split('-')])
        if '(g)' in url_keywords:
            url_keywords.add('growth')
        funds[fund_id]['keywords'] = url_keywords
    return funds

def get_all_data_for_fund(fund_url):
    print 'getting mf page'
    site = urllib2.urlopen(fund_url)
    fund_name_line = [line.strip() for line in site if line.find('h1') > -1][0]
    fund_family = [line.strip() for line in site if line.find('Fund Family') > -1]
    fund_family_line = '' if len(fund_family)==0 else fund_family[0]
    fund_class = [line.strip() for line in site if line.find('Fund Class') > -1]
    fund_class_line = '' if len(fund_class)==0 else fund_class[0]
    soup_name = BeautifulSoup(fund_name_line)
    soup_family = BeautifulSoup(fund_family_line)
    soup_class = BeautifulSoup(fund_class_line)

    heading = soup_name.h1.get_text().strip(' SET SMS ALERT')
    family = soup_family.p.span.get_text() if fund_family_line else fund_family_line
    Class = soup_class.p.span.get_text() if fund_class_line else fund_class_line
    
    print 'family, class', family, Class

    heading_keywords = set([kw.lower() for kw in heading.split(' ') if kw not in ['-']])

    if '(g)' in heading:
        heading_keywords.add('growth')
    return {'keywords': heading_keywords, 'family': family, 'class': Class}

shortcut_map = {'(g)': 'growth plan',
                'fpo': 'fixed pricing option',
                '(i)': 'india',
                'sl': 'sunlife',
                'inst': 'institutional plan',
                'ip': 'institutional plan',
                'rp': 'retail plan',
                'growth': 'growth plan', 
                'direct': 'direct plan',
                }

def fill_all_funds():
    """Fills all fund's all data except fund family and fund class."""
    categ_urls = get_all_category_urls()
    #categ = categ_urls.pop()
    #print categ
    for categ in categ_urls:
        funds = get_all_funds_for_category(categ)
        for fund in funds:
            db.session.add(models.Fund(fund, funds[fund]['name'], '', '', funds[fund]['url']))
            for keyword in funds[fund]['keywords']:
                db.session.add(models.Keyword(fund, keyword))
    db.session.commit()

fill_all_funds()    
#get_all_keywords_for_fund('http://www.moneycontrol.com/mutual-funds/nav/hdfc-index-sensex-plus-direct/MHD1154')

#funds = get_all_funds_for_category('http://www.moneycontrol.com/mutual-funds/performance-tracker/returns/large-cap.html')
#print len(funds)
#    fund_category_urls.[ url.a['href']  for url in ls if url.a['href'].startswith('/mutual-funds/performance-tracker/returns/')]     
# for fund in fund_category_urls:
#     print fund


