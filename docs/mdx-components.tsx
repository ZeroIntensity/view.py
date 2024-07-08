import React from "react";

export function useMDXComponents(components: React.ReactNode[]) {
    return { ...components };
}
