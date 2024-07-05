import React from "react";

type Level = "info" | "danger" | "warning" | "note" | "question";
type AdmonitionProps = {
    children: React.ReactNode;
    title: string | undefined;
    level: Level | undefined;
};

const LEVEL_BORDER_COLORS: Record<Level, string> = {
    info: "border-l-sky-500",
    warning: "border-l-amber-500",
    danger: "border-l-rose-500",
    note: "border-l-blue-500",
    question: "border-l-green-500",
};

function LevelTitle({
    level,
    title,
}: {
    level: Level;
    title: string | undefined;
}) {
    switch (level) {
        case "info":
            return (
                <div className="text-sky-400 flex items-center space-x-1">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-6"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
                        />
                    </svg>

                    <header className="font-light text-xl">
                        {title || "Info"}
                    </header>
                </div>
            );
        case "warning":
            return (
                <div className="text-amber-400 flex items-center space-x-1">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-6"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                        />
                    </svg>
                    <header className="font-light text-xl">
                        {title || "Warning"}
                    </header>
                </div>
            );
        case "danger":
            return (
                <div className="text-rose-500 flex items-center space-x-1">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-6"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M12 9v3.75m0-10.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.25-8.25-3.286Zm0 13.036h.008v.008H12v-.008Z"
                        />
                    </svg>

                    <header className="font-light text-xl">
                        {title || "Danger"}
                    </header>
                </div>
            );
        case "note":
            return (
                <div className="text-blue-400 flex items-center space-x-1">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-6"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"
                        />
                    </svg>

                    <header className="font-light text-xl">
                        {title || "Note"}
                    </header>
                </div>
            );
        case "question":
            return (
                <div className="text-green-400 flex items-center space-x-1">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-6"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z"
                        />
                    </svg>

                    <header className="font-light text-xl">
                        {title || "Question"}
                    </header>
                </div>
            );
    }
}

export default function Admonition(props: AdmonitionProps) {
    const level = props.level || "note";
    return (
        <div
            className={`border border-zinc-900 rounded-md bg-black ${LEVEL_BORDER_COLORS[level]} border-l-4 w-fit`}
        >
            <div className="border-b border-zinc-900 w-full px-4 py-2">
                <LevelTitle level={level} title={props.title} />
            </div>
            <div className="px-4 py-2">{props.children}</div>
        </div>
    );
}
