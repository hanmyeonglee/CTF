let currentNoteId = null;


function addNotesToList(notes){
    const notesList = document.getElementById('notesList');
    notesList.textContent = "";
    for (note of notes){
        let a = document.createElement('a');
        let li = document.createElement('li');
        let strong = document.createElement('strong');
        let p = document.createElement('p');
        a.href = "/api/notes/" + note._id
        strong.textContent = note.title
        p.textContent = note.content
        a.appendChild(strong)
        a.appendChild(p)
        li.appendChild(a)

        let button = document.createElement('button');
        button.className ="note-btn";
        button.id = note._id
        button.textContent = "report";
        button.onclick = function(){
            console.log('noteId token:', this.id);
            const params = new URLSearchParams();
            params.append('noteId', this.id);
            // Send POST with noteId and token
            fetch('/report', {
              method: 'POST',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: params.toString(),
            })

            alert("Note reported to the Admin. We will review it in a couple of minutes.")
        }
        li.appendChild(button)
        notesList.appendChild(li)
    }
}

// Handle Dashboard Load and Fetch Notes
const fetchNotes = async () => {
    const response = await fetch(`/api/notes/`);
    if (response.ok) {
        const notes = await response.json();
        addNotesToList(notes);
    } else {
        alert('Failed to fetch notes');
    }
};

// Handle Adding a New Note
document.getElementById('addNoteForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;
    const response = await fetch(`/api/notes`, {
        method: 'POST',
        body: new URLSearchParams({ title, content }),
    });

    if (response.ok) {
        fetchNotes();
    } else {
        alert('Failed to add note');
    }
});


const reviewNote = async (reviewNoteId) => {
    const showNoteDiv = document.getElementById('show-note');
    const response = await fetch(`/api/notes/`+reviewNoteId)
    const note = await response.text();
    showNoteDiv.style.display = 'block';
    
    showNoteDiv.innerHTML = `
        <h3>Note ID: ${reviewNoteId}</h3>
        <p>${note}</p>
    `;
}

let hcaptchaWidgetId = null; 

// Get the 'reviewNote' parameter from the URL
const reviewNoteId = (new URLSearchParams(window.location.search)).get('reviewNote');

// If the reviewNote parameter exists, display it in the 'show-note' div
if (reviewNoteId) {
    reviewNote(reviewNoteId).then(()=>{fetchNotes()});
} else { 
    fetchNotes();
}
