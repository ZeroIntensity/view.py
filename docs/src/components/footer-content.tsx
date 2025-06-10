import Image from "next/image";
import { FaRegCopyright, FaDiscord, FaGithub } from "react-icons/fa";
import { SiGithubsponsors } from "react-icons/si";

export default function FooterContent() {
    return (
        <div className="flex-col sm:flex-row flex lg:py-0 py-2 px-6 lg:px-48 justify-between w-full items-center">
            <Image
                src="/logo-white.svg"
                width={500}
                height={500}
                alt="view.py"
                className="size-32 sm:size-48"
            />
            <div className="flex flex-col items-center justify-center space-y-6">
                <div className="flex items-center space-x-6">
                    <a
                        href="https://github.com/ZeroIntensity/view.py"
                        target="_blank"
                        className="text-white hover:opacity-50"
                    >
                        <FaGithub className="size-8 md:size-10" />
                    </a>
                    <a
                        href="https://discord.gg/tZAfuWAbm2"
                        target="_blank"
                        className="text-white hover:opacity-50"
                    >
                        <FaDiscord className="size-9 md:size-11" />
                    </a>
                    <a
                        href="https://github.com/sponsors/ZeroIntensity/"
                        target="_blank"
                        className="text-white hover:opacity-50"
                    >
                        <SiGithubsponsors className="size-8 md:size-10" />
                    </a>
                </div>
                <div className="flex items-center space-x-1 text-zinc-800">
                    <FaRegCopyright />
                    <p className="font-light select-none md:text-base test-sm">
                        ZeroIntensity 2024
                    </p>
                </div>
            </div>
        </div>
    );
}
