;(function(){
  const BASE = window.BASE;
  const CURRENT_USER_ID = window.CURRENT_USER_ID;
  let selectedClass = null;
  let activeParent = null;

  // Завантажити класи вчителя
  async function loadClasses() {
    const container = document.getElementById('class-list');
    container.innerHTML = '<li>Завантаження...</li>';
    try {
      const res = await fetch(`${BASE}/api/messenger/classes`);
      if (!res.ok) throw new Error("Не вдалося завантажити класи");
      const classes = await res.json();
      if (!classes.length) {
        container.innerHTML = '<li>Немає класів</li>';
        return;
      }
      container.innerHTML = classes.map(c =>
        `<li><button class="class-btn" data-id="${c.class_id}">${c.title}</button></li>`
      ).join('');
      document.querySelectorAll('.class-btn').forEach(btn => {
        btn.onclick = () => onClassClick(btn);
      });
    } catch(err) {
      container.innerHTML = '<li style="color:#d33;">Помилка завантаження</li>';
    }
  }

  // При виборі класу
  async function onClassClick(btn) {
    document.querySelectorAll('.class-btn').forEach(x=>x.classList.remove('active'));
    btn.classList.add('active');
    selectedClass = btn.dataset.id;
    activeParent = null;
    loadParents(selectedClass);
    document.getElementById('chat-header').innerText = "Оберіть батька";
    document.getElementById('messages').innerHTML = '';
    document.getElementById('msg-text').value = '';
  }

  // Завантажити батьків класу
  async function loadParents(classId) {
    const container = document.getElementById('parent-list');
    container.innerHTML = '<li>Завантаження...</li>';
    try {
      const res = await fetch(`${BASE}/api/messenger/parents?class_id=${classId}`);
      if (!res.ok) throw new Error("Не вдалося завантажити батьків");
      const parents = await res.json();
      if (!parents.length) {
        container.innerHTML = '<li>Батьків не знайдено</li>';
        return;
      }
      container.innerHTML = parents.map(p =>
        `<li><button class="parent-btn" data-id="${p.id}">${p.name}</button></li>`
      ).join('');
      document.querySelectorAll('.parent-btn').forEach(btn => {
        btn.onclick = () => onParentClick(btn);
      });
    } catch(err) {
      container.innerHTML = '<li style="color:#d33;">Помилка завантаження</li>';
    }
  }

  // Вибір батька — завантажити чат
  async function onParentClick(btn) {
    document.querySelectorAll('.parent-btn').forEach(x=>x.classList.remove('active'));
    btn.classList.add('active');
    activeParent = btn.dataset.id;
    document.getElementById('chat-header').innerText = btn.innerText;
    await loadMessages();
  }

  // Завантажити повідомлення
  async function loadMessages() {
    if (!activeParent) return;
    const ct = document.getElementById('messages');
    ct.innerHTML = '<div class="no-messages">Завантаження...</div>';
    try {
      const res = await fetch(`${BASE}/api/messenger/messages/${activeParent}`);
      if (!res.ok) throw new Error();
      const msgs = await res.json();
      if (!msgs.length) {
        ct.innerHTML = `<div class="no-messages">Почніть розмову!</div>`;
        return;
      }
      ct.innerHTML = msgs.map(m => {
        const cls = (m.from == CURRENT_USER_ID) ? 'message you' : 'message other';
        return `<div class="${cls}">
          ${m.text}
          <time>${(new Date(m.sentAt)).toLocaleString('uk-UA', { hour: '2-digit', minute: '2-digit' })}</time>
        </div>`;
      }).join('');
      ct.scrollTop = ct.scrollHeight;
    } catch {
      ct.innerHTML = '<div class="no-messages" style="color:#d33;">Не вдалося завантажити повідомлення</div>';
    }
  }

  // Надсилання повідомлення
  document.getElementById('send-btn').onclick = async () => {
    const txt = document.getElementById('msg-text').value.trim();
    if (!txt || !activeParent) return;
    const res = await fetch(`${BASE}/api/messenger/send`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ receiver_id: activeParent, text: txt })
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

  window.addEventListener('DOMContentLoaded', loadClasses);
})();
