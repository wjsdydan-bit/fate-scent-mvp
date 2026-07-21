"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { getDaysInMonth, clampDay } from "@/lib/dateUtils";

export default function InputForm({ onSubmit, userInfo, apiError }: { onSubmit: (data: any) => void, userInfo?: any, apiError?: string }) {
    const [userName, setUserName] = useState(userInfo?.user_name || "");
    const [gender, setGender] = useState(userInfo?.gender || "선택 안 함");
    const [year, setYear] = useState(userInfo?.year ? String(userInfo.year) : "1995");
    const [month, setMonth] = useState(userInfo?.month ? String(userInfo.month) : "1");
    const [day, setDay] = useState(userInfo?.day ? String(userInfo.day) : "1");
    const [isBirthTimeUnknown, setIsBirthTimeUnknown] = useState(userInfo?.is_birth_time_unknown || false);
    const [timeBranch, setTimeBranch] = useState(userInfo?.hour !== null && userInfo?.hour !== undefined ? String(userInfo.hour) : "0"); // default 자시 = 0 hour
    const [errorMsg, setErrorMsg] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const daysInMonth = getDaysInMonth(parseInt(year), parseInt(month));
    const [perfBrand, setPerfBrand] = useState(userInfo?.perf_brand || "");
    const [perfName, setPerfName] = useState(userInfo?.perf_name || "");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userName.trim() || !perfBrand.trim() || !perfName.trim()) {
            setErrorMsg("이름, 브랜드명, 향수명을 모두 입력해주세요.");
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
            perf_brand: perfBrand.trim(),
            perf_name: perfName.trim()
        });
    };

    return (
        <div className="animate-in fade-in zoom-in-95 duration-500 mt-2">
            <Card className="border shadow-sm border-slate-100 rounded-[2rem] overflow-hidden bg-white">
                <div className="bg-slate-50 border-b border-slate-100 text-slate-900 p-6 text-center">
                    <h3 className="font-extrabold text-xl tracking-tight">어떤 향수를 사용 중이신가요?</h3>
                </div>
                <CardContent className="pt-8 px-5 sm:px-6">
                    <form onSubmit={handleSubmit} className="space-y-10">
                        {/* User Info Section */}
                        <div className="space-y-5">
                            <h3 className="font-bold text-lg text-slate-800 text-center">
                                1. 내 정보
                            </h3>

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
                                        <RadioGroupItem value="여성" id="gender-f" />
                                        <Label htmlFor="gender-f" className="cursor-pointer flex-1">여성</Label>
                                    </div>
                                    <div className="flex items-center space-x-2 bg-slate-50/50 px-3 py-2 rounded-lg border flex-1 cursor-pointer">
                                        <RadioGroupItem value="남성" id="gender-m" />
                                        <Label htmlFor="gender-m" className="cursor-pointer flex-1">남성</Label>
                                    </div>
                                    <div className="flex items-center space-x-2 bg-slate-50/50 px-3 py-2 rounded-lg border flex-1 cursor-pointer hidden">
                                        <RadioGroupItem value="선택 안 함" id="gender-none" />
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
                                        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
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
                                        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                        {Array.from({ length: 12 }).map((_, i) => (
                                            <option key={i + 1} value={i + 1}>{i + 1}월</option>
                                        ))}
                                    </select>
                                    <select
                                        aria-label="태어난 일"
                                        value={day}
                                        onChange={(e) => setDay(e.target.value)}
                                        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
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
                                            id="knowTime"
                                            checked={isBirthTimeUnknown}
                                            onCheckedChange={(c) => setIsBirthTimeUnknown(c as boolean)}
                                        />
                                        <Label htmlFor="knowTime" className="text-xs text-slate-500 font-normal cursor-pointer py-1">
                                            태어난 시간 모름
                                        </Label>
                                    </div>
                                </div>

                                {!isBirthTimeUnknown && (
                                    <div className="space-y-1">
                                        <select
                                            aria-label="태어난 시간대"
                                            value={timeBranch}
                                            onChange={(e) => setTimeBranch(e.target.value)}
                                            className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
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
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Perfume Info Section */}
                        <div className="space-y-5">
                            <div className="space-y-1">
                                <h3 className="font-bold text-lg text-slate-800 text-center">
                                    2. 지금 쓰는 향수
                                </h3>
                                <p className="text-sm text-slate-500 mt-1 text-center">현재 사용 중이거나 관심 있는 향수를 알려주세요.</p>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="perfBrand">브랜드명 <span className="text-orange-500 font-normal">(필수)</span></Label>
                                <Input
                                    id="perfBrand"
                                    placeholder="예: 조말론"
                                    value={perfBrand}
                                    onChange={(e) => setPerfBrand(e.target.value)}
                                    className="bg-slate-50/50"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="perfName">향수명 <span className="text-orange-500 font-normal">(필수)</span></Label>
                                <Input
                                    id="perfName"
                                    placeholder="예: 우드세이지 앤 씨솔트"
                                    value={perfName}
                                    onChange={(e) => setPerfName(e.target.value)}
                                    className="bg-slate-50/50"
                                />
                            </div>
                        </div>

                        {errorMsg && <div className="text-sm text-red-500 font-bold text-center bg-red-50 p-3 rounded-xl border border-red-100" role="alert">{errorMsg}</div>}
                        {apiError && !isSubmitting && <div className="text-sm text-red-500 font-bold text-center bg-red-50 p-3 rounded-xl border border-red-100" role="alert" aria-live="assertive">{apiError}</div>}
                        <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full h-14 text-lg font-bold rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-md transition-transform active:scale-95 text-white disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {isSubmitting ? "분석 중..." : "향수 케미 알아보기"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
