"use client";

import { useState, useEffect } from "react";

export default function LoadingStep1() {
    const [stepText, setStepText] = useState("만세력을 확인하고 있어요…");

    useEffect(() => {
        const steps = [
            { time: 1500, text: "오행 에너지를 분석하고 있어요…" },
            { time: 3500, text: "향수 노트를 찾고 있어요…" },
            { time: 5500, text: "궁합을 계산하고 있어요…" },
        ];
        const timers = steps.map(s => setTimeout(() => setStepText(s.text), s.time));
        return () => timers.forEach(clearTimeout);
    }, []);

    return (
        <div className="w-full flex flex-col items-center justify-center min-h-[60vh] space-y-6 text-center">
            <div className="relative w-16 h-16 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-slate-100 h-full w-full"></div>
                <div className="absolute inset-0 rounded-full border-4 border-orange-500 border-t-transparent animate-spin h-full w-full"></div>
            </div>

            <div className="space-y-2">
                <h2 className="text-xl font-extrabold text-slate-900 tracking-tight text-center">
                    {stepText}
                </h2>
                <p className="text-sm text-slate-500 mt-1 text-center">⚠️ 새로고침하지 마세요 🙏</p>
            </div>
        </div>
    );
}
