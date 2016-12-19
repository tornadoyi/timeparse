# -*- coding: utf-8 -*-
import datetime
class wordtype():
    unknown = 0
    digit = 1
    unit = 2
    relation = 3
    season = 4
    holiday = 5
    quantity = 6
    direct = 7
    degree = 8
    special_hour = 9
    calendar = 10
    lunar_month = 11
    lunar_day = 12
    quarterly = 13




# time unit description of yMdhms
class unit():
    year = 0
    month = 1
    day = 2
    hour = 3
    minute = 4
    second = 5
    week = 1.5
    quarter = 3.5

# relation
class relation():
    coo = 1
    span = 2
    start = 3



# calendar type
class calendar():
    solar = 1
    lunar = 2


# unit span
time_unit_range = {
    unit.year: (datetime.MINYEAR, datetime.MAXYEAR),
    unit.month: (1, 12),
    unit.day: (1, 31),
    unit.hour: (0, 23),
    unit.minute: (0, 59),
    unit.second: (0, 59),
    unit.week: (1, 4),
    unit.quarter: (0, 3),
}

# unit string
time_unit_desc = {
    unit.year: 'y',
    unit.month: 'm',
    unit.day: 'd',
    unit.hour: 'H',
    unit.minute: 'M',
    unit.second: 'S',
    unit.week: 'w',
    unit.quarter: 'q',
}

# time unit converter
time_unit_convert = {
    unit.year: 12 * 30 * 24 * 60 * 60,
    unit.month: 30 * 24 * 60 * 60,
    unit.day: 24 * 60 * 60,
    unit.hour: 60 * 60,
    unit.minute: 60,
    unit.second: 1,
    unit.week: 7 * 24 * 60 * 60,
    unit.quarter: 15 * 60,
}



# fill (direct, min/max)
def time_tuple(y = None, M = None, d = None, h = None , m = None, s = None, fill = (0, 0)):
    v = [y, M, d, h, m, s]
    if fill[0] == 0 or fill[1] == 0: return v
    (st, delta) = fill[0] > 0 and (len(v)-1, -1) or (0, 1)
    i = st
    while i >= 0 and i < len(v):
        if v[i] != None: break
        v[i] = fill[1] > 0 and time_unit_range[i][1] or     time_unit_range[i][0]
        i += delta
    return tuple(v)

def tuple_lmin(y = None, M = None, d = None, h = None , m = None, s = None): return time_tuple(y, M, d, h, m, s, (-1, -1))
def tuple_lmax(y = None, M = None, d = None, h = None , m = None, s = None): return time_tuple(y, M, d, h, m, s, (-1, 1))
def tuple_rmin(y = None, M = None, d = None, h = None , m = None, s = None): return time_tuple(y, M, d, h, m, s, (1, -1))
def tuple_rmax(y = None, M = None, d = None, h = None , m = None, s = None): return time_tuple(y, M, d, h, m, s, (1, 1))



