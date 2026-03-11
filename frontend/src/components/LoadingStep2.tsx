"use client";

import { useState, useEffect } from "react";

export default function LoadingStep2() {
    const [stepText, setStepText] = useState("조건에 맞는 향수를 찾고 있어요…");
    const [displayText, setDisplayText] = useState("");

    useEffect(() => {
        const steps = [
            { time: 2500, text: "어울리는 향수를 고르고 있어요…" },
            { time: 5500, text: "사주와 향수 궁합을 맞추고 있어요…" },
            { time: 9000, text: "마무리 정리 중이에요…" },
        ];
        const timers = steps.map(s => setTimeout(() => setStepText(s.text), s.time));
        return () => timers.forEach(clearTimeout);
    }, []);

    useEffect(() => {
        let i = 0;
        setDisplayText("");
        const interval = setInterval(() => {
            if (i < stepText.length) {
                setDisplayText(stepText.slice(0, i + 1));
                i++;
            } else {
                clearInterval(interval);
            }
        }, 60);
        return () => clearInterval(interval);
    }, [stepText]);

    return (
        <div className="w-full flex flex-col items-center justify-center min-h-[60vh] space-y-6 text-center">
            <div className="relative w-16 h-16 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-slate-100 h-full w-full"></div>
                <div className="absolute inset-0 rounded-full border-4 border-orange-500 border-t-transparent animate-spin h-full w-full"></div>
            </div>

            <div className="space-y-2">
                <h2 className="text-xl font-extrabold text-slate-900 tracking-tight text-center">
                    {displayText}
                    <span className="animate-pulse text-orange-500 ml-0.5">|</span>
                </h2>
                <p className="text-sm text-slate-500 mt-1 text-center">⚠️ 새로고침하지 마세요 🙏</p>
            </div>
        </div>
    );
}
