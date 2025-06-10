/* ================================================================
   static/js/student.js  — повністю оновлений
   ================================================================ */

/* ================================================================
   1. ІНІЦІАЛІЗАЦІЯ
   ================================================================ */
document.addEventListener('DOMContentLoaded', () => {
    const renderers = {
        schedule:      renderSchedule,
        homework:      renderHomework,
        teachers:      renderTeachers,
        attendance:    renderAttendance,
        announcements: renderAnnouncements,
    };

    /* навігація сайдбаром */
    document.getElementById('side-menu').addEventListener('click', e => {
        const link = e.target.closest('a[data-target]');
        if (!link) return;
        e.preventDefault();
        document.querySelectorAll('#side-menu a[data-target]')
            .forEach(a => a.classList.toggle('active', a === link));
        const target = link.dataset.target;
        document.querySelectorAll('.panel').forEach(p => p.hidden = p.id !== target);
        if (!link.dataset.loaded) {
            fetchPanel(target, renderers[target]);
            link.dataset.loaded = '1';
        }
    });

    /* позначити/скасувати домашнє завдання */
    document.getElementById('homework').addEventListener('click', e => {
        const btn = e.target.closest('.hw-toggle-btn');
        if (!btn) return;
        fetch(`/student/api/homework/${btn.dataset.id}/toggle`, { method: 'POST' })
            .then(() => fetchPanel('homework', renderHomework));
    });

    /* старт з «Розкладу» */
    document.querySelector('#side-menu a[data-target="schedule"]').click();
});

/* ================================================================
   2. УТИЛІТА ЗАПИТУ з кращою обробкою помилок
   ================================================================ */
