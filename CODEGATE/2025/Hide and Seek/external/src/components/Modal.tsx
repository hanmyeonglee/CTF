"use client";
import React from 'react';
import { motion } from "framer-motion";

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
    if (!isOpen) return null;
    return (
        <motion.div
            className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
        >
            <div className="bg-white p-4 rounded-lg w-1/3 text-black">
                <button onClick={onClose} className="absolute top-2 right-2 text-xl">
                    &times;
                </button>
                {children}
            </div>
        </motion.div>
    );
};

export default Modal;