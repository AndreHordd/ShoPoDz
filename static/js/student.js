function showModal(html) {
    const modal = document.getElementById('modal');
    modal.innerHTML = `<div class="modal-content">${html}<br><button onclick="closeModal()">Закрити</button></div>`;
    modal.style.display = "flex";
}
function closeModal() {
    document.getElementById('modal').style.display = "none";
}

function viewSchedule() {
    showModal('<h3>Мій розклад на тиждень</h3><div>...таблиця розкладу...</div>');
}

function viewHomework() {
    showModal(`
        <h3>Домашні завдання та оцінки</h3>
        <table style="width:100%; text-align:left;">
            <tr><th>Предмет</th><th>Завдання</th><th>Оцінка</th><th>Коментар учителя</th></tr>
            <tr><td>Математика</td><td>Вправи 25–28</td><td>10</td><td>Молодець!</td></tr>
            <tr><td>Українська мова</td><td>Твір про літо</td><td>8</td><td>Покращити структуру</td></tr>
            <tr><td>Фізика</td><td>Параграф 4 + тести</td><td>–</td><td>Очікую на перевірку</td></tr>
        </table>
        <br>
        <button onclick="markHomeworkDone()">Відмітити виконання</button>
    `);
}

function markHomeworkDone() {
    showModal('<h3>Відмітити виконання домашнього завдання</h3><form>...форма...</form>');
}

function viewTeachers() {
    showModal('<h3>Мої вчителі та кабінети</h3><div>...список вчителів...</div>');
}

function viewAttendance() {
    showModal('<h3>Моя відвідуваність</h3><div>...історія відвідуваності...</div>');
}

function viewAnnouncements() {
    showModal('<h3>Загальношкільні оголошення</h3><div>...оголошення...</div>');
}
