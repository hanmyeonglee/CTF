"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Modal from '../../components/Modal';
import { useRouter } from 'next/navigation';


export default function Game() {
    const router = useRouter();
    const [url, setUrl] = useState("");
    const [found, setFound] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [randomPos, setRandomPos] = useState({ top: "50%", left: "50%", cursor: "default" });

    useEffect(() => {
        setRandomPos({
            top: `${Math.random() * 80}%`,
            left: `${Math.random() * 80}%`,
            cursor: "default"
        });
    }, []);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    const resetGame = async () => {
        const res = await fetch("/api/reset-game", { method: "POST", body: JSON.stringify({ url }) });
        const data = await res.json();

        if (!res.ok) {
            alert(`Error: ${data.error}`);
        } else {
            alert(data.message)
        }
        return;
    };

    return (

        <motion.div
            className="relative w-[500px] h-[500px] bg-white rounded-lg flex items-center justify-center"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}

        >
            {found ? (
                <Modal isOpen={isModalOpen} onClose={closeModal}>
                    <h1 className="text-2xl">Congratulation! 🎉</h1>
                    Please provide the URL, and we'll send a congratulatory message.<br></br>
                    <input
                        name="url"
                        type="text"
                        style={{ border: "1px solid black", width: "300px" }}
                        onChange={(e) => setUrl(e.target.value)}
                    /><br></br>
                    <button
                        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg"
                        onClick={async () => {
                            await resetGame()
                            router.push("/")
                        }}
                    >
                        Submit
                    </button>
                </Modal>
            ) : (
                <button
                    className="absolute text-white px-4 py-2"
                    style={randomPos}
                    onClick={() => {
                        setFound(true)
                        openModal()
                    }}
                >
                    Find me!
                </button>
            )}
        </motion.div>
    );
}