// admin.js

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('a[href="#schedules"]').addEventListener('click', showClassSelector);
    document.querySelector('a[href="#classes"]').addEventListener('click', showClassManagement);
    document.querySelector('a[href="#announcements"]').addEventListener('click', showAnnouncements);
    document.querySelector('a[href="#users"]').addEventListener('click', showUserManagement);
    document.querySelector('a[href="#subjects"]').addEventListener('click', showSubjects);
    document.querySelector('a[href="#print"]').addEventListener('click', showScheduleReport);
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
        fetch(`/api/teachers`).then(res => res.json()),
        fetch(`/api/rooms`).then(res => res.json()),
        fetch(`/api/lessons/full/${classId}`).then(res => res.json())
    ])
    .then(([subjects, teachers, rooms, fullLessons]) => {
        const subjectMap = {};
        subjects.forEach(s => subjectMap[s.id] = s.title);

        const teacherMap = {};
        teachers.forEach(t => {
            teacherMap[t.user_id] = {
                name: `${t.last_name} ${t.first_name} ${t.middle_name || ''}`,
                subject_ids: t.subject_ids
            };
        });

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
                const selectedSubject = entry.subject_id || "";
                const selectedTeacher = entry.teacher_id || "";
                const selectedRoom = entry.room_id || "";

                // предмети: всі (але якщо вибрано викладача — фільтруємо)
                let subjectOptions = subjects;
                if (selectedTeacher && teacherMap[selectedTeacher]) {
                    subjectOptions = subjects.filter(s => teacherMap[selectedTeacher].subject_ids.includes(s.id));
                }

                const subjectSelect = `
                    <select name="day_${i}_lesson_${lesson}" class="subject-select fixed-width" data-day="${i}" data-lesson="${lesson}">
                        <option value="">—</option>
                        ${subjectOptions.map(s => `
                            <option value="${s.id}" ${s.id == selectedSubject ? 'selected' : ''}>${s.title}</option>
                        `).join('')}
                    </select>`;

                // викладачі: всі (але якщо вибрано предмет — фільтруємо)
                let teacherOptions = teachers;
                if (selectedSubject) {
                    teacherOptions = teachers.filter(t => t.subject_ids.includes(selectedSubject));
                }

                const teacherSelect = `
                    <select name="teacher_day_${i}_lesson_${lesson}" class="teacher-select fixed-width" data-day="${i}" data-lesson="${lesson}">
                        <option value="">—</option>
                        ${teacherOptions.map(t => `
                            <option value="${t.user_id}" ${t.user_id == selectedTeacher ? 'selected' : ''}>
                                ${t.last_name} ${t.first_name} ${t.middle_name || ''}
                            </option>
                        `).join('')}
                    </select>`;

                const roomSelect = `
                    <select name="room_day_${i}_lesson_${lesson}" class="fixed-width">
                        <option value="">—</option>
                        ${rooms.map(r => `
                            <option value="${r.id}" ${r.id == selectedRoom ? 'selected' : ''}>${r.number}</option>
                        `).join('')}
                    </select>`;

                formHTML += `<label>Урок ${lesson}: ${subjectSelect} Вчитель: ${teacherSelect} Кабінет: ${roomSelect}</label><br>`;
            }
            formHTML += `<hr>`;
        });

        formHTML += `<button type="submit">Зберегти розклад</button></form></section>`;
        content.innerHTML = formHTML;

        // === Динамічне оновлення ===
        const subjectSelects = document.querySelectorAll('.subject-select');
        const teacherSelects = document.querySelectorAll('.teacher-select');

        subjectSelects.forEach(subjectSelect => {
            subjectSelect.addEventListener('change', () => {
                const day = subjectSelect.dataset.day;
                const lesson = subjectSelect.dataset.lesson;
                const teacherSelect = document.querySelector(`.teacher-select[data-day="${day}"][data-lesson="${lesson}"]`);
                const selectedSubjectId = +subjectSelect.value;
                const selectedTeacher = teacherSelect.value;

                teacherSelect.innerHTML = '<option value="">—</option>';

                teachers.forEach(t => {
                    if (!selectedSubjectId || t.subject_ids.includes(selectedSubjectId)) {
                        const option = document.createElement('option');
                        option.value = t.user_id;
                        option.textContent = `${t.last_name} ${t.first_name} ${t.middle_name || ''}`;
                        if (String(t.user_id) === selectedTeacher) option.selected = true;
                        teacherSelect.appendChild(option);
                    }
                });
            });
        });

        teacherSelects.forEach(teacherSelect => {
            teacherSelect.addEventListener('change', () => {
                const day = teacherSelect.dataset.day;
                const lesson = teacherSelect.dataset.lesson;
                const subjectSelect = document.querySelector(`.subject-select[data-day="${day}"][data-lesson="${lesson}"]`);
                const selectedTeacherId = +teacherSelect.value;
                const selectedSubject = subjectSelect.value;

                subjectSelect.innerHTML = '<option value="">—</option>';

                if (teacherMap[selectedTeacherId]) {
                    teacherMap[selectedTeacherId].subject_ids.forEach(subjId => {
                        if (subjectMap[subjId]) {
                            const option = document.createElement('option');
                            option.value = subjId;
                            option.textContent = subjectMap[subjId];
                            if (String(subjId) === selectedSubject) option.selected = true;
                            subjectSelect.appendChild(option);
                        }
                    });
                } else {
                    subjects.forEach(s => {
                        const option = document.createElement('option');
                        option.value = s.id;
                        option.textContent = s.title;
                        if (String(s.id) === selectedSubject) option.selected = true;
                        subjectSelect.appendChild(option);
                    });
                }
            });
        });

        // === Надсилання форми ===
        document.getElementById('schedule-form').addEventListener('submit', function (e) {
            e.preventDefault();
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
                    <div>
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
                                        <button class="btn-small" onclick="showEditClassForm(${c.id}, '${c.name}', ${c.class_teacher_id})">✏️ Редагувати</button>
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

    fetch('/api/teachers')
        .then(res => res.json())
        .then(teachers => {
            const teacherOptions = teachers.map(t => {
              const fullName = `${t.last_name} ${t.first_name}${t.middle_name ? ' ' + t.middle_name : ''}`;
              return `<option value="${t.user_id}">${fullName}</option>`;
            }).join('');

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

function showEditClassForm(id, currentName, classTeacherId) {
    const [number, subclass] = currentName.split("-");

    fetch('/api/teachers')
        .then(res => res.json())
        .then(teachers => {
            const content = document.getElementById('main-content');

            let teacherOptions = teachers.map(t => {
                const fullName = `${t.last_name} ${t.first_name}${t.middle_name ? ' ' + t.middle_name : ''}`;
                const selected = String(t.user_id) === String(classTeacherId) ? 'selected' : '';
                return `<option value="${t.user_id}" ${selected}>${fullName}</option>`;
            }).join('');

            content.innerHTML = `
                <section class="dashboard-section">
                    <h2>Редагувати клас</h2>
                    <label>Номер класу: <input id="edit-class-number" value="${number}" type="number"></label><br><br>
                    <label>Буква: <input id="edit-subclass" value="${subclass}" maxlength="1"></label><br><br>
                    <label>Класний керівник:
                        <select id="edit-class-teacher-id">
                            <option value="">-- Оберіть вчителя --</option>
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
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showClassManagement();
                } else {
                    alert('❌ Не вдалося видалити клас:\n' + (data.error || 'Невідома помилка.'));
                }
            })
            .catch(err => {
                alert('❌ Сталася помилка при запиті: ' + err.message);
            });
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
                    <button class="btn-primary" onclick="showAddAnnouncementForm()">➕ Створити оголошення</button>
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

                            <button class="btn-small" onclick="showEditAnnouncementForm(${a.id}, '${a.title}', \`${a.text.replace(/`/g, '\\`')}\`)">✏️ Редагувати</button>
                            <button class="btn-small red" onclick="deleteAnnouncement(${a.id})">🗑️ Видалити</button>
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

function showUserManagement() {
    const content = document.getElementById('main-content');

    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Користувачі</h2>
            <button class="btn-primary" onclick="showAddUserForm()">➕ Додати користувача</button>

            <h3><a href="#" onclick="showClassList()">Учні</a></h3>
            <div id="student-list"></div>

            <h3><a href="#" onclick="loadUserList('parent')">Батьки</a></h3>
            <div id="parent-list"></div>

            <h3><a href="#" onclick="loadUserList('teacher')">Викладачі</a></h3>
            <div id="teacher-list"></div>
        </section>
    `;
}

function showClassList() {
    const container = document.getElementById('student-list');
    container.innerHTML = `<p>Завантаження класів...</p>`;

    fetch('/api/classes')
        .then(res => res.json())
        .then(classes => {
            container.innerHTML = `
                <p>Оберіть клас:</p>
                <ul>
                    ${classes.map(cls => `
                        <li><button class="btn-small" onclick="showStudentsByClass(${cls.id}, '${cls.name}')">${cls.name}</button></li>
                    `).join('')}
                </ul>
            `;
        });
}

function showStudentsByClass(classId, className) {
    const container = document.getElementById('student-list');
    container.innerHTML = `<p>Завантаження учнів...</p>`;

    fetch('/api/students')
        .then(res => res.json())
        .then(students => {
            const filtered = students.filter(s => s.class_id == classId);
            container.innerHTML = `
                <h4>Клас: ${className}</h4>
                <ul>
                    ${filtered.map(s => `
                        <li>
                            ${s.last_name} ${s.first_name}${s.middle_name ? ' ' + s.middle_name : ''}
                            <button class = "btn-small" onclick="showEditUserForm('student', ${s.user_id})">✏️ Редагувати</button>
                            <button class = "btn-small red" onclick="deleteUser('student', ${s.user_id})">🗑️ Видалити</button>
                        </li>
                    `).join('')}
                </ul>
                <button onclick="showClassList()">← Назад до класів</button>
            `;
        });
}

function loadUserList(type) {
    const url = type === 'teacher' ? '/api/teachers' : `/api/${type}s`;
    fetch(url)
        .then(res => res.json())
        .then(users => {
            const listId = `${type}-list`;
            const listEl = document.getElementById(listId);
            let html = '<ul>';

            if (type === 'teacher') {
                html += users.map(t => `
                    <li>
                        ${t.last_name} ${t.first_name}${t.middle_name ? ' ' + t.middle_name : ''}
                        <button class = "btn-small" onclick="showEditUserForm('teacher', ${t.user_id})">✏️ Редагувати</button>
                        <button class = "btn-small red" onclick="deleteUser('teacher', ${t.user_id})">🗑️ Видалити</button>
                    </li>
                `).join('');
            } else {
                html += users.map(u => `
                    <li>
                        ${u.last_name} ${u.first_name}${u.middle_name ? ' ' + u.middle_name : ''}
                        <button class = "btn-small" onclick="showEditUserForm('${type}', ${u.user_id})">✏️ Редагувати</button>
                        <button class = "btn-small red" onclick="deleteUser('${type}', ${u.user_id})">🗑️ Видалити</button>
                    </li>
                `).join('');
            }

            html += '</ul>';
            listEl.innerHTML = html;
        });
}

function showAddUserForm() {
    const content = document.getElementById('main-content');

    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Додати користувача</h2>
            <label>Тип:
                <select id="user-type">
                    <option value="student">Учень</option>
                    <option value="parent">Батько/Мати</option>
                    <option value="teacher">Викладач</option>
                </select>
            </label><br>
            <label>Прізвище: <input id="user-lastname" type="text"></label><br>
            <label>Ім’я: <input id="user-firstname" type="text"></label><br>
            <div id="extra-fields"></div>
            <button onclick="submitAddUser()">Зберегти</button>
            <button onclick="showUserManagement()">Назад</button>
        </section>
    `;

    document.getElementById('user-type').addEventListener('change', updateExtraFields);
    updateExtraFields();
}

function updateExtraFields() {
    const type = document.getElementById('user-type').value;
    const extra = document.getElementById('extra-fields');

    if (type === 'student') {
        fetch('/api/classes').then(res => res.json()).then(classes => {
            const classOptions = classes.map(c =>
                `<option value="${c.id}">${c.class_number}-${c.subclass}</option>`).join('');
            extra.innerHTML = `
                <label>По батькові: <input id="student-middlename"></label><br>
                <label>Клас:
                    <select id="student-class-id">${classOptions}</select>
                </label><br>
                <label>Номер телефону одного з батьків: <input id="student-parent-phone"></label><br>
            `;
        });
    } else if (type === 'parent') {
        extra.innerHTML = `<label>Телефон: <input id="parent-phone"></label>`;
    } else if (type === 'teacher') {
        fetch('/api/subjects')
            .then(res => res.json())
            .then(subjects => {
                const subjectOptions = subjects.map(s =>
                    `<option value="${s.subject_id}">${s.title}</option>`).join('');
                extra.innerHTML = `
                    <label>По батькові: <input id="teacher-middle"></label><br>
                    <label>Зарплата: <input id="teacher-salary" type="number" step="0.01"></label><br>
                    <label>Дата народження: <input id="teacher-birth" type="date"></label><br>
                    <label>Дата прийому: <input id="teacher-hire" type="date"></label><br>
                    <label>Предмети (утримуйте Ctrl або ⌘ для вибору кількох):</label><br>
                    <select id="teacher-subjects" multiple size="5" style="width: 300px; max-width: 100%;">
                        ${subjectOptions}
                    </select><br><br>
                `;
            });
    } else {
        extra.innerHTML = '';
    }
}

function submitAddUser() {
    const type = document.getElementById('user-type').value;
    const lastName = document.getElementById('user-lastname').value.trim();
    const firstName = document.getElementById('user-firstname').value.trim();

    if (!lastName || !firstName) {
        alert("❗ Заповніть ім’я та прізвище");
        return;
    }

    const body = {
        last_name: lastName,
        first_name: firstName
    };

    if (type === 'student') {
        const middleName = document.getElementById('student-middlename').value.trim();
        const classId = document.getElementById('student-class-id').value;
        const parentPhone = document.getElementById('student-parent-phone').value.trim();

        if (!classId || !parentPhone) {
            alert("❗ Заповніть усі поля для учня");
            return;
        }

        body.middle_name = middleName;
        body.class_id = classId;
        body.parent_phone = parentPhone;

    } else if (type === 'parent') {
        const phone = document.getElementById('parent-phone').value.trim();
        if (!phone) {
            alert("❗ Введіть номер телефону");
            return;
        }
        body.phone = phone;

    } else if (type === 'teacher') {
        const middle = document.getElementById('teacher-middle').value.trim();
        const salary = parseFloat(document.getElementById('teacher-salary').value);
        const birth = document.getElementById('teacher-birth').value;
        const hire = document.getElementById('teacher-hire').value;
        const subjects = Array.from(document.getElementById('teacher-subjects').selectedOptions).map(opt => +opt.value);

        if (!salary || !birth || !hire || subjects.length === 0) {
            alert("❗ Заповніть усі поля для викладача");
            return;
        }

        body.middle_name = middle;
        body.salary = salary;
        body.birth_date = birth;
        body.hire_date = hire;
        body.subject_ids = subjects;
    }

    fetch(`/api/${type}s`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showUserManagement();
        } else {
            alert("❌ Помилка: " + data.error);
        }
    })
    .catch(err => alert("❌ Серверна помилка: " + err.message));
}

function showEditUserForm(type, id) {
    if (type === 'teacher') {
        Promise.all([
            fetch(`/api/teachers`).then(res => res.json()),
            fetch(`/api/subjects`).then(res => res.json())
        ]).then(([teachers, subjects]) => {
            const t = teachers.find(t => t.user_id === id);
            if (!t) return alert("Викладача не знайдено");

            const subjectOptions = subjects.map(s => `
                <option value="${s.subject_id}" ${t.subject_ids.includes(s.subject_id) ? 'selected' : ''}>
                    ${s.title}
                </option>`).join('');

            const content = document.getElementById("main-content");
            content.innerHTML = `
                <section class="dashboard-section">
                    <h2>Редагувати викладача</h2>
                    <label>Прізвище: <input id="edit-lastname" value="${t.last_name}"></label><br>
                    <label>Ім'я: <input id="edit-firstname" value="${t.first_name}"></label><br>
                    <label>По батькові: <input id="edit-middlename" value="${t.middle_name || ''}"></label><br>
                    <label>Зарплата: <input id="teacher-salary" type="number" value="${t.salary}"></label><br>
                    <label>Дата народження: <input id="teacher-birth" type="date" value="${t.birth_date}"></label><br>
                    <label>Дата прийому: <input id="teacher-hire" type="date" value="${t.hire_date}"></label><br>
                    <label>Предмети:</label><br>
                    <select id="teacher-subjects" multiple size="5" style="width: 300px;">
                        ${subjectOptions}
                    </select><br><br>
                    <button onclick="submitEditUser('teacher', ${id})">Зберегти</button>
                    <button onclick="showUserManagement()">Назад</button>
                </section>
            `;
        });
    } else {
        fetch(`/api/${type}s/${id}`)
            .then(res => res.json())
            .then(user => {
                const content = document.getElementById('main-content');
                let extraField = '';

                if (type === 'student') {
                    fetch('/api/classes')
                        .then(res => res.json())
                        .then(classes => {
                            const options = classes.map(c => {
                                const selected = String(c.id) === String(user.class_id) ? 'selected' : '';
                                return `<option value="${c.id}" ${selected}>${c.class_number}-${c.subclass}</option>`;
                            }).join('');

                            content.innerHTML = `
                                <section class="dashboard-section">
                                    <h2>Редагувати учня</h2>
                                    <label>Прізвище: <input id="edit-lastname" value="${user.last_name}"></label><br>
                                    <label>Ім’я: <input id="edit-firstname" value="${user.first_name}"></label><br>
                                    <label>По батькові: <input id="edit-middlename" value="${user.middle_name || ''}"></label><br>
                                    <label>Клас: <select id="edit-class-id">${options}</select></label><br>
                                    <label>Телефон батьків: <input id="edit-parent-phone" value="${user.parent_phone || ''}"></label><br>
                                    <button onclick="submitEditUser('${type}', ${id})">Зберегти</button>
                                    <button onclick="showUserManagement()">Назад</button>
                                </section>
                            `;
                        });
                } else {
                    extraField = `<label>Телефон: <input id="edit-phone" value="${user.phone}"></label><br>`;
                    content.innerHTML = `
                        <section class="dashboard-section">
                            <h2>Редагувати батька/матір</h2>
                            <label>Прізвище: <input id="edit-lastname" value="${user.last_name}"></label><br>
                            <label>Ім’я: <input id="edit-firstname" value="${user.first_name}"></label><br>
                            ${extraField}
                            <button onclick="submitEditUser('${type}', ${id})">Зберегти</button>
                            <button onclick="showUserManagement()">Назад</button>
                        </section>
                    `;
                }
            });
    }
}

function submitEditUser(type, id) {
    const body = {
        first_name: document.getElementById('edit-firstname').value.trim(),
        last_name: document.getElementById('edit-lastname').value.trim(),
        middle_name: document.getElementById('edit-middlename')?.value.trim() || ''
    };

    if (!body.first_name || !body.last_name) {
        alert("❗ Заповніть обов’язкові поля");
        return;
    }

    if (type === 'student') {
        body.class_id = document.getElementById('edit-class-id').value;
        body.parent_phone = document.getElementById('edit-parent-phone').value.trim();
    } else if (type === 'parent') {
        body.phone = document.getElementById('edit-phone').value.trim();
    } else if (type === 'teacher') {
        body.salary = parseFloat(document.getElementById('teacher-salary').value);
        body.birth_date = document.getElementById('teacher-birth').value;
        body.hire_date = document.getElementById('teacher-hire').value;
        body.subject_ids = Array.from(document.getElementById('teacher-subjects').selectedOptions).map(opt => +opt.value);

        if (!body.salary || !body.birth_date || !body.hire_date || body.subject_ids.length === 0) {
            alert("❗ Заповніть усі поля викладача");
            return;
        }
    }

    fetch(`/api/${type}s/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then(res => {
        if (!res.ok) return res.json().then(data => { throw new Error(data.error || "Помилка оновлення") });
        return res.json();
    })
    .then(() => showUserManagement())
    .catch(err => alert("❌ " + err.message));
}

function deleteUser(type, id) {
    let confirmMessage = "Ви впевнені, що хочете видалити цього користувача?";
    if (type === 'teacher') confirmMessage = "Ви дійсно хочете видалити викладача?";

    if (confirm(confirmMessage)) {
        fetch(`/api/${type}s/${id}`, { method: 'DELETE' })
            .then(() => {
                if (type === 'teacher') {
                    loadUserList('teacher');
                } else {
                    showUserManagement();
                }
            })
            .catch(err => alert("❌ Помилка при видаленні: " + err.message));
    }
}

function showSubjects() {
    fetch('/api/subjects')
        .then(res => res.json())
        .then(subjects => {
            const content = document.getElementById("main-content");

            let rows = subjects.map(sub => `
                <tr>
                    <td>${sub.title}</td>
                    <td>${sub.first_teaching_grade}</td>
                    <td>${sub.last_teaching_grade}</td>
                    <td>
                        <button class = "btn-small" onclick="editSubject(${sub.subject_id})">✏️ Редагувати</button>
                        <button class = "btn-small red" onclick="deleteSubject(${sub.subject_id})">🗑️ Видалити</button>
                    </td>
                </tr>
            `).join("");

            content.innerHTML = `
                <section class="dashboard-section">
                  <h2>Предмети</h2>
                  <div style="margin-bottom: 1rem;">
                    <button onclick="showAddSubjectForm()" style="background-color: #16558F; color: white; padding: 8px 16px; border-radius: 8px; border: none;">
                      ➕ Додати предмет
                    </button>
                  </div>
                  <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 8px rgba(0,0,0,0.1);">
                    <thead style="background-color: #f0f0f0; text-align: left;">
                      <tr>
                        <th style="padding: 12px;">Назва</th>
                        <th style="padding: 12px;">З класу</th>
                        <th style="padding: 12px;">До класу</th>
                        <th style="padding: 12px;">Дії</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${subjects.map(sub => `
                        <tr>
                          <td style="padding: 12px;">${sub.title}</td>
                          <td style="padding: 12px;">${sub.first_teaching_grade}</td>
                          <td style="padding: 12px;">${sub.last_teaching_grade}</td>
                          <td style="padding: 12px;">
                            <button class = "btn-small" onclick="editSubject(${sub.subject_id})">
                              ✏️ Редагувати
                            </button>
                            <button class = "btn-small red" onclick="deleteSubject(${sub.subject_id})">
                              🗑️ Видалити
                            </button>
                          </td>
                        </tr>
                      `).join("")}
                    </tbody>
                  </table>
                </section>
                `;
        });
}

function showAddSubjectForm() {
    const content = document.getElementById("main-content");
    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Додати предмет</h2>
            <label>Назва: <input id="subject-title" type="text"></label><br>
            <label>З класу: <input id="first-grade" type="number" min="1" max="11"></label><br>
            <label>До класу: <input id="last-grade" type="number" min="1" max="11"></label><br>
            <button onclick="submitNewSubject()">Зберегти</button>
            <button onclick="showSubjects()">Назад</button>
        </section>
    `;
}

function submitNewSubject() {
    const title = document.getElementById("subject-title").value.trim();
    const first = document.getElementById("first-grade").value;
    const last = document.getElementById("last-grade").value;

    if (!title || !first || !last) {
        alert("❗ Усі поля обов'язкові");
        return;
    }

    fetch("/api/subjects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title: title,
            first_teaching_grade: parseInt(first),
            last_teaching_grade: parseInt(last)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) throw new Error(data.error || "Помилка додавання");
        showSubjects();
    })
    .catch(err => alert(err.message));
}

function editSubject(subjectId) {
    fetch(`/api/subjects`)
        .then(res => res.json())
        .then(subjects => {
            const subject = subjects.find(s => s.subject_id === subjectId);
            if (!subject) return alert("❗ Предмет не знайдено");

            const content = document.getElementById("main-content");
            content.innerHTML = `
                <section class="dashboard-section">
                    <h2>Редагувати предмет</h2>
                    <label>Назва: <input id="subject-title" type="text" value="${subject.title}"></label><br>
                    <label>З класу: <input id="first-grade" type="number" value="${subject.first_teaching_grade}" min="1" max="11"></label><br>
                    <label>До класу: <input id="last-grade" type="number" value="${subject.last_teaching_grade}" min="1" max="11"></label><br>
                    <button onclick="submitSubjectEdit(${subject.subject_id})">Зберегти</button>
                    <button onclick="showSubjects()">Назад</button>
                </section>
            `;
        });
}

function submitSubjectEdit(subjectId) {
    const title = document.getElementById("subject-title").value.trim();
    const first = document.getElementById("first-grade").value;
    const last = document.getElementById("last-grade").value;

    if (!title || !first || !last) {
        alert("❗ Усі поля обов'язкові");
        return;
    }

    fetch(`/api/subjects/${subjectId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title: title,
            first_teaching_grade: parseInt(first),
            last_teaching_grade: parseInt(last)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) throw new Error(data.error || "Помилка оновлення");
        showSubjects();
    })
    .catch(err => alert(err.message));
}

function deleteSubject(id) {
    if (!confirm("Ви впевнені, що хочете видалити цей предмет?")) return;

    fetch(`/api/subjects/${id}`, { method: 'DELETE' })
        .then(res => {
            if (!res.ok) return res.json().then(err => Promise.reject(err));
            return res.json();
        })
        .then(data => {
            if (data.success) {
                loadSubjects();  // або showSubjectList();
            } else {
                alert("❌ " + (data.error || "Не вдалося видалити предмет"));
            }
        })
        .catch(err => {
            alert("❌ " + (err.error || "Сталася помилка при видаленні предмета"));
        });
}


function showScheduleReport() {
    const content = document.getElementById('main-content');
    content.innerHTML = `
        <section class="dashboard-section">
            <h2>Звіт по розкладу</h2>
            <label>Оберіть клас:
                <select id="report-class-select">
                    <option disabled selected>-- Виберіть клас --</option>
                </select>
            </label>
            <button id="open-preview">🖨️ Друкувати</button>
        </section>
    `;

    fetch('/api/classes')
        .then(res => res.json())
        .then(classes => {
            const select = document.getElementById('report-class-select');
            classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls.id;
                option.textContent = cls.name;
                select.appendChild(option);
            });
        });

    document.getElementById('open-preview').addEventListener('click', () => {
        const classId = document.getElementById('report-class-select').value;
        if (!classId) {
            alert("❗ Спочатку виберіть клас");
            return;
        }

        fetch(`/api/reports/schedule/preview/${classId}`)
            .then(res => res.text())
            .then(html => {
                const printFrame = document.createElement('iframe');
                printFrame.style.position = 'fixed';
                printFrame.style.right = '0';
                printFrame.style.bottom = '0';
                printFrame.style.width = '0';
                printFrame.style.height = '0';
                printFrame.style.border = 'none';
                document.body.appendChild(printFrame);

                printFrame.contentDocument.open();
                printFrame.contentDocument.write(html);
                printFrame.contentDocument.close();

                printFrame.onload = () => {
                    printFrame.contentWindow.focus();
                    printFrame.contentWindow.print();
                    setTimeout(() => {
                        document.body.removeChild(printFrame);
                    }, 1000);
                };
            })
            .catch(err => {
                console.error("❌ Помилка завантаження розкладу:", err);
                alert("❌ Не вдалося згенерувати звіт.");
            });
    });
}