word_class_dict = {
    wordtype.digit: {
        u"半": 0.5,
        u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
        u"两":2, u"俩": 2,
        u'十': 10,
        u'百': 100, u'千': 1000, u'万': 10000,
        u'0': 0, u'1': 1, u'2': 2, u'3': 3, u'4': 4, u'5': 5, u'6': 6, u'7': 7, u'8': 8, u'9': 9,
        u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4, u'５': 5, u'６': 6, u'７': 7, u'８': 8, u'９': 9,
        u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4, u'伍': 5, u'陆': 6, u'柒': 7, u'捌': 8, u'玖': 9, u'拾': 10,
        u'佰': 100,
        u'仟': 1000, u'萬': 10000,
        u'亿': 100000000
    },

    wordtype.unit: {
        u"年": unit.year,
        u"月": unit.month,
        u"日": unit.day, u"天": unit.day, u"号": unit.day,
        u"时": unit.hour, u"h": unit.hour, u"点": unit.hour, u"小时": unit.hour,
        u"分": unit.minute,
        u"秒": unit.second,
        u"周": unit.week, u"星期": unit.week, u"礼拜": unit.week,
        u"刻": unit.quarter,
    },

    wordtype.relation:{
        u"到": relation.span, u"至": relation.span, u"to": relation.span, u"-": relation.span, u"~": relation.span,
        u"和": relation.coo, u"以及": relation.coo, u"跟": relation.coo,
        u"起": relation.start, u"持续": relation.start, u"开始": relation.start,
    },

    wordtype.season:{
        u"春": (1, 3), u"春天": (1, 3), u"春季": (1, 3),
        u"夏": (4, 6), u"夏天": (4, 6), u"夏季": (4, 6),
        u"秋": (7, 9), u"秋天": (7, 9), u"秋季": (7, 9),
        u"冬": (10, 12), u"冬天": (10, 12), u"冬季": (10, 12),
    },

    wordtype.quarterly:{
        u"季度": None,
        u"季": None,
    },

    wordtype.quantity:{
        u"个": 1,
    },


    # (relative, unit, front-time, back-time)
    # relative 0: currrent -1: previous unit
    wordtype.direct:{
        u"今": (0, 0, None, None), u"本": (0, 0, None, None), u"当": (0, 0, None, None),
        u"去": (0, -1, None, None), u"上": (0, -1, (-1, 0), None), u"昨": (0, -1, None, None),
        u"前": (0, -2, (-1, 0), (float('-inf'), -1)), u"以前": (0, None, None, (float('-inf'), -1)),
        u"明": (0, 1, None, None), u"下": (0, 1, (0, 1), None),
        u"后": (0, 2, (0, 1), (1, float('inf'))), u"以后": (0, None, None, (1, float('inf'))),
        u"第": (-1, None, 1, None),
        u"倒数第": (-1, None, -1, None), u"后数第": (-1, None, -1, None),
        u"来": (0, None, None, (-1, 0)),
        u"内": (0, None, None, (-1, 1)), u"近": (0, None, (-1, 1), None),
    },

    wordtype.degree: {
        u"大": 1,
        u"上" : 1,
        u"下" : 1,
    },

    # (is solar, month, day, duration)
    wordtype.holiday:{
        u"国庆": (calendar.solar, 10, 1, 7),
        u"愚人": (calendar.solar, 4, 1, 1),
        u"元旦": (calendar.solar, 1, 1, 1),
        u"新年": (calendar.solar, 1, 1, 1),
        u"情人节": (calendar.solar, 2, 14, 1),
        u"清明节": (calendar.solar, 4, 4, 3),
        u"劳动节": (calendar.solar, 5, 1, 3),
        u"五一": (calendar.solar, 5, 1, 3),
        u"端午节": (calendar.lunar, 5, 5, 3),
        u"元宵节": (calendar.lunar, 1, 15, 1),
        u"正月十五": (calendar.lunar, 1, 15, 1),
        u"七夕": (calendar.lunar, 7, 7, 1),
        u"腊八": (calendar.lunar, 12, 8, 1),
        u"平安夜": (calendar.solar, 12, 24, 1),
        u"圣诞节": (calendar.solar, 12, 25, 1),
        u"万圣节": (calendar.solar, 10, 31, 1),
        u"中秋": (calendar.lunar, 8, 15, 3),
        u"春节": (calendar.lunar, 1, 1, 7),
        u"过年": (calendar.lunar, 1, 1, 7),
        u"大年三十": (calendar.lunar, 12, -1, 1),
        u"大年30": (calendar.lunar, 12, -1, 1),
        u"年三十": (calendar.lunar, 12, -1, 1),
        u"除夕": (calendar.lunar, 12, -1, 1),
    },


    # (start, end, convert)
    wordtype.special_hour:{
        u"am": (tuple_rmin(h=0), tuple_rmax(h=11), None),
        u"早": (tuple_rmin(h=4), tuple_rmax(h=10), None),
        u"早上": (tuple_rmin(h=4), tuple_rmax(h=10), None),
        u"上午": (tuple_rmin(h=8), tuple_rmax(h=11), None),
        u"白天": (tuple_rmin(h=6), tuple_rmax(h=17), None),

        u"中午": (tuple_rmin(h=11), tuple_rmax(h=14), lambda h: (h+12,False) if 0<=h and h<=6 else (h,False)),

        u"pm": (tuple_rmin(h=12), tuple_rmax(h=23), lambda h: (h+12,False) if h<=12 else (h,False)),
        u"下午": (tuple_rmin(h=13), tuple_rmax(h=18), lambda h: (h+12,False) if h<=12 else (h,False)),

        u"晚": (tuple_rmin(h=18), tuple_rmax(h=23), lambda h: (h,True) if 0<=h and h<=5 else (h+12,False) if 6<=h and h<=12 else (h,False)),
        u"晚上": (tuple_rmin(h=18), tuple_rmax(h=23), lambda h: (h,True) if 0<=h and h<=5 else (h+12,False) if 6<=h and h<=12 else (h,False)),
        u"傍晚": (tuple_rmin(h=18), tuple_rmax(h=23), lambda h: (h,True) if 0<=h and h<=5 else (h+12,False) if 6<=h and h<=12 else (h,False)),

        u"夜": (tuple_rmin(h=0), tuple_rmax(h=3), lambda h: (h,True) if 0<=h and h<=5 else (h+12,False) if 6<=h and h<=12 else (h,False)),

        u"凌晨": (tuple_rmin(h=0), tuple_rmax(h=6), None),

    },

    wordtype.calendar:{
        u"阳历": calendar.solar, u"新历": calendar.solar,
        u"公历": calendar.solar, u"太阳历": calendar.solar,
        u"农历": calendar.lunar, u"阴历": calendar.lunar,
        u"旧历": calendar.lunar, u"夏历": calendar.lunar,
        u"殷历": calendar.lunar, u"黄历": calendar.lunar,
    },

    wordtype.lunar_month:{
        u"大年":1, u"正月":1, u"端月":1, u"征月":1, u"开岁":1, u"华岁":1, u"早春":1, u"孟春":1, u"新正":1,
        u"命月":2, u"如月":2, u"丽月":2, u"杏月":2, u"酣香":2, u"仲春":2,
        u"蚕月":3, u"桃月":3, u"桐月":3, u"季春":3, u"晓春":3, u"鸢时":3, u"桃良":3, u"樱笋时":3,
        u"余月":4, u"阴月":4, u"梅月":4, u"清和月":4, u"初夏":4, u"孟夏":4, u"正阳":4, u"朱明":4,
        u"皋月":5, u"榴月":5, u"蒲月":5, u"仲夏":5, u"郁蒸":5, u"天中":5,
        u"且月":6, u"焦月":6, u"荷月":6, u"暑月":6, u"伏月":6, u"精阳":6, u"季夏":6,
        u"相月":7, u"兰月":7, u"凉月":7, u"瓜月":7, u"巧月":7, u"孟秋":7, u"初秋":7, u"早秋":7,
        u"壮月":8, u"桂月":8, u"仲秋":8, u"正秋":8, u"仲商":8, #u"中秋":8,
        u"玄月":9, u"菊月":9, u"青女月":9, u"季秋":9, u"穷秋":9, u"抄秋":9,
        u"良月":10, u"正阴月":10, u"小阳春":10, u"初冬":10, u"开冬":10, u"孟冬":10,
        u"冬月":11, u"幸月":11, u"畅月":11, u"仲冬":11,
        u"涂月":12, u"蜡月":12, u"腊月":12, u"季冬":12, u"暮冬":12, u"残冬":12, u"末冬":12, u"嘉平月":12,
    },

    wordtype.lunar_day: {
        u"初": 0,
    }
}

