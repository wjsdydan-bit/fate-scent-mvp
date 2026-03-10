"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const TAG_OPTIONS = [
    "꽃향기(플로럴)", "과일향(프루티)", "나무향(우디)", "상큼한(시트러스)",
    "포근한(머스크)", "달콤한(앰버/바닐라)", "시원한(아쿠아/마린)", "스모키/가죽"
];

const INTEREST_OPTIONS = [
    "금전운 💰", "연애운 💕", "학업운 📚", "취업/직장운 💼", "대인관계 🤝"
];

export default function RecommendationForm({ userInfo, onNext, onReset }: any) {
    const [prefTags, setPrefTags] = useState<string[]>([]);
    const [dislikeTags, setDislikeTags] = useState<string[]>([]);
    const [genderFilter, setGenderFilter] = useState("전체");
    const [interests, setInterests] = useState<string[]>([]);

    const handleNextSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onNext({
            pref_tags: prefTags,
            dislike_tags: dislikeTags,
            gender_filter: genderFilter,
            brand_filter_mode: "전체 뷰티 브랜드 포함", // Hidden setting or removed if not needed.
            interests: interests
        });
    };

    const toggleArrayItem = (arr: string[], setArr: any, item: string) => {
        if (arr.includes(item)) setArr(arr.filter(i => i !== item));
        else setArr([...arr, item]);
    };

    return (
        <div className="space-y-6 pb-6 animate-in fade-in zoom-in-95 duration-500">
            <Card className="border shadow-sm border-slate-100 rounded-[2rem] overflow-hidden mt-8 bg-white">
                <div className="bg-slate-50 border-b border-slate-100 text-slate-900 p-6 text-center">
                    <h3 className="font-extrabold text-xl tracking-tight">어떤 향수를 찾으시나요?</h3>
                </div>
                <CardContent className="pt-8 px-6">
                    <form onSubmit={handleNextSubmit} className="space-y-6">

                        <div className="space-y-4">
                            <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">
                                선호하는 향기 (복수 선택)
                            </Label>
                            <div className="flex flex-wrap gap-2">
                                {TAG_OPTIONS.map(tag => (
                                    <button
                                        key={tag}
                                        type="button"
                                        onClick={() => {
                                            if (dislikeTags.includes(tag)) toggleArrayItem(dislikeTags, setDislikeTags, tag);
                                            toggleArrayItem(prefTags, setPrefTags, tag);
                                        }}
                                        className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${prefTags.includes(tag)
                                            ? 'bg-orange-100 border-orange-200 text-orange-800'
                                            : 'bg-white text-slate-500 hover:bg-slate-50'
                                            }`}
                                    >
                                        {tag}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">
                                피하고 싶은 향기
                            </Label>
                            <div className="flex flex-wrap gap-2">
                                {TAG_OPTIONS.filter(tag => !prefTags.includes(tag)).map(tag => (
                                    <button
                                        key={tag}
                                        type="button"
                                        onClick={() => toggleArrayItem(dislikeTags, setDislikeTags, tag)}
                                        className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${dislikeTags.includes(tag)
                                            ? 'bg-red-100 border-red-200 text-red-800'
                                            : 'bg-white text-slate-500 hover:bg-slate-50'
                                            }`}
                                    >
                                        {tag}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-4 pt-2">
                            <Label className="font-bold text-slate-800 text-base block border-b border-slate-100 pb-2 text-center">가장 끌어올리고 싶은 운 (복수 선택)</Label>
                            <div className="flex flex-wrap gap-2">
                                {INTEREST_OPTIONS.map(interest => (
                                    <button
                                        key={interest}
                                        type="button"
                                        onClick={() => toggleArrayItem(interests, setInterests, interest)}
                                        className={`px-4 py-2.5 rounded-full text-sm font-bold border transition-all ${interests.includes(interest)
                                            ? 'bg-orange-500 border-orange-500 text-white shadow-md'
                                            : 'bg-white text-slate-500 hover:bg-slate-50'
                                            }`}
                                    >
                                        {interest}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-4 pt-2">
                            <Label className="font-bold text-slate-800 text-base block border-b border-slate-100 pb-2 text-center">향수 타겟 선호도</Label>
                            <RadioGroup value={genderFilter} onValueChange={setGenderFilter} className="flex gap-2">
                                {["전체", "여성향", "남성향", "중성향"].map(g => (
                                    <div key={g} className="flex-1">
                                        <RadioGroupItem value={g} id={`gf-${g}`} className="peer sr-only" />
                                        <Label htmlFor={`gf-${g}`} className="flex items-center justify-center px-2 py-3 border rounded-2xl text-sm font-medium bg-white cursor-pointer peer-data-[state=checked]:border-orange-500 peer-data-[state=checked]:bg-orange-50 peer-data-[state=checked]:font-extrabold peer-data-[state=checked]:text-orange-700 transition-all">
                                            {g}
                                        </Label>
                                    </div>
                                ))}
                            </RadioGroup>
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-14 text-lg font-bold rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-md mt-6 transition-transform active:scale-95 text-white"
                        >
                            결과 확인하기
                        </Button>

                        <Button
                            type="button"
                            variant="ghost"
                            onClick={onReset}
                            className="w-full text-slate-400 text-sm"
                        >
                            사주 분석 다시보기
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