function fetchPanel(name, cb) {
    fetch(`/student/api/${name}`)
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP ${response.status}: ${text.trim().slice(0, 200)}…`);
                });
            }
            return response.json();
        })
        .then(cb)
        .catch(err => {
            inject(name, `<p class="error">${err.message}</p>`);
        });
}

/* ================================================================
   3. РЕНДЕРИ
   ================================================================ */
function renderSchedule(data) {
    console.log('▼ Schedule raw data:', data);
    const days = ['', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'];

    const head = ['День', 'Час', 'Предмет', 'Кабінет', 'Вчитель'];
    const rows = data.map(item => {
        // подивіться в консолі, які ключі там є:
        // console.log(Object.keys(item));

        // фолбеки на випадок інших назв полів
        const start = item.start_time ?? item.start ?? item['startTime'] ?? '??';
        const end   = item.end_time   ?? item.end   ?? item['endTime']   ?? '??';
        const subj  = item.subject     ?? item.title ?? item.class       ?? '';
        const room  = item.room        ?? item.room_number ?? item.roomNumber ?? '';
        const teacher = item.teacher   ?? item.teacher_name ?? '';

        // якщо item.day — не число, теж покаже
        const day = Number.isInteger(item.day) ? days[item.day] : item.day;

        return [ day, `${start}-${end}`, subj, room, teacher ];
    });

    inject('schedule', tableMarkup(head, rows));
}


function renderHomework(data) {
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

function renderTeachers(data) {
    if (!data.length) {
        inject('teachers', '<p>Немає даних.</p>');
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

/* ================================================================
   4. ВІДВІДУВАНІСТЬ з окремим фільтром періоду та статистикою внизу
   ================================================================ */
const statusUkr = {
    present: 'Присутній',
    absent:  'Відсутній',
    late:    'Запізнився',
    excused: 'Поважна'
};

let attRaw = [];
let attSubjects = [];

document.addEventListener('change', e => {
    if (e.target.closest('#att-main-filters') || e.target.id === 'stats-filter-range') {
        buildAttendance();
    }
});

function renderAttendance(data) {
    attRaw = data;
    attSubjects = [...new Set(data.map(a => a.subject))].sort();
    buildAttendance();
}

function buildAttendance() {
    const days    = [...new Set(attRaw.map(a => a.day))].sort();
    const selDay    = getVal('att-filter-day',    'all');
    const selStatus = getVal('att-filter-status', 'all');
    const selSubj   = getVal('att-filter-subj',   'all');

    const sched = attRaw.filter(a =>
        (selDay    === 'all' || a.day     === selDay) &&
        (selStatus === 'all' || a.status  === selStatus) &&
        (selSubj   === 'all' || a.subject === selSubj)
    );

    const mainFilters = `
      <div class="att-filter" id="att-main-filters">
        <label class="att-select">День:
          <select id="att-filter-day">
            <option value="all">усі</option>
            ${days.map(d => `<option${d===selDay?' selected':''}>${d}</option>`).join('')}
          </select>
        </label>
        <label class="att-select">Статус:
          <select id="att-filter-status">
            <option value="all">усі</option>
            ${Object.entries(statusUkr).map(([val,txt]) =>
              `<option value="${val}"${val===selStatus?' selected':''}>${txt}</option>`
            ).join('')}
          </select>
        </label>
        <label class="att-select">Предмет:
          <select id="att-filter-subj">
            <option value="all">усі</option>
            ${attSubjects.map(s => `<option${s===selSubj?' selected':''}>${s}</option>`).join('')}
          </select>
        </label>
      </div>`;

    let scheduleHTML = '';
    if (!sched.length) {
        scheduleHTML = '<p class="no-data">Нічого не знайдено.</p>';
    } else {
        const byDay = {};
        sched.forEach(a => (byDay[a.day] = byDay[a.day]||[]).push(a));
        scheduleHTML = Object.keys(byDay).sort().map(day => `
          <h4 class="day-title">${day}</h4>
          <table class="schedule-table">
            <tr><th>Предмет</th><th>Статус</th><th>Коментар</th></tr>
            ${byDay[day].map(a => `
              <tr>
                <td>${a.subject}</td>
                <td><span class="badge status-${a.status}">${statusUkr[a.status]}</span></td>
                <td>${a.comment||''}</td>
              </tr>`).join('')}
          </table>`).join('');
    }

    const selRange = getVal('stats-filter-range', 'all');
    const statsPeriodFilter = `
      <div class="stats-filter">
        <label>Період статистики:
          <select id="stats-filter-range">
            <option value="all"${selRange==='all'?' selected':''}>весь час</option>
            <option value="7"${selRange==='7'?' selected':''}>останні 7 днів</option>
            <option value="30"${selRange==='30'?' selected':''}>останні 30 днів</option>
          </select>
        </label>
      </div>`;

    const now = Date.now();
    const inRange = a => {
        if (selRange==='all') return true;
        return ((now - new Date(a.day).getTime())/86400000) <= Number(selRange);
    };
    const statsData = attRaw.filter(inRange);
    const stats = {present:0, absent:0, late:0, excused:0};
    statsData.forEach(a => stats[a.status]++);
    const statsHTML = `
      <div class="att-stats-grid">
        <div class="stat-box present">Присутніх <strong>${stats.present}</strong></div>
        <div class="stat-box absent">Відсутніх <strong>${stats.absent}</strong></div>
        <div class="stat-box late">Запізнень <strong>${stats.late}</strong></div>
        <div class="stat-box excused">Поважн. <strong>${stats.excused}</strong></div>
        <div class="stat-box total">Уроків <strong>${statsData.length}</strong></div>
      </div>`;

    inject('attendance',
      mainFilters +
      scheduleHTML +
      statsPeriodFilter +
      statsHTML
    );
}

function renderAnnouncements(data) {
    inject('announcements', data.map(n => `
      <article>
        <h4>${n.title}</h4>
        <time>${new Date(n.created_at).toLocaleString()}</time>
        <p>${n.text}</p>
      </article>`).join(''));
}

/* ================================================================
   5. УТИЛІТИ
   ================================================================ */
function inject(id, html) {
    document.getElementById(id).innerHTML = html || '<p class="no-data">Немає даних.</p>';
}

function getVal(id, def) {
    const el = document.getElementById(id);
    return el ? el.value : def;
}

function tableMarkup(head, rows) {
    if (!rows.length) return '<p class="no-data">Немає даних.</p>';
    return `
      <table class="single-table">
        <tr>${head.map(h => `<th>${h}</th>`).join('')}</tr>
        ${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}
      </table>`;
}
