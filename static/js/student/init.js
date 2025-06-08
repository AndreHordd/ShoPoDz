export default function initSidebar(renderers, fetchPanel) {
    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('side-menu')
            .addEventListener('click', e => {
                const link = e.target.closest('a[data-target]');
                if (!link) return;
                e.preventDefault();

                document.querySelectorAll('#side-menu a[data-target]')
                    .forEach(a => a.classList.toggle('active', a === link));

                const target = link.dataset.target;
                document.querySelectorAll('.panel')
                    .forEach(p => p.hidden = p.id !== target);

                if (!link.dataset.loaded) {
                    fetchPanel(target, renderers[target]);
                    link.dataset.loaded = '1';
                }
            });

        document.getElementById('homework')
            .addEventListener('click', e => {
                const btn = e.target.closest('.hw-toggle-btn');
                if (btn) {
                    fetchPanel('homework', renderers.homework, { toggleId: btn.dataset.id });
                }
            });

        // відкриваємо першу вкладку
        document.querySelector('#side-menu a[data-target="schedule"]').click();
    });
}
