"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";

export default function InputForm({ onSubmit }: { onSubmit: (data: any) => void }) {
    const [userName, setUserName] = useState("");
    const [gender, setGender] = useState("선택 안 함");
    const [year, setYear] = useState("1995");
    const [month, setMonth] = useState("1");
    const [day, setDay] = useState("1");
    const [knowTime, setKnowTime] = useState(false);
    const [timeBranch, setTimeBranch] = useState("0"); // default 자시 = 0 hour
    const [perfBrand, setPerfBrand] = useState("");
    const [perfName, setPerfName] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userName.trim() || !perfBrand.trim() || !perfName.trim()) {
            alert("이름, 브랜드명, 향수명을 모두 입력해주세요.");
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
            perf_brand: perfBrand.trim(),
            perf_name: perfName.trim()
        });
    };

    return (
        <Card className="w-full border-none shadow-none bg-transparent pt-4">
            <CardHeader className="text-center pb-6 px-1">
                <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight leading-snug mb-2">
                    어떤 향수를<br />사용 중이신가요?
                </h1>
            </CardHeader>
            <CardContent className="px-1">
                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* User Info Section */}
                    <div className="space-y-5 bg-white p-5 sm:p-6 rounded-2xl shadow-sm border border-slate-100">
                        <h3 className="font-bold text-lg text-slate-800 text-center">
                            내 정보
                        </h3>

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
                            <Label>생년월일 (양력)</Label>
                            <div className="flex gap-2">
                                <select
                                    value={year}
                                    onChange={(e) => setYear(e.target.value)}
                                    className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {Array.from({ length: 100 }).map((_, i) => {
                                        const y = new Date().getFullYear() - i;
                                        return <option key={y} value={y}>{y}년</option>;
                                    })}
                                </select>
                                <select
                                    value={month}
                                    onChange={(e) => setMonth(e.target.value)}
                                    className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {Array.from({ length: 12 }).map((_, i) => (
                                        <option key={i + 1} value={i + 1}>{i + 1}월</option>
                                    ))}
                                </select>
                                <select
                                    value={day}
                                    onChange={(e) => setDay(e.target.value)}
                                    className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-slate-50/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
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
                                        id="knowTime"
                                        checked={knowTime}
                                        onCheckedChange={(c) => setKnowTime(c as boolean)}
                                    />
                                    <Label htmlFor="knowTime" className="text-xs text-slate-500 font-normal cursor-pointer">
                                        시간을 몰라요
                                    </Label>
                                </div>
                            </div>

                            {!knowTime && (
                                <div className="space-y-1">
                                    <select
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
                    <div className="space-y-5 bg-white p-5 sm:p-6 rounded-2xl shadow-sm border border-slate-100">
                        <div className="space-y-1">
                            <h3 className="font-bold text-lg text-slate-800 text-center">
                                지금 쓰는 향수
                            </h3>
                            <p className="text-sm text-slate-500 mt-1">현재 사용 중이거나 관심 있는 향수를 알려주세요.</p>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="perfBrand">브랜드명</Label>
                            <Input
                                id="perfBrand"
                                placeholder="예: 조말론"
                                value={perfBrand}
                                onChange={(e) => setPerfBrand(e.target.value)}
                                className="bg-slate-50/50"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="perfName">향수명</Label>
                            <Input
                                id="perfName"
                                placeholder="예: 우드세이지 앤 씨솔트"
                                value={perfName}
                                onChange={(e) => setPerfName(e.target.value)}
                                className="bg-slate-50/50"
                            />
                        </div>
                    </div>

                    <Button
                        type="submit"
                        className="w-full h-14 text-lg font-bold rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-md transition-transform active:scale-95 text-white"
                    >
                        향수 케미 알아보기
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}
