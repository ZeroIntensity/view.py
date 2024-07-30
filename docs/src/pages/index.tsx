import { BackgroundBeams } from "@/components/background-beams";
import React from "react";
import { cn } from "@/utils/cn";
import { AuroraBackground } from "@/components/aurora-background";
import { motion } from "framer-motion";
import { StarsBackground } from "@/components/stars-background";
import { Meteors } from "@/components/meteors";
import FooterContent from "@/components/footer-content";

export const Highlight = ({
    children,
    className,
}: {
    children: React.ReactNode;
    className?: string;
}) => {
    return (
        <span
            className={cn(
                `relative inline-block pb-1 px-1 rounded-lg bg-gradient-to-r dark:from-cyan-600 dark:to-blue-700 text-white`,
                className
            )}
        >
            {children}
        </span>
    );
};

function Card({
    title,
    children,
    icon,
}: {
    title: string;
    children: React.ReactNode;
    icon: React.ReactNode;
}) {
    return (
        <div className="w-full relative max-w-lg">
            <div className="absolute inset-0 h-full w-full bg-gradient-to-r from-zinc-700 to-zinc-900 transform scale-[0.80] rounded-full blur-3xl" />
            <div className="relative shadow-xl px-4 py-8 overflow-hidden flex flex-col justify-between items-start rounded-2xl h-full w-full p-4 sm:p-10 bg-black bg-opacity-25 transition-all backdrop-blur-xl border-zinc-950 border border-opacity-25 space-y-3">
                <StarsBackground className="opacity-50 -z-20" />

                <div className="flex items-center space-x-1 text-white">
                    {icon}
                    <p className="text-lg sm:text-2xl text-black dark:text-neutral-200 font-semibold flex items-center justify-center">
                        {title}
                    </p>
                </div>

                <p className="text-base text-neutral-600 dark:text-neutral-400">
                    {children}
                </p>

                {/* Meaty part - Meteor effect */}
                <Meteors number={20} />
            </div>
        </div>
    );
}

