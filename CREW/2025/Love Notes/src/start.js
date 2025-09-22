const mongoose = require('mongoose');
const User = require('./models/user');
const Note = require('./models/note');
const { randomUUID } = require('crypto');
const FLAG = process.env.FLAG ?? 'crewctf{REDACTED}'
const ADMIN_USER = randomUUID();
const ADMIN_PASS = randomUUID();


// Function to create a default user and notes
async function createDefaultUserAndNotes() {
  if (await Note.countDocuments() !== 0) return
  try {
    // Create a default user
    const user = new User({
      email: ADMIN_USER,
      password: ADMIN_PASS,
    });
    
    console.log('Default user created');
    console.log(user);
    await user.save();

    // Create a few notes for the default user
    const notes = [
      { title: FLAG, content:  "My heart’s beloved: I am writing you again, because I am alone and because it troubles me always to have a dialogue with you in my head, without your knowing anything about it or hearing it or being able to answer… There are many females in the world, and some among them are beautiful. But where could I find again a face, whose every feature, even every wrinkle, is a reminder of the greatest and sweetest memories of my life? Even my endless pains, my irreplaceable losses I read in your sweet countenance, and I kiss away the pain when I kiss your sweet face… "},

      { title: 'Vorläufige Überlegungen', content: 'A spectre is haunting Europe – the spectre of communism. All the powers of old Europe have entered into a holy alliance to exorcise this spectre: Pope and Tsar, Metternich and Guizot, French Radicals and German police-spies.' }
    ];

    for (let note of notes) {
      const newNote = new Note({
        title: note.title,
        content: note.content,
        userId: user._id,  
      });
      await newNote.save();
      console.log(newNote);
    }

    console.log('Default notes created');
  } catch (error) {
    console.error('Error creating default user or notes:', error);
  }
}

// MongoDB connection and initialization
async function initializeApp() {
  try {
    await mongoose.connect(process.env.DB_URI, { useNewUrlParser: true, useUnifiedTopology: true });
    console.log('MongoDB connected');
    
    // Call the function to create the default user and notes
    await createDefaultUserAndNotes();
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
  } finally {
    // Close the connection after operations are done
    await mongoose.connection.close();
    console.log('MongoDB connection closed');
  }
}

initializeApp();
