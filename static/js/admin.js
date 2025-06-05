// admin.js

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('a[href="#schedules"]').addEventListener('click', showClassSelector);
    document.querySelector('a[href="#classes"]').addEventListener('click', showClassManagement);
    document.querySelector('a[href="#announcements"]').addEventListener('click', showAnnouncements);
});


function showClassSelector() {
    const content = document.getElementById('main-content');
    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Оберіть клас</h2>
            <select id="class-select">
                <option disabled selected>-- Виберіть клас --</option>
            </select>
            <button id="load-schedule-btn">Переглянути розклад</button>
        </section>
    `;

    fetch('/api/classes')
        .then(res => res.json())
        .then(classes => {
            const select = document.getElementById('class-select');
            classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls.id;
                option.textContent = cls.name;
                option.dataset.classNumber = cls.class_number;
                select.appendChild(option);
            });

            document.getElementById('load-schedule-btn').addEventListener('click', () => {
                const selectElement = document.getElementById('class-select');
                const selectedClassId = selectElement.value;
                const selectedOption = selectElement.options[selectElement.selectedIndex];
                const selectedClassName = selectedOption.text;
                const selectedClassNumber = selectedOption.dataset.classNumber;
                loadSchedule(selectedClassId, selectedClassName, selectedClassNumber);
            });
        })
        .catch(err => {
            console.error('❌ Помилка при завантаженні класів:', err);
        });
}

function loadSchedule(classId, className, classNumber) {
    const content = document.getElementById('main-content');

    fetch(`/api/lessons/${classId}`)
        .then(res => res.json())
        .then(schedule => {
            const hasAnyLessons = Object.values(schedule).some(day => Object.keys(day).length > 0);

            let html = `
                <section class="dashboard-section">
                    <h2>Розклад для класу ${className}</h2>
            `;

            if (hasAnyLessons) {
                html += `
                    <table class="schedule-table">
                        <thead>
                            <tr>
                                <th>Урок / День</th>
                                ${["Понеділок", "Вівторок", "Середа", "Четвер", "П’ятниця"]
                                    .map(day => `<th>${day}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                `;

                for (let lessonNum = 1; lessonNum <= 7; lessonNum++) {
                    html += `<tr><td>Урок ${lessonNum}</td>`;
                    for (let dayIndex = 1; dayIndex <= 5; dayIndex++) {
                        const subjectMap = schedule[dayIndex] || {};
                        const subject = subjectMap[lessonNum] || "-";
                        html += `<td>${subject}</td>`;
                    }
                    html += `</tr>`;
                }

                html += `
                        </tbody>
                    </table>
                    <div class="button-row" style="margin-top: 20px;">
                        <button class="btn-small" id="edit-btn">✏️ Редагувати розклад</button>
                        <button class="btn-small red" onclick="deleteSchedule('${classId}', '${className}', '${classNumber}')">🗑️ Видалити розклад</button>
                    </div>
                `;

                content.innerHTML = html;

                document.getElementById('edit-btn').addEventListener('click', () => {
                    createSchedule(classId, className, classNumber, true, schedule);
                });
            } else {
                html += `
                    <div class="button-row" style="margin-top: 20px;">
                        <button onclick="createSchedule('${classId}', '${className}', '${classNumber}', false, null)">➕ Створити розклад</button>
                    </div>
                `;
                content.innerHTML = html;
            }

            html += `</section>`;
        })
        .catch(err => {
            console.error('❌ Помилка при завантаженні розкладу:', err);
            alert('❌ Помилка при завантаженні розкладу');
        });
}

