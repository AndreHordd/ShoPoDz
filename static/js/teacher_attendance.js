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
        .then(r => r.json()).then(showSessions);
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
        btn.onclick = () => loadStudents(s.session_id, s.class_title, s.subject, s.start_time);
        cont.appendChild(btn);
    });
}

function loadStudents(session_id, class_title, subject, time) {
    fetch(`/api/teacher/attendance/session/${session_id}`)
        .then(r => r.json())
        .then(students => showStudents(students, session_id, class_title, subject, time));
}

function showStudents(students, session_id, class_title, subject, time) {
    let html = `<h3>${class_title} — ${subject} (${time})</h3>
    <table class="attendance-table">
    <tr><th>Учень</th><th>Статус</th><th>Коментар</th></tr>`;
    students.forEach(st => {
        html += `<tr>
          <td>${st.full_name}</td>
          <td>
            <select onchange="markAttendance(${session_id},${st.student_id},this.value)">
              <option value="">---</option>
              <option value="present"${st.status==='present'?' selected':''}>Присутній</option>
              <option value="absent"${st.status==='absent'?' selected':''}>Відсутній</option>
              <option value="late"${st.status==='late'?' selected':''}>Запізнився</option>
              <option value="excused"${st.status==='excused'?' selected':''}>Поваж. причина</option>
            </select>
          </td>
          <td>
            <input type="text" value="${st.comment || ''}" 
              onblur="markAttendanceComment(${session_id},${st.student_id},this.parentElement.previousElementSibling.firstChild.value,this.value)">
          </td>
        </tr>`;
    });
    html += '</table>';
    document.getElementById('students').innerHTML = html;
}

window.markAttendance = function(session_id, student_id, status) {
    fetch('/api/teacher/attendance/mark', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({session_id, student_id, status})
    });
}

window.markAttendanceComment = function(session_id, student_id, status, comment) {
    fetch('/api/teacher/attendance/mark', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({session_id, student_id, status, comment})
    });
}
