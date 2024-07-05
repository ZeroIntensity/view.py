import withMDX from "@next/mdx";
/** @type {import('next').NextConfig} */
const nextConfig = withMDX()({
    pageExtensions: ["js", "jsx", "mdx", "ts", "tsx"],
    transpilePackages: ["geist"], // https://github.com/vercel/geist-font/issues/59
});

export default nextConfig;
