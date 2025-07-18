from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>🎉 성공! 독서모임 앱이 작동합니다!</h1><p>이제 기능을 추가할 준비가 되었습니다.</p>"

@app.route('/test')
def test():
    return "<h1>테스트 성공!</h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port) 