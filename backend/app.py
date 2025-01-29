from flask import Flask, render_template, request, jsonify
from openai import OpenAI

client = OpenAI(api_key="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")

app = Flask(__name__)

# Налаштування API-ключа OpenAI

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
        return jsonify({"email_text": email_text})

    except Exception as e:
        print(f"Помилка генерації листа: {e}")  # Лог помилки
        return jsonify({"error": "Не вдалося згенерувати текст. Деталі: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
