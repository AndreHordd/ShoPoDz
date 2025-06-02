function showModal(html) {
    const modal = document.getElementById('modal');
    modal.innerHTML = `<div class="modal-content">${html}<br><button onclick="closeModal()">Закрити</button></div>`;
    modal.style.display = "flex";
}
function closeModal() {
    document.getElementById('modal').style.display = "none";
}

function viewDiary() {
    showModal('<h3>Оцінки, домашні завдання та відвідуваність</h3><div>...Щоденник дитини...</div>');
}
function markAsRead() {
    showModal('<h3>Підписано!</h3><p>Ви позначили, що переглянули щоденник дитини.</p>');
}
function viewMessages() {
    showModal('<h3>Повідомлення від учителів</h3><div>...список повідомлень...</div>');
}
function replyMessage() {
    showModal('<h3>Відповідь учителю</h3><form>...форма для відповіді...</form>');
}
function viewSchedule() {
    showModal('<h3>Розклад дитини</h3><div>...таблиця розкладу...</div>');
}
function viewAnnouncements() {
    showModal('<h3>Загальношкільні оголошення</h3><div>...оголошення...</div>');
}