class special():
    day = u"天"
    half = u"半"
    month = u"月"
    year = u"年"
    week_digit = {u"日": 7, u"天": 7,}
    lunar_desc = []
    lunar_unit_day  = u"初"


class Word(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            orig = super(Word, cls)
            cls.__instance = orig.__new__(cls, *args, **kwargs)
        return  cls.__instance

    def __init__(self):
        global word_class_dict

        # word dict
        self._word_dict = {}
        for (t, dict) in word_class_dict.items():
            for (k, v) in dict.items():
                array = self._word_dict.get(k, None)
                if array == None:
                    array = []
                    self._word_dict[k] = array
                array.append((t, v))


        # reversed word dict
        self._reverse_word_dict = {k: {} for (k,v) in word_class_dict.items()}
        for (t,dict) in word_class_dict.items():
            rdict = self._reverse_word_dict[t]
            for (k,v) in dict.items():
                array = rdict.get(v, None)
                if array == None:
                    array = []
                    rdict[v] = array
                array.append(k)

    def property(self, word, wordtype):
        for v in self.properties(word):
            if v[0] != wordtype: continue
            return v[1]
        return None

    def properties(self, word):
        return self._word_dict.get(word, [])

    def texts(self, wordtype, property):
        dict = self._reverse_word_dict.get(wordtype, None)
        if dict == None: raise Exception("unsupport word type {0}".format(wordtype))
        return dict.get(property, [])

    def split_texts(self, wordtype, property = None, delimiter=None):
        if not delimiter: delimiter = "|"
        strs = []
        dict = self._reverse_word_dict.get(wordtype, None)
        if dict == None: raise Exception("unsupport word type {0}".format(wordtype))
        if property == None:
            for (prop, keys) in dict.items():
                for k in keys:
                    strs.append(k)
        else:
            keys = dict.get(property, [])
            for k in keys:
                strs.append(k)
        # sort
        strs.sort(lambda x, y: 1 if len(x)<len(y) else -1 if len(x)>len(y) else 0 )
        str = u""
        for s in strs:
            if len(str) > 0: str += delimiter
            str += s
        return str

word = Word()
property = word.property
properties = word.properties
texts = word.texts
split_texts = word.split_texts