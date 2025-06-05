// admin.js

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('a[href="#schedules"]').addEventListener('click', showClassSelector);
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
                        <button id="edit-btn">Редагувати розклад</button>
                        <button onclick="deleteSchedule('${classId}', '${className}', '${classNumber}')">Видалити розклад</button>
                    </div>
                `;

                content.innerHTML = html;

                document.getElementById('edit-btn').addEventListener('click', () => {
                    createSchedule(classId, className, classNumber, true, schedule);
                });
            } else {
                html += `
                    <div class="button-row" style="margin-top: 20px;">
                        <button onclick="createSchedule('${classId}', '${className}', '${classNumber}', false, null)">Створити розклад</button>
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
