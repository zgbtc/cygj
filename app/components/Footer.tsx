"use client";

import Link from "next/link";

interface FooterProps {
  lang?: "en" | "zh";
}

export default function Footer({ lang = "en" }: FooterProps) {
  const t = {
    en: {
      disclaimer: "Disclaimer",
      terms: "Terms of Service",
      privacy: "Privacy Policy",
      copyright: "© 2024 CYGJ Crypto Tools. All rights reserved."
    },
    zh: {
      disclaimer: "免责声明",
      terms: "服务条款",
      privacy: "隐私政策",
      copyright: "© 2024 CYGJ 加密工具集. 保留所有权利."
    }
  };

  return (
    <footer className="w-full border-t border-gray-200 bg-white mt-auto">
      <div className="container mx-auto px-6 py-6">
        {/* Links */}
        <div className="flex items-center justify-center gap-6 text-sm text-gray-600 mb-3">
          <Link 
            href="/disclaimer" 
            className="hover:text-[#d4af37] transition-colors duration-200"
          >
            {t[lang].disclaimer}
          </Link>
          <span className="text-gray-400">|</span>
          <Link 
            href="/terms" 
            className="hover:text-[#d4af37] transition-colors duration-200"
          >
            {t[lang].terms}
          </Link>
          <span className="text-gray-400">|</span>
          <Link 
            href="/privacy" 
            className="hover:text-[#d4af37] transition-colors duration-200"
          >
            {t[lang].privacy}
          </Link>
        </div>
        
        {/* Copyright */}
        <div className="text-center text-xs text-gray-500">
          {t[lang].copyright}
        </div>
      </div>
    </footer>
  );
}
