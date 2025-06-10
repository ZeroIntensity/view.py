import { useEffect, useState } from "react";
import {
    Modal,
    ModalBody,
    ModalContent,
    ModalFooter,
    ModalTrigger,
} from "./animated-modal";
import { PlaceholdersAndVanishInput } from "./placeholders-and-vanish-input";
import Link from "next/link";

/* Pagefind post-build types are not on NPM */

type PagefindSearchResult = {
    id: string;
    score: number;
    words: number[];
    data: () => Promise<PagefindSearchFragment>;
};

type PagefindSearchFragment = {
    url: string;
    raw_url?: string;
    content: string;
    raw_content?: string;
    excerpt: string;
    sub_results: PagefindSubResult[];
    word_count: number;
    locations: number[];
    weighted_locations: PagefindWordLocation[];
    filters: Record<string, string[]>;
    meta: Record<string, string>;
    anchors: PagefindSearchAnchor[];
};

type PagefindSubResult = {
    title: string;
    url: string;
    locations: number[];
    weighted_locations: PagefindWordLocation[];
    excerpt: string;
    anchor?: PagefindSearchAnchor;
};

type PagefindWordLocation = {
    weight: number;
    balanced_score: number;
    location: number;
};

type PagefindSearchAnchor = {
    element: string;
    id: string;
    text?: string;
    location: number;
};

interface WindowWithPagefind {
    pagefind: {
        search: (query: string) => Promise<{ results: PagefindSearchResult[] }>;
    };
}

declare var window: Window & WindowWithPagefind;

function Result({ result }: { result: PagefindSearchResult }) {
    const [data, setData] = useState<PagefindSearchFragment | null>(null);

    useEffect(() => {
        async function fetchData() {
            const data = await result.data();
            setData(data);
        }
        fetchData();
    }, [result]);

    if (!data) return null;

    return (
        <Link
            href={data.url}
            className="p-2 border border-zinc-900 rounded-lg font-semibold text-lg"
        >
            <div>
                <h3>{data.meta.title}</h3>
            </div>
        </Link>
    );
}

export function SearchBar() {
    const placeholders = [
        "Click to search...",
        "What is the airspeed velocity of an unladen swallow?",
        "Search the documentation...",
        "My hovercraft is full of eels...",
    ];

    useEffect(() => {
        async function loadPagefind() {
            if (typeof window.pagefind === "undefined") {
                try {
                    window.pagefind = await import(
                        // @ts-expect-error pagefind.js generated after build
                        /* webpackIgnore: true */ "./pagefind/pagefind.js"
                    );
                } catch (e) {
                    window.pagefind = {
                        search: async q => ({ results: [] }),
                    };
                }
            }
        }
        loadPagefind();
    }, []);

    const [results, setResults] = useState<PagefindSearchResult[]>([]);

    return (
        <Modal>
            <ModalTrigger className="w-1/6 bg-zinc-900 rounded-lg p-1 px-2 flex items-center justify-between hover:bg-zinc-800 text-zinc-600 hover:text-zinc-500 transition-all group/modal-btn group">
                <p className="text-sm font-thin select-none text-zinc-600 group-hover:text-zinc-500 transition-all">
                    Search documentation...
                </p>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="size-6 text-zinc-600 group-hover:text-zinc-500 transition-all"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Zm3.75 11.625a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z"
                    />
                </svg>
            </ModalTrigger>
            <ModalBody>
                <ModalContent>
                    <h4 className="text-lg md:text-2xl text-neutral-600 dark:text-neutral-100 font-bold text-center mb-8">
                        Search the documentation!
                    </h4>
                    <div className="flex items-center flex-col space-y-3">
                        {results.map(result => (
                            <Result key={result.id} result={result} />
                        ))}
                        <Link
                            href="/"
                            className="p-2 border border-zinc-900 rounded-lg font-thin text-lg hover:bg-zinc-950 text-white"
                        >
                            <div className="flex space-x-1 items-center">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    strokeWidth={1.5}
                                    stroke="currentColor"
                                    className="size-7"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="m12.75 15 3-3m0 0-3-3m3 3h-7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                                    />
                                </svg>

                                <h3 className="">Configuration</h3>
                            </div>
                        </Link>
                        <Link
                            href="/"
                            className="p-2 border border-zinc-900 rounded-lg font-thin text-lg hover:bg-zinc-950 text-white"
                        >
                            <div className="flex space-x-1 items-center">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    strokeWidth={1.5}
                                    stroke="currentColor"
                                    className="size-7"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="m12.75 15 3-3m0 0-3-3m3 3h-7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                                    />
                                </svg>

                                <h3 className="">Configuration</h3>
                            </div>
                        </Link>
                        <Link
                            href="/"
                            className="p-2 border border-zinc-900 rounded-lg font-thin text-lg hover:bg-zinc-950 text-white"
                        >
                            <div className="flex space-x-1 items-center">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    strokeWidth={1.5}
                                    stroke="currentColor"
                                    className="size-7"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="m12.75 15 3-3m0 0-3-3m3 3h-7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                                    />
                                </svg>

                                <h3 className="">Configuration</h3>
                            </div>
                        </Link>
                    </div>
                </ModalContent>
                <ModalFooter>
                    <PlaceholdersAndVanishInput
                        placeholders={placeholders}
                        onChange={async e => {
                            const search = await window.pagefind.search(
                                e.currentTarget.value
                            );
                            setResults(search.results);
                        }}
                        onSubmit={async e => {
                            const search = await window.pagefind.search(
                                (
                                    e.currentTarget
                                        .elements[0] as HTMLInputElement
                                ).value
                            );
                            setResults(search.results);
                        }}
                    />
                </ModalFooter>
            </ModalBody>
        </Modal>
    );
}
