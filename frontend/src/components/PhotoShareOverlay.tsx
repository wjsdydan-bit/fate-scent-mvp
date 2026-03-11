"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Rnd } from "react-rnd";

interface PhotoShareOverlayProps {
    userInfo: {
        user_name: string;
        gender: string;
    };
    perfumeDetails: {
        brand: string;
        name: string;
        image_url?: string;
        notes?: string | string[];
    };
    sajuData: {
        strongest: string;
        weakest: string;
    };
    additionalData: {
        type: "compatibility" | "recommendation";
        score?: number;
        scoreComment?: string;
        heroTitle?: string;
    };
    onClose: () => void;
}

const ELEMENTS_KO: Record<string, string> = {
    Wood: "목(나무)", Fire: "화(불)", Earth: "토(흙)", Metal: "금(쇠)", Water: "수(물)"
};
const ELEMENT_EMOJI: Record<string, string> = {
    Wood: "🌳", Fire: "🔥", Earth: "🏔️", Metal: "⚙️", Water: "💧"
};

const Sticker = ({
    defaultX, defaultY, baseWidth, baseHeight, angle, setAngle, children, id, startRotate
}: {
    defaultX: number, defaultY: number, baseWidth: number, baseHeight: number, angle: number, setAngle: any, children: React.ReactNode, id: string, startRotate: any
}) => {
    const [size, setSize] = useState({ width: baseWidth, height: baseHeight });
    const scale = size.width / baseWidth;
    const innerRef = useRef<HTMLDivElement>(null);

    return (
        <Rnd
            default={{ x: defaultX, y: defaultY, width: baseWidth, height: baseHeight }}
            size={{ width: size.width, height: size.height }}
            onResize={(e, direction, ref) => {
                setSize({
                    width: parseInt(ref.style.width, 10),
                    height: parseInt(ref.style.height, 10)
                });
            }}
            enableResizing={{ bottom: true, bottomRight: true, right: true, top: true, topRight: true, left: true, bottomLeft: true, topLeft: true }}
            className="z-50"
            lockAspectRatio={true}
            minWidth={baseWidth * 0.3}
        >
            <div
                ref={innerRef}
                className="sticker-container relative w-full h-full cursor-move drop-shadow-2xl"
                style={{ transform: `rotate(${angle}deg)` }}
                id={id}
            >
                <div
                    className="rotation-handle absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 bg-white/30 backdrop-blur-md border border-white/50 rounded-full flex items-center justify-center cursor-alias text-white shadow-lg pointer-events-auto z-[60] text-xl pb-1"
                    onMouseDown={(e) => startRotate(e, innerRef, setAngle)}
                    onTouchStart={(e) => startRotate(e, innerRef, setAngle)}
                >
                    ↻
                </div>
                <div
                    className="absolute top-0 left-0 flex flex-col items-center justify-center w-full h-full pointer-events-none"
                    style={{
                        transform: `scale(${scale})`,
                        transformOrigin: 'top left',
                        width: baseWidth,
                        height: baseHeight
                    }}
                >
                    {children}
                </div>
            </div>
        </Rnd>
    );
};

