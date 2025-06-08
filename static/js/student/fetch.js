export function fetchPanel(name, cb, opts) {
    let url = `/student/api/${name}`;
    let init = {};
    if (name === 'homework' && opts && opts.toggleId) {
        url += `/${opts.toggleId}/toggle`;
        init = { method: 'POST' };
    }
    fetch(url, init)
        .then(r => r.json())
        .then(cb)
        .catch(err => inject(name, `<p class="error">${err}</p>`));
}
