// Wait for DOM to be ready before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
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
                    const errorMsg = document.getElementById("error-message");
                    if (errorMsg) {
                        errorMsg.style.display = "block";
                        errorMsg.innerText = "Server returned invalid response. Status: " + response.status;
                    }
                    return;
                }
                
                if (!response.ok) {
                    // Show error message
                    const errorMsg = document.getElementById("error-message");
                    if (errorMsg) {
                        errorMsg.style.display = "block";
                        errorMsg.innerText = data.detail || "An error occurred";
                    }
                } else {
                    // Store user_id in localStorage for later use
                    console.log('=== LOGIN SUCCESS ===');
                    console.log('Login response data:', data);
                    console.log('data.user_id:', data.user_id);
                    console.log('Type of data.user_id:', typeof data.user_id);
                    
                    if (data.user_id !== undefined && data.user_id !== null) {
                        const userIdStr = String(data.user_id);
                        console.log('Storing user_id in localStorage:', userIdStr);
                        localStorage.setItem('user_id', userIdStr);
                        
                        // Verify it was stored
                        const stored = localStorage.getItem('user_id');
                        console.log('✅ Verification - user_id in localStorage:', stored);
                        console.log('✅ All localStorage:', {...localStorage});
                        
                        if (!stored || stored !== userIdStr) {
                            console.error('❌ ERROR: user_id was NOT stored correctly!');
                        }
                    } else {
                        console.error('❌ ERROR: No user_id in login response!');
                        console.error('Response data:', JSON.stringify(data, null, 2));
                    }
                    
                    // Redirect to dashboard on successful login
                    const errorMsg = document.getElementById("error-message");
                    if (errorMsg) {
                        errorMsg.style.display = "none";
                    }
                    
                    // Small delay to ensure localStorage is set before redirect
                    setTimeout(() => {
                        console.log('About to redirect. Final check - user_id:', localStorage.getItem('user_id'));
                        window.location.href = "/dashboard";
                    }, 100);
                }
            } catch (error) {
                const errorMsg = document.getElementById("error-message");
                if (errorMsg) {
                    errorMsg.style.display = "block";
                    errorMsg.innerText = "Network error: " + error.message;
                }
                console.error("Full error:", error);
                console.error("Error stack:", error.stack);
            }
        });
    }

    // Register form handler
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // prevent default form submission

            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm-password").value;

            if (password !== confirmPassword) {
                const errorMsg = document.getElementById("error-message");
                if (errorMsg) {
                    errorMsg.style.display = "block";
                    errorMsg.innerText = "Passwords do not match.";
                }
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
                    const errorMsg = document.getElementById("error-message");
                    if (errorMsg) {
                        errorMsg.style.display = "block";
                        errorMsg.innerText = "Server returned invalid response. Status: " + response.status;
                    }
                    return;
                }
                
                console.log("Response data:", data);
                
                if (!response.ok) {
                    // Show error message - handle both string and array formats
                    const errorMsgEl = document.getElementById("error-message");
                    if (errorMsgEl) {
                        errorMsgEl.style.display = "block";
                        let errorMsg = "An error occurred";
                        if (data.detail) {
                            if (Array.isArray(data.detail)) {
                                errorMsg = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
                            } else {
                                errorMsg = data.detail;
                            }
                        }
                        errorMsgEl.innerText = errorMsg;
                    }
                } else {
                    // Store user_id in localStorage for later use
                    console.log('Registration response data:', data);
                    if (data.user_id) {
                        console.log('Storing user_id in localStorage:', data.user_id);
                        localStorage.setItem('user_id', String(data.user_id)); // Ensure it's a string
                        console.log('user_id stored. Current value:', localStorage.getItem('user_id'));
                        console.log('Verifying localStorage after 100ms...');
                        setTimeout(() => {
                            console.log('user_id still in localStorage:', localStorage.getItem('user_id'));
                        }, 100);
                    } else {
                        console.warn('No user_id in registration response!');
                    }
                    // Redirect to recommendations page on successful registration
                    const errorMsg = document.getElementById("error-message");
                    if (errorMsg) {
                        errorMsg.style.display = "none";
                    }
                    window.location.href = "/recommendations";
                }
            } catch (error) {
                const errorMsg = document.getElementById("error-message");
                if (errorMsg) {
                    errorMsg.style.display = "block";
                    errorMsg.innerText = "Network error: " + error.message;
                }
                console.error("Full error:", error);
                console.error("Error stack:", error.stack);
            }
        });
    }
}); // End of DOMContentLoaded