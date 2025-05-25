# main.py
import json
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

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

@app.route('/')
def index():
    """首页显示API信息"""
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>微博热搜 API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .endpoint { background: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace; margin: 10px 0; }
            .test-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .test-btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 微博热搜 API</h1>
            <h3>API 接口</h3>
            <div class="endpoint">GET /api</div>
            <p>返回 JSON 格式的微博热搜数据</p>
            <button class="test-btn" onclick="window.open('/api', '_blank')">测试 API</button>
        </div>
    </body>
    </html>
    '''

@app.route('/api')
def api():
    """API接口"""
    data = get_data()
    return jsonify(data)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)