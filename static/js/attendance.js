// attendance.js
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const submitBtn = document.getElementById('submitBtn');
const nameInput = document.getElementById("name");
// Get access to the camera
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function(error) {
            console.error("Error accessing the camera: ", error);
        });
} else {
    console.error("getUserMedia not supported in this browser.");
}

submitBtn.addEventListener('click', () => {
    // Draw the video frame to the canvas
    const name = nameInput.value;
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = dataURITOBlob(canvas.toDataURL());
    // Create a FormData object
    const formData = new FormData();
    formData.append('image', imageData,`${name}.jpg`);
    // Send the image data to the server
    fetch('/attendance_taken', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            window.location.href = `/success?user_name=${encodeURIComponent(data.name)}&image_url=${encodeURIComponent(data.image_url)}`;
        } else {
            alert(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function dataURITOBlob(dataURI) {
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ia], { type: mimeString });
}