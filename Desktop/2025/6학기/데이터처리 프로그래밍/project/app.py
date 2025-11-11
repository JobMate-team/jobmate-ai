# chatbot.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL 
import MySQLdb.cursors


from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI



# 파일을 저장할 디렉토리 설정
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


mysql = MySQL(app)


#app = Flask(__name__)
#CORS(app)  # React랑 연동 시 필요

client = OpenAI(api_key="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")  # 🔑 본인 키 입력

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # OpenAI API 호출
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 투자 자문을 돕는 AI 챗봇이야."},
            {"role": "user", "content": user_message}
        ]
    )

    bot_reply = completion.choices[0].message.content.strip()
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True, port=5001)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 투자 자문을 돕는 AI 챗봇이야."},
            {"role": "user", "content": user_message}
        ]
    )

    bot_reply = completion.choices[0].message.content.strip()
    return jsonify({"reply": bot_reply})
