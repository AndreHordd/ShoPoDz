/* ------------- renderAttendance.js ------------- */
export function renderAttendance(data) {
    // Словник для українських назв статусів
    const statusUkr = {
        present: 'Присутній',
        absent:  'Відсутній',
        late:    'Запізнився',
        excused: 'Поважна'
    };

    /* ---------------- ДАНІ ---------------- */
    let attRaw      = data;
    let attSubjects = [...new Set(data.map(a => a.subject))].sort();

    /* ---------------- ФІЛЬТРИ ---------------- */
    let selDay    = 'all';
    let selStatus = 'all';
    let selSubj   = 'all';
    let selRange  = 'all';

    const days = [...new Set(data.map(a => a.day))].sort();

    function inRange(a) {
        if (selRange === 'all') return true;
        const diff = (Date.now() - new Date(a.day).getTime()) / 8.64e7;
        return diff <= Number(selRange);
    }

    function filteredItem(a) {
        return (selDay    === 'all' || a.day    === selDay) &&
               (selStatus === 'all' || a.status === selStatus) &&
               (selSubj   === 'all' || a.subject=== selSubj) && inRange(a);
    }

    /* ---------------- РЕНДЕР ---------------- */
    buildAttendance();

    function buildAttendance() {
        const filtered = attRaw.filter(filteredItem);

        /* -- тулбар фільтрів -- */
        const mainFilters = `
          <div id="att-main-filters" class="att-filter">
            ${select('День:',     'att-filter-day',    days,       selDay, 'усі')}
            ${select('Статус:',   'att-filter-status', Object.entries(statusUkr), selStatus, 'усі', true)}
            ${select('Предмет:',  'att-filter-subj',   attSubjects, selSubj, 'усі')}
            ${select('Період:',   'stats-filter-range',[7,30],      selRange, 'весь час', false, true)}
          </div>`;

        /* -- статистика -- */
        const stats = {present:0, absent:0, late:0, excused:0};
        filtered.forEach(a => stats[a.status]++);
        const statsHTML = `
          <div class="att-stats-grid">
            ${statBox('present', 'Присутніх', stats.present)}
            ${statBox('absent',  'Відсутніх', stats.absent)}
            ${statBox('late',    'Запізнень', stats.late)}
            ${statBox('excused', 'Поважна',   stats.excused)}
            ${statBox('total',   'Уроків',    filtered.length)}
          </div>`;

        /* -- акордеон за днями -- */
        let scheduleHTML = '';
        if (!filtered.length) {
            scheduleHTML = '<p class="no-data">Нічого не знайдено.</p>';
        } else {
            const byDay = {};
            filtered.forEach(a => (byDay[a.day] ??= []).push(a));
            scheduleHTML = Object.keys(byDay).sort().map(day => `
              <h4 class="day-title">${day}</h4>
              <table class="schedule-table">
                <tr><th>Предмет</th><th>Статус</th><th>Коментар</th></tr>
                ${byDay[day].map(a => `
                  <tr>
                    <td>${a.subject}</td>
                    <td><span class="badge status-${a.status}">${statusUkr[a.status]}</span></td>
                    <td>${a.comment ?? ''}</td>
                  </tr>`).join('')}
              </table>`).join('');
        }

        inject('attendance', mainFilters + statsHTML + scheduleHTML);

        /* -- обробники -- */
        document.querySelectorAll('#att-main-filters select').forEach(sel =>
            sel.addEventListener('change', e => {
                const {id, value} = e.target;
                if (id === 'att-filter-day')    selDay    = value;
                if (id === 'att-filter-status') selStatus = value;
                if (id === 'att-filter-subj')   selSubj   = value;
                if (id === 'stats-filter-range')selRange  = value;
                buildAttendance();
            }));

        document.querySelectorAll('.day-title').forEach(title => {
            const tbl = title.nextElementSibling;
            tbl.classList.add('open');            // відкрито за замовч.
            title.classList.add('open');

            title.addEventListener('click', () => {
                tbl.classList.toggle('open');
                title.classList.toggle('open');
            });
        });
    }

    /* ---------- helpers ---------- */
    function select(label, id, items, selected, allTxt, isPair = false, addAll=false) {
        let opts = addAll ? `<option value="all"${selected==='all'?' selected':''}>${allTxt}</option>` : '';
        if (isPair) {
            items.forEach(([v,t]) =>
                opts += `<option value="${v}"${v===selected?' selected':''}>${t}</option>`);
        } else {
            items.forEach(v =>
                opts += `<option value="${v}"${v===selected?' selected':''}>${v}</option>`);
        }
        return `<div class="att-select"><label>${label}
                  <select id="${id}">${opts}</select></label></div>`;
    }

    function statBox(css, title, num) {
        return `<div class="stat-box ${css}">${title} <strong>${num}</strong></div>`;
    }
}
