import { BackgroundBeams } from "@/components/background-beams";
import React from "react";
import { cn } from "@/utils/cn";
import { AuroraBackground } from "@/components/aurora-background";
import { BackgroundGradient } from "@/components/background-gradient";
import { motion } from "framer-motion";

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
}: {
    title: string;
    children: React.ReactNode;
}) {
    return (
        <BackgroundGradient className="rounded-[22px] h-full w-full p-4 sm:p-10 bg-white dark:bg-zinc-950 hover:dark:bg-zinc-900 transition-all">
            <a className="flex items-start flex-col text-left">
                <p className="text-base sm:text-xl text-black mt-4 mb-2 dark:text-neutral-200">
                    {title}
                </p>

                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    {children}
                </p>
            </a>
        </BackgroundGradient>
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
                <AuroraBackground>
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
                            <Card title="Batteries Detachable">
                                Everything you need, right out of the box, while
                                natively supporting your favorite libraries.
                            </Card>
                            <Card title="Lightning Fast">
                                Powered by our own{" "}
                                <a href="https://github.com/ZeroIntensity/pyawaitable">
                                    PyAwaitable
                                </a>
                                , view.py is the world&apos;s first web
                                framework to implement ASGI in pure C, without
                                the use of transpilers.
                            </Card>
                            <Card title="Developer Oriented">
                                APIs are designed with the developer in mind.
                                We&apos;ll give ourselves way more work in order
                                to make things nice for you.
                            </Card>
                        </div>
                    </motion.div>
                </AuroraBackground>
            </section>
        </>
    );
}
