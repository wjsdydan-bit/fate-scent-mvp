"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { getDaysInMonth, clampDay } from "@/lib/dateUtils";

const TAG_OPTIONS = [
    "꽃향기(플로럴)", "과일향(프루티)", "나무향(우디)", "상큼한(시트러스)",
    "포근한(머스크)", "달콤한(앰버/바닐라)", "시원한(아쿠아/마린)", "스모키/가죽"
];

const INTEREST_OPTIONS = [
    "금전운 💰", "연애운 💕", "학업운 📚", "취업/직장운 💼", "대인관계 🤝"
];

export default function DirectRecommendForm({ onSubmit, userInfo, apiError }: { onSubmit: (data: any) => void, userInfo?: any, apiError?: string }) {
    // User Info State
    const [userName, setUserName] = useState(userInfo?.user_name || "");
    const [gender, setGender] = useState(userInfo?.gender || "선택 안 함");
    const [year, setYear] = useState(userInfo?.year ? String(userInfo.year) : "1995");
    const [month, setMonth] = useState(userInfo?.month ? String(userInfo.month) : "1");
    const [day, setDay] = useState(userInfo?.day ? String(userInfo.day) : "1");
    const [isBirthTimeUnknown, setIsBirthTimeUnknown] = useState(userInfo?.is_birth_time_unknown || false);
    const [timeBranch, setTimeBranch] = useState(userInfo?.hour !== null && userInfo?.hour !== undefined ? String(userInfo.hour) : "0");
    const [errorMsg, setErrorMsg] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const daysInMonth = getDaysInMonth(parseInt(year), parseInt(month));

    // Preference State
    const [prefTags, setPrefTags] = useState<string[]>(userInfo?.pref_tags || []);
    const [dislikeTags, setDislikeTags] = useState<string[]>(userInfo?.dislike_tags || []);
    const [genderFilter, setGenderFilter] = useState(userInfo?.gender_filter || "전체");
    const [interests, setInterests] = useState<string[]>(userInfo?.interests || []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userName.trim()) {
            setErrorMsg("이름(또는 닉네임)을 입력해주세요.");
            return;
        }
        setErrorMsg("");
        setIsSubmitting(true);

        onSubmit({
            user_name: userName.trim(),
            gender,
            year: parseInt(year),
            month: parseInt(month),
            day: parseInt(day),
            hour: isBirthTimeUnknown ? null : parseInt(timeBranch),
            minute: isBirthTimeUnknown ? null : 0,
            is_birth_time_unknown: isBirthTimeUnknown,
            know_time: isBirthTimeUnknown,
            pref_tags: prefTags,
            dislike_tags: dislikeTags,
            gender_filter: genderFilter,
            brand_filter_mode: "전체 뷰티 브랜드 포함",
            interests: interests
        });
    };

    const toggleArrayItem = (arr: string[], setArr: any, item: string) => {
        if (arr.includes(item)) setArr(arr.filter(i => i !== item));
        else setArr([...arr, item]);
    };

    return (
        <div className="animate-in fade-in zoom-in-95 duration-500 mt-2">
            <Card className="border shadow-sm border-slate-100 rounded-[2rem] overflow-hidden bg-white">
                <div className="bg-slate-50 border-b border-slate-100 text-slate-900 p-6 text-center">
                    <h3 className="font-extrabold text-xl tracking-tight">나만의 향수 찾기</h3>
                </div>
                <CardContent className="pt-8 px-5 sm:px-6">
                    <form onSubmit={handleSubmit} className="space-y-10">
                        {/* User Info Section */}
                        <div className="space-y-5">
                            <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">1. 내 정보</Label>

                            <div className="space-y-2">
                                <Label htmlFor="userName">이름 (또는 닉네임) <span className="text-orange-500 font-normal">(필수)</span></Label>
                                <Input
                                    id="userName"
                                    placeholder="예: 홍길동"
                                    value={userName}
                                    onChange={(e) => setUserName(e.target.value)}
                                    className="bg-slate-50/50"
                                />
                            </div>

                            <div className="space-y-3">
                                <Label>성별 <span className="text-orange-500 font-normal">(필수)</span></Label>
                                <RadioGroup value={gender} onValueChange={setGender} className="flex gap-4">
                                    <div className="flex items-center space-x-2 bg-slate-50/50 px-3 py-2 rounded-lg border flex-1 cursor-pointer">
                                        <RadioGroupItem value="여성" id="gender-f-direct" />
                                        <Label htmlFor="gender-f-direct" className="cursor-pointer flex-1">여성</Label>
                                    </div>
                                    <div className="flex items-center space-x-2 bg-slate-50/50 px-3 py-2 rounded-lg border flex-1 cursor-pointer">
                                        <RadioGroupItem value="남성" id="gender-m-direct" />
                                        <Label htmlFor="gender-m-direct" className="cursor-pointer flex-1">남성</Label>
                                    </div>
                                </RadioGroup>
                            </div>

                            <div className="space-y-2">
                                <Label>생년월일 (양력) <span className="text-orange-500 font-normal">(필수)</span></Label>
                                <div className="flex gap-2">
                                    <select
                                        aria-label="태어난 연도"
                                        value={year}
                                        onChange={(e) => {
                                            const newYear = e.target.value;
                                            setYear(newYear);
                                            const clamped = clampDay(parseInt(day), parseInt(newYear), parseInt(month));
                                            if (clamped !== parseInt(day)) setDay(String(clamped));
                                        }}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        {Array.from({ length: 100 }).map((_, i) => {
                                            const y = new Date().getFullYear() - i;
                                            return <option key={y} value={y}>{y}년</option>;
                                        })}
                                    </select>
                                    <select
                                        aria-label="태어난 월"
                                        value={month}
                                        onChange={(e) => {
                                            const newMonth = e.target.value;
                                            setMonth(newMonth);
                                            const clamped = clampDay(parseInt(day), parseInt(year), parseInt(newMonth));
                                            if (clamped !== parseInt(day)) setDay(String(clamped));
                                        }}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        {Array.from({ length: 12 }).map((_, i) => (
                                            <option key={i + 1} value={i + 1}>{i + 1}월</option>
                                        ))}
                                    </select>
                                    <select
                                        aria-label="태어난 일"
                                        value={day}
                                        onChange={(e) => setDay(e.target.value)}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        {Array.from({ length: daysInMonth }).map((_, i) => (
                                            <option key={i + 1} value={i + 1}>{i + 1}일</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="space-y-3 pt-2">
                                <div className="flex items-center justify-between">
                                    <Label>태어난 시간 <span className="text-slate-400 font-normal">(선택)</span></Label>
                                    <div className="flex items-center space-x-2">
                                        <Checkbox
                                            id="knowTimeDirect"
                                            checked={isBirthTimeUnknown}
                                            onCheckedChange={(c) => setIsBirthTimeUnknown(c as boolean)}
                                        />
                                        <Label htmlFor="knowTimeDirect" className="text-xs text-slate-500 font-normal cursor-pointer py-1">
                                            태어난 시간 모름
                                        </Label>
                                    </div>
                                </div>
                                {!isBirthTimeUnknown && (
                                    <select
                                        aria-label="태어난 시간대"
                                        value={timeBranch}
                                        onChange={(e) => setTimeBranch(e.target.value)}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        <option value="0">자시 (23:30 ~ 01:29)</option>
                                        <option value="2">축시 (01:30 ~ 03:29)</option>
                                        <option value="4">인시 (03:30 ~ 05:29)</option>
                                        <option value="6">묘시 (05:30 ~ 07:29)</option>
                                        <option value="8">진시 (07:30 ~ 09:29)</option>
                                        <option value="10">사시 (09:30 ~ 11:29)</option>
                                        <option value="12">오시 (11:30 ~ 13:29)</option>
                                        <option value="14">미시 (13:30 ~ 15:29)</option>
                                        <option value="16">신시 (15:30 ~ 17:29)</option>
                                        <option value="18">유시 (17:30 ~ 19:29)</option>
                                        <option value="20">술시 (19:30 ~ 21:29)</option>
                                        <option value="22">해시 (21:30 ~ 23:29)</option>
                                    </select>
                                )}
                            </div>
                        </div>

                        {/* Preferences Section */}
                        <div className="space-y-8">
                            <div className="space-y-4">
                                <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">2. 향수 취향 입력</Label>
                                <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center mt-2">선호하는 향 <span className="text-slate-400 font-normal text-sm">(선택)</span></Label>
                                <div className="flex flex-wrap gap-2">
                                    {TAG_OPTIONS.map(tag => (
                                        <button
                                            key={tag}
                                            type="button"
                                            onClick={() => {
                                                if (dislikeTags.includes(tag)) toggleArrayItem(dislikeTags, setDislikeTags, tag);
                                                toggleArrayItem(prefTags, setPrefTags, tag);
                                            }}
                                            className={`px-3 py-2.5 rounded-full text-xs font-medium border transition-colors ${prefTags.includes(tag) ? 'bg-orange-100 border-orange-200 text-orange-800' : 'bg-white text-slate-500 hover:bg-slate-50'}`}
                                        >
                                            {tag}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">피하고 싶은 향 <span className="text-slate-400 font-normal text-sm">(선택)</span></Label>
                                <div className="flex flex-wrap gap-2">
                                    {TAG_OPTIONS.filter(tag => !prefTags.includes(tag)).map(tag => (
                                        <button
                                            key={tag}
                                            type="button"
                                            onClick={() => toggleArrayItem(dislikeTags, setDislikeTags, tag)}
                                            className={`px-3 py-2.5 rounded-full text-xs font-medium border transition-colors ${dislikeTags.includes(tag) ? 'bg-red-100 border-red-200 text-red-800' : 'bg-white text-slate-500 hover:bg-slate-50'}`}
                                        >
                                            {tag}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4 pt-2">
                                <Label className="font-bold text-slate-800 text-base block border-b border-slate-100 pb-2 text-center">가장 끌어올리고 싶은 운 <span className="text-slate-400 font-normal text-sm">(선택)</span></Label>
                                <div className="flex flex-wrap gap-2">
                                    {INTEREST_OPTIONS.map(interest => (
                                        <button
                                            key={interest}
                                            type="button"
                                            onClick={() => toggleArrayItem(interests, setInterests, interest)}
                                            className={`px-4 py-2.5 rounded-full text-sm font-bold border transition-all ${interests.includes(interest) ? 'bg-orange-500 border-orange-500 text-white shadow-md' : 'bg-white text-slate-500 hover:bg-slate-50'}`}
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
                                            <RadioGroupItem value={g} id={`gfd-${g}`} className="peer sr-only" />
                                            <Label htmlFor={`gfd-${g}`} className="flex items-center justify-center px-2 py-3 border rounded-2xl text-sm font-medium bg-white cursor-pointer peer-data-[state=checked]:border-orange-500 peer-data-[state=checked]:bg-orange-50 peer-data-[state=checked]:font-extrabold peer-data-[state=checked]:text-orange-700 transition-all">
                                                {g}
                                            </Label>
                                        </div>
                                    ))}
                                </RadioGroup>
                            </div>
                        </div>

                        {errorMsg && <div className="text-sm text-red-500 font-bold text-center bg-red-50 p-3 rounded-xl border border-red-100" role="alert">{errorMsg}</div>}
                        {apiError && !isSubmitting && <div className="text-sm text-red-500 font-bold text-center bg-red-50 p-3 rounded-xl border border-red-100" role="alert" aria-live="assertive">{apiError}</div>}
                        <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full h-14 text-lg font-bold rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-md mt-6 transition-transform active:scale-95 text-white disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {isSubmitting ? "분석 중..." : "향수 추천받기"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div >
    );
}
