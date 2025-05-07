"use client";
import Game from "./Game";
import { motion } from 'framer-motion';

export default function HideAndSeekPage() {
    return (
        <main className="flex flex-col items-center justify-center h-screen bg-black text-white">
            <motion.h1
                className="text-3xl font-bold mb-4"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, ease: "easeOut" }}
            >
                Find the Hidden Button!
            </motion.h1>
            <Game />
        </main>
    );
}