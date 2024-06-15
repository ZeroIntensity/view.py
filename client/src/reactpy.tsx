import {
    BaseReactPyClient,
    ReactPyClient,
    ReactPyModule,
} from "@reactpy/client";
import React from "react";
import ReactDOM from "react-dom/client";
import { Layout } from "@reactpy/client/src/components";

export function createReconnectingWebSocket(props: {
    url: URL;
    readyPromise: Promise<void>;
    onOpen?: () => void;
    onMessage: (message: MessageEvent<any>) => void;
    onClose?: () => void;
    startInterval: number;
    maxInterval: number;
    maxRetries: number;
    backoffMultiplier: number;
}) {
    const { startInterval, maxInterval, maxRetries, backoffMultiplier } = props;
    let retries = 0;
    let interval = startInterval;
    let everConnected = false;
    const closed = false;
    const socket: { current?: WebSocket } = {};

    const connect = () => {
        if (closed) {
            return;
        }
        socket.current = new WebSocket(props.url);
        socket.current.onopen = () => {
            everConnected = true;
            console.info("ReactPy connected!");
            interval = startInterval;
            retries = 0;
            if (props.onOpen) {
                props.onOpen();
            }
        };
        socket.current.onmessage = props.onMessage;
        socket.current.onclose = () => {
            if (props.onClose) {
                props.onClose();
            }
            if (!everConnected) {
                console.info("ReactPy failed to connect!");
                return;
            }
            console.info("ReactPy disconnected!");
            if (retries >= maxRetries) {
                console.info("ReactPy connection max retries exhausted!");
                return;
            }
            console.info(
                `ReactPy reconnecting in ${(interval / 1000).toPrecision(
                    4
                )} seconds...`
            );
            setTimeout(connect, interval);
            interval = nextInterval(interval, backoffMultiplier, maxInterval);
            retries++;
        };
    };

    props.readyPromise
        .then(() => console.info("Starting ReactPy client..."))
        .then(connect);

    return socket;
}

export function nextInterval(
    currentInterval: number,
    backoffMultiplier: number,
    maxInterval: number
): number {
    return Math.min(
        // increase interval by backoff multiplier
        currentInterval * backoffMultiplier,
        // don't exceed max interval
        maxInterval
    );
}

export type ReconnectOptions = {
    startInterval: number;
    maxInterval: number;
    maxRetries: number;
    backoffMultiplier: number;
};

export type ReactPyUrls = {
    componentUrl: URL;
    query: string;
    jsModules: string;
};

export type ReactPyDjangoClientProps = {
    urls: ReactPyUrls;
    reconnectOptions: ReconnectOptions;
    mountElement: HTMLElement;
    prerenderElement: HTMLElement | null;
    offlineElement: HTMLElement | null;
};

export class ReactPyDjangoClient
    extends BaseReactPyClient
    implements ReactPyClient {
    urls: ReactPyUrls;
    socket: { current?: WebSocket };
    mountElement: HTMLElement;
    prerenderElement: HTMLElement | null = null;
    offlineElement: HTMLElement | null = null;

    constructor(props: ReactPyDjangoClientProps) {
        super();
        this.urls = props.urls;
        this.socket = createReconnectingWebSocket({
            readyPromise: this.ready,
            url: this.urls.componentUrl,
            onMessage: async ({ data }) =>
                this.handleIncoming(JSON.parse(data)),
            ...props.reconnectOptions,
            onClose: () => {
                // If offlineElement exists, show it and hide the mountElement/prerenderElement
                if (this.prerenderElement) {
                    this.prerenderElement.remove();
                    this.prerenderElement = null;
                }
                if (this.offlineElement) {
                    this.mountElement.hidden = true;
                    this.offlineElement.hidden = false;
                }
            },
            onOpen: () => {
                // If offlineElement exists, hide it and show the mountElement
                if (this.offlineElement) {
                    this.offlineElement.hidden = true;
                    this.mountElement.hidden = false;
                }
            },
        });
        this.mountElement = props.mountElement;
        this.prerenderElement = props.prerenderElement;
        this.offlineElement = props.offlineElement;
    }

    sendMessage(message: any): void {
        this.socket.current?.send(JSON.stringify(message));
    }

    loadModule(moduleName: string): Promise<ReactPyModule> {
        return import(`${this.urls.jsModules}/${moduleName}`);
    }
}

export function mountComponent(
    mountElement: HTMLElement,
    host: string,
    urlPrefix: string,
    routeId: string,
    resolvedJsModulesPath: string,
    reconnectStartInterval: number,
    reconnectMaxInterval: number,
    reconnectMaxRetries: number,
    reconnectBackoffMultiplier: number
) {
    // Protocols
    let httpProtocol = window.location.protocol;
    let wsProtocol = `ws${httpProtocol === "https:" ? "s" : ""}:`;

    // WebSocket route (for Python components)
    let wsOrigin: string;
    if (host) {
        wsOrigin = `${wsProtocol}//${host}`;
    } else {
        wsOrigin = `${wsProtocol}//${window.location.host}`;
    }

    // HTTP route (for JavaScript modules)
    let httpOrigin: string;
    let jsModulesPath: string;
    if (host) {
        httpOrigin = `${httpProtocol}//${host}`;
        jsModulesPath = `${urlPrefix}/web_module`;
    } else {
        httpOrigin = `${httpProtocol}//${window.location.host}`;
        if (resolvedJsModulesPath) {
            jsModulesPath = resolvedJsModulesPath;
        } else {
            jsModulesPath = `${urlPrefix}/web_module`;
        }
    }

    // Embed the initial HTTP path into the WebSocket URL
    let componentUrl = new URL(`${wsOrigin}/${urlPrefix}`);
    componentUrl.searchParams.append("route", routeId);
    if (window.location.search) {
        componentUrl.searchParams.append("http_search", window.location.search);
    }

    // Configure a new ReactPy client
    const client = new ReactPyDjangoClient({
        urls: {
            componentUrl: componentUrl,
            query: document.location.search,
            jsModules: `${httpOrigin}/${jsModulesPath}`,
        },
        reconnectOptions: {
            startInterval: reconnectStartInterval,
            maxInterval: reconnectMaxInterval,
            backoffMultiplier: reconnectBackoffMultiplier,
            maxRetries: reconnectMaxRetries,
        },
        mountElement: mountElement,
        prerenderElement: document.getElementById(
            mountElement.id + "-prerender"
        ),
        offlineElement: document.getElementById(mountElement.id + "-offline"),
    });

    // Replace the prerender element with the real element on the first layout update
    if (client.prerenderElement) {
        client.onMessage("layout-update", () => {
            if (client.prerenderElement) {
                client.prerenderElement.replaceWith(client.mountElement);
                client.prerenderElement = null;
            }
        });
    }

    // Start rendering the component
    const root = ReactDOM.createRoot(client.mountElement);
    root.render(<Layout client={client} />);
}

mountComponent(
    document.getElementById("_view-root")!,
    window.location.host,
    "_view/reactpy-stream",
    document.getElementById("_view-route-hook")!.innerText,
    "",
    750,
    60000,
    150,
    1.25
);
