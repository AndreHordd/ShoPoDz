// static/js/grades.js
;(function() {
  const BASE = window.location.origin;
  const WS   = document.body.dataset.weekStart;

  function changeWeek(delta) {
    /* … */
  }

  document.addEventListener('DOMContentLoaded', () => {
    /* … навігація по тижнях … */

    document.querySelectorAll('.set-grade-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const lessonId = btn.dataset.lesson;
        const classId  = btn.dataset.class;

        try {
          const resp = await fetch(`${BASE}/teacher/grades/students?class_id=${classId}`);
          if (!resp.ok) throw new Error('Не вдалося завантажити учнів');
          const students = await resp.json();

          // 1) створюємо overlay
          const overlay = document.createElement('div');
          overlay.className = 'modal-overlay';
          document.body.appendChild(overlay);

          // 2) створюємо сам модал
          const modal = document.createElement('div');
          modal.className = 'modal';
          modal.innerHTML = `
            <h3>Оберіть учня</h3>
            <ul class="student-list">
              ${students.map(s => `<li data-id="${s.id}">${s.name}</li>`).join('')}
            </ul>
          `;
          document.body.appendChild(modal);

          // клік поза вікном закриває модал
          overlay.addEventListener('click', () => {
            overlay.remove();
            modal.remove();
          });

          // 3) вибір учня
          modal.querySelectorAll('.student-list li').forEach(li => {
            li.addEventListener('click', () => {
              // прибираємо попередню форму
              modal.querySelectorAll('.grade-form').forEach(f => f.remove());

              const form = document.createElement('div');
              form.className = 'grade-form';
              form.innerHTML = `
                <select class="grade-val">
                  ${Array.from({length:12}, (_,i)=>`<option value="${i+1}">${i+1}</option>`).join('')}
                </select>
                <input type="text" class="grade-com" placeholder="Коментар" />
                <button>Поставити</button>
              `;
              li.after(form);

              // 4) зберігаємо оцінку
              form.querySelector('button').addEventListener('click', async () => {
                const value   = form.querySelector('.grade-val').value;
                const comment = form.querySelector('.grade-com').value;
                const res = await fetch(`${BASE}/teacher/grades/add`, {
                  method: 'POST',
                  headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({
                    lesson_id:  lessonId,
                    student_id: li.dataset.id,
                    value, comment
                  })
                });
                if (res.ok) {
                  window.location.reload();
                } else {
                  const err = await res.json();
                  alert(err.error || 'Помилка збереження');
                }
              });
            });
          });
        } catch (e) {
          alert(e.message);
        }
      });
    });
  });
})();
