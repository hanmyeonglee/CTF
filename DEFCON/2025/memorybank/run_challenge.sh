#!/bin/bash

ulimit -m 22400 

timeout 60s deno run --allow-read index.js

echo "⏰ 🚫 BANK IS NOW CLOSED FOR THE DAY 🚫 ⏰"