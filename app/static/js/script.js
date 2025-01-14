document.getElementById('add-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const source = document.getElementById('source').value;
    const relation = document.getElementById('relation').value;
    const target = document.getElementById('target').value;

    const response = await fetch('/add_relationship', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, relation, target }),
    });

    const result = await response.json();
    alert(result.message);
});


document.getElementById('query-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const entity = document.getElementById('query-entity').value;

    // Query entity relationships
    const response = await fetch(`/query?entity=${entity}`);
    const result = await response.json();

    const outputDiv = document.getElementById('output');
    outputDiv.innerHTML = '';
    if (result.length === 0) {
        outputDiv.innerHTML = `<p>No relationships found for entity ${entity}.</p>`;
        return;
    }
    const graphResponse = await fetch(`/query_graph_visualization?entity=${entity}`);
    if (graphResponse.ok) {
        const graphBlob = await graphResponse.blob();
        const graphUrl = URL.createObjectURL(graphBlob);
        outputDiv.innerHTML += `<img src="${graphUrl}" alt="Graph Visualization" style="margin-top: 20px;">`;
    } else {
        outputDiv.innerHTML += `<p class="error-message">Failed to generate graph visualization.</p>`;
    }
});

document.getElementById("upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const uploadStatus = document.getElementById("upload-status");
    uploadStatus.innerHTML = ""; 

    const fileInput = document.getElementById("file-upload");
    const file = fileInput.files[0];
    if (!file) {
        uploadStatus.innerHTML = '<span class="error-message">Please select a file to upload.</span>';
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            uploadStatus.innerHTML = `<span> ${result.message}</span>`;
        } else {
            uploadStatus.innerHTML = '<span class="error-message">Failed to process the file. Please check the format and try again.</span>';
        }
    } catch (error) {
        uploadStatus.innerHTML = '<span class="error-message">An unexpected error occurred. Please try again later.</span>';
    }
});


// document.getElementById('upload-form').addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const fileInput = document.getElementById('file-upload');
//     const file = fileInput.files[0];
    
//     if (!file) {
//         alert("Please select a file.");
//         return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);

//     const response = await fetch('/upload', {
//         method: 'POST',
//         body: formData,
//     });


//     const statusDiv = document.getElementById('upload-status');
//     if (response.ok) {
//         statusDiv.textContent = "File uploaded and processed successfully!!!";
//     } else {
//         statusDiv.textContent = "Failed to process the file.";
//     }
// });
