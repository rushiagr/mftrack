import urllib2
from bs4 import BeautifulSoup

from db import models
from app import db

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
    site = urllib2.urlopen(fund_url).read().split('\n')
    fund_name_line = [line.strip() for line in site if line.find('h1') > -1][0]
#    print fund_name_line
    fund_family = [line.strip() for line in site if line.find('Fund Family') > -1]
#    print 'fund family:', fund_family
    fund_family_line = '' if len(fund_family)==0 else fund_family[0]
    fund_class = [line.strip() for line in site if line.find('Fund Class') > -1]
    fund_class_line = '' if len(fund_class)==0 else fund_class[0]
    soup_name = BeautifulSoup(fund_name_line)
    soup_family = BeautifulSoup(fund_family_line)
    soup_class = BeautifulSoup(fund_class_line)

    heading = soup_name.h1.get_text()
    heading = heading[:-16] # Removing ' SET SMS ALERTS ' at the end
    family = soup_family.p.a.get_text() if fund_family_line else fund_family_line
    Class = soup_class.p.a.get_text() if fund_class_line else fund_class_line
    
    heading_keywords = set([kw.lower() for kw in heading.split(' ') if kw not in ['-']])

    if '(g)' in heading:
        heading_keywords.add('growth')

    return {'keywords': heading_keywords, 'family': family, 'class': Class}

# QUERY TO ADD 'GROWTH' KEYWORD FOR MUTUAL FUNDS FOR WHICH KEYWORD '(G)' IS PRESENT:
# NOTE: query is very slow, IDK why
# insert into keyword  (select id, 'growth' from keyword 
# where keyword.keyword='(g)' and keyword.id not in 
#     (select t1.id from keyword as t1, keyword as t2 
#     where t1.id = t2.id and t1.keyword='(g)' and t2.keyword='growth'));
 
## WARNINGNNNGGGNNGGG!!!! I inserted this erroneous query into DB. Remove all these entries in future :( :(:(:(
# insert into keyword  (select id, 'institutional' from keyword where keyword.keyword='(g)' and keyword.id not in (select t1.id from keyword as t1, keyword as t2 where t1.id = t2.id and t1.keyword='ip' and t2.keyword='institutional'))


shortcut_map = {'(g)': 'growth plan',
                'fpo': 'fixed pricing option',
                '(i)': 'india',
                'sl': 'sunlife',
                'inst': 'institutional plan',
                'ip': 'institutional plan',
                'rp': 'retail plan',
                'growth': 'growth plan', 
                'direct': 'direct plan',
                'ft': 'franklin templeton',
                
                'vpo': 'variable pricing option',
                'usbf': 'ultra short term bond fund',
                'ustbf': 'ultra short term bond fund',
                'ustf': 'ultra short term fund',
                'ultra-short': 'ultra short fund',
                }

def fill_all_funds():
    """Fills all fund's data from fund category page (e.g. Large Cap)."""
    categ_urls = get_all_category_urls()
    for categ in categ_urls:
        funds = get_all_funds_for_category(categ)
        for fund in funds:
            db.session.add(models.Fund(fund, funds[fund]['name'], '', '', funds[fund]['url']))
            for keyword in funds[fund]['keywords']:
                db.session.add(models.Keyword(fund, keyword))
    db.session.commit()

def get_and_insert_detail_from_fund_page(fund_id):
    """Given the fund ID, we will go to the page of that fund, take keywords
    from that fund's name, get the fund's family and class, and update these
    information into the database."""
    fund = models.Fund.query.filter_by(id=fund_id).first()
    fund_url = fund.url
    return_dict = get_all_data_for_fund(fund_url)
    fund.family = return_dict['family']
    fund.Class = return_dict['class']
    db_kw_entries = models.Keyword.query.filter_by(id=fund_id).all()
    db_kws = [entry.keyword for entry in db_kw_entries]
    kws_to_insert = [kw for kw in return_dict['keywords'] if kw not in db_kws]
    print 'inserting keywords', kws_to_insert, 'for fund', fund.name
    for kw in kws_to_insert:
        db.session.add(models.Keyword(fund_id, kw))
    db.session.commit()


def update_unupdated_fund_details():
    """Takes all the funds from FundDataExtracted table for which data is not
    extracted, and updates them."""
    while True:
        fund = models.FundDataExtracted.query.filter_by(is_updated=0).first()
        fund_id = fund.id
        print 'inserting data for fund', fund_id
        get_and_insert_detail_from_fund_page(fund_id)
        fund.is_updated=1
        db.session.commit()

if __name__ == '__main__':
    # Get only primary fund details from 'fund categories' pages
    #fill_all_funds()
    
    # Get fund family, fund category and most importantly, the important
    # keywords for all the funds
    update_unupdated_fund_details()