function createSchedule(classId, className, classNumber, isEdit = false, existingSchedule = {}) {
    const content = document.getElementById('main-content');
    const days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П’ятниця"];

    if (!classId || !classNumber) {
        alert("❌ Неможливо створити розклад: відсутній classId або classNumber");
        return;
    }

    Promise.all([
        fetch(`/api/subjects/for-class/${classNumber}`).then(res => res.json()),
        fetch(`/teacher/api/teachers`).then(res => res.json()),
        fetch(`/api/rooms`).then(res => res.json()),
        fetch(`/api/lessons/full/${classId}`).then(res => res.json())
    ])
    .then(([subjects, teachers, rooms, fullLessons]) => {
        let formHTML = `
            <section class="dashboard-section">
                <h2>${isEdit ? 'Редагування' : 'Створення'} розкладу для ${className}</h2>
                <form id="schedule-form">
                    <input type="hidden" name="class_id" value="${classId}">
        `;

        days.forEach((day, i) => {
            formHTML += `<h3>${day}</h3>`;
            for (let lesson = 1; lesson <= 7; lesson++) {
                const key = `${i + 1}_${lesson}`;
                const entry = fullLessons[key] || {};
                formHTML += `
                    <label>Урок ${lesson}:
                        <select name="day_${i}_lesson_${lesson}">
                            <option value="">—</option>
                            ${subjects.map(s => `<option value="${s.id}" ${s.id == entry.subject_id ? 'selected' : ''}>${s.title}</option>`).join('')}
                        </select>
                        Вчитель:
                        <select name="teacher_day_${i}_lesson_${lesson}">
                            <option value="">—</option>
                            ${teachers.map(t => `<option value="${t.id}" ${t.id == entry.teacher_id ? 'selected' : ''}>${t.name}</option>`).join('')}
                        </select>
                        Кабінет:
                        <select name="room_day_${i}_lesson_${lesson}">
                            <option value="">—</option>
                            ${rooms.map(r => `<option value="${r.id}" ${r.id == entry.room_id ? 'selected' : ''}>${r.number}</option>`).join('')}
                        </select>
                    </label><br>
                `;
            }
            formHTML += `<hr>`;
        });

        formHTML += `<button type="submit">Зберегти розклад</button></form></section>`;
        content.innerHTML = formHTML;

        document.getElementById('schedule-form').addEventListener('submit', function (e) {
            e.preventDefault();

            // Перевірка на неповне заповнення
            let hasError = false;
            for (let day = 0; day < 5; day++) {
                for (let lesson = 1; lesson <= 7; lesson++) {
                    const subj = this[`day_${day}_lesson_${lesson}`].value;
                    const teach = this[`teacher_day_${day}_lesson_${lesson}`].value;
                    const room = this[`room_day_${day}_lesson_${lesson}`].value;
                    const countFilled = [subj, teach, room].filter(val => val !== "").length;
                    if (countFilled > 0 && countFilled < 3) {
                        alert(`❌ Помилка: для ${days[day]}, уроку ${lesson} заповніть і предмет, і вчителя, і кабінет.`);
                        hasError = true;
                        break;
                    }
                }
                if (hasError) break;
            }
            if (hasError) return;

            // Відправка форми
            const formData = new FormData(this);
            fetch('/api/lessons/create', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    loadSchedule(classId, className, classNumber);
                } else {
                    alert('❌ Помилка збереження: ' + data.error);
                }
            })
            .catch(err => {
                alert('❌ Помилка мережі: ' + err.message);
            });
        });
    })
    .catch(err => {
        alert('❌ Не вдалося завантажити дані: ' + err.message);
    });
}


function deleteSchedule(classId, className, classNumber) {
    const confirmDelete = confirm(`Видалити розклад для ${className}?`);
    if (confirmDelete) {
        fetch(`/api/lessons/delete/${classId}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadSchedule(classId, className, classNumber);
            } else {
                alert('❌ Не вдалося видалити розклад');
            }
        })
        .catch(err => {
            alert('❌ Помилка мережі: ' + err.message);
        });
    }
}

function showClassManagement() {
    const content = document.getElementById('main-content');

    fetch('/api/classes')
        .then(res => res.json())
        .then(classes => {
            let html = `
                <section class="dashboard-section">
                    <h2>Класи</h2>
                    <div style="margin-bottom: 20px;">
                        <button class="btn-primary" onclick="showAddClassForm()">➕ Створити клас</button>
                    </div>
            `;

            if (classes.length === 0) {
                html += `<p>Класів поки що немає.</p>`;
            } else {
                html += `
                    <table class="class-table">
                        <thead>
                            <tr>
                                <th>Клас</th>
                                <th>Дії</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${classes.map(c => `
                                <tr>
                                    <td>${c.name}</td>
                                    <td>
                                        <button class="btn-small" onclick="showEditClassForm(${c.id}, '${c.name}')">✏️ Редагувати</button>
                                        <button class="btn-small red" onclick="deleteClass(${c.id})">🗑️ Видалити</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }

            html += `</section>`;
            content.innerHTML = html;
        });
}


function showAddClassForm() {
    const content = document.getElementById('main-content');

    fetch('/teacher/api/teachers')
        .then(res => res.json())
        .then(teachers => {
            const teacherOptions = teachers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');

            content.innerHTML = `
                <section class="dashboard-section">
                    <h2>Додати клас</h2>
                    <label>Номер класу: <input id="class-number" type="number" placeholder="Наприклад, 10"></label><br><br>
                    <label>Буква: <input id="subclass" type="text" placeholder="Наприклад, А" maxlength="1"></label><br><br>
                    <label>Класний керівник:
                        <select id="class-teacher-id">
                            <option value="">-- Оберіть вчителя --</option>
                            ${teacherOptions}
                        </select>
                    </label><br><br>
                    <button onclick="addClass()">Зберегти</button>
                    <button onclick="showClassManagement()">Назад</button>
                </section>
            `;
        });
}


function addClass() {
    const number = document.getElementById('class-number').value;
    const subclass = document.getElementById('subclass').value;
    const teacherId = document.getElementById('class-teacher-id').value;

    if (!number || !subclass || !teacherId) {
        alert("❌ Заповніть усі поля для створення класу.");
        return;
    }

    fetch('/api/classes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class_number: number,
            subclass: subclass,
            class_teacher_id: teacherId
        })
    }).then(() => showClassManagement());
}


function showEditClassForm(id, currentName) {
    const [number, subclass] = currentName.split("-");

    fetch('/teacher/api/teachers')
        .then(res => res.json())
        .then(teachers => {
            const content = document.getElementById('main-content');
            let teacherOptions = teachers.map(t =>
                `<option value="${t.id}">${t.name}</option>`).join('');

            content.innerHTML = `
                <section class="dashboard-section">
                    <h2>Редагувати клас</h2>
                    <label>Номер класу: <input id="edit-class-number" value="${number}" type="number"></label><br><br>
                    <label>Буква: <input id="edit-subclass" value="${subclass}" maxlength="1"></label><br><br>
                    <label>Класний керівник:
                        <select id="edit-class-teacher-id">
                            ${teacherOptions}
                        </select>
                    </label><br><br>
                    <button onclick="editClass(${id})">Зберегти</button>
                    <button onclick="showClassManagement()">Назад</button>
                </section>
            `;
        });
}

function editClass(id) {
    const number = document.getElementById('edit-class-number').value;
    const subclass = document.getElementById('edit-subclass').value;
    const teacherId = document.getElementById('edit-class-teacher-id').value;

    if (!number || !subclass || !teacherId) {
        alert("❌ Заповніть усі поля для редагування класу.");
        return;
    }

    fetch(`/api/classes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class_number: number,
            subclass: subclass,
            class_teacher_id: teacherId
        })
    }).then(() => showClassManagement());
}

