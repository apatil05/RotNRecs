document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault(); // prevent default form submission

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (password !== confirmPassword) {
        document.getElementById("error-message").style.display = "block";
        document.getElementById("error-message").innerText = "Passwords do not match.";
        return;
    }

    const response = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({name, email, password })
    });

    const data = await response.json();
    console.log(data);
});