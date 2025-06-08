export function renderHomework(data) {
    inject('homework', tableMarkup(
        ['Предмет','Опис','Дедлайн','Оцінка','Коментар','Дія'],
        data.map(h => {
            const dl = new Date(h.deadline);
            const active = Date.now() < dl.getTime();
            const btn = active
                ? (h.done
                    ? `<button class="btn btn-undo hw-toggle-btn" data-id="${h.homework_id}">Скасувати</button>`
                    : `<button class="btn btn-done hw-toggle-btn" data-id="${h.homework_id}">Готово</button>`)
                : (h.done ? '✅' : '—');
            return [
                h.subject,
                h.description,
                dl.toLocaleString(),
                h.grade ?? '',
                h.comment ?? '',
                btn
            ];
        })
    ));
}
