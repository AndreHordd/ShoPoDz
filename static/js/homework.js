// Дата початку тижня (ISO-формат)
const WEEK_START = document.body.dataset.weekStart;

// Відображення модального вікна для додавання/редагування ДЗ
function openHWModal({title, desc = '', date = '', onSave}) {
  document.getElementById('hw-modal-title').innerText = title;
  document.getElementById('hw-desc').value = desc;
  document.getElementById('hw-date').value = date;
  document.getElementById('hw-modal').style.display = 'flex';

  // flatpickr календар
  if (window.hwFlatpickr) window.hwFlatpickr.destroy();
  window.hwFlatpickr = flatpickr("#hw-date", {
    dateFormat: "Y-m-d",
    locale: "uk",
    minDate: "today",
    defaultDate: date,
    disableMobile: true
  });

  document.getElementById('hw-modal-close').onclick = () => {
    document.getElementById('hw-modal').style.display = 'none';
    document.getElementById('hw-form').onsubmit = null;
    if (window.hwFlatpickr) window.hwFlatpickr.destroy();
  };

  // Клік по бекдропу для закриття
  document.getElementById('hw-modal').onclick = (e) => {
    if (e.target === document.getElementById('hw-modal')) {
      document.getElementById('hw-modal-close').click();
    }
  };

  document.getElementById('hw-form').onsubmit = async (e) => {
    e.preventDefault();
    const description = document.getElementById('hw-desc').value.trim();
    const deadline = document.getElementById('hw-date').value;
    if (!description || !deadline) return;
    try {
      await onSave({description, deadline});
      document.getElementById('hw-modal').style.display = 'none';
      document.getElementById('hw-form').onsubmit = null;
      if (window.hwFlatpickr) window.hwFlatpickr.destroy();
    } catch (err) {
      showHWError(err.message || "Виникла помилка");
    }
  };
}

// Помилка — показати модальне вікно з текстом
function showHWError(msg) {
  document.getElementById('hw-error-message').innerText = msg;
  document.getElementById('hw-error-modal').style.display = 'flex';
  document.getElementById('hw-error-close').onclick = () => {
    document.getElementById('hw-error-modal').style.display = 'none';
  };
}


// Перехід по тижнях
function changeWeek(deltaDays) {
   document.getElementById('hw-modal').style.display = 'none';
  document.getElementById('hw-error-modal').style.display = 'none';
  document.getElementById('hw-delete-modal').style.display = 'none';
  const url = new URL(window.location.href);
  let start = url.searchParams.get('week_start') || WEEK_START;
  let d = new Date(start);
  d.setDate(d.getDate() + deltaDays);
  url.searchParams.set('week_start', d.toISOString().slice(0,10));
  window.location.href = url;
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('prev-week').addEventListener('click', () => changeWeek(-7));
  document.getElementById('next-week').addEventListener('click', () => changeWeek(7));

  // ДОДАТИ ДЗ
document.querySelectorAll('.add-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const classId   = btn.dataset.class;
    const subjectId = btn.dataset.subject;
    const dateStr   = btn.dataset.date;
    openHWModal({
      title: 'Додати домашнє завдання',
      date: dateStr,
      onSave: async ({description, deadline}) => {
        // перевіряємо дату локально...
        const today = new Date(); today.setHours(0,0,0,0);
        const picked = new Date(deadline); picked.setHours(0,0,0,0);
        if (picked < today) throw new Error("Дату у минулому вибрати не можна!");

        // відсилаємо class_id і subject_id
        const res = await fetch(`/teacher/homework/add`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            class_id:   classId,
            subject_id: subjectId,
            description,
            deadline
          })
        });
        if (res.ok) {
          window.location.reload();
        } else {
          const err = await res.json();
          throw new Error(err.error || "Виникла помилка при додаванні ДЗ");
        }
      }
    });
  });
});


  // РЕДАГУВАТИ ДЗ
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const hwId = btn.dataset.id;
      const desc = btn.dataset.desc || '';
      const deadline = btn.dataset.deadline || new Date().toISOString().slice(0,10);
      openHWModal({
        title: 'Редагувати домашнє завдання',
        desc: desc,
        date: deadline,
        onSave: async ({description, deadline}) => {
          // deadline ігноруємо, він незмінний
          const res = await fetch(`/teacher/homework/${hwId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({description, deadline})
          });
          if (res.ok) window.location.reload();
          else {
            let data = await res.json();
            throw new Error(data.error || "Виникла помилка при редагуванні ДЗ");
          }
        }
      });
      // Робимо інпут дедлайну недоступним для редагування:
      setTimeout(() => {
        document.getElementById('hw-date').setAttribute('readonly', true);
        document.getElementById('hw-date').setAttribute('disabled', true);
      }, 100);
    });
  });

  // ВИДАЛИТИ ДЗ
  function showHWDeleteModal({onConfirm}) {
    document.getElementById('hw-delete-modal').style.display = 'flex';
    document.getElementById('hw-delete-cancel').onclick = () => {
      document.getElementById('hw-delete-modal').style.display = 'none';
    };
    document.getElementById('hw-delete-confirm').onclick = async () => {
      await onConfirm();
      document.getElementById('hw-delete-modal').style.display = 'none';
    };
  }

  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const hwId = btn.dataset.id;
      showHWDeleteModal({
        onConfirm: async () => {
          const res = await fetch(`/teacher/homework/${hwId}`, {
            method: 'DELETE'
          });
          if (res.ok) window.location.reload();
          else {
            let data = await res.json();
            showHWError(data.error || "Виникла помилка при видаленні ДЗ");
          }
        }
      });
    });
  });

});
