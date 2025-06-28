import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Building Agents with Claude on Vertex AI",
  description: "Interactive presentation on Claude Agents with Vertex AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
} 