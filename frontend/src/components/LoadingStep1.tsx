"use client";

import { useState, useEffect } from "react";
import { AlertCircle } from "lucide-react";
export default function LoadingStep1() {
    const [stepText, setStepText] = useState("만세력을 탈탈 터는 중… 📖");
    const [displayText, setDisplayText] = useState("");

    useEffect(() => {
        const steps = [
            { time: 1500, text: "타고난 오행 기운을 확인하고 있어요… 🔍" },
            { time: 3500, text: "사주와 향수 노트의 궁합을 비교하는 중… 🧪" },
            { time: 6000, text: "AI가 맞춤형 케미 점수를 분석하고 있어요… 🎯" },
            { time: 8500, text: "분석 결과를 보기 좋게 정리하는 중입니다… 📝" },
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
