"use client";
import { motion } from "framer-motion";
import { redirectGame } from "./actions";

export default function HomePage() {
  const desc = "Hide-and-Seek with Button";

  return (
    <main className="flex flex-col items-center justify-center h-screen bg-black text-white">
      <motion.h1
        className="text-4xl font-bold"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: "easeOut" }}
      >
        Hide and Seek
      </motion.h1>

      <motion.p
        className="mt-4 text-lg"
        initial="hidden"
        animate="visible"
        variants={{
          visible: { transition: { staggerChildren: 0.1, delayChildren: 0.8 } },
        }}
      >
        {desc.split("").map((char, index) => (
          <motion.span
            key={index}
            variants={{
              hidden: { opacity: 0, x: -10 },
              visible: { opacity: 1, x: 0 },
            }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            {char}
          </motion.span>
        ))}
      </motion.p>

      <motion.button
        className="mt-6 px-6 py-3 bg-gray-500 text-white rounded-lg shadow-xl opacity-80"
        initial={{ opacity: 0, scale: 1 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{
          duration: 0.6,
          ease: "easeOut",
          opacity: { delay: 0.8 }
        }}
        whileHover={{
          scale: 1.1,
          transition: { type: "spring", stiffness: 300, damping: 20 },
        }}
        whileTap={{
          scale: 0.95,
          transition: { type: "spring", stiffness: 300, damping: 20 },
        }}
        onClick={async () => await redirectGame()}
      >
        Play
      </motion.button>
    </main >
  );
}