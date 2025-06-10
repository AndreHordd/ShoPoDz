;(function() {
  const BASE = window.location.origin;
  const WS   = document.body.dataset.weekStart;

  function changeWeek(deltaDays) {
    const url = new URL(window.location.href);
    const startStr = url.searchParams.get('week_start') || WS;
    const d = new Date(startStr);
    d.setDate(d.getDate() + deltaDays);
    url.searchParams.set('week_start', d.toISOString().slice(0,10));
    window.location.href = url.toString();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const prevBtn = document.getElementById('prev-week');
    const nextBtn = document.getElementById('next-week');
    if (prevBtn) prevBtn.addEventListener('click', () => changeWeek(-7));
    if (nextBtn) nextBtn.addEventListener('click', () => changeWeek(7));

    document.querySelectorAll('.set-grade-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const lessonId = btn.dataset.lesson;
        const classId  = btn.dataset.class;
        const gradeDate = btn.dataset.date; // дата уроку

        try {
          const resp = await fetch(`${BASE}/teacher/grades/students?class_id=${classId}`);
          if (!resp.ok) throw new Error('Не вдалося завантажити учнів');
          const students = await resp.json();

          // Дізнаємось вже виставлені оцінки для цієї пари (lesson_id) і дати (gradeDate)
          const gradesResp = await fetch(
            `${BASE}/teacher/grades/existing?lesson_id=${lessonId}&date=${gradeDate}`
          );
          const gradesArr = gradesResp.ok ? await gradesResp.json() : [];

          const gradesMap = {};
          for (const g of gradesArr) gradesMap[g.student_id] = g;

          // overlay
          const overlay = document.createElement('div');
          overlay.className = 'modal-overlay';
          document.body.appendChild(overlay);

          const modal = document.createElement('div');
          modal.className = 'modal';
          modal.innerHTML = `
            <h3>Оберіть учня</h3>
            <ul class="student-list">
              ${students.map(s => 
                `<li data-id="${s.id}" data-existing="${gradesMap[s.id]?.grade_value ?? ''}">
                   ${s.name}${gradesMap[s.id] ? ` (${gradesMap[s.id].grade_value})` : ''}
                 </li>`
              ).join('')}
            </ul>
          `;
          document.body.appendChild(modal);

          overlay.onclick = () => { overlay.remove(); modal.remove(); };

          modal.querySelectorAll('.student-list li').forEach(li => {
            li.addEventListener('click', () => {
              modal.querySelectorAll('.grade-form').forEach(f=>f.remove());
              const form = document.createElement('div');
              form.className = 'grade-form';
              form.innerHTML = `
                <select class="grade-val">
                  ${Array.from({length:12},(_,i)=>i+1)
                    .map(v=>
                      `<option value="${v}" ${v==li.dataset.existing? 'selected':''}>${v}</option>`
                    ).join('')}
                </select>
                <input type="text" class="grade-com" placeholder="Коментар" value="${gradesMap[li.dataset.id]?.comment || ''}" />
                <button>Поставити</button>
              `;
              li.after(form);

              form.querySelector('button').onclick = async () => {
                const value   = form.querySelector('.grade-val').value;
                const comment = form.querySelector('.grade-com').value;
                const payload = {
                  lesson_id:  lessonId,
                  student_id: li.dataset.id,
                  value, comment,
                  date: gradeDate
                };
                const res = await fetch(`${BASE}/teacher/grades/add`, {
                  method: 'POST',
                  headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify(payload)
                });
                if (res.ok) window.location.reload();
                else {
                  const err = await res.json();
                  alert(err.error || 'Помилка збереження');
                }
              };
            });
          });
        } catch (e) {
          alert(e.message);
        }
      });
    });
  });
})();
