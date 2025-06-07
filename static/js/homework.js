document.addEventListener('DOMContentLoaded', function() {
    // Слухаємо кнопки тижня
    document.getElementById('prev-week').onclick = function() {
        // змінити URL із ?week_start=yyyy-mm-dd
    };
    document.getElementById('next-week').onclick = function() {
        // аналогічно
    };

    // Редагування та видалення дз
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.onclick = function() {
            // відкрити форму для редагування (можна modal, prompt, etc)
        };
    });
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.onclick = function() {
            // підтвердити і відправити запит DELETE
        };
    });
});
