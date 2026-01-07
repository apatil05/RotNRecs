// Login form handler
const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        // Create URLSearchParams to send as application/x-www-form-urlencoded
        const formData = new URLSearchParams();
        formData.append("email", email);
        formData.append("password", password);

        try {
            const response = await fetch("http://localhost:8000/login", {
                method: "POST",
                body: formData
            });

            console.log("Login response status:", response.status);
            
            const responseText = await response.text();
            console.log("Login response text:", responseText);
            
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (parseError) {
                console.error("Failed to parse JSON:", parseError);
                document.getElementById("error-message").style.display = "block";
                document.getElementById("error-message").innerText = "Server returned invalid response. Status: " + response.status;
                return;
            }
            
            if (!response.ok) {
                // Show error message
                document.getElementById("error-message").style.display = "block";
                document.getElementById("error-message").innerText = data.detail || "An error occurred";
            } else {
                // Redirect to dashboard on successful login
                document.getElementById("error-message").style.display = "none";
                window.location.href = "/dashboard";
            }
        } catch (error) {
            document.getElementById("error-message").style.display = "block";
            document.getElementById("error-message").innerText = "Network error: " + error.message;
            console.error("Full error:", error);
            console.error("Error stack:", error.stack);
        }
    });
}

// Register form handler
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

    // Create URLSearchParams to send as application/x-www-form-urlencoded
    const formData = new URLSearchParams();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("password", password);

    try {
        const response = await fetch("http://localhost:8000/register", {
            method: "POST",
            body: formData
        });

        console.log("Response status:", response.status);
        console.log("Response headers:", response.headers);
        
        // Get response text first to see what we're dealing with
        const responseText = await response.text();
        console.log("Response text:", responseText);
        
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            console.error("Failed to parse JSON:", parseError);
            document.getElementById("error-message").style.display = "block";
            document.getElementById("error-message").innerText = "Server returned invalid response. Status: " + response.status;
            return;
        }
        
        console.log("Response data:", data);
        
        if (!response.ok) {
            // Show error message - handle both string and array formats
            document.getElementById("error-message").style.display = "block";
            let errorMsg = "An error occurred";
            if (data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
                } else {
                    errorMsg = data.detail;
                }
            }
            document.getElementById("error-message").innerText = errorMsg;
        } else {
            // Redirect to recommendations page on successful registration
            document.getElementById("error-message").style.display = "none";
            window.location.href = "/recommendations";
        }
    } catch (error) {
        document.getElementById("error-message").style.display = "block";
        document.getElementById("error-message").innerText = "Network error: " + error.message;
        console.error("Full error:", error);
        console.error("Error stack:", error.stack);
    }
});