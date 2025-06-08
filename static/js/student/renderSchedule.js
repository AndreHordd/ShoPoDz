export function renderSchedule(data) {
    const days = ['','Пн','Вт','Ср','Чт','Пт','Сб','Нд'];
    inject('schedule', tableMarkup(
        ['День','Час','Предмет','Кабінет','Вчитель'],
        data.map(l => [
            days[l.day],
            `${l.start}-${l.end}`,
            l.subject,
            l.room,
            l.teacher
        ])
    ));
}
