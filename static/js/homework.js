// читаємо початок тижня із data-атрибуту body
const WEEK_START = document.body.dataset.weekStart;

function changeWeek(deltaDays) {
  const url = new URL(window.location.href);
  let start = url.searchParams.get('week_start') || WEEK_START;
  let d = new Date(start);
  d.setDate(d.getDate() + deltaDays);
  url.searchParams.set('week_start', d.toISOString().slice(0,10));
  window.location.href = url;
}

document.addEventListener('DOMContentLoaded', () => {
  // кнопки навігації по тижнях
  document.getElementById('prev-week')
          .addEventListener('click', () => changeWeek(-7));
  document.getElementById('next-week')
          .addEventListener('click', () => changeWeek(7));

  // Додати домашку
  document.querySelectorAll('.add-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const lessonId = btn.dataset.lesson;
      const description = prompt('Умова домашнього завдання:');
      if (!description) return;
      const deadline = prompt(
        'Крайній термін (YYYY-MM-DD):',
        new Date().toISOString().slice(0,10)
      );
      const res = await fetch(`/teacher/homework/add`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({lesson_id: lessonId, description, deadline})
      });
      if (res.ok) window.location.reload();
      else alert((await res.json()).error);
    });
  });

  // Редагувати домашку
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const hwId = btn.dataset.id;
      const currentDesc = btn.closest('tr')
                             .querySelector('td:nth-child(3)')
                             .innerText.trim();
      const description = prompt('Нова умова:', currentDesc);
      if (description === null) return;
      const deadline = prompt(
        'Крайній термін (YYYY-MM-DD):',
        new Date().toISOString().slice(0,10)
      );
      const res = await fetch(`/teacher/homework/${hwId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({description, deadline})
      });
      if (res.ok) window.location.reload();
      else alert((await res.json()).error);
    });
  });

  // Видалити домашку
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Ви дійсно хочете видалити?')) return;
      const hwId = btn.dataset.id;
      const res = await fetch(`/teacher/homework/${hwId}`, {
        method: 'DELETE'
      });
      if (res.ok) window.location.reload();
      else alert((await res.json()).error);
    });
  });
});