function deleteClass(id) {
    if (confirm("Ви впевнені, що хочете видалити цей клас?")) {
        fetch(`/api/classes/${id}`, { method: 'DELETE' })
            .then(() => showClassManagement());
    }
}

function showAnnouncements() {
    const content = document.getElementById('main-content');
    fetch('/api/announcements')
        .then(res => res.json())
        .then(announcements => {
            let html = `
                <section class="dashboard-section">
                    <h2>Оголошення</h2>
                    <button class="create-button" onclick="showAddAnnouncementForm()">➕ Створити оголошення</button>
                    <div class="announcement-list">
            `;

            announcements.forEach(a => {
                html += `
                    <div class="announcement-card">
                        <div class="announcement-header">
                            <strong>${a.title}</strong>
                            <span class="announcement-date">(${a.created_at})</span>
                        </div>
                        <p class="announcement-text">${a.text}</p>
                        <div class="button-row">
                            <button class="edit-button" onclick="showEditAnnouncementForm(${a.id}, '${a.title}', \`${a.text.replace(/`/g, '\\`')}\`)">✏️ Редагувати</button>
                            <button class="delete-button" onclick="deleteAnnouncement(${a.id})">🗑️ Видалити</button>
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </section>
            `;
            content.innerHTML = html;
        });
}

function showAddAnnouncementForm() {
    const content = document.getElementById('main-content');
    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Нове оголошення</h2>
            <label>Заголовок: <input id="announcement-title"></label><br>
            <label>Текст: <textarea id="announcement-text"></textarea></label><br>
            <button onclick="addAnnouncement()">Зберегти</button>
            <button onclick="showAnnouncements()">Назад</button>
        </section>
    `;
}

function addAnnouncement() {
    const title = document.getElementById('announcement-title').value.trim();
    const text = document.getElementById('announcement-text').value.trim();

    if (!title || !text) {
        alert("❗ Заповніть усі поля");
        return;
    }

    fetch('/api/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, text })
    }).then(res => res.json())
      .then(data => {
          if (data.success) {
              showAnnouncements();
          } else {
              alert("❌ Помилка: " + data.error);
          }
      });
}

function showEditAnnouncementForm(id, currentTitle, currentText) {
    const content = document.getElementById('main-content');
    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Редагування оголошення</h2>
            <label>Заголовок: <input id="edit-title" value="${currentTitle}"></label><br>
            <label>Текст: <textarea id="edit-text">${currentText}</textarea></label><br>
            <button onclick="editAnnouncement(${id})">Зберегти</button>
            <button onclick="showAnnouncements()">Назад</button>
        </section>
    `;
}

function editAnnouncement(id) {
    const title = document.getElementById('edit-title').value.trim();
    const text = document.getElementById('edit-text').value.trim();

    if (!title || !text) {
        alert("❗ Заповніть усі поля");
        return;
    }

    fetch(`/api/announcements/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, text })
    }).then(res => res.json())
      .then(data => {
          if (data.success) {
              showAnnouncements();
          } else {
              alert("❌ Помилка: " + data.error);
          }
      });
}

function deleteAnnouncement(id) {
    if (confirm("Ви дійсно хочете видалити це оголошення?")) {
        fetch(`/api/announcements/${id}`, {
            method: 'DELETE'
        }).then(res => res.json())
          .then(data => {
              if (data.success) {
                  showAnnouncements();
              } else {
                  alert("❌ Помилка при видаленні");
              }
          });
    }
}
