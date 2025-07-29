"""
RPGshare.board
主榜单接口
"""

from .utils import fetch_board_data, clean_bindata

# 通用请求参数
_url = 'https://weixin.citicsinfo.com/reqxml?action=1230'
_headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://weixin.citicsinfo.com/',
    'Content-Type': 'application/x-www-form-urlencoded',
}

def get_top_gainers(count=20):
    """获取涨幅榜数据"""
    data = {
        'c.funcno': '21000',
        'c.version': '1',
        'c.sort': '1',
        'c.order': '0',
        'c.type': '0:2:9:18',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.field': '1:2:22:23:24:3:8:16:21:31',
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(data, _url, _headers, clean_func=clean_bindata)

def get_top_losers(count=20):
    """获取跌幅榜数据"""
    data = {
        'c.funcno': '21000',
        'c.version': '1',
        'c.sort': '1',
        'c.order': '1',
        'c.type': '0:2:9:18',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.field': '1:2:22:23:24:3:8:16:21:31',
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(data, _url, _headers, clean_func=clean_bindata)

def get_money_inflow(count=20):
    """获取资金流入榜"""
    data = {
        'c.funcno': '70001',
        'c.version': '1',
        'c.sortType': '0',
        'c.ioType': '1',
        'c.trading_day': '0',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(
        data, _url, _headers,
        sort_key=lambda x: float(x['net_money_flow']), sort_reverse=True
    )

def get_money_outflow(count=20):
    """获取资金流出榜"""
    data = {
        'c.funcno': '70001',
        'c.version': '1',
        'c.sortType': '0',
        'c.ioType': '0',
        'c.trading_day': '0',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(
        data, _url, _headers,
        sort_key=lambda x: float(x['net_money_flow'])
    )

def get_turnover_rate(count=20):
    """获取换手率榜"""
    data = {
        'c.funcno': '21000',
        'c.version': '1',
        'c.sort': '8',
        'c.order': '0',
        'c.type': '0:2:9:18',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.from': 'H5',
        'c.field': '1:2:22:23:24:3:8:16:21:31',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    field_mapping = [
        '涨跌额', '最新价', '名称', '市场', '代码', '涨跌幅', '换手率', '振幅', '等级', '总市值'
    ]
    return fetch_board_data(
        data, _url, _headers,
        field_mapping=field_mapping,
        sort_key=lambda x: float(x['换手率']), sort_reverse=True
    )

def get_leading_sectors(count=20):
    """获取领涨板块榜"""
    data = {
        'c.funcno': '30004',
        'c.version': '1',
        'c.sort': '1',
        'c.order': '0',
        'c.bkType': '1',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.field': '22:24:2:10:11:9:12:14:6:34:35:21:3:1:38:39:40',
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(data, _url, _headers, clean_func=clean_bindata)

def get_industry_sectors(count=20):
    """获取行业板块榜"""
    data = {
        'c.funcno': '30004',
        'c.version': '1',
        'c.sort': '1',
        'c.order': '0',
        'c.bkType': '1',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.field': '22:24:2:10:11:9:12:14:6:34:35:21:3:1:38:39:40',
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(data, _url, _headers, clean_func=clean_bindata)

def get_concept_sectors(count=20):
    """获取概念板块榜"""
    data = {
        'c.funcno': '30004',
        'c.version': '1',
        'c.sort': '1',
        'c.order': '0',
        'c.bkType': '2',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.field': '22:24:2:10:11:9:12:14:6:34:35:21:3:1:38:39:40',
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(data, _url, _headers, clean_func=clean_bindata)

def get_region_sectors(count=20):
    """获取地域板块榜"""
    data = {
        'c.funcno': '30004',
        'c.version': '1',
        'c.sort': '1',
        'c.order': '0',
        'c.bkType': '3',
        'c.curPage': '1',
        'c.rowOfPage': str(count),
        'c.field': '22:24:2:10:11:9:12:14:6:34:35:21:3:1:38:39:40',
        'c.from': 'H5',
        'c.tfrom': 'ANDROID',
        'c.CHANNEL': '',
    }
    return fetch_board_data(data, _url, _headers, clean_func=clean_bindata) 