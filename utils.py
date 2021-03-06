import datetime

def get_float(val):
    """Converts argument to a float value. Throws error if it cant."""
    if type(val) == float:
        return val
    elif type(val) == int:
        return float(val)
    elif type(val) in [str, unicode]:
        val = val.replace(',', '')
        try:
            return float(val)
        except ValueError:
            raise

def int_date(date):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
              'sep', 'oct', 'nov', 'dec']
    if type(date) in [str, unicode]:
        # Date format '01/01/2014' (DD/MM/YYYY)
        if (len(date) == 10 and date[2] == date[5] and 
                                            date[2] in ['/', '.', '-']):
            return int(date[6:10]+date[3:5]+date[0:2])
        # Date format '01 Jan 2014' or '01-jan-2014'
        elif len(date) == 11 and date[3:6].lower() in months:
            month_int = months.index(date[3:6].lower())+1
            month = ('%2s' % month_int).replace(' ', '0')
            return int(date[7:11]+month+date[0:2])
        else:
            raise BaseException
    elif type(date) == int:
        if date < 20300000 and date > 19500000:
            return date
        else:
            raise BaseException
    elif isinstance(date, datetime.date):
        return (date.year*10000 + date.month*100 + date.day)

def today():
    return int_date(datetime.date.today())

def last_month():
    return int_date(datetime.date.today() - datetime.timedelta(days=30))

def diff_days(date1, date2):
    """Provides the difference between the int dates, in number of days."""
    if date1 < date2:
        date1, date2 = date2, date1
    date_1 = datetime.date(date1/10000, date1/100%100, date1%100)
    date_2 = datetime.date(date2/10000, date2/100%100, date2%100)
    return (date_1 - date_2).days

def prettify_number(num):
    num = float(num)
    num = "%.2f" % num
    int_part, frac_part = tuple(num.split('.'))
    if 5 >= len(int_part) > 3:
        int_part = int_part[:-3] + ',' + int_part[-3:]
    elif 7 >= len(int_part) > 5:
        int_part = int_part[:-5] + ',' + int_part[-5:-3] + ',' + int_part[-3:]
    elif len(int_part) > 7:
        int_part = int_part[:-7] + ',' + int_part[-7:-5] + ',' + \
            int_part[-5:-3] + ',' + int_part[-3:]
    int_part = int_part.replace('-,', '-')
    return int_part + '.' + frac_part

def get_config(filename=None):
    filename = filename or 'mftrack.conf'
    lines = open(filename).readlines()
    return_dict = {}
    for line in lines:
        if line.strip() and not line.strip().startswith('#'):
            key, _meh, val = line.strip().partition('=')
            if val in ['True', 'False']:
                return_dict[key] = bool(val)
                continue
            return_dict[key] = val
    return return_dict

def get_mftrack_config():
    conf = get_config()
    ret = {}
    # TODO: exception handling
    db_uri = conf['db'] + '://' + conf['dbuser'] + ':' + conf['dbpass'] + '@' + conf['dbhost'] + '/' + conf['dbname']
    ret['db_uri'] = db_uri
    ret['secret_key'] = conf['secretkey']
    ret['debug'] = conf['debug']
    ret['host'] = conf['host']
    ret['port'] = int(conf['port'])
    return ret
