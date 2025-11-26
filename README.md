
 # 📘 Overview

This project is an AI-powered dermatology assistant that performs **preliminary skin-disease detection** using a **ResNet-50 deep learning model** and provides **conversational medical guidance** through a GPT-based chatbot.
It empowers users—especially in rural and semi-urban areas with limited dermatology access—to receive early, reliable, and accessible skin-health insights.

---
 🧭 Table of Contents

* [Inspiration](#-inspiration)
* [What It Does](#-what-it-does)
* [How We Built It](#-how-we-built-it)
* [Challenges](#-challenges-we-ran-into)
* [Accomplishments](#-accomplishments-were-proud-of)
* [What We Learned](#-what-we-learned)
* [Future Enhancements](#-whats-next-for-this-project)
* [Tech Stack](#-tech-stack)
* [Architecture](#-system-architecture)
* [Installation](#-installation--setup)
* [Usage](#-usage)
* [Folder Structure](#-folder-structure)
* [Authors](#-authors)

---

# 🚀 Inspiration

Skin diseases affect over **900 million people worldwide**, and India has a severe shortage of dermatologists, especially in rural regions.
People often rely on self-diagnosis, home remedies, or general practitioners who may misinterpret skin conditions.

This project was inspired by the need to:

* Detect skin diseases early
* Reduce misdiagnosis
* Provide **accessible healthcare technology**
* Bridge the rural healthcare gap
* Offer trustworthy guidance through AI

---

# 🧠 What It Does

### 🔍 1. Classifies Skin Disease from Images

* Uses a ResNet-50 CNN
* Processes user-uploaded images
* Predicts the most likely skin condition

### 💬 2. Provides AI-Driven Medical Guidance

A GPT-powered chatbot explains:

* Probable causes & symptoms
* Suggested precautions
* Treatment options
* When to consult a dermatologist

# 🌐 3. Easy-to-Use Web Interface

* Image upload
* Prediction dashboard
* Chatbot assistance
* Mobile & PC compatible

---

# ⚙ How We Built It

### ⭐ Hybrid Development Methodology

✔ Agile – For fast iterative development
✔ V-Model – For structured verification & validation
✔ Spiral – For continuous refinement and risk management

### 🔧 Technologies

| Layer        | Technologies               |
| ------------ | -------------------------- |
| **Frontend** | HTML, CSS, JavaScript      |
| **Backend**  | Python, Flask              |
| **AI Model** | PyTorch, ResNet-50         |
| **Chatbot**  | GPT API                    |
| **Database** | SQLite                     |
| **Tools**    | Google Colab, VS Code, Git |

### 📐 Workflow

1. User uploads an image
2. Image → preprocessing
3. ResNet-50 → predicts condition
4. Prediction → GPT chatbot
5. Explanation returned to user

---

# 💡 Challenges We Ran Into

* Dataset bias for darker skin tones
* Highly variable images (light, angle, resolution)
* Integrating ML model + chatbot + UI
* Ethical & legal concerns with medical data
* Ensuring medical-safe explanations

---

# 🏆 Accomplishments We're Proud Of

* Achieved high-accuracy ResNet-50 model
* Fully working classifier + chatbot combination
* Intuitive UI with real-time guidance
* Secure handling of sensitive images
* Strong alignment with SDGs (3, 9, 10)

---

# 🧪 What We Learned

* Deep learning model tuning & evaluation
* Building healthcare-grade UI/UX
* Enhancing accessibility for general users
* Ensuring ethically safe AI guidance
* Handling sensitive medical datasets
* Integrating multimodal AI (CV + NLP)

---

# 🔮 What’s Next for This Project

* Add explainable AI (Grad-CAM heatmaps)
* Build Android & iOS mobile app
* Increase dataset diversity (skin tones, lighting)
* Deploy a lightweight model for offline use
* Integrate clinical decision support
* Full cloud deployment for telemedicine
* Conduct testing with dermatology professionals

---

# 💻 Tech Stack

### **Frontend:**

* HTML5, CSS3, JavaScript

### **Backend:**

* Python
* Flask
* SQLite

### AI / ML

* PyTorch
* ResNet-50 CNN
* Data Augmentation

### APIs / Services:

* GPT API
* Cloud Storage (optional)

---

# 🏗 System Architecture

```
                   ┌─────────────────────┐
                   │       User UI       │
                   │ (Upload & Chat UI)  │
                   └─────────┬───────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │  Image Preprocessing │
                 └─────────┬────────────┘
                           │
                           ▼
             ┌────────────────────────────┐
             │     ResNet-50 Classifier   │
             │  (Skin Disease Prediction) │
             └──────────┬────────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │   GPT-Based Chat System  │
            │ (Explanation & Guidance) │
            └───────────┬─────────────┘
                        │
                        ▼
               ┌───────────────────┐
               │   Results Page    │
               │ (Diagnosis + Tips)│
               └───────────────────┘
```

---

# 🛠 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. Add `.env` File

```
OPENAI_API_KEY=your_key_here
```

 # 5. Run the App

```bash
python app.py
```

 # 6. Open in Browser
 

```
http://127.0.0.1:5000
```

---

# ▶ Usage

1. Open the web app
2. Upload your skin image
3. Model predicts the condition
4. Chatbot explains the prediction
5. Follow provided guidance

---

# 📂 Folder Structure

```
project/
│── app.py
│── skin_disease_model.pth
│── class_to_idx.pth
│── database.db
│── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│── static/
│   ├── css/
│   ├── js/
│   ├── images/
│── .env
│── requirements.txt
│── README.md
```

---
# Images 


# 🧑‍🤝‍🧑 Authors

* **Vinod**
* **Nallin Kumar A B**
* **Deeksha D**
