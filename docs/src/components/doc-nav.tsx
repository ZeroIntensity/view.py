export type DocNavPage = {
    name: string;
    url: string;
};

interface DocNavProps {
    next: DocNavPage | null;
    last: DocNavPage | null;
}

export default function DocNav(props: DocNavProps) {
    return (
        <div className="flex items-center space-x-3 justify-between">
            {props.last ? (
                <a
                    href={props.last.url}
                    className="flex space-x-1 items-center justify-center hover:scale-105 px-8 py-2 rounded-lg font-semibold bg-gradient-to-b from-sky-500 to-blue-600 !text-white focus:ring-2 hover:shadow-xl transition duration-200 focus:outline-none"
                >
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
                            d="M6.75 15.75 3 12m0 0 3.75-3.75M3 12h18"
                        />
                    </svg>

                    <p>{props.last.name}</p>
                </a>
            ) : (
                <div></div>
            )}
            {props.next && (
                <a
                    href={props.next.url}
                    className="flex space-x-1 items-center justify-center hover:scale-105 px-8 py-2 rounded-lg font-semibold bg-gradient-to-b from-sky-500 to-blue-600 !text-white focus:ring-2 hover:shadow-xl transition duration-200 focus:outline-none"
                >
                    <p>{props.next.name}</p>
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
                            d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3"
                        />
                    </svg>
                </a>
            )}
        </div>
    );
}
