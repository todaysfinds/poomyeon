#!/usr/bin/env python3
import os
from flask import Flask

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>독서모임 성공!</title></head>
    <body style='font-family: Arial; text-align: center; padding: 50px;'>
        <h1 style='color: green;'>🎉 드디어 성공!</h1>
        <h2>독서모임 앱이 정상 작동합니다!</h2>
        <p>이제 기능을 하나씩 추가할 수 있습니다.</p>
        <a href='/test' style='color: blue;'>테스트 페이지</a>
    </body>
    </html>
    """

@app.route('/test')
def test():
    return """
    <html>
    <body style='font-family: Arial; text-align: center; padding: 50px;'>
        <h1 style='color: blue;'>✅ 테스트 성공!</h1>
        <p>모든 라우트가 정상 작동합니다.</p>
        <a href='/' style='color: green;'>홈으로 돌아가기</a>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "ok", "message": "Server is running"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 