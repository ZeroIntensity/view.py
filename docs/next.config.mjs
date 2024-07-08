import withMDX from "@next/mdx";
/** @type {import('next').NextConfig} */
const nextConfig = withMDX()({
    pageExtensions: ["js", "jsx", "mdx", "ts", "tsx"],
    transpilePackages: [
        "geist",
        "highlight.js",
    ] /* https://github.com/vercel/geist-font/issues/59, https://github.com/highlightjs/highlight.js/issues/3982 */,
});

export default nextConfig;