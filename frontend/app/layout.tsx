import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });

export const metadata: Metadata = {
  title: "EmoStories — Real Stories, Real Emotions",
  description: "Curated emotional stories from real people, anonymized and polished for you.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geist.variable} font-sans antialiased bg-neutral-950 text-neutral-100 min-h-screen`}>
        <header className="border-b border-neutral-800 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold tracking-tight">EmoStories</h1>
              <p className="text-xs text-neutral-500 mt-0.5">Real stories, real emotions</p>
            </div>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-6 py-10">{children}</main>
        <footer className="border-t border-neutral-800 px-6 py-6 text-center text-xs text-neutral-600">
          Stories are anonymized and curated daily from public Reddit posts.
        </footer>
      </body>
    </html>
  );
}
