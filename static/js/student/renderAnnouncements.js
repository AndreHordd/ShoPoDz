export function renderAnnouncements(data) {
    inject('announcements', data.map(n => `
        <article>
            <h4>${n.title}</h4>
            <time>${new Date(n.created_at).toLocaleString()}</time>
            <p>${n.text}</p>
        </article>
    `).join(''));
}
