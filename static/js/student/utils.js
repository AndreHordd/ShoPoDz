export function inject(id, html) {
    document.getElementById(id).innerHTML = html || '<p class="no-data">Немає даних.</p>';
}

export function getVal(id, def) {
    const el = document.getElementById(id);
    return el ? el.value : def;
}

export function tableMarkup(head, rows) {
    if (!rows.length) return '<p class="no-data">Немає даних.</p>';
    return `
        <table class="single-table">
            <tr>${head.map(h => `<th>${h}</th>`).join('')}</tr>
            ${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}
        </table>`;
}
