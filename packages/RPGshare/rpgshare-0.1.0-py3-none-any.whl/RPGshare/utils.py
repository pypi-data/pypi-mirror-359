"""
RPGshare.utils
通用工具函数
"""

import requests
import json
import re
from .exceptions import RPGshareException

def fetch_board_data(data, url, headers, clean_func=None, field_mapping=None, sort_key=None, sort_reverse=False):
    """
    通用榜单数据请求与处理
    - data: POST请求体参数
    - url, headers: 请求参数
    - clean_func: 可选，BINDATA清洗函数
    - field_mapping: 可选，字段映射（如换手率榜）
    - sort_key: 可选，排序key（如资金流入/流出）
    - sort_reverse: 排序顺序
    """
    try:
        resp = requests.post(url, headers=headers, data=data)
        result_json = resp.json()
        bindata_raw = result_json.get('BINDATA')
        if not bindata_raw:
            raise RPGshareException('BINDATA为空')
        if clean_func:
            bindata_raw = clean_func(bindata_raw)
        bindata_dict = json.loads(bindata_raw)
        results = bindata_dict.get('results', [])
        # 字段映射（如换手率榜）
        if field_mapping:
            mapped = []
            for item in results:
                if len(item) != len(field_mapping):
                    continue
                mapped.append(dict(zip(field_mapping, item)))
            results = mapped
        # 排序
        if sort_key:
            results = sorted(results, key=sort_key, reverse=sort_reverse)
        return results
    except Exception as ex:
        raise RPGshareException(f'请求或解析异常: {ex}')

def clean_bindata(bindata_raw):
    """
    修正 BINDATA 字符串：给股票代码和带单位的数值加双引号，保持JSON格式合法
    适用于涨幅榜、跌幅榜、领涨板块
    """
    clean_data = re.sub(r'[\x00-\x1f]+', '', bindata_raw)
    # 给包含单位的数值加上双引号（如：468.19万手 -> "468.19万手"）
    clean_data = re.sub(r'(?<!")(+\.?\d*(?:万手|亿手|手))(?!")', r'"\1"', clean_data)
    # 合并市场代码和股票代码，并加双引号
    clean_data = re.sub(r'"(SZ|SH)"\s*,\s*"(\d{6})"', r'"\1.\2"', clean_data)
    clean_data = re.sub(r'null\s*,\s*"(\d{6})"', r'"\1"', clean_data)
    clean_data = re.sub(r'(?<!["\w])(\d{6})(?!["\w])', r'"\1"', clean_data)
    clean_data = re.sub(r'(?<!["\w])(SZ|SH)(?!["\w])', r'"\1"', clean_data)
    return clean_data 