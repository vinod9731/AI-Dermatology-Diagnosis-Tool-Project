document.addEventListener('DOMContentLoaded', () => {

    // --- Page-Aware Logic ---
    // This checks which page we are on and only runs the relevant code.

    // --- HOME PAGE SCRIPT (Analysis Tool Page) ---
    if (document.getElementById('predictBtn')) {
        // --- State for Home Page ---
        let currentDisease = '';
        let imageDataForDB = '';
        let currentFile = null;
        let cameraStream = null;

        // --- DOM Elements for Home Page ---
        const imageUpload = document.getElementById('imageUpload');
        const predictBtn = document.getElementById('predictBtn');
        const resultDiv = document.getElementById('result');
        const sendBtn = document.getElementById('sendBtn');
        const userInput = document.getElementById('userInput');
        const chatbox = document.getElementById('chatbox');
        const imagePreview = document.getElementById('imagePreview');
        const languageSelector = document.getElementById('language');

        // Camera Elements
        const uploadFileBtn = document.getElementById('uploadFileBtn');
        const useCameraBtn = document.getElementById('useCameraBtn');
        const cameraView = document.getElementById('cameraView');
        const videoElement = document.getElementById('videoElement');
        const captureBtn = document.getElementById('captureBtn');

        // --- Slider Logic ---
        let slideIndex = 0;
        showSlides();

        function showSlides() {
            const slides = document.getElementsByClassName("slide");
            if (slides.length === 0) return;
            for (let i = 0; i < slides.length; i++) {
                slides[i].style.display = "none";
            }
            slideIndex++;
            if (slideIndex > slides.length) { slideIndex = 1 }
            slides[slideIndex - 1].style.display = "block";
            setTimeout(showSlides, 4000);
        }

        // --- Interaction Logic (Upload and Camera) ---
        uploadFileBtn.addEventListener('click', () => imageUpload.click());
        
        useCameraBtn.addEventListener('click', async () => {
            if (cameraStream) {
                stopCamera();
                return;
            }
            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
                videoElement.srcObject = cameraStream;
                cameraView.style.display = 'block';
                imagePreview.style.display = 'none';
                predictBtn.style.display = 'none';
            } catch (err) {
                console.error("Error accessing camera: ", err);
                alert("Could not access the camera. Please ensure you have given permission.");
            }
        });
        
        captureBtn.addEventListener('click', () => {
            const canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            canvas.getContext('2d').drawImage(videoElement, 0, 0);
            
            imagePreview.src = canvas.toDataURL('image/jpeg');
            imagePreview.style.display = 'block';
            
            canvas.toBlob(blob => {
                currentFile = new File([blob], "capture.jpg", { type: "image/jpeg" });
                predictBtn.style.display = 'block';
            }, 'image/jpeg');
            
            stopCamera();
        });

        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                currentFile = file;
                const reader = new FileReader();
                reader.onload = (event) => {
                    imagePreview.src = event.target.result;
                    imagePreview.style.display = 'block';
                    cameraView.style.display = 'none';
                    predictBtn.style.display = 'block';
                    stopCamera();
                };
                reader.readAsDataURL(file);
            }
        });

        // --- Prediction Logic ---
        predictBtn.addEventListener('click', async () => {
            if (!currentFile) {
                resultDiv.textContent = 'No image selected.';
                return;
            }
            resultDiv.textContent = 'Analyzing...';
            predictBtn.disabled = true;
            const formData = new FormData();
            formData.append('file', currentFile);

            try {
                const response = await fetch('/predict', { method: 'POST', body: formData });
                const data = await response.json();

                if (data.disease) {
                    currentDisease = data.disease;
                    imageDataForDB = data.image_data;
                    resultDiv.innerHTML = `<strong>Detected:</strong> ${currentDisease}`;
                    userInput.placeholder = `Ask about ${currentDisease}...`;
                    getAutomaticExplanation(`Give a brief, user-friendly overview of ${currentDisease}.`);
                } else {
                    resultDiv.innerHTML = `<span style="color: red;">Error: ${data.error}</span>`;
                }
            } catch (error) {
                console.error('Error:', error);
                resultDiv.innerHTML = '<span style="color: red;">An error occurred during prediction.</span>';
            } finally {
                predictBtn.disabled = false;
            }
        });

        // --- Chatbot Logic ---
        const getAutomaticExplanation = async (message) => {
            try {
                const response = await fetch('/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        disease: currentDisease, message: message,
                        imageData: imageDataForDB, language: languageSelector.value
                    })
                });
                const data = await response.json();
                appendMessage('Assistant', data.response || `<span style="color: red;">${data.error}</span>`);
            } catch (error) {
                appendMessage('Assistant', 'Sorry, could not fetch initial details.');
            }
        };

        const handleChat = async () => {
            const message = userInput.value.trim();
            if (!message) return;

            appendMessage('User', message);
            userInput.value = '';

            try {
                const response = await fetch('/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        disease: currentDisease, message: message,
                        imageData: imageDataForDB, language: languageSelector.value
                    })
                });
                const data = await response.json();
                appendMessage('Assistant', data.response || `<span style="color: red;">${data.error}</span>`);
            } catch (error) {
                console.error('Error:', error);
                appendMessage('Assistant', 'Sorry, an error occurred. Please try again.');
            }
        };

        sendBtn.addEventListener('click', handleChat);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleChat();
        });

        function stopCamera() {
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
                cameraView.style.display = 'none';
            }
        }

        function appendMessage(sender, message) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('chat-message', sender === 'User' ? 'user-msg' : 'assistant-msg');
            messageElement.innerHTML = message;
            chatbox.appendChild(messageElement);
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    }

    // --- DASHBOARD SCRIPT ---
    if (document.querySelector('.dashboard-container')) {
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', async () => {
                const historyId = button.dataset.id;
                if (confirm('Are you sure you want to delete this entry?')) {
                    try {
                        const response = await fetch(`/delete_history/${historyId}`, { method: 'POST' });
                        const data = await response.json();
                        if (data.success) {
                            document.getElementById(`history-${historyId}`).remove();
                        } else {
                            alert('Failed to delete the entry.');
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        alert('An error occurred while deleting.');
                    }
                }
            });
        });
    }

});