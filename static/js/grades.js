// static/js/grades.js
;(function() {
  // Базова частина URL
  const BASE = window.location.origin;
  // Початок тижня з атрибута <body data-week-start="YYYY-MM-DD">
  const WS   = document.body.dataset.weekStart;

  // Функція навігації між тижнями
  function changeWeek(deltaDays) {
    const url = new URL(window.location.href);
    // Якщо в URL вже є ?week_start=…, беремо його, інакше – WS
    const startStr = url.searchParams.get('week_start') || WS;
    const d = new Date(startStr);
    d.setDate(d.getDate() + deltaDays);
    // Оновлюємо параметр і перезавантажуємо
    url.searchParams.set('week_start', d.toISOString().slice(0,10));
    window.location.href = url.toString();
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Прив’язуємо кнопки ← і →
    const prevBtn = document.getElementById('prev-week');
    const nextBtn = document.getElementById('next-week');
    if (prevBtn) prevBtn.addEventListener('click', () => changeWeek(-7));
    if (nextBtn) nextBtn.addEventListener('click', () => changeWeek(7));

    // Існуючий код для «Виставити оцінки»
    document.querySelectorAll('.set-grade-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const lessonId = btn.dataset.lesson;
        const classId  = btn.dataset.class;

        try {
          const resp = await fetch(
            `${BASE}/teacher/grades/students?class_id=${classId}`
          );
          if (!resp.ok) throw new Error('Не вдалося завантажити учнів');
          const students = await resp.json();

          // 1) overlay
          const overlay = document.createElement('div');
          overlay.className = 'modal-overlay';
          document.body.appendChild(overlay);

          // 2) вікно
          const modal = document.createElement('div');
          modal.className = 'modal';
          modal.innerHTML = `
            <h3>Оберіть учня</h3>
            <ul class="student-list">
              ${students.map(s => 
                `<li data-id="${s.id}">
                   ${s.name}${s.existing_grade!=null?` (${s.existing_grade})`:''}
                 </li>`
              ).join('')}
            </ul>
          `;
          document.body.appendChild(modal);

          // закриття по кліку поза вікном
          overlay.onclick = () => { overlay.remove(); modal.remove(); };

          // 3) вибір учня
          modal.querySelectorAll('.student-list li').forEach(li => {
            li.addEventListener('click', () => {
              // прибираємо попередні форми
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
                <input type="text" class="grade-com" placeholder="Коментар" />
                <button>Поставити</button>
              `;
              li.after(form);

              // 4) збереження
              form.querySelector('button').onclick = async () => {
                const value   = form.querySelector('.grade-val').value;
                const comment = form.querySelector('.grade-com').value;
                const payload = {
                  lesson_id:  lessonId,
                  student_id: li.dataset.id,
                  value, comment
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
