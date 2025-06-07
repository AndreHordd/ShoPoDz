document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/teacher/schedule")
    .then(r => r.json())
    .then(data => {
      const tbody = document.getElementById("schedule-body");
      tbody.innerHTML = "";

      const dayName = [
        "",                    // 0 (не використ.)
        "Понеділок",
        "Вівторок",
        "Середа",
        "Четвер",
        "Пʼятниця",
        "Субота",
        "Неділя"
      ];

      data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${dayName[row.day]}</td>
          <td>${row.start_time}</td>
          <td>${row.end_time}</td>
          <td>${row.class}</td>
          <td>${row.subject}</td>
          <td>${row.room_number}</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(err => console.error("schedule fetch error", err));
});
