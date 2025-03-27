let uploadedFilePath = "";

// Upload File Function
function uploadFile() {
    let fileInput = document.getElementById("fileInput").files[0];

    if (!fileInput) {
        alert("Please select a file to upload.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);

    fetch("/upload", { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        if (data.filepath) {
            uploadedFilePath = data.filepath;
            document.getElementById("uploadStatus").innerText = "✅ File uploaded successfully!";
        } else {
            document.getElementById("uploadStatus").innerText = "❌ Upload failed: " + data.error;
        }
    })
    .catch(error => {
        console.error(error);
        document.getElementById("uploadStatus").innerText = "❌ Upload error!";
    });
}

// Calculate Bill Function
function calculateBill() {
    let customerName = document.getElementById("customerName").value.trim();

    if (!uploadedFilePath) {
        alert("Please upload the file first.");
        return;
    }
    if (!customerName) {
        alert("Please enter the customer's name.");
        return;
    }

    fetch("/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filepath: uploadedFilePath, customer_name: customerName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.total_bill !== undefined) {
            document.getElementById("result").innerHTML = `
                🧾 Bill for <b>${data.customer_name}</b><br>
                🥛 Cow Milk: <b>${data.cow_milk} L</b> <br>
                🐃 Buffalo Milk: <b>${data.buffalo_milk} L</b> <br>
                💰 Total: <b>₹${data.total_bill}</b> <br>🙏 Dhanyavad 🙏
            `;
        } else {
            document.getElementById("result").innerText = `❌ Error: ${data.error || "Unknown issue"}`;
        }
    })
    .catch(error => console.error(error));
}

// Send WhatsApp Function
function sendWhatsApp() {
    let phoneNumber = document.getElementById("phoneNumber").value.trim();
    let message = document.getElementById("result").innerText;

    if (!phoneNumber) {
        alert("Please enter a WhatsApp number.");
        return;
    }

    fetch("/send_whatsapp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: phoneNumber, message: message })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("whatsappStatus").innerText = data.message || data.error;
    })
    .catch(error => console.error(error));
}
