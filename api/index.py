# api/index.py
import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

def get_data():
    """微博热搜
    Returns:
        list: [{title: 标题, url: 地址, num: 热度数值, hot: 热搜等级}]
    """
    data = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get("https://weibo.com/ajax/side/hotSearch", headers=headers, timeout=10)
        response.raise_for_status()
        
        data_json = response.json()['data']['realtime']
        
        # 扩展的热搜等级映射
        jyzy = {
            '电影': '影',
            '剧集': '剧',
            '综艺': '综',
            '音乐': '音',
            '游戏': '游',
            '体育': '体',
            '财经': '财'
        }
        
        for data_item in data_json:
            hot = ''
            # 如果是广告，则不添加
            if 'is_ad' in data_item and data_item['is_ad']:
                continue
            
            # 调试：打印每个条目的所有字段（可选，用于调试）
            # print(f"Debug item keys: {data_item.keys()}")
            
            # 按优先级检查各种热搜标识
            # 最高优先级：沸腾
            if data_item.get('is_fei') or data_item.get('icon_desc') == '沸' or data_item.get('icon') == 'fei':
                hot = '沸'
            # 次高优先级：爆炸
            elif data_item.get('is_boom') or data_item.get('icon_desc') == '爆' or data_item.get('icon') == 'boom':
                hot = '爆'
            # 第三优先级：热门
            elif data_item.get('is_hot') or data_item.get('icon_desc') == '热' or data_item.get('icon') == 'hot':
                hot = '热'
            # 第四优先级：新
            elif data_item.get('is_new') or data_item.get('icon_desc') == '新' or data_item.get('icon') == 'new':
                hot = '新'
            # 检查flag_desc字段（分类标识）
            elif 'flag_desc' in data_item and data_item['flag_desc']:
                hot = jyzy.get(data_item['flag_desc'], data_item['flag_desc'][:1])
            # 检查icon_desc字段（可能包含其他标识）
            elif 'icon_desc' in data_item and data_item['icon_desc']:
                icon_desc = data_item['icon_desc']
                hot = jyzy.get(icon_desc, icon_desc[:1] if len(icon_desc) > 0 else '')
            # 检查category字段
            elif 'category' in data_item and data_item['category']:
                category = data_item['category']
                hot = jyzy.get(category, category[:1] if len(category) > 0 else '')
            # 检查其他可能的标识字段
            elif 'label_name' in data_item and data_item['label_name']:
                label = data_item['label_name']
                hot = jyzy.get(label, label[:1] if len(label) > 0 else '')
            # 根据热度数值判断（如果没有其他标识）
            elif data_item.get('num', 0) > 1000000:  # 超过100万热度
                hot = '热'
            
            # 构建URL，处理可能的编码问题
            word = data_item.get('word', '')
            if word:
                # URL编码处理
                import urllib.parse
                encoded_word = urllib.parse.quote(word)
                url = f'https://s.weibo.com/weibo?q=%23{encoded_word}%23'
            else:
                url = 'https://weibo.com'
            
            dic = {
                'title': data_item.get('note', '') or data_item.get('word', ''),
                'url': url,
                'num': data_item.get('num', 0),
                'hot': hot,
                # 可选：添加原始数据用于调试
                # 'raw_data': {k: v for k, v in data_item.items() if k in ['is_hot', 'is_new', 'is_fei', 'is_boom', 'flag_desc', 'icon_desc', 'category', 'label_name']}
            }
            data.append(dic)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        # 返回更详细的错误信息
        return [{'error': f'Failed to fetch data: {str(e)}', 'type': 'fetch_error'}]
    
    return data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 解析URL参数，支持调试模式
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            debug_mode = 'debug' in query_params
            
            data = get_data()
            
            # 如果是调试模式，添加更多信息
            if debug_mode and data and 'error' not in data[0]:
                # 可以在这里添加一些统计信息
                hot_stats = {}
                for item in data:
                    hot_level = item.get('hot', '无')
                    hot_stats[hot_level] = hot_stats.get(hot_level, 0) + 1
                
                response_data = {
                    'data': data,
                    'stats': hot_stats,
                    'total': len(data),
                    'debug': True
                }
            else:
                response_data = data
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            error_response = {'error': str(e), 'type': 'server_error'}
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        return
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return