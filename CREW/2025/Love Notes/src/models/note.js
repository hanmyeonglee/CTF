const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');


// Define the schema for a Note
const noteSchema = new mongoose.Schema(
  {
    _id: {
      type: String,
      default: () => uuidv4(), 
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    content: {
      type: String,
      required: true,
    },
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
  },
  { timestamps: true } 
);

module.exports = mongoose.model('Note', noteSchema);
