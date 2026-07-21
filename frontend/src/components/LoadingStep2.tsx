"use client";

import { useState, useEffect } from "react";
import { AlertCircle } from "lucide-react";
export default function LoadingStep2() {
    const [stepText, setStepText] = useState("사주팔자 스캔 완료! 👀");
    const [displayText, setDisplayText] = useState("");

    useEffect(() => {
        const steps = [
            { time: 1500, text: "사주 오행에 어울리는 향수를 찾는 중… 🔎" },
            { time: 3500, text: "사용자님의 취향에 맞는 노트를 고르고 있어요… 🧪" },
            { time: 6000, text: "가장 운명적인 향수 3가지를 선발하는 중… 🏆" },
            { time: 8500, text: "AI가 맞춤형 사주 향수 풀이를 작성하고 있습니다… ✍️" },
            { time: 11000, text: "조금만 더 기다려주세요! ✨" },
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
                <p className="text-sm text-slate-500 mt-2 flex items-center justify-center gap-1 font-medium" aria-live="polite">
                    <AlertCircle className="w-4 h-4 text-slate-400" strokeWidth={2} aria-hidden="true" /> AI 분석에는 약 5~10초가 소요됩니다
                </p>
            </div>
        </div>
    );
}
