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
        
        jyzy = {
            '电影': '影',
            '剧集': '剧',
            '综艺': '综',
            '音乐': '音'
        }
        
        for data_item in data_json:
            hot = ''
            # 如果是广告，则不添加
            if 'is_ad' in data_item:
                continue
            if 'flag_desc' in data_item:
                hot = jyzy.get(data_item['flag_desc'], '')
            if 'is_boom' in data_item:
                hot = '爆'
            if 'is_hot' in data_item:
                hot = '热'
            if 'is_fei' in data_item:
                hot = '沸'
            if 'is_new' in data_item:
                hot = '新'
            
            dic = {
                'title': data_item.get('note', ''),
                'url': 'https://s.weibo.com/weibo?q=%23' + data_item.get('word', '') + '%23',
                'num': data_item.get('num', 0),
                'hot': hot
            }
            data.append(dic)
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        return [{'error': f'Failed to fetch data: {str(e)}'}]
    
    return data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = get_data()
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
        return
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return