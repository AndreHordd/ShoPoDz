// Модальне вікно для форм (дуже спрощено)
function showModal(html) {
    const modal = document.getElementById('modal');
    modal.innerHTML = `<div class="modal-content">${html}<br><button onclick="closeModal()">Закрити</button></div>`;
    modal.style.display = "flex";
}
function closeModal() {
    document.getElementById('modal').style.display = "none";
}

// CRUD для розкладів (шаблон)
function showScheduleForm(type) {
    let title = "";
    if (type === 'add') title = "Створити розклад";
    if (type === 'edit') title = "Редагувати розклад";
    if (type === 'delete') title = "Видалити розклад";
    showModal(`<h3>${title}</h3><form>...форма тут...</form>`);
}
function showAssignTeacherForm() {
    showModal("<h3>Призначити викладача на урок</h3><form>...форма тут...</form>");
}
function showAssignRoomForm() {
    showModal("<h3>Розподіл занять по кабінетах</h3><form>...форма тут...</form>");
}
function viewAllSchedules() {
    showModal("<h3>Весь розклад</h3><div>...таблиця розкладу...</div>");
}

// CRUD для користувачів
function showUserForm(type) {
    let title = "";
    if (type === 'add') title = "Додати користувача";
    if (type === 'edit') title = "Редагувати користувача";
    if (type === 'delete') title = "Видалити користувача";
    showModal(`<h3>${title}</h3><form>...форма тут...</form>`);
}

// CRUD для класів
function showClassForm(type) {
    let title = "";
    if (type === 'add') title = "Додати клас";
    if (type === 'edit') title = "Редагувати клас";
    if (type === 'delete') title = "Видалити клас";
    showModal(`<h3>${title}</h3><form>...форма тут...</form>`);
}

// CRUD для предметів
function showSubjectForm(type) {
    let title = "";
    if (type === 'add') title = "Додати предмет";
    if (type === 'edit') title = "Редагувати предмет";
    if (type === 'delete') title = "Видалити предмет";
    showModal(`<h3>${title}</h3><form>...форма тут...</form>`);
}

// Оголошення
function showAnnouncementForm() {
    showModal("<h3>Створити оголошення</h3><form>...форма тут...</form>");
}

// Друк / експорт розкладу
function printSchedules(type) {
    if (type === 'pdf') alert("Розклад буде збережено у PDF (імплементація)");
    if (type === 'csv') alert("Розклад буде збережено у CSV (імплементація)");
}
