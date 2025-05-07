import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hide and Seek",
  description: "Seek the hidden button.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <title>Hide and Seek</title>
      </head>
      <body className="bg-gray-100 text-gray-900">{children}</body>
    </html>
  );
}
