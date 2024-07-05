import { BackgroundBeams } from "@/components/background-beams";
import React from "react";
import { cn } from "@/utils/cn";

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

export default function Home() {
    return (
        <>
            <section className="h-[40rem] w-full rounded-md bg-neutral-950 relative flex flex-col items-center justify-center antialiased">
                <div className="p-4 max-w-7xl mx-auto relative z-10 w-full pt-20 md:pt-0 flex items-center justify-center flex-col">
                    <div className="flex space-x-2 items-center py-4">
                        <p className="bg-sky-800 p-1 border rounded-full border-sky-800 font-semibold text-sky-200">
                            Alpha
                        </p>
                        <p className="text-zinc-500 font-light">
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
                </div>

                <BackgroundBeams />
            </section>
            <section className="flex items-center justify-center flex-col space-y-6">
                <div className="flex items-center justify-center flex-col space-y-1">
                    <h2 className="text-2xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                        What's view.py?
                    </h2>
                    <p className="text-zinc-500 font-light text-xl">
                        Not your ordinary web framework
                    </p>
                </div>
                <div>
                    <article>
                        <h2 className="text-2xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                            Batteries-Detachable
                        </h2>
                    </article>
                    <article>
                        <h2 className="text-2xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                            Modern
                        </h2>
                    </article>
                    <article>
                        <h2 className="text-2xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                            Developer-Oriented
                        </h2>
                    </article>
                </div>
            </section>
        </>
    );
}
