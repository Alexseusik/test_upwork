from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///history.db")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class EmailHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    last_contact_date = db.Column(db.DateTime, nullable=False)
    company = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255), nullable=False)
    employees = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(50), nullable=False)
    competitors = db.Column(db.Text, nullable=True)
    chat_history = db.Column(db.Text, nullable=True)
    email_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<EmailHistory {self.id} - {self.first_name} {self.last_name} ({self.company})>"

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.json

        # Формування запиту для ШІ
        prompt = f"""Write down a follow up email in businesslike style using this type of information 
        Name: {data['first_name']}
        Surname: {data['last_name']}
        Country: {data['country']}
        City: {data['city']}
        Last contact date: {data['last_contact']}
        Company name: {data['company']}
        Company industry: {data['industry']}
        Amount of workers: {data['employees']}
        Email to write to: {data['email']}
        Service expactations: {data['feedback']}
        Client`s language (write email in this language): {data['language']}
        Company competitors: {data['competitors']}
        Previous conversation with manager: {data['chat_history']}
        The letter should base on this information and analyze it. Also do not include a subject for this letter. Make just a body of letter
        Use \"Oleksii Hnybida\" as a writer name"""

        # Виклик OpenAI для генерації тексту
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a professional sales assistant that write businesslike follow up emails for customers"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Шановний пане Колін,  \n\nЯ сподіваюся, що цей лист знаходить Вас у доброму здоров'ї та позитивному настрої. Мені приємно писати Вам від імені компанії, щоб продовжити наше обговорення щодо послуг, які могли б надавати Салону Краси \"Світлана\".  \n\nПісля нашого останнього контакту 28 березня 2023 року, я мав час проаналізувати Ваші вимоги та очікування щодо створення автоматичного бота для підвищення продажів. Ми розуміємо, що автоматизація процесів може значно підвищити ефективність роботи Вашої команди у складі 12 осіб та збільшити конкурентоспроможність Салону у Mykolaiv, Україна.  \n\nЗ огляду на специфіку індустрії краси, наші спеціалісти готові запропонувати рішення, яке ідеально відповідатиме потребам Вашої компанії та сприятиме її зростанню. Наш автоматичний бот може бути інтегрований для управління записами клієнтів, підтримки рекламних кампаній і навіть збору зворотного зв'язку, що дозволить Вашій команді сфокусуватися на інноваціях та покращенні обслуговування клієнтів.  \n\nПрошу Вас підтвердити зручний час для обговорення подальших кроків у цьому напрямку. Ваша зацікавленість у сучасних рішеннях є важливою для нас, і ми впевнені, що наша співпраця принесе Вашій компанії відчутні переваги.  \n\nЩиро дякую за Вашу увагу. Чекаю на Ваш зворотний зв'язок.  \n\nЗ найкращими побажаннями,  \nОлексій Гнибіда"
                        }
                    ]
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=1,
            max_completion_tokens=10000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        email_text = response.choices[0].message.content.replace("\n", "\n")

        new_email = EmailHistory(
            first_name=data['first_name'],
            last_name=data['last_name'],
            country=data['country'],
            city=data['city'],
            last_contact_date=data['last_contact'],
            company=data['company'],
            industry=data['industry'],
            employees=data['employees'],
            email=data['email'],
            feedback=data['feedback'],
            language=data['language'],
            competitors=data['competitors'],
            chat_history=data['chat_history'],
            email_text=email_text
        )

        db.session.add(new_email)
        db.session.commit()

        return jsonify({"email_text": email_text})

    except Exception as e:
        print(f"Помилка генерації листа: {e}")
        return jsonify({"error": "Не вдалося згенерувати текст. Деталі: " + str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
