document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('clientForm');
    const resultContainer = document.getElementById('resultContainer');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value.trim();
        });

        try {
            const response = await fetch('/generate-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(jsonData),
            });

            if (!response.ok) throw new Error('Сервер повернув помилку.');

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            resultContainer.textContent = data.email_text;
            resultContainer.style.display = 'block';
            setTimeout(() => {
                resultContainer.style.opacity = '1';
            }, 50);
        } catch (error) {
            resultContainer.textContent = `❌ Помилка: ${error.message}`;
            resultContainer.style.display = 'block';
            setTimeout(() => {
                resultContainer.style.opacity = '1';
            }, 50);
        }
    });
});
