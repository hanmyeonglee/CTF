const express = require('express');
const Note = require('../models/note');
const router = express.Router();


router.post('/', async (req, res) => {
  const { title, content } = req.body;
  if (!title || !content){ return res.status(400).json({ message: 'Title or content missing' }); }

  if ( typeof title !== 'string' || title.length > 10000 || typeof content !== 'string' || content.length > 10000){ return res.status(400).json({ message: 'Title or content too big or not an string.' }); } 

  try {
    const note = new Note({
      title,
      content,
      userId: req.user.userId,
    });
    
    await note.save();
    res.status(201).json({"id": note._id, "title": note.title, "content": note.content});
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

router.get('/', async (req, res) => {
  try {
    const notes = await Note.find({ userId: req.user.userId }).sort({ createdAt: -1 }).select('_id title content');
    res.json(notes);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

router.get('/:noteId', async (req, res) => {
  const { noteId } = req.params;
  try {
    const note = await Note.findById(noteId);
    if (!note) {
      return res.status(404).json({ message: 'Note not found' });
    }

    // Look mom, I wrote a raw HTTP response all by myself!
    // Can I go outside now and play with my friends?
    const responseMessage = `HTTP/1.1 200 OK
Date: Sun, 7 Nov 1917 11:26:07 GMT
Last-Modified: the-second-you-blinked
Type: flag-extra-salty, thanks
Length: 1337 bytes of pain
Server: thehackerscrew/1970 
Cache-Control: never-ever-cache-this
Allow: pizza, hugs, high-fives
X-CTF-Player-Reminder: drink-water-and-keep-hydrated

${note.title}: ${note.content}

`
    res.socket.end(responseMessage)
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});


module.exports = router;

