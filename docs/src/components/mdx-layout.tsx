import { usePathname } from "next/navigation";
import styles from "./docs.module.css";
import DocNav, { DocNavPage } from "./doc-nav";
import { useRef, useEffect, useState } from "react";

type Section = Record<string, string>;
type Nav = Record<string, Section>;
const NAV: Nav = {
    "Getting Started": {
        Introduction: "/docs",
        Installation: "/docs/getting-started/installation",
        "Creating a project": "/docs/getting-started/creating-a-project",
        Configuration: "/docs/getting-started/configuration",
    },
    "Building Projects": {
        "App Basics": "/docs/building-projects/app-basics",
        "URL Routing": "/docs/building-projects/routing",
        "Returning Responses": "/docs/building-projects/responses",
        "Taking Parameters": "/docs/building-projects/parameters",
        "Getting Request Data": "/docs/building-projects/request-data",
        "HTML Templating": "/docs/building-projects/templating",
        "Runtime Builds": "/docs/building-projects/builds",
        "Writing Documentation": "/docs/building-projects/documenting",
        "Using WebSockets": "/docs/building-projects/websockets",
    },
    "API Reference": {
        Types: "/docs/reference/types",
        Utilities: "/docs/reference/utils",
        Exceptions: "/docs/reference/exceptions",
        Apps: "/docs/reference/apps",
        Configuration: "/docs/reference/config",
        Routing: "/docs/reference/routing",
        Templates: "/docs/reference/templates",
        Build: "/docs/reference/build",
        WebSockets: "/docs/reference/websockets",
    },
};

