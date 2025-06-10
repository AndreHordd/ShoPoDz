;(function(){
  const BASE = window.BASE;
  const CURRENT_USER_ID = window.CURRENT_USER_ID;
  let activeTeacher = null;

  // Завантажити вчителів класу дитини
  async function loadTeachers() {
    const container = document.getElementById('teacher-list');
    container.innerHTML = '<li>Завантаження...</li>';
    try {
      const res = await fetch(`${BASE}/api/messenger/teachers`);
      if (!res.ok) throw new Error("Не вдалося завантажити вчителів");
      const teachers = await res.json();
      if (!teachers.length) {
        container.innerHTML = '<li>Вчителів не знайдено</li>';
        return;
      }
      container.innerHTML = teachers.map(t =>
        `<li><button class="teacher-btn" data-id="${t.id}">${t.name}</button></li>`
      ).join('');
      document.querySelectorAll('.teacher-btn').forEach(btn => {
        btn.onclick = () => onTeacherClick(btn);
      });
    } catch(err) {
      container.innerHTML = '<li style="color:#d33;">Помилка завантаження</li>';
    }
  }

  // При виборі вчителя
  async function onTeacherClick(btn) {
    document.querySelectorAll('.teacher-btn').forEach(x=>x.classList.remove('active'));
    btn.classList.add('active');
    activeTeacher = btn.dataset.id;
    document.getElementById('chat-header').innerText = btn.innerText;
    await loadMessages();
  }

  // --- Відображення дати між повідомленнями ---
  function renderMessagesWithDates(msgs) {
    const ct = document.getElementById('messages');
    ct.innerHTML = '';
    let lastDate = null;
    msgs.forEach(m => {
      const msgDateObj = new Date(m.sentAt);
      const msgDate = msgDateObj.toLocaleDateString('uk-UA', {
        day: 'numeric', month: 'long', year: 'numeric'
      });
      if (msgDate !== lastDate) {
        lastDate = msgDate;
        ct.innerHTML += `
          <div class="chat-date-divider">
            <span>${msgDate}</span>
          </div>
        `;
      }
      const cls = (m.from == CURRENT_USER_ID) ? 'message you' : 'message other';
      ct.innerHTML += `
        <div class="${cls}">
          ${m.text}
          <time>${msgDateObj.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}</time>
        </div>
      `;
    });
    ct.scrollTop = ct.scrollHeight;
  }

  // Завантажити повідомлення
  async function loadMessages() {
    if (!activeTeacher) return;
    const ct = document.getElementById('messages');
    ct.innerHTML = '<div class="no-messages">Завантаження...</div>';
    try {
      const res = await fetch(`${BASE}/api/messenger/messages/${activeTeacher}`);
      if (!res.ok) throw new Error();
      const msgs = await res.json();
      if (!msgs.length) {
        ct.innerHTML = `<div class="no-messages">Почніть розмову!</div>`;
        return;
      }
      renderMessagesWithDates(msgs);
    } catch {
      ct.innerHTML = '<div class="no-messages" style="color:#d33;">Не вдалося завантажити повідомлення</div>';
    }
  }

  // Надсилання повідомлення
  document.getElementById('send-btn').onclick = async () => {
    const txt = document.getElementById('msg-text').value.trim();
    if (!txt || !activeTeacher) return;
    const res = await fetch(`${BASE}/api/messenger/send`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ receiver_id: activeTeacher, text: txt })
    });
    if (res.ok) {
      document.getElementById('msg-text').value = '';
      await loadMessages();
    }
  };

  // Надсилання Enter
  document.getElementById('msg-text').addEventListener('keydown', function(e){
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('send-btn').click();
    }
  });

  window.addEventListener('DOMContentLoaded', loadTeachers);
})();
