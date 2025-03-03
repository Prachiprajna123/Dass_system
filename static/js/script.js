


// Capture photo from the video stream and display it on the canvas
// Access the video and canvas elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const statusElement = document.getElementById('status');

// Function to start the camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error('Error accessing the camera:', error);
        statusElement.textContent = 'Error accessing the camera. Please allow camera access.';
    }
}

// Function to capture an image from the video feed
function captureImage() {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL(); // Convert canvas image to base64 string
    console.log('Captured image data:', imageData); // Debugging: Log the image data
    return imageData;
}

// Function to handle registration
// Function to handle registration
// Function to handle registration
async function register() {
    // Capture the image
    const imageData = captureImage();

    // Get form data
    const name = document.getElementById('name').value;
    const age = document.getElementById('age').value;
    const email = document.getElementById('email').value;
    const gender = document.getElementById('gender').value;
    const contact = document.getElementById('contact').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const photo = dataURItoBlob(imageData)// Get the status element

    // Validate form data

    // Check if passwords match
    if (password !== confirmPassword) {
        statusElement.textContent = 'Passwords do not match.';
        return;
    }

    // Create a FormData object to send form data and the image
    const formData = new FormData();
    formData.append("name", name);
    formData.append("age", age);
    formData.append("email", email);
    formData.append("gender", gender);
    formData.append("contact", contact);
    formData.append("password", password);
    formData.append("photo", photo,`${name}.jpg`); // Convert base64 to Blob for file upload

    // Send the data to the server
    try {
        const response = await fetch('/register', {
            method: 'POST',
            body: formData, // Send the FormData object (with file)
        });

        const result = await response.json();
        if (result.success) {
            statusElement.textContent = 'Registration successful!';
            alert('Registration successful!'); // Add alert here
            window.location.href = '/user_login'; // Redirect to login page
        } else {
            statusElement.textContent = `Registration failed: ${result.error}`;
        }
    } catch (error) {
        console.error('Error during registration:', error);
        statusElement.textContent = 'Registration failed. Please try again.';
    }
}

// Helper function to convert base64 image data to Blob (file)
function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ua = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ua[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

// Admin registration function
function admin_register() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get form inputs
    const nameInput = document.getElementById('name');
    const passwordInput = document.getElementById('password');

    // Check if elements exist
    if (!nameInput || !passwordInput) {
        console.error("Required form elements not found!");
        alert("Form elements missing. Please check the page.");
        return;
    }

    const name = nameInput.value;
    const password = passwordInput.value;
    const photo = dataURItoBlob(canvas.toDataURL());

    // Validate fields
    if (!name || !photo || !password) {
        alert("All fields are required, please.");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("password", password);
    formData.append("photo", photo, `${name}.jpg`);

    // Send admin registration data
    fetch("/admin_register", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Data successfully registered");
            window.location.href = "/admin_login";
        } else {
            alert("Sorry, registration not successful");
        }
    })
    .catch(error => {
        console.log("Error", error);
    });
}
// Login function for regular users

// Admin login function
function admin_login() {
    const name = document.getElementById("name").value;
    const password = document.getElementById('password').value;

    // Validate fields
    if (!name || !password) {
        alert("Name and photo required, please.");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("password", password);

    // Send admin login request
    fetch("/admin_login", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Login successful");
            window.location.href = `/admin`;
        } else {
            alert(data.error || "Login not successful");
        }
    })
    .catch(error => {
        console.log("Error", error);
        alert("Error with the login request");
    });
}
// Convert data URI to Blob
function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ua = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ua[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

// Initialize the camera and set up the form
 // Call init when the page loads
 async function loginUser(event) {
    event.preventDefault(); // Prevent form submission

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    const result = await response.json();
    if (result.success) {
        alert('Login successful!');
        window.location.href = '/success'; // Redirect to success page
    } else {
        alert(`Login failed: ${result.error}`);
    }
}

// Function to handle user logout
async function logoutUser() {
    const response = await fetch('/logout', {
        method: 'POST',
    });

    const result = await response.json();
    if (result.success) {
        alert('Logged out successfully!');
        window.location.href = '/'; // Redirect to home page
    } else {
        alert('Logout failed. Please try again.');
    }
}
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the camera
    startCamera();

    // Attach event listeners
    const registerButton = document.getElementById('register-button');
    if (registerButton) {
        registerButton.addEventListener('click', register);
    }

    const adminRegisterButton = document.getElementById('admin-register-button');
    if (adminRegisterButton) {
        adminRegisterButton.addEventListener('click', admin_register);
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', loginUser);
    }

    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', logoutUser);
    }
});
window.onload = startCamera;