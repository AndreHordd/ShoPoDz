let currDate = new Date();

function pad(n) { return n < 10 ? '0'+n : n; }
function formatDate(d) {
    return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate());
}
function updateDateDisplay() {
    document.getElementById('curr-date').innerText =
        currDate.toLocaleDateString('uk-UA', {weekday:'long', day:'2-digit', month:'2-digit', year:'numeric'});
}
function changeDay(delta) {
    currDate.setDate(currDate.getDate() + delta);
    loadSessions();
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('prev-day').onclick = () => changeDay(-1);
    document.getElementById('next-day').onclick = () => changeDay(1);
    loadSessions();
});

function loadSessions() {
    updateDateDisplay();
    fetch(`/api/teacher/attendance/sessions?date=${formatDate(currDate)}`)
        .then(r => r.json())
        .then(showSessions);
}
function showSessions(sessions) {
    const cont = document.getElementById('sessions');
    cont.innerHTML = '';
    document.getElementById('students').innerHTML = '';
    if (!sessions.length) {
        cont.innerHTML = '<div class="empty">У цей день у вас немає уроків</div>';
        return;
    }
    sessions.forEach(s => {
        const btn = document.createElement('button');
        btn.innerText = `${s.class_title} (${s.subject}) ${s.start_time}`;
        btn.className = "session-btn";
        btn.onclick = () => {
            if (s.session_id)
                loadStudents(s.session_id, s.class_title, s.subject, s.start_time);
            else
                createSessionAndLoad(s.lesson_id, s.class_title, s.subject, s.start_time);
        };
        cont.appendChild(btn);
    });
}

function createSessionAndLoad(lesson_id, class_title, subject, time) {
    fetch('/api/teacher/attendance/create_session', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            lesson_id: lesson_id,
            date: formatDate(currDate)
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.session_id)
            loadStudents(data.session_id, class_title, subject, time);
        else
            alert(data.error || "Не вдалося створити сесію уроку");
        // Оновити список кнопок
        loadSessions();
    });
}

function loadStudents(session_id, class_title, subject, time) {
    fetch(`/api/teacher/attendance/session/${session_id}`)
        .then(r => r.json())
        .then(students => showStudents(students, session_id, class_title, subject, time));
}

function showStudents(students, session_id, class_title, subject, time) {
    const statusMap = {
        'present': 'Присутній',
        'absent': 'Відсутній',
        'late': 'Запізнився',
        'excused': 'Поваж. причина'
    };
    const statusOptions = [
        {value: "", label: "---"},
        {value: "present", label: "Присутній"},
        {value: "absent", label: "Відсутній"},
        {value: "late", label: "Запізнився"},
        {value: "excused", label: "Поваж. причина"}
    ];
    let html = `<h3>${class_title} — ${subject} (${time})</h3>
    <table class="attendance-table">
    <tr><th>Учень</th><th>Статус</th><th>Коментар</th></tr>`;
    students.forEach(st => {
        html += `<tr>
          <td>${st.full_name}</td>
          <td>
            <select data-student="${st.student_id}">
              ${statusOptions.map(opt =>
                `<option value="${opt.value}"${st.status === opt.value ? ' selected' : ''}>${opt.label}</option>`
              ).join('')}
            </select>
          </td>
          <td>
            <input type="text" value="${st.comment || ''}" data-student="${st.student_id}" />
          </td>
        </tr>`;
    });
    html += '</table>';
    document.getElementById('students').innerHTML = html;

    // Навішуємо події після вставки у DOM
    document.querySelectorAll('.attendance-table select').forEach(select => {
        select.onchange = function() {
            const student_id = this.dataset.student;
            const status = this.value;
            const comment = this.closest('tr').querySelector('input[type="text"]').value;
            markAttendance(session_id, student_id, status, comment);
        };
    });
    document.querySelectorAll('.attendance-table input[type="text"]').forEach(input => {
        input.onblur = function() {
            const student_id = this.dataset.student;
            const status = this.closest('tr').querySelector('select').value;
            const comment = this.value;
            markAttendance(session_id, student_id, status, comment);
        };
    });
}

function markAttendance(session_id, student_id, status, comment="") {
    fetch('/api/teacher/attendance/mark', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({session_id, student_id, status, comment})
    });
}
