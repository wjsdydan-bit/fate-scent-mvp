"use client";

import { useState, useEffect } from "react";

export default function LoadingStep2() {
    const [stepText, setStepText] = useState("사주팔자 스캔 완료! 👀");
    const [displayText, setDisplayText] = useState("");

    useEffect(() => {
        const steps = [
            { time: 1500, text: "넘치는 기운 덜어낼 향수 찾는 중… 🔎" },
            { time: 3000, text: "부족한 매력 채워줄 노트 고르는 중… 🧪" },
            { time: 4500, text: "운명적인 향수 리스트업 중… 📝" },
            { time: 6000, text: "최고의 궁합 3대장 선발 중… 🏆" },
            { time: 8000, text: "분석 결과를 정성껏 쓰는 중… ✍️" },
            { time: 10000, text: "타자 진짜 빨리 치고 있어요! 조금만요! 💦" },
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
