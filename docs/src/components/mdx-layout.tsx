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
    let next: DocNavPage | null = null;
    let last: DocNavPage | null = null;
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
                        next = {
                            name: pageName,
                            url,
                        };
                    }

                    if (entries[index - 1] != undefined) {
                        let [pageName, url] = entries[index - 1];
                        last = {
                            name: pageName,
                            url,
                        };
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
                    <hr className="border-t border-zinc-800" />
                    <DocNav next={next} last={last} />
                </div>
                <div className="lg:w-1/4 hidden lg:block px-4 sticky top-0">
                    <p className="uppercase font-bold text-white select-none">
                        On this page
                    </p>
                    <div className="flex flex-col space-y-1 items-start">
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
                </div>
            </div>
        </div>
    );
}