export default function Home() {
    const [copied, setCopied] = React.useState(false);

    return (
        <>
            <section className="h-[40rem] w-full rounded-md bg-neutral-950 relative flex flex-col items-center justify-center antialiased">
                <div className="p-4 max-w-7xl mx-auto relative z-10 w-full pt-20 md:pt-0 flex items-center justify-center flex-col">
                    <div className="flex space-x-2 items-center py-4">
                        <p className="bg-sky-800 p-1 border rounded-full border-sky-800 font-medium text-sky-200">
                            Alpha
                        </p>
                        <p className="text-zinc-500">
                            view.py is currently in alpha!
                        </p>
                    </div>
                    <h1 className="text-4xl md:text-7xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                        The <Highlight>Batteries-Detachable</Highlight> Web
                        Framework
                    </h1>
                    <div className="grid auto-rows-fr grid-cols-2 space-x-3 text-white py-4">
                        <a
                            href="/docs"
                            className="flex items-center justify-center hover:scale-105 px-8 py-2 rounded-lg font-semibold bg-gradient-to-b from-sky-500 to-blue-600 text-white focus:ring-2 hover:shadow-xl transition duration-200 focus:outline-none"
                        >
                            <p>Documentation</p>
                        </a>
                        <a
                            href="#what-is-it"
                            className="hover:border-zinc-700 inline-flex h-12 animate-shimmer items-center justify-center rounded-lg border border-zinc-800 bg-[linear-gradient(110deg,#000103,45%,#282d33,55%,#000103)] bg-[length:200%_100%] px-6 font-medium text-zinc-400 transition-colors focus:outline-none"
                        >
                            What is it?
                        </a>
                    </div>
                    <button
                        className="text-zinc-700 text-sm font-light hover:text-zinc-600 transition-all group flex items-center justify-center space-x-2"
                        onClick={async () => {
                            await navigator.clipboard.writeText(
                                "pipx run view-py init"
                            );
                            setCopied(true);
                            setTimeout(() => {
                                setCopied(false);
                            }, 1000);
                        }}
                    >
                        <code>~ pipx run view-py init</code>
                        {copied ? (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-4 opacity-0 group-hover:opacity-100 transition-all text-emerald-500"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M11.35 3.836c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m8.9-4.414c.376.023.75.05 1.124.08 1.131.094 1.976 1.057 1.976 2.192V16.5A2.25 2.25 0 0 1 18 18.75h-2.25m-7.5-10.5H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V18.75m-7.5-10.5h6.375c.621 0 1.125.504 1.125 1.125v9.375m-8.25-3 1.5 1.5 3-3.75"
                                />
                            </svg>
                        ) : (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="size-4 opacity-0 group-hover:opacity-100 transition-all"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M8.25 7.5V6.108c0-1.135.845-2.098 1.976-2.192.373-.03.748-.057 1.123-.08M15.75 18H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08M15.75 18.75v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5A3.375 3.375 0 0 0 6.375 7.5H5.25m11.9-3.664A2.251 2.251 0 0 0 15 2.25h-1.5a2.251 2.251 0 0 0-2.15 1.586m5.8 0c.065.21.1.433.1.664v.75h-6V4.5c0-.231.035-.454.1-.664M6.75 7.5H4.875c-.621 0-1.125.504-1.125 1.125v12c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V16.5a9 9 0 0 0-9-9Z"
                                />
                            </svg>
                        )}
                    </button>
                </div>

                <BackgroundBeams />
            </section>
            <section className="flex items-center justify-center flex-col space-y-6">
                <AuroraBackground className="flex flex-col justify-between">
                    <motion.div
                        initial={{ opacity: 0.0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{
                            delay: 0.3,
                            duration: 0.8,
                            ease: "easeInOut",
                        }}
                        className="flex flex-col items-center justify-center px-4"
                    >
                        <div className="flex items-center justify-center flex-col space-y-1 py-12">
                            <h2 className="text-2xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                                What&apos;s view.py?
                            </h2>
                            <p className="text-zinc-500 font-light text-xl">
                                Not your ordinary web framework
                            </p>
                        </div>
                        <div className="grid auto-rows-fr grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-12 px-12">
                            <Card
                                title="Removable Batteries"
                                icon={
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        strokeWidth={1.5}
                                        stroke="currentColor"
                                        className="size-9"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M4.5 10.5h6.75V15H4.5v-4.5ZM3.75 18h15A2.25 2.25 0 0 0 21 15.75v-6a2.25 2.25 0 0 0-2.25-2.25h-15A2.25 2.25 0 0 0 1.5 9.75v6A2.25 2.25 0 0 0 3.75 18Z"
                                        />
                                    </svg>
                                }
                            >
                                We provide everything you need, right out of the
                                box, while including native support your
                                favorite third-party libraries. Don&apos;t want
                                to relearn anything? No problem.
                            </Card>
                            <Card
                                title="Written in C"
                                icon={
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        strokeWidth={1.5}
                                        stroke="currentColor"
                                        className="size-8"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            d="m3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z"
                                        />
                                    </svg>
                                }
                            >
                                Powered by our own{" "}
                                <a href="https://github.com/ZeroIntensity/pyawaitable">
                                    PyAwaitable
                                </a>
                                , view.py is the world&apos;s first web
                                framework to implement ASGI in pure C, without
                                the use of transpilers.
                            </Card>
                            <Card
                                title="Developer Oriented"
                                icon={
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        strokeWidth={1.5}
                                        stroke="currentColor"
                                        className="size-8"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            d="M14.25 9.75 16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z"
                                        />
                                    </svg>
                                }
                            >
                                view.py is written by developers, for
                                developers, under the MIT license.
                            </Card>
                        </div>
                    </motion.div>
                    <footer className="border-t border-zinc-900 bg-black z-30 bg-opacity-65 backdrop-blur-2xl border-opacity-25 w-full">
                        <FooterContent />
                    </footer>
                </AuroraBackground>
            </section>
        </>
    );
}