export default function MdxLayout({ children }: { children: React.ReactNode }) {
    const path = usePathname();
    let [next, setNext] = useState<DocNavPage | null>(null);
    let [last, setLast] = useState<DocNavPage | null>(null);
    const mdRef = useRef<HTMLDivElement>(null);

    let [query, setQuery] = useState<NodeListOf<HTMLElement> | null>(null);
    useEffect(() => {
        Object.entries(NAV).forEach((firstEntry, firstIndex) => {
            const entries = Object.entries(firstEntry[1]);
            entries.forEach((entry, index) => {
                let [pageName, url] = entry;
                if (url == path) {
                    // This is the page!
                    if (entries[index + 1] != undefined) {
                        let [pageName, url] = entries[index + 1];
                        setNext({
                            name: pageName,
                            url,
                        });
                    }

                    if (entries[index - 1] != undefined) {
                        let [pageName, url] = entries[index - 1];
                        setLast({
                            name: pageName,
                            url,
                        });
                    }
                }
            });
        });
        setQuery(mdRef.current!.querySelectorAll("h2"));
    }, [mdRef]);

    return (
        <div
            className="w-full dark:bg-black bg-white  dark:bg-grid-small-white/[0.2] bg-grid-small-black/[0.2] relative flex items-center justify-center"
            ref={mdRef}
        >
            {/* Radial gradient for the container to give a faded look */}
            <div className="absolute pointer-events-none inset-0 flex items-center justify-center dark:bg-black bg-white [mask-image:radial-gradient(ellipse_at_center,transparent_80%,black)]"></div>
            <div className="flex justify-between py-16">
                <nav className="lg:w-1/4 hidden lg:flex pl-12 z-10 flex-col space-y-8">
                    {Object.entries(NAV).map(([title, section]) => (
                        <div className="flex flex-col space-y-1">
                            <p className="uppercase font-bold text-white select-none">
                                {title}
                            </p>
                            {Object.entries(section).map(([pageName, url]) => (
                                <a
                                    href={url}
                                    className={
                                        url == path ? "text-sky-500" : ""
                                    }
                                >
                                    {pageName}
                                </a>
                            ))}
                        </div>
                    ))}
                </nav>

                <div className="lg:px-0 px-4 w-full lg:w-1/2 flex flex-col space-y-3 break-words">
                    <hr className="border-t border-zinc-800" />
                    <section className={styles.docs}>{children}</section>
                    <div className="py-2">
                        <hr className="border-t border-zinc-800" />
                    </div>
                    <DocNav next={next} last={last} />
                </div>
                <div className="lg:w-1/4 hidden lg:block px-4 sticky top-0">
                    <div className="flex flex-col space-y-1 items-start">
                        <p className="uppercase font-bold text-white select-none">
                            On this page
                        </p>
                        {query &&
                            Array.from(query).map(element => {
                                return (
                                    <a
                                        onClick={() => element.scrollIntoView()}
                                        className="cursor-pointer"
                                    >
                                        {element.innerText}
                                    </a>
                                );
                            })}
                    </div>
                    <div className="py-6 w-1/2">
                        <hr className="border-t border-zinc-800" />
                    </div>
                    <div>
                        <div className="grid grid-cols-1 auto-rows-fr gap-1 w-fit">
                            <a
                                href={`https://github.com/ZeroIntensity/view.py/edit/master/docs/src/pages${
                                    path == "/docs" ? "/docs/index" : path
                                }.mdx`}
                                target="_blank"
                                className="bg-slate-800 no-underline group cursor-pointer relative shadow-2xl shadow-zinc-900 rounded-lg p-px text-xs font-semibold leading-6  text-white inline-block"
                            >
                                <span className="absolute inset-0 overflow-hidden rounded-lg">
                                    <span className="absolute inset-0 rounded-lg bg-[image:radial-gradient(75%_100%_at_50%_0%,rgba(56,189,248,0.6)_0%,rgba(56,189,248,0)_75%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                                </span>
                                <div className="relative flex justify-between space-x-2 items-center z-10 rounded-lg bg-zinc-950 py-0.5 px-4 ring-1 ring-white/10 ">
                                    <div className="flex space-x-1 items-center">
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
                                                d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
                                            />
                                        </svg>

                                        <span>Edit this page</span>
                                    </div>
                                    <svg
                                        fill="none"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        width="16"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M10.75 8.75L14.25 12L10.75 15.25"
                                            stroke="currentColor"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="1.5"
                                        />
                                    </svg>
                                </div>
                                <span className="absolute -bottom-0 left-[1.125rem] h-px w-[calc(100%-2.25rem)] bg-gradient-to-r from-emerald-400/0 via-emerald-400/90 to-emerald-400/0 transition-opacity duration-500 group-hover:opacity-40" />
                            </a>
                            <a
                                href="https://discord.gg/tZAfuWAbm2"
                                target="_blank"
                                className="bg-slate-800 no-underline group cursor-pointer relative shadow-2xl shadow-zinc-900 rounded-lg p-px text-xs font-semibold leading-6  text-white inline-block"
                            >
                                <span className="absolute inset-0 overflow-hidden rounded-lg">
                                    <span className="absolute inset-0 rounded-lg bg-[image:radial-gradient(75%_100%_at_50%_0%,rgba(56,189,248,0.6)_0%,rgba(56,189,248,0)_75%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                                </span>
                                <div className="relative flex justify-between space-x-2 items-center z-10 rounded-lg bg-zinc-950 py-0.5 px-4 ring-1 ring-white/10 ">
                                    <div className="flex space-x-1 items-center">
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
                                                d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
                                            />
                                        </svg>

                                        <span>Chat on Discord</span>
                                    </div>
                                    <svg
                                        fill="none"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        width="16"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M10.75 8.75L14.25 12L10.75 15.25"
                                            stroke="currentColor"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="1.5"
                                        />
                                    </svg>
                                </div>
                                <span className="absolute -bottom-0 left-[1.125rem] h-px w-[calc(100%-2.25rem)] bg-gradient-to-r from-emerald-400/0 via-emerald-400/90 to-emerald-400/0 transition-opacity duration-500 group-hover:opacity-40" />
                            </a>
                            <a
                                href="https://github.com/ZeroIntensity/view.py"
                                target="_blank"
                                className="bg-slate-800 no-underline group cursor-pointer relative shadow-2xl shadow-zinc-900 rounded-lg p-px text-xs font-semibold leading-6  text-white inline-block"
                            >
                                <span className="absolute inset-0 overflow-hidden rounded-lg">
                                    <span className="absolute inset-0 rounded-lg bg-[image:radial-gradient(75%_100%_at_50%_0%,rgba(56,189,248,0.6)_0%,rgba(56,189,248,0)_75%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                                </span>
                                <div className="relative flex justify-between space-x-2 items-center z-10 rounded-lg bg-zinc-950 py-0.5 px-4 ring-1 ring-white/10 ">
                                    <div className="flex space-x-1 items-center">
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
                                                d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"
                                            />
                                        </svg>

                                        <span>Star the project</span>
                                    </div>
                                    <svg
                                        fill="none"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        width="16"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M10.75 8.75L14.25 12L10.75 15.25"
                                            stroke="currentColor"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="1.5"
                                        />
                                    </svg>
                                </div>
                                <span className="absolute -bottom-0 left-[1.125rem] h-px w-[calc(100%-2.25rem)] bg-gradient-to-r from-emerald-400/0 via-emerald-400/90 to-emerald-400/0 transition-opacity duration-500 group-hover:opacity-40" />
                            </a>
                            <a
                                href="https://github.com/sponsors/ZeroIntensity"
                                target="_blank"
                                className="bg-slate-800 no-underline group cursor-pointer relative shadow-2xl shadow-zinc-900 rounded-lg p-px text-xs font-semibold leading-6  text-white inline-block"
                            >
                                <span className="absolute inset-0 overflow-hidden rounded-lg">
                                    <span className="absolute inset-0 rounded-lg bg-[image:radial-gradient(75%_100%_at_50%_0%,rgba(56,189,248,0.6)_0%,rgba(56,189,248,0)_75%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                                </span>
                                <div className="relative flex justify-between space-x-2 items-center z-10 rounded-lg bg-zinc-950 py-0.5 px-4 ring-1 ring-white/10 ">
                                    <div className="flex space-x-1 items-center">
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
                                        <span>Become a sponsor</span>
                                    </div>
                                    <svg
                                        fill="none"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        width="16"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M10.75 8.75L14.25 12L10.75 15.25"
                                            stroke="currentColor"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="1.5"
                                        />
                                    </svg>
                                </div>
                                <span className="absolute -bottom-0 left-[1.125rem] h-px w-[calc(100%-2.25rem)] bg-gradient-to-r from-emerald-400/0 via-emerald-400/90 to-emerald-400/0 transition-opacity duration-500 group-hover:opacity-40" />
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