export default function PhotoShareOverlay({
    userInfo,
    perfumeDetails,
    sajuData,
    additionalData,
    onClose
}: PhotoShareOverlayProps) {
    const [bgImage, setBgImage] = useState<string | null>(null);
    const captureRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [theme, setTheme] = useState<"white" | "black">("white");
    const [angleTop, setAngleTop] = useState(0);
    const [angleSaju, setAngleSaju] = useState(0);
    const [angleBrand, setAngleBrand] = useState(0);
    const [angleName, setAngleName] = useState(0);
    const [angleHeart, setAngleHeart] = useState(0);
    const [angleRemark, setAngleRemark] = useState(0);

    const startRotate = (e: React.MouseEvent | React.TouchEvent, ref: React.RefObject<HTMLDivElement | null>, setAngle: React.Dispatch<React.SetStateAction<number>>) => {
        e.preventDefault();
        e.stopPropagation();
        if (!ref.current) return;

        const rect = ref.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        const handleMove = (moveEvent: MouseEvent | TouchEvent) => {
            const clientX = 'touches' in moveEvent ? moveEvent.touches[0].clientX : moveEvent.clientX;
            const clientY = 'touches' in moveEvent ? moveEvent.touches[0].clientY : moveEvent.clientY;
            const angleRad = Math.atan2(clientY - centerY, clientX - centerX);
            const angleDeg = (angleRad * 180) / Math.PI;
            setAngle(angleDeg + 90);
        };

        const handleUp = () => {
            document.removeEventListener('mousemove', handleMove);
            document.removeEventListener('mouseup', handleUp);
            document.removeEventListener('touchmove', handleMove);
            document.removeEventListener('touchend', handleUp);
        };

        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleUp);
        document.addEventListener('touchmove', handleMove);
        document.addEventListener('touchend', handleUp);
    };

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                if (typeof event.target?.result === 'string') {
                    setBgImage(event.target.result);
                }
            };
            reader.readAsDataURL(file);
        }
    };

    const handleCapture = async () => {
        if (!captureRef.current) return;
        try {
            const { toPng } = await import("html-to-image");

            // Hide rotation handles temporarily for capture
            const handles = document.querySelectorAll('.rotation-handle');
            handles.forEach((h: any) => h.style.display = 'none');

            // Force a small delay to ensure DOM updates are applied
            await new Promise(resolve => setTimeout(resolve, 50));

            const dataUrl = await toPng(captureRef.current, {
                pixelRatio: 2,
            });

            // Restore handles
            handles.forEach((h: any) => h.style.display = '');

            const link = document.createElement("a");
            const namePrefix = additionalData.type === "compatibility" ? "궁합" : "추천";
            const filename = `fatescent_${namePrefix}_${userInfo.user_name}.png`;

            link.download = filename;
            link.href = dataUrl;
            link.target = "_blank"; // Helpful for iOS Safari
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (err: any) {
            console.error(err);
            alert(`이미지 저장 중 오류가 발생했습니다: ${err?.message || err}`);
        }
    };


    const textColor = theme === 'white' ? "text-white" : "text-slate-900";
    const textShadow = theme === 'white'
        ? "drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)]"
        : "drop-shadow-[0_2px_2px_rgba(255,255,255,0.8)]";


    return (
        <div className="fixed inset-0 z-50 flex flex-col bg-slate-900/95 backdrop-blur-md items-center overflow-y-auto">
            <div className="w-full max-w-md p-4 flex justify-between items-center sticky top-0 z-10 bg-gradient-to-b from-slate-900/80 to-transparent pb-6">
                <h3 className="text-white font-bold pl-2 text-lg drop-shadow-md flex-1">포토카드</h3>
                <div className="flex items-center gap-3">
                    <div className="flex bg-black/40 rounded-full p-1 border border-white/20 backdrop-blur-md">
                        <button onClick={() => setTheme("white")} className={`px-3 py-1 text-xs rounded-full font-bold transition-all ${theme === 'white' ? 'bg-white text-black shadow-sm' : 'text-white/70 hover:text-white'}`}>White</button>
                        <button onClick={() => setTheme("black")} className={`px-3 py-1 text-xs rounded-full font-bold transition-all ${theme === 'black' ? 'bg-black text-white shadow-sm' : 'text-white/70 hover:text-white'}`}>Black</button>
                    </div>
                    <Button onClick={onClose} variant="ghost" className="text-white hover:bg-white/20 rounded-full w-10 h-10 p-0 shadow-lg backdrop-blur-sm shadow-black/20 shrink-0">
                        ✕
                    </Button>
                </div>
            </div>

            <div className="w-full max-w-[380px] px-4 flex-1 flex flex-col items-center">
                {!bgImage ? (
                    <div className="w-full aspect-[3/4] rounded-[2.5rem] bg-white/5 border-2 border-dashed border-white/20 flex flex-col items-center justify-center space-y-4 mb-6 shadow-2xl transition hover:bg-white/10 active:scale-95 cursor-pointer" onClick={() => fileInputRef.current?.click()}>
                        <div className="text-5xl drop-shadow-lg">📸</div>
                        <div className="text-white/60 font-bold text-center">
                            여기를 눌러<br />배경 사진을 선택해주세요
                        </div>
                        <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            ref={fileInputRef}
                            onChange={handleImageUpload}
                        />
                    </div>
                ) : (
                    <div className="relative w-full aspect-[3/4] mb-6 rounded-[2rem] overflow-hidden shadow-2xl ring-1 ring-white/20">
                        {/* Capture Target Area */}
                        <div ref={captureRef} className="w-full h-full relative flex flex-col bg-black">
                            {/* Background Image */}
                            <img src={bgImage} alt="Background" className="absolute inset-0 w-full h-full object-cover z-0" />
                            {/* Subtler gradient just for readability at the top and bottom */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30 z-0 pointer-events-none"></div>

                            {/* Minimal Watermark */}
                            <div className="absolute bottom-4 right-5 z-20 font-black tracking-tighter uppercase text-lg opacity-80 pointer-events-none text-white drop-shadow-md">
                                PERFUMANCE
                            </div>

                            {/* Draggable: Title / Score */}
                            <Sticker id="sticker-title" defaultX={40} defaultY={40} baseWidth={280} baseHeight={60} angle={angleTop} setAngle={setAngleTop} startRotate={startRotate}>
                                {additionalData.type === "recommendation" ? (
                                    <div className={`font-black text-[36px] tracking-tighter whitespace-nowrap ${textColor} ${textShadow}`}>
                                        👑 케미 1등 향수
                                    </div>
                                ) : (
                                    <div className={`flex items-baseline gap-1 ${textColor} ${textShadow}`}>
                                        <span className={`font-black text-[56px] tracking-tighter`}>
                                            {additionalData.score}
                                        </span>
                                        <span className={`opacity-90 font-bold text-[24px]`}>
                                            점
                                        </span>
                                    </div>
                                )}
                            </Sticker>

                            {/* Draggable: Saju Badge Support - Recommendation Only */}
                            {additionalData.type === "recommendation" && (
                                <Sticker id="sticker-saju" defaultX={40} defaultY={280} baseWidth={140} baseHeight={30} angle={angleSaju} setAngle={setAngleSaju} startRotate={startRotate}>
                                    <div className={`flex items-center justify-center gap-1.5 text-[14px] font-bold px-2 py-1 ${textColor} ${textShadow} w-full h-full`}>
                                        <span>{ELEMENT_EMOJI[sajuData.strongest]}</span>
                                        <span>{ELEMENTS_KO[sajuData.strongest].split('(')[0]} 기운 보충</span>
                                    </div>
                                </Sticker>
                            )}

                            {/* Draggable: Heart Emoji - Compatibility Only */}
                            {additionalData.type === "compatibility" && (
                                <Sticker id="sticker-heart" defaultX={300} defaultY={40} baseWidth={60} baseHeight={60} angle={angleHeart} setAngle={setAngleHeart} startRotate={startRotate}>
                                    <div className="text-[40px] drop-shadow-md cursor-grab">❤️</div>
                                </Sticker>
                            )}

                            {/* Draggable: Score Remark - Compatibility Only */}
                            {additionalData.type === "compatibility" && additionalData.scoreComment && (
                                <Sticker id="sticker-remark" defaultX={40} defaultY={100} baseWidth={200} baseHeight={40} angle={angleRemark} setAngle={setAngleRemark} startRotate={startRotate}>
                                    <div className={`font-bold text-[18px] px-3 py-1 rounded-full border border-current backdrop-blur-sm ${textColor} ${textShadow} whitespace-nowrap`}>
                                        {additionalData.scoreComment}
                                    </div>
                                </Sticker>
                            )}

                            {/* Draggable: Perfume Brand */}
                            {perfumeDetails.brand && (
                                <Sticker id="sticker-brand" defaultX={40} defaultY={320} baseWidth={160} baseHeight={30} angle={angleBrand} setAngle={setAngleBrand} startRotate={startRotate}>
                                    <div className={`flex items-center justify-center gap-1.5 px-2 py-1 w-full h-full ${textColor} ${textShadow}`}>
                                        <div className={`font-extrabold text-[16px] leading-tight`}>{perfumeDetails.brand}</div>
                                    </div>
                                </Sticker>
                            )}

                            {/* Draggable: Perfume Name */}
                            <Sticker id="sticker-name" defaultX={40} defaultY={360} baseWidth={260} baseHeight={80} angle={angleName} setAngle={setAngleName} startRotate={startRotate}>
                                <div className={`font-black text-[30px] leading-snug whitespace-normal break-keep text-center ${textColor} ${textShadow} w-full h-full flex items-center justify-center`}>
                                    {perfumeDetails.name}{additionalData.type === "compatibility" ? " 🧴" : ""}
                                </div>
                            </Sticker>

                            {/* End of Stickers */}
                        </div>

                        {/* Re-upload Button Overlay (outside capture context) */}
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="absolute top-4 right-4 bg-black/40 hover:bg-black/60 backdrop-blur-md text-white border border-white/20 px-3 py-1.5 rounded-full text-[11px] font-bold shadow-lg transition z-20"
                        >
                            사진 바꾸기
                        </button>
                        <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            ref={fileInputRef}
                            onChange={handleImageUpload}
                        />
                    </div>
                )}

                {bgImage && (
                    <div className="w-full space-y-3 pb-8">
                        <Button
                            onClick={handleCapture}
                            className="w-full h-14 text-base font-bold rounded-2xl bg-orange-500 hover:bg-orange-600 shadow-xl transition-all active:scale-95 text-white"
                        >
                            📸 완성된 사진 저장하기
                        </Button>
                        <Button
                            onClick={onClose}
                            variant="outline"
                            className="w-full h-14 text-base font-bold rounded-2xl border-white/20 bg-white/5 hover:bg-white/10 text-white backdrop-blur-sm transition-all"
                        >
                            돌아가기
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
