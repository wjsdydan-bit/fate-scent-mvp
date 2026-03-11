"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";

const TAG_OPTIONS = [
    "꽃향기(플로럴)", "과일향(프루티)", "나무향(우디)", "상큼한(시트러스)",
    "포근한(머스크)", "달콤한(앰버/바닐라)", "시원한(아쿠아/마린)", "스모키/가죽"
];

const INTEREST_OPTIONS = [
    "금전운 💰", "연애운 💕", "학업운 📚", "취업/직장운 💼", "대인관계 🤝"
];

export default function DirectRecommendForm({ onSubmit }: { onSubmit: (data: any) => void }) {
    // User Info State
    const [userName, setUserName] = useState("");
    const [gender, setGender] = useState("선택 안 함");
    const [year, setYear] = useState("1995");
    const [month, setMonth] = useState("1");
    const [day, setDay] = useState("1");
    const [knowTime, setKnowTime] = useState(false);
    const [timeBranch, setTimeBranch] = useState("0");

    // Preference State
    const [prefTags, setPrefTags] = useState<string[]>([]);
    const [dislikeTags, setDislikeTags] = useState<string[]>([]);
    const [genderFilter, setGenderFilter] = useState("전체");
    const [interests, setInterests] = useState<string[]>([]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userName.trim()) {
            alert("이름(또는 닉네임)을 입력해주세요.");
            return;
        }

        onSubmit({
            user_name: userName.trim(),
            gender,
            year: parseInt(year),
            month: parseInt(month),
            day: parseInt(day),
            hour: knowTime ? null : parseInt(timeBranch),
            minute: knowTime ? null : 0,
            know_time: knowTime,
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
                            <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">내 정보</Label>

                            <div className="space-y-2">
                                <Label htmlFor="userName">이름 (또는 닉네임)</Label>
                                <Input
                                    id="userName"
                                    placeholder="예: 홍길동"
                                    value={userName}
                                    onChange={(e) => setUserName(e.target.value)}
                                    className="bg-slate-50/50"
                                />
                            </div>

                            <div className="space-y-3">
                                <Label>성별</Label>
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
                                <Label>생년월일 (양력)</Label>
                                <div className="flex gap-2">
                                    <select
                                        value={year}
                                        onChange={(e) => setYear(e.target.value)}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        {Array.from({ length: 100 }).map((_, i) => {
                                            const y = new Date().getFullYear() - i;
                                            return <option key={y} value={y}>{y}년</option>;
                                        })}
                                    </select>
                                    <select
                                        value={month}
                                        onChange={(e) => setMonth(e.target.value)}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        {Array.from({ length: 12 }).map((_, i) => (
                                            <option key={i + 1} value={i + 1}>{i + 1}월</option>
                                        ))}
                                    </select>
                                    <select
                                        value={day}
                                        onChange={(e) => setDay(e.target.value)}
                                        className="flex h-10 w-full rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm"
                                    >
                                        {Array.from({ length: 31 }).map((_, i) => (
                                            <option key={i + 1} value={i + 1}>{i + 1}일</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="space-y-3 pt-2">
                                <div className="flex items-center justify-between">
                                    <Label>태어난 시간</Label>
                                    <div className="flex items-center space-x-2">
                                        <Checkbox
                                            id="knowTimeDirect"
                                            checked={knowTime}
                                            onCheckedChange={(c) => setKnowTime(c as boolean)}
                                        />
                                        <Label htmlFor="knowTimeDirect" className="text-xs text-slate-500 font-normal cursor-pointer">
                                            시간을 몰라요
                                        </Label>
                                    </div>
                                </div>
                                {!knowTime && (
                                    <select
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
                                <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">선호하는 향</Label>
                                <div className="flex flex-wrap gap-2">
                                    {TAG_OPTIONS.map(tag => (
                                        <button
                                            key={tag}
                                            type="button"
                                            onClick={() => {
                                                if (dislikeTags.includes(tag)) toggleArrayItem(dislikeTags, setDislikeTags, tag);
                                                toggleArrayItem(prefTags, setPrefTags, tag);
                                            }}
                                            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${prefTags.includes(tag) ? 'bg-orange-100 border-orange-200 text-orange-800' : 'bg-white text-slate-500 hover:bg-slate-50'}`}
                                        >
                                            {tag}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <Label className="font-bold text-slate-800 text-base border-b border-slate-100 pb-2 block text-center">피하고 싶은 향</Label>
                                <div className="flex flex-wrap gap-2">
                                    {TAG_OPTIONS.filter(tag => !prefTags.includes(tag)).map(tag => (
                                        <button
                                            key={tag}
                                            type="button"
                                            onClick={() => toggleArrayItem(dislikeTags, setDislikeTags, tag)}
                                            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${dislikeTags.includes(tag) ? 'bg-red-100 border-red-200 text-red-800' : 'bg-white text-slate-500 hover:bg-slate-50'}`}
                                        >
                                            {tag}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4 pt-2">
                                <Label className="font-bold text-slate-800 text-base block border-b border-slate-100 pb-2 text-center">가장 끌어올리고 싶은 운</Label>
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

                        <Button
                            type="submit"
                            className="w-full h-14 text-lg font-bold rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-md mt-6 transition-transform active:scale-95 text-white"
                        >
                            운명 향수 추천받기
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div >
    );
}
