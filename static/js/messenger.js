;(function(){
  const BASE = window.BASE;
  const CURRENT_USER_ID = window.CURRENT_USER_ID;
  let activePeer = null;

  async function loadClasses() {
    const container = document.getElementById('class-list');
    try {
      const res = await fetch(`${BASE}/api/messenger/classes`);
      if (!res.ok) throw new Error(`status ${res.status}`);
      const classes = await res.json();
      container.innerHTML = classes.map(c =>
        `<button class="class-btn" data-id="${c.id}">${c.name}</button>`
      ).join('');
      container.querySelectorAll('.class-btn')
        .forEach(btn=> btn.addEventListener('click', ()=> onClassClick(btn)));
    } catch(err) {
      alert('Не вдалося завантажити класи');
    }
  }

  async function onClassClick(btn) {
    document.querySelectorAll('.class-btn').forEach(x=>x.classList.remove('active'));
    btn.classList.add('active');

    const cid = btn.dataset.id;
    const parentList = document.getElementById('parent-list');
    parentList.innerHTML = '';
    document.getElementById('chat-header').innerText = 'Завантажуємо батьків…';

    try {
      const res = await fetch(`${BASE}/api/messenger/parents?class_id=${cid}`);
      if (!res.ok) throw new Error(`status ${res.status}`);
      const parents = await res.json();
      document.getElementById('chat-header').innerText = 'Оберіть батька';
      parentList.innerHTML = parents.map(p =>
        `<li data-id="${p.id}">${p.name}</li>`
      ).join('');
      parentList.querySelectorAll('li')
        .forEach(li=> li.addEventListener('click', ()=> onParentClick(li)));
      document.getElementById('messages').innerHTML = '';
      activePeer = null;
    } catch(err) {
      alert('Не вдалося завантажити батьків');
      document.getElementById('chat-header').innerText = 'Оберіть клас';
    }
  }

  async function onParentClick(li) {
    document.querySelectorAll('#parent-list li').forEach(x=>x.classList.remove('active'));
    li.classList.add('active');
    activePeer = li.dataset.id;
    document.getElementById('chat-header').innerText = li.innerText;
    await loadMessages();
  }

  async function loadMessages() {
    if (!activePeer) return;
    try {
      const res = await fetch(`${BASE}/api/messenger/messages/${activePeer}`);
      if (!res.ok) throw new Error(`status ${res.status}`);
      const msgs = await res.json();
      const ct = document.getElementById('messages');
      ct.innerHTML = msgs.map(m=>{
        const cls = (m.from == CURRENT_USER_ID) ? 'you' : 'other';
        return `<div class="message ${cls}">
                  ${m.text}
                  <time>${new Date(m.sentAt).toLocaleTimeString()}</time>
                </div>`;
      }).join('');
      ct.scrollTop = ct.scrollHeight;
    } catch(err) {
      alert('Не вдалося завантажити повідомлення');
    }
  }

  document.getElementById('send-btn').addEventListener('click', async ()=>{
    const txt = document.getElementById('msg-text').value.trim();
    if (!txt || !activePeer) return;
    try {
      const res = await fetch(`${BASE}/api/messenger/send`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          receiver_id: activePeer,
          text: txt
        })
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      document.getElementById('msg-text').value = '';
      await loadMessages();
    } catch(err) {
      alert('Не вдалося відправити повідомлення');
    }
  });

  window.addEventListener('DOMContentLoaded', loadClasses);
})();
