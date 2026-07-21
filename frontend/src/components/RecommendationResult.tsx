"use client";

import { useRef, useState } from "react";
import {
    Card, CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import PhotoShareOverlay from "./PhotoShareOverlay";
import { 
    Sprout, Flame, Mountain, Gem, Droplets, 
    Sparkles, Info, Share2, Award, SprayCan, AlertCircle, RefreshCw,
    ChevronDown, ChevronUp 
} from "lucide-react";

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

function translateNotes(notes: string): string {
    if (!notes) return "";
    let result = notes;
    const sorted = Object.entries(NOTE_KO_MAP).sort((a, b) => b[0].length - a[0].length);
    sorted.forEach(([en, ko]) => {
        const re = new RegExp(en.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
        result = result.replace(re, ko);
    });
    return result;
}

const ELEMENTS_KO: Record<string, string> = {
    Wood: "목(나무)", Fire: "화(불)", Earth: "토(흙)", Metal: "금(쇠)", Water: "수(물)"
};
const ELEMENT_EMOJI: Record<string, React.ReactNode> = {
    Wood: <Sprout className="w-5 h-5 text-green-500" strokeWidth={1.75} aria-hidden="true" />,
    Fire: <Flame className="w-5 h-5 text-red-500" strokeWidth={1.75} aria-hidden="true" />,
    Earth: <Mountain className="w-5 h-5 text-amber-600" strokeWidth={1.75} aria-hidden="true" />,
    Metal: <Gem className="w-5 h-5 text-slate-400" strokeWidth={1.75} aria-hidden="true" />,
    Water: <Droplets className="w-5 h-5 text-blue-500" strokeWidth={1.75} aria-hidden="true" />
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

export default function RecommendationResult({ data, userInfo, onReset }: any) {
    const shareRef = useRef<HTMLDivElement>(null);
    const [showPhotoOverlay, setShowPhotoOverlay] = useState(false);
    // 각 향수 카드별 아코디언(더보기) 토글 상태
    const [expandedIndex, setExpandedIndex] = useState<Record<number, boolean>>({});
    // 파비콘 로딩 에러 상태
    const [faviconError, setFaviconError] = useState<Record<number, boolean>>({});

    if (!data) return null;

    const { top3, reading_result } = data;
    const { saju_analysis, luck_analysis, hero_title, summary } = reading_result;

    const handleSearch = (brand: string, name: string) => {
        const query = encodeURIComponent(`${brand} ${name} 향수`);
        window.open(`https://search.shopping.naver.com/search/all?query=${query}`, "_blank");
    };

    const bestPerfume = top3[0] || {};

    const weakElements: string[] = userInfo?.saju_data?.weakest_elements || reading_result?.saju_data?.weakest_elements || 
        [userInfo?.saju_data?.weakest || reading_result?.saju_data?.weakest || ""].filter(Boolean);
    const strongElements: string[] = userInfo?.saju_data?.strongest_elements || reading_result?.saju_data?.strongest_elements || 
        [userInfo?.saju_data?.strongest || reading_result?.saju_data?.strongest || ""].filter(Boolean);
    const weakElement = weakElements[0] || "";
    const strongElement = strongElements[0] || "";
    const weakElementKo = weakElements.map(e => ELEMENTS_KO[e] || e).join("·") || weakElement;
    const strongElementKo = strongElements.map(e => ELEMENTS_KO[e] || e).join("·") || strongElement;
    const genderEmoji = userInfo?.gender === "여성" ? "🙋‍♀️" : "🙋‍♂️";
    const interestsList: string[] = userInfo?.interests || [];

    const handleShareCapture = async () => {
        if (!shareRef.current) return;
        try {
            const { toPng } = await import("html-to-image");
            await new Promise(resolve => setTimeout(resolve, 50));
            const filter = (node: HTMLElement) => {
                if (node.classList && node.classList.contains('share-favicon')) {
                    return false;
                }
                return true;
            };
            const dataUrl = await toPng(shareRef.current, {
                pixelRatio: 2,
                backgroundColor: "#ffffff",
                filter: filter as any
            });
            const link = document.createElement("a");
            const filename = `fatescent_${userInfo?.user_name || "결과"}.png`;
            link.download = filename;
            link.href = dataUrl;
            link.target = "_blank";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (err: any) {
            console.error(err);
            alert(`캡쳐 중 오류가 발생했습니다: ${err?.message || err}`);
        }
    };

    // 요약 한두 문장 축소
    const displaySummary = summary 
        ? summary.split(/[.!?]/).filter(Boolean).slice(0, 2).map((s: string) => s.trim()).join(". ") + "." 
        : `당신의 사주는 ${strongElementKo} 기운이 강하고 ${weakElementKo} 기운이 부족해요. 추천된 향수가 오행의 균형을 보완하는 데 도움을 줍니다.`;

    const toggleExpand = (idx: number) => {
        setExpandedIndex(prev => ({ ...prev, [idx]: !prev[idx] }));
    };

    return (
        <div className="space-y-6 pb-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {showPhotoOverlay && (
                <PhotoShareOverlay
                    userInfo={userInfo}
                    perfumeDetails={{
                        brand: bestPerfume.Brand || bestPerfume.brand,
                        name: bestPerfume.Name || bestPerfume.name,
                        image_url: bestPerfume.image_url,
                        notes: translateNotes(bestPerfume.Notes || bestPerfume.notes_ko || "")
                    }}
                    sajuData={{ strongest: strongElement, weakest: weakElement }}
                    additionalData={{ type: "recommendation", heroTitle: hero_title }}
                    onClose={() => setShowPhotoOverlay(false)}
                />
            )}

            {/* Header */}
            <div className="text-center space-y-3 mt-4 bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
                <Sparkles className="w-8 h-8 text-orange-500 mx-auto mb-2" strokeWidth={1.75} aria-hidden="true" />
                <h2 className="text-xl font-extrabold text-slate-900 tracking-tight leading-snug break-keep">
                    {hero_title}
                </h2>
                <p className="text-sm text-slate-500 bg-white py-1.5 px-4 rounded-full inline-block font-bold shadow-sm border border-slate-100">
                    {userInfo?.user_name}님의 사주 향수 분석
                </p>
            </div>

            <Tabs defaultValue="summary" className="w-full">
                <TabsList className="grid w-full grid-cols-3 bg-slate-100 p-1.5 rounded-2xl">
                    <TabsTrigger value="summary" className="rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-orange-600 font-bold text-xs"><Sparkles className="w-3.5 h-3.5 mr-1" strokeWidth={2} aria-hidden="true" />요약</TabsTrigger>
                    <TabsTrigger value="analysis" className="rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-orange-600 font-bold text-xs"><Info className="w-3.5 h-3.5 mr-1" strokeWidth={2} aria-hidden="true" />사주풀이</TabsTrigger>
                    <TabsTrigger value="share" className="rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-sm data-[state=active]:text-orange-600 font-bold text-xs"><Share2 className="w-3.5 h-3.5 mr-1" strokeWidth={2} aria-hidden="true" />공유</TabsTrigger>
                </TabsList>

                {/* ─── TAB 1: SUMMARY ─── */}
                <TabsContent value="summary" className="space-y-5 pt-4 outline-none">

                    {/* 핵심 요약 */}
                    <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
                        <h3 className="font-extrabold text-slate-900 mb-2 flex items-center gap-2 font-bold">
                            <span className="bg-white p-1.5 rounded-xl shadow-sm border border-slate-100 flex items-center justify-center"><Info className="w-4 h-4 text-slate-700" strokeWidth={2} aria-hidden="true" /></span> 핵심 요약
                        </h3>
                        <p className="text-[13px] text-slate-600 leading-[1.8] font-medium">
                            {displaySummary}
                        </p>
                    </div>

                    {/* 추천 향수 Top 3 */}
                    <div className="space-y-4">
                        <h3 className="font-bold text-slate-800 pl-1 flex items-center gap-1.5">
                            <Award className="w-5 h-5 text-orange-500" strokeWidth={2} aria-hidden="true" /> 추천 향수 Top 3
                        </h3>
                        {top3.map((perfume: any, idx: number) => {
                            const topKo = translateNotes(perfume.top_ko || perfume.Top || "");
                            const midKo = translateNotes(perfume.middle_ko || perfume.Middle || "");
                            const baseKo = translateNotes(perfume.base_ko || perfume.Base || "");
                            const notesKo = translateNotes(perfume.notes_ko || perfume.Notes || "");
                            const compactNotes = [topKo, midKo, baseKo].filter(Boolean).join(" - ");
                            const displayNotes = compactNotes || notesKo || "매치 향조 포함";
                            const isBest = idx === 0;
                            const isExpanded = expandedIndex[idx] || false;

                            if (isBest) {
                                // 1위 향수 (🥇 Best Match로 크게 강조)
                                return (
                                    <Card key={idx} className="border border-orange-200/80 shadow-md flex flex-col overflow-hidden rounded-[2rem] transition-all bg-gradient-to-b from-orange-50/10 to-white">
                                        <div className="bg-orange-100/60 px-5 py-4 flex justify-between items-center border-b border-orange-100">
                                            <div className="font-black text-orange-900 text-lg flex items-center gap-2 truncate pr-2">
                                                <Award className="w-6 h-6 text-orange-600" strokeWidth={2} aria-hidden="true" /> Best Match
                                                {faviconError[idx] ? (
                                                    <SprayCan className="w-4 h-4 text-slate-400 shrink-0" strokeWidth={1.75} aria-hidden="true" />
                                                ) : (
                                                    <img
                                                        src={`https://www.google.com/s2/favicons?domain=${(perfume.Brand || perfume.brand || "").toLowerCase().replace(/\s+/g, '')}.com&sz=128`}
                                                        onError={() => setFaviconError(prev => ({ ...prev, [idx]: true }))}
                                                        className="w-5 h-5 rounded-full shadow-sm object-cover bg-white shrink-0"
                                                        alt=""
                                                    />
                                                )}
                                                <span className="truncate">{perfume.Brand || perfume.brand}</span>
                                            </div>
                                            <span className="text-[11px] font-extrabold text-orange-700 bg-orange-200/50 py-1 px-3 rounded-full shrink-0">Top 1</span>
                                        </div>
                                        <CardContent className="p-5 space-y-4 bg-white">
                                            <div className="flex gap-4 items-center">
                                                {perfume.image_url ? (
                                                    <img src={perfume.image_url} alt={perfume.Name || perfume.name} className="w-20 h-20 object-contain rounded-xl border p-1 shadow-sm bg-slate-50 shrink-0" />
                                                ) : (
                                                    <div className="w-20 h-20 bg-slate-50 border rounded-xl flex items-center justify-center shadow-sm shrink-0"><SprayCan className="w-10 h-10 text-slate-300" strokeWidth={1.5} aria-hidden="true" /></div>
                                                )}
                                                <div>
                                                    <div className="text-xs font-bold text-slate-400 mb-1">{perfume.Brand || perfume.brand}</div>
                                                    <div className="text-lg font-black text-slate-800 leading-tight">{perfume.Name || perfume.name}</div>
                                                </div>
                                            </div>

                                            {/* Notes 상세 정보 */}
                                            {(topKo || midKo || baseKo) ? (
                                                <div className="space-y-1.5 text-xs text-slate-600 bg-slate-50/80 p-3.5 rounded-2xl border border-slate-100 break-keep">
                                                    {topKo && <div className="leading-relaxed"><span className="font-bold text-orange-600 shrink-0">탑</span>&nbsp;{topKo}</div>}
                                                    {midKo && <div className="leading-relaxed"><span className="font-bold text-slate-700 shrink-0">미들</span>&nbsp;{midKo}</div>}
                                                    {baseKo && <div className="leading-relaxed"><span className="font-bold text-slate-500 shrink-0">베이스</span>&nbsp;{baseKo}</div>}
                                                </div>
                                            ) : notesKo ? (
                                                <div className="text-xs text-slate-600 bg-slate-50/80 p-3.5 rounded-2xl border border-slate-100 break-keep leading-relaxed">
                                                    <span className="font-bold text-orange-600 shrink-0">노트</span>&nbsp;{notesKo}
                                                </div>
                                            ) : null}

                                            {/* AI Match Reason 아코디언 */}
                                            {perfume.element_match_reason && (
                                                <div className="mt-3 p-4 bg-orange-50/40 rounded-2xl border border-orange-100">
                                                    <h4 className="text-xs font-bold text-orange-950/80 mb-1.5 flex items-center gap-1">
                                                        <Sparkles className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 매칭 포인트
                                                    </h4>
                                                    <p className={`text-[13px] text-orange-950/80 leading-[1.8] font-medium transition-all break-keep ${isExpanded ? "" : "line-clamp-2"}`}>
                                                        {perfume.element_match_reason}
                                                    </p>
                                                    <button 
                                                        onClick={() => toggleExpand(idx)}
                                                        className="text-xs font-bold text-orange-600 hover:text-orange-700 mt-2 flex items-center gap-1 w-full text-left py-2 active:bg-orange-100/50 rounded-lg"
                                                    >
                                                        {isExpanded ? (
                                                            <><ChevronUp className="w-4 h-4" strokeWidth={2} aria-hidden="true" /> 추천 사유 접기</>
                                                        ) : (
                                                            <><ChevronDown className="w-4 h-4" strokeWidth={2} aria-hidden="true" /> 추천 사유 더 보기</>
                                                        )}
                                                    </button>
                                                </div>
                                            )}

                                            <Button
                                                variant="default"
                                                className="w-full mt-2 text-xs font-extrabold bg-orange-500 hover:bg-orange-600 text-white rounded-xl h-12 shadow-sm"
                                                onClick={() => handleSearch(perfume.Brand || perfume.brand || "", perfume.Name || perfume.name || "")}
                                            >
                                                🛒 네이버 최저가 검색 및 구매
                                            </Button>
                                        </CardContent>
                                    </Card>
                                );
                            } else {
                                // 2·3위 향수 (작은 보조 카드로 표시)
                                return (
                                    <Card key={idx} className="border border-slate-100 shadow-sm flex flex-col overflow-hidden rounded-2xl bg-white transition hover:shadow-md">
                                        <div className="bg-slate-50/70 px-4 py-2.5 flex justify-between items-center border-b border-slate-100 text-xs">
                                            <div className="font-extrabold text-slate-600 flex items-center gap-1.5 truncate">
                                                <span className="shrink-0 flex items-center gap-1">
                                                    <Award className="w-4 h-4 text-slate-400" strokeWidth={2} aria-hidden="true" /> {idx}위
                                                </span>
                                                <span className="text-slate-400 shrink-0">|</span>
                                                <span className="truncate font-bold">{perfume.Brand || perfume.brand}</span>
                                            </div>
                                            <span className="text-[10px] text-slate-400 font-bold shrink-0 ml-2">보완 추천</span>
                                        </div>
                                        <CardContent className="p-3.5 space-y-2">
                                            <div className="flex gap-3 items-center">
                                                {perfume.image_url ? (
                                                    <img src={perfume.image_url} alt={perfume.Name || perfume.name} className="w-11 h-11 object-contain rounded-lg border p-0.5 bg-slate-50 shrink-0" />
                                                ) : (
                                                    <div className="w-11 h-11 bg-slate-50 border rounded-lg flex items-center justify-center shrink-0"><SprayCan className="w-5 h-5 text-slate-300" strokeWidth={1.5} aria-hidden="true" /></div>
                                                )}
                                                <div className="truncate flex-1">
                                                    <div className="text-xs font-bold text-slate-700 leading-tight truncate">{perfume.Name || perfume.name}</div>
                                                    <div className="text-[10px] text-slate-400 truncate mt-0.5">{displayNotes}</div>
                                                </div>
                                                <Button
                                                    variant="outline"
                                                    className="text-[10px] font-bold border-slate-200 text-slate-600 hover:bg-slate-50 rounded-lg px-2.5 h-8 shrink-0"
                                                    onClick={() => handleSearch(perfume.Brand || perfume.brand || "", perfume.Name || perfume.name || "")}
                                                >
                                                    검색
                                                </Button>
                                            </div>

                                            {/* 2·3위 AI 설명 아코디언 */}
                                            {perfume.element_match_reason && (
                                                <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-[11px] text-slate-500">
                                                    <p className={`leading-relaxed break-keep ${isExpanded ? "" : "line-clamp-1"}`}>
                                                        {perfume.element_match_reason}
                                                    </p>
                                                    <button 
                                                        onClick={() => toggleExpand(idx)}
                                                        className="text-[10px] font-bold text-slate-400 hover:text-slate-600 mt-1 flex items-center gap-1 w-full text-left py-1"
                                                    >
                                                        {isExpanded ? (
                                                            <><ChevronUp className="w-3 h-3" strokeWidth={2} aria-hidden="true" /> 접기</>
                                                        ) : (
                                                            <><ChevronDown className="w-3 h-3" strokeWidth={2} aria-hidden="true" /> 매칭 사유 보기</>
                                                        )}
                                                    </button>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                );
                            }
                        })}
                    </div>
                </TabsContent>

                {/* ─── TAB 2: SAJU ANALYSIS ─── */}
                <TabsContent value="analysis" className="space-y-4 pt-4 outline-none">
                    <Card className="border shadow-sm border-slate-100 bg-white rounded-[2rem] overflow-hidden">
                        <div className="bg-slate-800 text-white font-bold p-4 flex items-center gap-2">
                            <Info className="w-5 h-5 text-slate-300" strokeWidth={2} aria-hidden="true" /> 나의 사주 상세 풀이
                        </div>
                        <CardContent className="p-5 space-y-6 text-sm text-slate-700 leading-[1.85]">

                            {saju_analysis?.overview && (
                                <section className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                                    <p className="font-semibold text-slate-800 leading-[1.8]">{saju_analysis.overview}</p>
                                </section>
                            )}

                            {saju_analysis?.advantages && (
                                <section>
                                    <h3 className="text-base font-extrabold text-slate-800 border-b-2 border-slate-100 pb-2 mb-3 flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 강점 — 내가 가진 힘</h3>
                                    <p>{saju_analysis.advantages}</p>
                                </section>
                            )}

                            {saju_analysis?.disadvantages && (
                                <section>
                                    <h3 className="text-base font-extrabold text-slate-800 border-b-2 border-slate-100 pb-2 mb-3 flex items-center gap-1.5"><AlertCircle className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 주의점 — 과할 때 조심</h3>
                                    <p>{saju_analysis.disadvantages}</p>
                                </section>
                            )}

                            {saju_analysis?.weakness_signals && (
                                <section>
                                    <h3 className="text-base font-extrabold text-slate-800 border-b-2 border-slate-100 pb-2 mb-3 flex items-center gap-1.5"><AlertCircle className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 기운 부족 신호</h3>
                                    <p>{saju_analysis.weakness_signals}</p>
                                </section>
                            )}

                            {/* 관심 운 집중 풀이 */}
                            {Array.isArray(luck_analysis) && luck_analysis.length > 0 && (
                                <section className="space-y-3">
                                    <h3 className="text-base font-extrabold text-slate-800 border-b-2 border-slate-100 pb-2 mb-1 text-center flex items-center justify-center gap-1.5"><Sparkles className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 선택한 운 상세 풀이</h3>
                                    {luck_analysis.map((luck: any, idx: number) => (
                                        <div key={idx} className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                                            <h4 className="font-extrabold text-slate-800 text-base mb-2">{luck.luck_name}</h4>
                                            <p className="text-slate-700 leading-[1.9] whitespace-pre-line font-medium">
                                                {luck.detail}
                                            </p>
                                        </div>
                                    ))}
                                </section>
                            )}

                            {!Array.isArray(luck_analysis) && interestsList.length > 0 && luck_analysis?.primary && (
                                <section className="space-y-3 mt-4">
                                    <h3 className="text-base font-extrabold text-slate-800 border-b-2 border-slate-100 pb-2 mb-1 text-center flex items-center justify-center gap-1.5"><Sparkles className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 선택한 운 상세 풀이</h3>
                                    {interestsList.map((interest: string, idx: number) => (
                                        <div key={idx} className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                                            <h4 className="font-extrabold text-slate-800 text-base mb-2">{interest}</h4>
                                            <p className="text-slate-700 leading-[1.9] font-medium">
                                                {idx === 0 ? luck_analysis.primary : (luck_analysis.secondary || "전체적인 운의 흐름이 점차 안정되고 있어요.")}
                                            </p>
                                        </div>
                                    ))}
                                </section>
                            )}

                            {luck_analysis?.secondary && interestsList.length <= 1 && (
                                <section className="mt-4">
                                    <h3 className="text-base font-extrabold text-slate-800 border-b-2 border-slate-100 pb-2 mb-3 flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-orange-500" strokeWidth={2} aria-hidden="true" /> 전체 운의 흐름</h3>
                                    <p>{luck_analysis.secondary}</p>
                                </section>
                            )}

                            {/* 향수 처방 효과 */}
                            {(saju_analysis?.balance_effect || saju_analysis?.perfume_effect) && (
                                <section className="bg-slate-100/50 rounded-2xl p-5 border border-slate-100 mt-4">
                                    <h3 className="text-base font-extrabold text-slate-900 mb-3 flex items-center gap-1.5"><SprayCan className="w-5 h-5 text-slate-600" strokeWidth={2} aria-hidden="true" /> 향수 처방 효과</h3>
                                    {saju_analysis.balance_effect && (
                                        <p className="text-slate-700 leading-[1.9] mb-3">{saju_analysis.balance_effect}</p>
                                    )}
                                    {saju_analysis.perfume_effect && (
                                        <p className="text-slate-600 leading-[1.9] font-medium">{saju_analysis.perfume_effect}</p>
                                    )}
                                </section>
                            )}

                        </CardContent>
                    </Card>
                </TabsContent>

                {/* ─── TAB 3: SHARE ─── */}
                <TabsContent value="share" className="pt-4 outline-none">
                    <div className="flex flex-col items-center gap-4">
                        <div ref={shareRef} className="w-full max-w-[360px]">
                            <div className="text-center space-y-4 bg-orange-50 p-6 rounded-[2rem] border border-orange-100 shadow-sm relative overflow-hidden">
                                <div className="text-sm font-bold text-slate-500 tracking-wide">나의 사주 향수 매칭</div>
                                <div className="flex justify-center items-center gap-4 mt-2">
                                    <div className="flex flex-col items-center">
                                        <span className="text-3xl bg-white border p-3 rounded-full shadow-sm mb-2 aspect-square flex items-center justify-center">{genderEmoji}</span>
                                        <span className="text-xs font-bold text-slate-700">{userInfo?.user_name}</span>
                                    </div>
                                    <span className="text-orange-500 font-extrabold text-xl">X</span>
                                    <div className="flex flex-col items-center max-w-[100px]">
                                        {bestPerfume.image_url ? (
                                            <img src={bestPerfume.image_url} alt={bestPerfume.name} crossOrigin="anonymous" className="w-14 h-14 object-contain bg-white border p-1 rounded-full shadow-sm mb-2" />
                                        ) : (
                                            <span className="bg-white border p-3 rounded-full shadow-sm mb-2 aspect-square flex items-center justify-center"><SprayCan className="w-7 h-7 text-slate-300" strokeWidth={1.5} aria-hidden="true" /></span>
                                        )}
                                        <div className="flex items-center gap-1 justify-center w-full">
                                            <img
                                                src={`https://www.google.com/s2/favicons?domain=${(bestPerfume.Brand || bestPerfume.brand || "").toLowerCase().replace(/\s+/g, '')}.com&sz=128`}
                                                onError={(e) => e.currentTarget.style.display = 'none'}
                                                className="w-3.5 h-3.5 rounded-full shadow-sm object-cover bg-white share-favicon"
                                                alt=""
                                            />
                                            <span className="text-[10px] font-bold text-slate-700 text-center leading-tight truncate">
                                                {bestPerfume.Brand || bestPerfume.brand}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-xl font-black text-orange-500 mt-2 leading-snug px-2">
                                    {hero_title}
                                </div>

                                <div className="grid grid-cols-2 gap-2 mt-4">
                                    <div className="bg-white/80 backdrop-blur-sm border border-slate-100 p-3 rounded-2xl flex flex-col items-center shadow-sm">
                                        <span className="text-[10px] font-bold text-slate-500 mb-1">내 강한 기운</span>
                                        <span className="mb-0.5 flex flex-wrap justify-center gap-0.5">{strongElements.map((e, i) => <span key={i}>{ELEMENT_EMOJI[e]}</span>)}</span>
                                        <span className="font-extrabold text-slate-800 text-xs text-center break-keep">{strongElementKo}</span>
                                    </div>
                                    <div className="bg-white/80 backdrop-blur-sm border border-slate-100 p-3 rounded-2xl flex flex-col items-center shadow-sm">
                                        <span className="text-[10px] font-bold text-slate-500 mb-1">내 부족한 기운</span>
                                        <span className="mb-0.5 flex flex-wrap justify-center gap-0.5">{weakElements.map((e, i) => <span key={i}>{ELEMENT_EMOJI[e]}</span>)}</span>
                                        <span className="font-extrabold text-slate-800 text-xs text-center break-keep">{weakElementKo}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <Button
                            onClick={() => setShowPhotoOverlay(true)}
                            className="w-full max-w-[360px] h-16 text-base font-extrabold rounded-2xl bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 text-white shadow-lg shadow-fuchsia-500/30 transition-all active:scale-95 mt-4 flex items-center justify-center gap-2"
                        >
                            <Share2 className="w-5 h-5 mr-1" strokeWidth={2} aria-hidden="true" /> 내 사진에 결과 입히기
                        </Button>
                        <Button
                            onClick={handleShareCapture}
                            variant="outline"
                            className="w-full max-w-[360px] h-12 text-sm font-bold rounded-2xl border-slate-200 text-slate-600 hover:bg-slate-50 mt-2 transition-colors"
                        >
                            결과화면 캡처만 하기
                        </Button>
                    </div>
                </TabsContent>
            </Tabs>

            <div className="pt-6 text-center pb-6 border-t mt-6 border-slate-100">
                <Button onClick={onReset} variant="outline" className="text-slate-500 font-bold hover:bg-slate-50 rounded-2xl px-8 h-12 border-slate-200 flex items-center gap-2 mx-auto">
                    <RefreshCw className="w-4 h-4" strokeWidth={2} aria-hidden="true" /> 처음부터 다시 검사하기
                </Button>
            </div>
        </div>
    );
}
