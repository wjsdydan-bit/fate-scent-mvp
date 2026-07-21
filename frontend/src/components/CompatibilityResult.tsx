"use client";

import { useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import PhotoShareOverlay from "./PhotoShareOverlay";
import { 
    Sprout, Flame, Mountain, Gem, Droplets, SprayCan, Share2, Info, Check, X, Heart, HeartCrack
} from "lucide-react";

const ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"];
const ELEMENTS_KO: Record<string, string> = {
    Wood: "목(나무)", Fire: "화(불)", Earth: "토(흙)", Metal: "금(쇠)", Water: "수(물)"
};
const ELEMENT_EMOJI: Record<string, React.ReactNode> = {
    Wood: <Sprout className="w-4 h-4 text-green-500 inline-block" strokeWidth={1.75} aria-hidden="true" />,
    Fire: <Flame className="w-4 h-4 text-red-500 inline-block" strokeWidth={1.75} aria-hidden="true" />,
    Earth: <Mountain className="w-4 h-4 text-amber-600 inline-block" strokeWidth={1.75} aria-hidden="true" />,
    Metal: <Gem className="w-4 h-4 text-slate-400 inline-block" strokeWidth={1.75} aria-hidden="true" />,
    Water: <Droplets className="w-4 h-4 text-blue-500 inline-block" strokeWidth={1.75} aria-hidden="true" />
};
const ELEMENT_KEYWORDS: Record<string, string[]> = {
    Wood: [
        "bergamot", "lemon", "mandarin", "grapefruit", "orange",
        "petitgrain", "green", "galbanum", "bamboo", "tea", "cypress",
        "apple", "fig", "neroli", "citrus"
    ],
    Fire: [
        "jasmine", "rose", "ylang", "tuberose", "blossom", "peony",
        "geranium", "lily", "saffron", "leather", "tobacco", "incense",
        "pepper", "cinnamon", "carnation", "magnolia", "freesia", "orchid", "spicy"
    ],
    Earth: [
        "vanilla", "tonka", "patchouli", "iris", "benzoin", "peach",
        "pear", "heliotrope", "violet", "oakmoss", "vetiver", "sandalwood",
        "chocolate", "caramel", "honey", "almond", "plum", "amber", "sweet"
    ],
    Metal: [
        "white musk", "lavender", "cardamom", "nutmeg", "coriander",
        "ginger", "mint", "aldehyde", "cedar", "metallic",
        "eucalyptus", "rosemary", "juniper", "sage", "pine", "herb"
    ],
    Water: [
        "musk", "ambergris", "sea", "marine", "aquatic", "salt",
        "seaweed", "water", "cucumber", "melon", "calone", "castoreum", "civet"
    ]
};
const ELEMENT_BAR_COLORS: Record<string, string> = {
    Wood: "bg-emerald-400", Fire: "bg-rose-400", Earth: "bg-amber-400", Metal: "bg-slate-400", Water: "bg-sky-400"
};

const NOTE_KO_MAP: Record<string, string> = {
    "bergamot": "베르가못", "lemon": "레몬", "orange": "오렌지", "grapefruit": "자몽",
    "lime": "라임", "mandarin": "만다린", "yuzu": "유자", "rose": "로즈",
    "jasmine": "자스민", "ylang": "일랑일랑", "tuberose": "튜베로즈",
    "iris": "아이리스", "neroli": "네롤리", "violet": "바이올렛",
    "sandalwood": "샌달우드", "cedar": "시더", "vetiver": "베티버",
    "patchouli": "패출리", "oud": "우드", "oakmoss": "오크모스", "moss": "모스",
    "musk": "머스크", "white musk": "화이트 머스크", "amber": "앰버",
    "vanilla": "바닐라", "tonka": "통카", "benzoin": "벤조인",
    "aquatic": "아쿠아틱", "sea salt": "씨솔트", "marine": "마린",
    "incense": "인센스", "leather": "레더", "tobacco": "타바코",
    "pepper": "페퍼", "ginger": "진저", "cinnamon": "시나몬",
    "green": "그린", "tea": "티", "mint": "민트", "pine": "파인",
    "white floral": "화이트 플로럴", "floral": "플로럴", "fruity": "프루티",
    "woody": "우디", "citrus": "시트러스", "spicy": "스파이시",
    "powdery": "파우더리", "sweet": "스위트", "warm": "웜", "fresh": "프레시",
    "petitgrain": "쁘띠그레인", "galbanum": "갈바넘", "bamboo": "대나무", "cypress": "사이프러스",
    "apple": "사과", "fig": "무화과", "blossom": "블러썸", "peony": "작약", "geranium": "제라늄",
    "lily": "백합", "saffron": "사프란", "carnation": "카네이션", "magnolia": "목련", "freesia": "프리지아",
    "orchid": "난초", "peach": "복숭아", "pear": "서양배", "heliotrope": "헬리오트로프",
    "chocolate": "초콜릿", "caramel": "카라멜", "honey": "꿀", "almond": "아몬드", "plum": "자두",
    "cardamom": "카다멈", "nutmeg": "너트멕", "coriander": "코리앤더", "metallic": "메탈릭",
    "eucalyptus": "유칼립투스", "rosemary": "로즈마리", "juniper": "주니퍼", "sage": "세이지",
    "herb": "허브", "ambergris": "앰버그리스", "salt": "소금", "sea": "바다", "seaweed": "해초",
    "water": "워터", "cucumber": "오이", "melon": "멜론", "calone": "카론", "castoreum": "카스토륨", "civet": "시벳"
};

function translateNote(note: string): string {
    let result = note;
    Object.entries(NOTE_KO_MAP).forEach(([en, ko]) => {
        const re = new RegExp(`\\b${en}\\b`, "gi");
        result = result.replace(re, ko);
    });
    return result;
}

function getMatchedNotes(notesText: string, elem: string): string[] {
    const kws = ELEMENT_KEYWORDS[elem] || [];
    return kws.filter(kw => notesText.toLowerCase().includes(kw)).map(kw => translateNote(kw));
}

export default function CompatibilityResult({ data, userInfo, onNext, onReset }: any) {
    const captureRef = useRef<HTMLDivElement>(null);
    const [showPhotoOverlay, setShowPhotoOverlay] = useState(false);

    if (!data) return null;

    const { saju_data, compatibility_score, compatibility_result, perfume_details } = data;
    const strongElements: string[] = saju_data?.strongest_elements || [saju_data?.strongest].filter(Boolean);
    const weakElements: string[] = saju_data?.weakest_elements || [saju_data?.weakest].filter(Boolean);
    const strongest = strongElements[0] || "";
    const weakest = weakElements[0] || "";
    const strongestKo = strongElements.map((e: string) => ELEMENTS_KO[e] || e).join("·");
    const weakestKo = weakElements.map((e: string) => ELEMENTS_KO[e] || e).join("·");
    const { pillars } = saju_data;
    const perf_vec = perfume_details.element_vector;
    const cr = compatibility_result;

    let scoreColor = "text-rose-500";
    let scoreBg = "bg-rose-50";
    if (compatibility_score >= 75) {
        scoreColor = "text-orange-500";
        scoreBg = "bg-orange-50";
    } else if (compatibility_score >= 50) {
        scoreColor = "text-slate-700";
        scoreBg = "bg-slate-100";
    }

    const genderEmoji = userInfo?.gender === "여성" ? "🙋‍♀️" : userInfo?.gender === "남성" ? "🙋‍♂️" : "🙋";

    const handleCapture = async () => {
        if (!captureRef.current) return;
        try {
            const { toPng } = await import("html-to-image");
            await new Promise(resolve => setTimeout(resolve, 50));
            const dataUrl = await toPng(captureRef.current, {
                pixelRatio: 2,
                backgroundColor: "#f8fafc"
            });
            const link = document.createElement("a");
            const filename = `fatescent_궁합결과_${userInfo?.user_name || "결과"}.png`;
            link.download = filename;
            link.href = dataUrl;
            link.target = "_blank";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (err: any) {
            alert(`캡쳐 중 오류가 발생했습니다: ${err?.message || err}`);
        }
    };

    return (
        <div className="space-y-6 pb-6 animate-in fade-in zoom-in-95 duration-500">
            {showPhotoOverlay && (
                <PhotoShareOverlay
                    userInfo={userInfo}
                    perfumeDetails={{
                        ...perfume_details,
                        notes: getMatchedNotes(perfume_details.notes || "", strongest).slice(0, 3)
                    }}
                    sajuData={{ strongest, weakest }}
                    additionalData={{ type: "compatibility", score: compatibility_score, scoreComment: cr.score_comment }}
                    onClose={() => setShowPhotoOverlay(false)}
                />
            )}

            <div ref={captureRef} className="space-y-6">
                {/* Hero Header */}
                <div className={`text-center space-y-4 mt-6 ${scoreBg} p-8 rounded-[2rem]`}>
                    <div className="text-sm font-bold text-slate-500 tracking-wide">케미 점수</div>

                    <div className="flex justify-center items-center gap-6 mt-2">
                        <div className="flex flex-col items-center">
                            <span className="text-4xl bg-white border p-3 rounded-full shadow-sm mb-2 aspect-square flex items-center justify-center">{genderEmoji}</span>
                            <span className="text-sm font-bold text-slate-700">{userInfo?.user_name}</span>
                        </div>
                        <span className="text-orange-500 font-extrabold text-2xl">X</span>
                        <div className="flex flex-col items-center">
                            {perfume_details.image_url ? (
                                <img src={perfume_details.image_url} alt={perfume_details.name} crossOrigin="anonymous" className="w-16 h-16 object-contain bg-white border p-1 rounded-full shadow-sm mb-2" />
                            ) : (
                                <span className="bg-white border p-3 rounded-full shadow-sm mb-2 aspect-square flex items-center justify-center"><SprayCan className="w-8 h-8 text-slate-300" strokeWidth={1.5} aria-hidden="true" /></span>
                            )}
                            <span className="text-xs font-bold text-slate-700 text-center leading-tight max-w-[80px] break-words">
                                {perfume_details.brand}<br />{perfume_details.name}
                            </span>
                        </div>
                    </div>

                    <div className={`text-6xl font-black ${scoreColor} mt-4`}>
                        {compatibility_score}<span className="text-2xl text-slate-400">/100</span>
                    </div>

                    {/* One-liner */}
                    <div className="text-lg font-extrabold text-slate-800 mt-2 px-4 leading-relaxed">
                        &ldquo;{cr.one_liner}&rdquo;
                    </div>

                    {/* Score comment */}
                    {cr.score_comment && (
                        <div className="inline-block bg-white/85 backdrop-blur-sm text-sm font-bold text-slate-600 px-5 py-2.5 rounded-full shadow-sm border border-slate-100 leading-normal">
                            {cr.score_comment}
                        </div>
                    )}
                </div>

                {/* Saju 8 Characters */}
                <Card className="border shadow-sm bg-white overflow-hidden rounded-[2rem] border-slate-100 border">
                    <div className="bg-slate-50 text-slate-800 p-4 text-center font-extrabold text-base flex items-center justify-center gap-2 border-b">
                        나의 사주 팔자
                    </div>
                    <div className="grid grid-cols-4 divide-x border-b text-center bg-slate-50">
                        {["일(나)", "월", "년", "시"].map(l => (
                            <div key={l} className="py-2 text-xs font-semibold text-slate-500">{l}</div>
                        ))}
                    </div>
                    <div className="grid grid-cols-4 divide-x border-b bg-white text-center">
                        {["day", "month", "year", "hour"].map(key => (
                            <div key={key} className="py-2.5 font-bold text-base flex flex-col items-center">
                                <span className="mb-1 flex items-center justify-center">{ELEMENT_EMOJI[pillars[key]?.stem_element] || <span className="text-xs text-slate-300">?</span>}</span>
                                {pillars[key]?.stem || "?"}
                            </div>
                        ))}
                    </div>
                    <div className="grid grid-cols-4 divide-x bg-white text-center">
                        {["day", "month", "year", "hour"].map(key => (
                            <div key={key} className="py-2.5 font-bold text-base flex flex-col items-center">
                                <span className="mb-1 flex items-center justify-center">{ELEMENT_EMOJI[pillars[key]?.branch_element] || <span className="text-xs text-slate-300">?</span>}</span>
                                {pillars[key]?.branch || "?"}
                            </div>
                        ))}
                    </div>
                </Card>

                {/* Saju Summary - grid spacing improved */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 border border-slate-100 p-5 rounded-[2rem] flex flex-col items-center shadow-sm">
                        <span className="text-xs font-bold text-slate-500 mb-2">내 강한 기운</span>
                        <span className="flex flex-wrap gap-1 mb-1.5">{strongElements.map((e: string, i) => <span key={i}>{ELEMENT_EMOJI[e]}</span>)}</span>
                        <span className="font-extrabold text-slate-800 text-sm">{strongestKo}</span>
                    </div>
                    <div className="bg-slate-50 border border-slate-100 p-5 rounded-[2rem] flex flex-col items-center shadow-sm">
                        <span className="text-xs font-bold text-slate-500 mb-2">내 부족한 기운</span>
                        <span className="flex flex-wrap gap-1 mb-1.5">{weakElements.map((e: string, i) => <span key={i}>{ELEMENT_EMOJI[e]}</span>)}</span>
                        <span className="font-extrabold text-slate-800 text-sm">{weakestKo}</span>
                    </div>
                </div>

                {/* 향수 오행 밸런스 */}
                <Card className="border shadow-sm border-slate-100 rounded-[2rem] overflow-hidden bg-white pt-5 pb-2">
                    <h3 className="font-extrabold text-center text-slate-800 mb-2 text-lg">향수의 오행 밸런스</h3>
                    <CardContent className="space-y-4 mt-4">
                        {ELEMENTS.map(elem => {
                            const val = (perf_vec[elem] || 0) * 100;
                            const matched = getMatchedNotes(perfume_details.notes || "", elem);
                            return (
                                <div key={elem} className="space-y-1">
                                    <div className="flex justify-between text-sm font-bold text-slate-700">
                                        <span className="flex items-center gap-1">{ELEMENT_EMOJI[elem]} {ELEMENTS_KO[elem]}</span>
                                        <span>{val.toFixed(0)}%</span>
                                    </div>
                                    <div className="w-full bg-slate-100 rounded-full h-3">
                                        <div className={`${ELEMENT_BAR_COLORS[elem]} h-3 rounded-full transition-all duration-700`} style={{ width: `${Math.max(val, 2)}%` }}></div>
                                    </div>
                                    <div className="text-[11px] text-slate-400 pl-1">
                                        {matched.length > 0 ? `→ ${matched.join(", ")}` : "해당 노트 없음"}
                                    </div>
                                </div>
                            );
                        })}
                    </CardContent>
                    {/* 중복 및 사주 요약 분석문이 다소 겹치는 부분을 위해 패딩 및 구조 압축 */}
                    {cr.perf_element_summary && (
                        <div className="p-5 bg-slate-50/70 text-sm text-slate-600 leading-relaxed border-t whitespace-pre-line font-medium">
                            {cr.perf_element_summary}
                        </div>
                    )}
                </Card>

                {/* Pros & Cons - text size 12px -> 13.5px, padding/line-height optimized */}
                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="space-y-2.5">
                        <h4 className="font-extrabold text-sm text-center text-emerald-800 bg-emerald-50 py-2 rounded-xl flex items-center justify-center gap-1.5"><Heart className="w-4 h-4 fill-emerald-600 text-emerald-600" strokeWidth={2} aria-hidden="true" /> 잘 맞는 이유</h4>
                        <ul className="space-y-2">
                            {cr.good_reasons?.map((r: string, idx: number) => (
                                <li key={idx} className="bg-white border text-[13.5px] p-3 rounded-xl shadow-sm text-slate-700 leading-relaxed flex items-start">
                                    <Check className="w-3.5 h-3.5 text-emerald-600 mt-1 mr-1.5 shrink-0" strokeWidth={2.5} aria-hidden="true" />
                                    <span>{r}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="space-y-2.5">
                        <h4 className="font-extrabold text-sm text-center text-rose-800 bg-rose-50 py-2 rounded-xl flex items-center justify-center gap-1.5"><HeartCrack className="w-4 h-4 fill-rose-600 text-rose-600" strokeWidth={2} aria-hidden="true" /> 아쉬운 점</h4>
                        <ul className="space-y-2">
                            {cr.bad_reasons?.map((r: string, idx: number) => (
                                <li key={idx} className="bg-white border text-[13.5px] p-3 rounded-xl shadow-sm text-slate-700 leading-relaxed flex items-start">
                                    <X className="w-3.5 h-3.5 text-rose-600 mt-1 mr-1.5 shrink-0" strokeWidth={2.5} aria-hidden="true" />
                                    <span>{r}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {perfume_details.source === "ai" && (
                    <p className="text-xs text-center text-slate-400 mt-2 flex items-center justify-center gap-1">
                        <Info className="w-3.5 h-3.5" strokeWidth={2} aria-hidden="true" /> 이 향수는 DB에 없어 노트를 추론했습니다.
                    </p>
                )}
            </div>

            <div className="flex gap-2 mt-6">
                <Button
                    onClick={() => setShowPhotoOverlay(true)}
                    variant="default"
                    className="flex-1 h-16 text-base font-extrabold rounded-2xl bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 text-white shadow-lg shadow-fuchsia-500/30 transition-all active:scale-95 flex items-center justify-center gap-2"
                >
                    <Share2 className="w-5 h-5" strokeWidth={2} aria-hidden="true" /> 내 사진에 결과 입히기
                </Button>
            </div>

            <div className="flex gap-2">
                <Button
                    onClick={handleCapture}
                    variant="outline"
                    className="flex-1 h-12 text-sm font-bold rounded-2xl border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
                >
                    결과화면 캡처만 하기
                </Button>
            </div>

            <Button
                onClick={() => onNext()}
                className="w-full h-16 text-lg font-black rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-xl shadow-orange-500/20 transition-all active:scale-95 text-white mt-4 border-2 border-orange-400"
            >
                나에게 맞는 향수 추천받기
            </Button>

            <Button
                type="button"
                variant="ghost"
                onClick={onReset}
                className="w-full h-12 text-slate-400 text-sm mt-1"
            >
                처음으로 돌아가기
            </Button>
        </div>
    );
}
