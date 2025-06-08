export function renderTeachers(data) {
    if (!data.length) {
        inject('teachers', '<p class="no-data">Немає даних.</p>');
        return;
    }
    inject('teachers', `
        <table class="single-table">
            <tr><th>Викладач</th><th>Предмет(и)</th><th>Кабінет(и)</th></tr>
            ${data.map(t => `
                <tr>
                    <td>${t.last_name} ${t.first_name}</td>
                    <td>${t.subjects.join(', ')}</td>
                    <td>${t.rooms.join(', ')}</td>
                </tr>`).join('')}
        </table>
    `);
}
