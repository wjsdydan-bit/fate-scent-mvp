"use client";

import { useState, useEffect } from "react";

export default function LoadingStep1() {
    const [stepText, setStepText] = useState("만세력을 탈탈 터는 중… 📖");
    const [displayText, setDisplayText] = useState("");

    useEffect(() => {
        const steps = [
            { time: 1500, text: "타고난 오행 기운 분석 중… 🔍" },
            { time: 3000, text: "부족한 기운 영끌하는 중… 💨" },
            { time: 4500, text: "향수 노트에 사주 비비는 중… 🧪" },
            { time: 6000, text: "운명의 케미 점수 매기는 중… 🎯" },
            { time: 8000, text: "거의 다 왔어요! 영혼을 갈아넣는 중… 🔥" },
            { time: 10000, text: "너무 열심히 하고 있어서 금방 돼요! 제발! 🙏" },
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
