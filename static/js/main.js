
// Mobile navigation
const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
        navLinks.classList.toggle("active");

        const expanded = navLinks.classList.contains("active");
        menuToggle.setAttribute("aria-expanded", expanded);
    });
}

// Show/hide password
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("id_password");

if (togglePassword && passwordInput) {
    togglePassword.addEventListener("click", () => {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePassword.textContent = "Hide";
        } else {
            passwordInput.type = "password";
            togglePassword.textContent = "Show";
        }
    });
}

// Automatically hide success/error messages
document.querySelectorAll(".message").forEach((message) => {
    setTimeout(() => {
        message.style.transition = "opacity 0.5s";
        message.style.opacity = "0";

        setTimeout(() => {
            message.remove();
        }, 500);
    }, 4500);
});

document.addEventListener("DOMContentLoaded", function () {

    const menuButton = document.getElementById("adminMenuToggle");
    const sidebar = document.getElementById("adminSidebar");

    if (menuButton && sidebar) {
        menuButton.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }

});
