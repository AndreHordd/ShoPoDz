document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".class-button");
    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const container = button.closest(".class-container");
            const studentList = container.querySelector(".students-list");
            studentList.style.display = (studentList.style.display === "none" || !studentList.style.display)
                ? "block"
                : "none";
        });
    });
});
