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
        attendance:    renderAttendance,
        announcements: renderAnnouncements,
    };

    // Загружаем информацию о пользователе
    loadUserInfo();

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

    /* фільтри домашніх завдань та відвідуваності */
    document.addEventListener('change', e => {
        if (e.target.closest('#homework-filters')) {
            filterHomework();
        }
        // Обробка фільтрів відвідуваності відбувається в setupAttendanceEventHandlers
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

// Функция загрузки информации о пользователе
function loadUserInfo() {
    fetch('/student/api/profile')
        .then(response => response.json())
        .then(data => {
            const userInfoHTML = `
                <div class="user-info-card">
                    <div class="user-avatar">👤</div>
                    <div class="user-details">
                        <h1>${data.first_name} ${data.last_name}</h1>
                        <p class="user-role">Учень • Клас ${data.class_name}</p>
                    </div>
                </div>
            `;
            document.getElementById('user-info').innerHTML = userInfoHTML;
        })
        .catch(err => {
            console.error('Помилка завантаження інформації користувача:', err);
        });
}

/* ================================================================
   3. РЕНДЕРИ
   ================================================================ */
function renderSchedule(data) {
    console.log('▼ Schedule raw data:', data);
    
    // Фиксированные дни недели как у администратора (только 5 дней)
    const daysOfWeek = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"];

    // Определяем стандартные временные слоты для уроков
    const timeSlots = [
        { slot: 1, time: '08:00-08:45' },
        { slot: 2, time: '08:55-09:40' },
        { slot: 3, time: '09:50-10:35' },
        { slot: 4, time: '10:45-11:30' },
        { slot: 5, time: '11:40-12:25' },
        { slot: 6, time: '12:35-13:20' },
        { slot: 7, time: '13:30-14:15' }
    ];

    // Группируем уроки по дням недели и времени
    const scheduleMap = {};
    data.forEach(lesson => {
        const day = lesson.day;
        const startTime = lesson.start_time || '00:00';

        // Определяем номер урока по времени начала
        let lessonNumber = 0;
        const startHour = parseInt(startTime.split(':')[0]);
        const startMinute = parseInt(startTime.split(':')[1] || 0);
        
        if (startHour === 8 && startMinute === 0) lessonNumber = 1;
        else if (startHour === 8 && startMinute === 55) lessonNumber = 2;
        else if (startHour === 9 && startMinute === 50) lessonNumber = 3;
        else if (startHour === 10 && startMinute === 45) lessonNumber = 4;
        else if (startHour === 11 && startMinute === 40) lessonNumber = 5;
        else if (startHour === 12 && startMinute === 35) lessonNumber = 6;
        else if (startHour === 13 && startMinute === 30) lessonNumber = 7;
        else {
            // Если время не стандартное, подбираем ближайший слот
            const totalMinutes = startHour * 60 + startMinute;
            if (totalMinutes < 8 * 60 + 30) lessonNumber = 1;
            else if (totalMinutes < 9 * 60 + 22) lessonNumber = 2;
            else if (totalMinutes < 10 * 60 + 17) lessonNumber = 3;
            else if (totalMinutes < 11 * 60 + 12) lessonNumber = 4;
            else if (totalMinutes < 12 * 60 + 7) lessonNumber = 5;
            else if (totalMinutes < 13 * 60 + 2) lessonNumber = 6;
            else lessonNumber = 7;
        }
        
        const key = `${day}_${lessonNumber}`;
        scheduleMap[key] = lesson;
    });

    // Создаем таблицу точно как у администратора
    const scheduleHTML = `
        <div class="schedule-container">
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Урок / День</th>
                        ${daysOfWeek.map(day => `<th>${day}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${timeSlots.map(slot => {
                        return `
                            <tr>
                                <td class="lesson-time">
                                    <div class="lesson-number">Урок ${slot.slot}</div>
                                    <div class="time-slot">${slot.time}</div>
                                </td>
                                ${daysOfWeek.map((dayName, dayIndex) => {
                                    const dayNumber = dayIndex + 1; // День 1-5
                                    const lesson = scheduleMap[`${dayNumber}_${slot.slot}`];
                                    if (lesson) {
                                        const subject = lesson.subject || '';
                                        const room = lesson.room || '';
                                        const teacher = lesson.teacher || '';
                                        
                                        return `
                                            <td class="lesson-cell">
                                                <div class="lesson-subject">${subject}</div>
                                                ${(room || teacher) ? `<div class="lesson-info">
                                                    👨‍🏫 ${teacher || 'Невідомо'}${room ? ` - ${room}` : ''}
                                                </div>` : ''}
                                            </td>
                                        `;
                                    } else {
                                        return '<td class="empty-cell">—</td>';
                                    }
                                }).join('')}
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    const content = `
        <div class="card">
            <h2>📅 Мій розклад</h2>
            ${scheduleHTML}
        </div>
    `;
    
    inject('schedule', content);
}

// Глобальная переменная для хранения данных домашних заданий
let homeworkData = [];

function renderHomework(data) {
    homeworkData = data; // Сохраняем данные для фильтрации
    
    // Получаем уникальные предметы для фильтра
    const subjects = [...new Set(data.map(h => h.subject))].sort();
    
    const filtersHTML = `
        <div id="homework-filters" class="homework-filters">
            <div class="filter-group">
                <label class="filter-label">
                    <span>Предмет:</span>
                    <select id="hw-filter-subject">
                        <option value="all">Усі предмети</option>
                        ${subjects.map(subject => `<option value="${subject}">${subject}</option>`).join('')}
                    </select>
                </label>
                <label class="filter-label">
                    <span>Статус:</span>
                    <select id="hw-filter-status">
                        <option value="all">Усі завдання</option>
                        <option value="done">Виконані</option>
                        <option value="pending">Невиконані</option>
                        <option value="overdue">Прострочені</option>
                        <option value="history">Історія</option>
                    </select>
                </label>
            </div>
        </div>
    `;
    
    const content = `
        <div class="card">
            <h2>📚 Домашні завдання</h2>
            ${filtersHTML}
            <div id="homework-table-container">
                ${generateHomeworkTable(data)}
            </div>
        </div>
    `;
    
    inject('homework', content);
}

function filterHomework() {
    const subjectFilter = getVal('hw-filter-subject', 'all');
    const statusFilter = getVal('hw-filter-status', 'all');
    
    let filteredData = homeworkData.filter(h => {
        // Фильтр по предмету
        if (subjectFilter !== 'all' && h.subject !== subjectFilter) {
            return false;
        }
        
        // Фильтр по статусу
        if (statusFilter !== 'all') {
            const now = Date.now();
            const deadline = new Date(h.deadline).getTime();
            const isOverdue = now > deadline;
            
            switch (statusFilter) {
                case 'done':
                    return h.done;
                case 'pending':
                    return !h.done && !isOverdue;
                case 'overdue':
                    return !h.done && isOverdue;
                case 'history':
                    return isOverdue; // Усі завдання після дедлайну (і виконані, і невиконані)
            }
        }
        
        return true;
    });
    
    document.getElementById('homework-table-container').innerHTML = generateHomeworkTable(filteredData);
}

function generateHomeworkTable(data) {
    return tableMarkup(
        ['Предмет','Опис','Дедлайн','Оцінка','Коментар','Дія'],
        data.map(h => {
            const dl = new Date(h.deadline);
            const now = Date.now();
            const active = now < dl.getTime();
            const isOverdue = now > dl.getTime();
            
            let deadlineText = dl.toLocaleString();
            if (isOverdue && !h.done) {
                deadlineText = `<span style="color: var(--danger); font-weight: bold;">${deadlineText} ⚠️</span>`;
            }
            
            const btn = active
                ? (h.done
                    ? `<button class="btn btn-undo hw-toggle-btn" data-id="${h.homework_id}">Скасувати</button>`
                    : `<button class="btn btn-done hw-toggle-btn" data-id="${h.homework_id}">Готово</button>`)
                : (h.done ? '✅' : (isOverdue ? '❌' : '—'));
            return [
                h.subject,
                h.description,
                deadlineText,
                h.grade ?? '',
                h.comment ?? '',
                btn
            ];
        })
    );
}

/* ================================================================
   4. ВІДВІДУВАНІСТЬ - КОМПАКТНИЙ ТА ЗРУЧНИЙ ІНТЕРФЕЙС
   ================================================================ */
const statusUkr = {
    present: 'Присутній',
    absent:  'Відсутній',
    late:    'Запізнився',
    excused: 'Поважна'
};

const statusIcons = {
    present: '✅',
    absent:  '❌',
    late:    '⏰',
    excused: '📝'
};

let attRaw = [];
let attSubjects = [];
let attFiltered = [];

function renderAttendance(data) {
    attRaw = data;
    attSubjects = [...new Set(data.map(a => a.subject))].sort();
    attFiltered = [...data];
    buildCompactAttendance();
    
    setTimeout(() => {
        setupCompactAttendanceHandlers();
    }, 100);
}

function buildCompactAttendance() {
    if (!attRaw.length) {
        inject('attendance', createEmptyAttendanceState());
        return;
    }
    
    const content = `
        <div class="card">
            <h2>📋 Моя відвідуваність</h2>
            ${createCompactFilters()}
            ${createCompactStats()}
            ${createAttendanceTable()}
        </div>
    `;
    
    inject('attendance', content);
}

function createCompactFilters() {
    const days = [...new Set(attRaw.map(a => a.day))].sort().reverse();
    
    // Отримуємо поточні значення фільтрів
    const currentPeriod = getVal('att-filter-period-compact', '30');
    const currentSubject = getVal('att-filter-subject-compact', 'all');
    const currentStatus = getVal('att-filter-status-compact', 'all');
    const currentView = getVal('att-view-mode', 'table');
    
    return `
        <div class="attendance-compact-filters">
            <div class="compact-filters-single-row">
                <div class="filter-compact">
                    <label>📊 Період:</label>
                    <select id="att-filter-period-compact">
                        <option value="7" ${currentPeriod === '7' ? 'selected' : ''}>7 днів</option>
                        <option value="30" ${currentPeriod === '30' ? 'selected' : ''}>30 днів</option>
                        <option value="90" ${currentPeriod === '90' ? 'selected' : ''}>3 місяці</option>
                        <option value="all" ${currentPeriod === 'all' ? 'selected' : ''}>Весь час</option>
          </select>
                </div>
                <div class="filter-compact">
                    <label>📚 Предмет:</label>
                    <select id="att-filter-subject-compact">
                        <option value="all" ${currentSubject === 'all' ? 'selected' : ''}>Усі</option>
                        ${attSubjects.map(subject => 
                            `<option value="${subject}" ${currentSubject === subject ? 'selected' : ''}>${subject}</option>`
            ).join('')}
          </select>
                </div>
                <div class="filter-compact">
                    <label>⚡ Статус:</label>
                    <select id="att-filter-status-compact">
                        <option value="all" ${currentStatus === 'all' ? 'selected' : ''}>Усі</option>
                        <option value="present" ${currentStatus === 'present' ? 'selected' : ''}>Присутні</option>
                        <option value="absent" ${currentStatus === 'absent' ? 'selected' : ''}>Відсутні</option>
                        <option value="late" ${currentStatus === 'late' ? 'selected' : ''}>Запізнення</option>
                        <option value="excused" ${currentStatus === 'excused' ? 'selected' : ''}>Поважні</option>
                    </select>
                </div>
                <div class="filter-compact">
                    <label>📊 Вигляд:</label>
                    <select id="att-view-mode">
                        <option value="table" ${currentView === 'table' ? 'selected' : ''}>Таблиця</option>
                        <option value="summary" ${currentView === 'summary' ? 'selected' : ''}>Підсумок</option>
          </select>
                </div>
            </div>
        </div>
    `;
}

function createCompactStats() {
    const stats = calculateAttendanceStats(attFiltered);
    const total = attFiltered.length;
    const attendanceRate = total > 0 ? Math.round((stats.present / total) * 100) : 0;
    
    return `
        <div class="attendance-compact-stats">
            <div class="compact-stat-item present">
                <span class="stat-icon">✅</span>
                <span class="stat-number">${stats.present}</span>
                <span class="stat-text">Присутній</span>
            </div>
            <div class="compact-stat-item absent">
                <span class="stat-icon">❌</span>
                <span class="stat-number">${stats.absent}</span>
                <span class="stat-text">Відсутній</span>
            </div>
            <div class="compact-stat-item late">
                <span class="stat-icon">⏰</span>
                <span class="stat-number">${stats.late}</span>
                <span class="stat-text">Запізнення</span>
            </div>
            <div class="compact-stat-item rate">
                <span class="stat-icon">📊</span>
                <span class="stat-number">${attendanceRate}%</span>
                <span class="stat-text">Відвідуваність</span>
            </div>
        </div>
    `;
}

function createAttendanceTable() {
    const viewMode = getVal('att-view-mode', 'table');
    
    if (viewMode === 'summary') {
        return createAttendanceSummary();
    }
    
    if (!attFiltered.length) {
        return `
            <div class="attendance-empty">
                <div class="empty-icon">📅</div>
                <div class="empty-title">Немає даних за вибраними фільтрами</div>
                <div class="empty-message">Спробуйте змінити параметри фільтрації</div>
            </div>
        `;
    }
    
    // Сортуємо за датою (найновіші зверху)
    const sortedData = [...attFiltered].sort((a, b) => new Date(b.day) - new Date(a.day));
    
    return `
        <div class="attendance-table-container">
            <table class="attendance-compact-table">
                <thead>
                    <tr>
                        <th>Дата</th>
                        <th>Предмет</th>
                        <th>Статус</th>
                        <th>Час</th>
                        <th>Кабінет</th>
                    </tr>
                </thead>
                <tbody>
                    ${sortedData.slice(0, 50).map(item => createAttendanceRow(item)).join('')}
                </tbody>
            </table>
            ${sortedData.length > 50 ? `
                <div class="table-pagination">
                    <p class="pagination-info">Показано 50 з ${sortedData.length} записів</p>
                    <button id="load-more-attendance" class="btn-load-more">Завантажити ще</button>
                </div>
            ` : ''}
        </div>
    `;
}

function createAttendanceRow(item) {
    return `
        <tr class="attendance-row status-${item.status}">
            <td class="att-date">${formatCompactDate(item.day)}</td>
            <td class="att-subject">${item.subject}</td>
            <td class="att-status">
                <span class="status-badge ${item.status}">
                    ${statusIcons[item.status]} ${statusUkr[item.status]}
                </span>
            </td>
            <td class="att-time">${item.time || '—'}</td>
            <td class="att-room">${item.room || '—'}</td>
        </tr>
    `;
}

function createAttendanceSummary() {
    if (!attFiltered.length) {
        return `
            <div class="attendance-empty">
                <div class="empty-icon">📅</div>
                <div class="empty-title">Немає даних за вибраними фільтрами</div>
            </div>
        `;
    }
    
    // Групуємо по днях
    const byDay = {};
    attFiltered.forEach(a => {
        const day = a.day;
        if (!byDay[day]) byDay[day] = [];
        byDay[day].push(a);
    });
    
    const sortedDays = Object.keys(byDay).sort().reverse();
    
    return `
        <div class="attendance-summary-container">
            ${sortedDays.slice(0, 20).map(day => createDaySummary(day, byDay[day])).join('')}
            ${sortedDays.length > 20 ? `
                <div class="summary-pagination">
                    <p>Показано 20 останніх днів з ${sortedDays.length}</p>
                </div>
            ` : ''}
        </div>
    `;
}

function createDaySummary(day, lessons) {
    const stats = calculateDayStats(lessons);
    const hasIssues = stats.absent > 0 || stats.late > 0;
    
    return `
        <div class="day-summary-card ${hasIssues ? 'has-issues' : 'no-issues'}">
            <div class="day-summary-header">
                <div class="day-summary-date">${formatCompactDate(day)}</div>
                <div class="day-summary-stats">
                    <span class="summary-stat present">${stats.present} ✅</span>
                    ${stats.absent > 0 ? `<span class="summary-stat absent">${stats.absent} ❌</span>` : ''}
                    ${stats.late > 0 ? `<span class="summary-stat late">${stats.late} ⏰</span>` : ''}
                    ${stats.excused > 0 ? `<span class="summary-stat excused">${stats.excused} 📝</span>` : ''}
                </div>
            </div>
            <div class="day-summary-subjects">
                ${lessons.map(lesson => `
                    <span class="subject-tag ${lesson.status}">${lesson.subject}</span>
                `).join('')}
            </div>
        </div>
    `;
}

function formatCompactDate(dateStr) {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const yesterdayOnly = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate());
    
    if (dateOnly.getTime() === todayOnly.getTime()) {
        return 'Сьогодні';
    } else if (dateOnly.getTime() === yesterdayOnly.getTime()) {
        return 'Вчора';
    } else {
        return date.toLocaleDateString('uk-UA', { 
            day: '2-digit', 
            month: '2-digit' 
        });
    }
}

function setupCompactAttendanceHandlers() {
    // Обробка фільтрів
    ['att-filter-period-compact', 'att-filter-subject-compact', 'att-filter-status-compact', 'att-view-mode'].forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) {
            element.addEventListener('change', applyCompactAttendanceFilters);
    }
    });
    
    // Кнопка "Завантажити ще"
    const loadMoreBtn = document.getElementById('load-more-attendance');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreAttendanceRecords);
    }
}

function applyCompactAttendanceFilters() {
    const period = getVal('att-filter-period-compact', '30');
    const subject = getVal('att-filter-subject-compact', 'all');
    const status = getVal('att-filter-status-compact', 'all');
    
    // Фільтрація за періодом
    const now = Date.now();
    let filtered = attRaw.filter(a => {
        if (period === 'all') return true;
        const daysDiff = (now - new Date(a.day).getTime()) / (1000 * 60 * 60 * 24);
        return daysDiff <= Number(period);
    });
    
    // Фільтрація за предметом
    if (subject !== 'all') {
        filtered = filtered.filter(a => a.subject === subject);
    }
    
    // Фільтрація за статусом
    if (status !== 'all') {
        filtered = filtered.filter(a => a.status === status);
    }
    
    attFiltered = filtered;
    
    // Перебудовуємо інтерфейс
    buildCompactAttendance();
    setTimeout(() => {
        setupCompactAttendanceHandlers();
    }, 100);
}

function loadMoreAttendanceRecords() {
    // Тут можна реалізувати завантаження додаткових записів
    alert('Функція завантаження додаткових записів буде реалізована пізніше');
}

function createEmptyAttendanceState() {
    return `
        <div class="card">
            <h2>📋 Моя відвідуваність</h2>
            <div class="attendance-empty">
                <div class="empty-icon">📊</div>
                <div class="empty-title">Немає даних про відвідуваність</div>
                <div class="empty-message">Дані про відвідуваність з'являться після початку навчального процесу</div>
            </div>
        </div>
    `;
}

function calculateAttendanceStats(data) {
    const stats = {present: 0, absent: 0, late: 0, excused: 0};
    data.forEach(a => stats[a.status]++);
    return stats;
}

function calculateDayStats(lessons) {
    return calculateAttendanceStats(lessons);
}

function renderAnnouncements(data) {
    const content = `
        <div class="card">
            <h2>📢 Оголошення</h2>
            ${data.length ? data.map(n => `
                <article style="background: var(--primary-light); padding: 1rem; margin-bottom: 1rem; border-radius: 8px; border-left: 4px solid var(--primary);">
                    <h4 style="margin: 0 0 0.5rem; color: var(--primary);">${n.title}</h4>
                    <time style="display: block; font-size: 0.85rem; color: var(--muted); margin-bottom: 0.5rem;">${new Date(n.created_at).toLocaleString()}</time>
                    <p style="margin: 0; line-height: 1.6;">${n.text}</p>
                </article>
            `).join('') : '<div class="no-data">Немає оголошень.</div>'}
        </div>
    `;
    
    inject('announcements', content);
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
