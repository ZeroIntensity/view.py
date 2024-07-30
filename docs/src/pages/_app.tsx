import { GeistSans } from "geist/font/sans";
import "./globals.css";
import "highlight.js/styles/github-dark-dimmed.css";
import type { AppProps } from "next/app";
import hljs from "highlight.js";
import python from "highlight.js/lib/languages/python";
import bash from "highlight.js/lib/languages/bash";
import { useEffect } from "react";
import Image from "next/image";
import { Spotlight } from "@/components/Spotlight";
import Link from "next/link";
import { PlaceholdersAndVanishInput } from "@/components/placeholders-and-vanish-input";

export function PlaceholdersAndVanishInputDemo() {
    const placeholders = [
        "Click to search...",
        "What is the airspeed velocity of an unladen swallow?",
        "Search the documentation...",
        "My hovercraft is full of eels...",
    ];

    return (
        <div className="w-1/3">
            <PlaceholdersAndVanishInput
                placeholders={placeholders}
                onChange={() => {}}
                onSubmit={() => {}}
            />
        </div>
    );
}

export default function MyApp({ Component, pageProps }: AppProps) {
    useEffect(() => {
        hljs.registerLanguage("py", python);
        hljs.registerLanguage("bash", bash);
        hljs.highlightAll();
    }, [Component]);
    return (
        <div className="dark">
            <div className="hidden md:flex overflow-hidden">
                <Spotlight className="-top-40 left-0 md:left-60 md:-top-20" />
            </div>
            <nav>
                <div className="flex justify-center items-center lg:justify-between lg:flex-row flex-col xl:px-64">
                    <Image
                        src="/logo.svg"
                        height={500}
                        width={500}
                        alt="view.py"
                        className="h-32 w-64"
                    />
                    <div className="flex md:flex-row flex-col py-2 lg:py-0 md:space-x-3 items-center md:justify-center">
                        <Link
                            className="flex space-x-1 items-center p-2 rounded-lg hover:bg-zinc-900"
                            href="/"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
                                />
                            </svg>
                            <span>Home</span>
                        </Link>
                        <Link
                            className="flex space-x-1 items-center p-2 rounded-lg hover:bg-zinc-900"
                            href="/docs"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25"
                                />
                            </svg>

                            <span>Docs</span>
                        </Link>
                        <a
                            className="flex space-x-1 items-center p-2 rounded-lg hover:bg-zinc-900"
                            href="https://github.com/ZeroIntensity/view.py"
                            target="_blank"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
                                />
                            </svg>

                            <span>Source</span>
                        </a>{" "}
                        <a
                            className="flex space-x-1 items-center p-2 rounded-lg hover:bg-zinc-900"
                            href="https://pypi.org/project/view.py"
                            target="_blank"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z"
                                />
                            </svg>

                            <span>Package</span>
                        </a>{" "}
                        <a
                            className="flex space-x-1 items-center p-2 rounded-lg hover:bg-zinc-900"
                            href="https://github.com/sponsors/ZeroIntensity"
                            target="_blank"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
                                />
                            </svg>

                            <span>Donate</span>
                        </a>{" "}
                    </div>
                    <PlaceholdersAndVanishInputDemo />
                </div>
                <hr className="border-t border-zinc-800" />
            </nav>
            <main className={GeistSans.className}>
                <Component {...pageProps} />
            </main>
        </div>
    );
}
