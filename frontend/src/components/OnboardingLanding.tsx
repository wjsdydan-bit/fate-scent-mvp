import React, { useState, useRef, useEffect } from 'react';
import { Compass, Heart, Sparkles, Award, ArrowRight, ArrowLeft } from 'lucide-react';

interface OnboardingLandingProps {
  onStart: (flow: 'direct' | 'compat') => void;
}

export default function OnboardingLanding({ onStart }: OnboardingLandingProps) {
  const [page, setPage] = useState<number>(0);
  const titleRef = useRef<HTMLHeadingElement>(null);

  // 페이지 전환 시 제목으로 포커스 이동하여 스크린 리더가 바로 읽을 수 있도록 함
  useEffect(() => {
    if (titleRef.current) {
      titleRef.current.focus();
    }
  }, [page]);

  const handleNext = () => {
    if (page < 2) setPage(page + 1);
  };

  const handlePrev = () => {
    if (page > 0) setPage(page - 1);
  };

  return (
    <div className="flex flex-col flex-1 h-screen max-h-screen justify-between bg-white text-slate-900 overflow-hidden select-none">
      {/* 상단 헤더 */}
      <header className="w-full flex items-center justify-between px-6 py-4 border-b border-slate-50 shrink-0 h-14">
        <span className="text-lg font-black tracking-tighter text-slate-900">
          PERFUMANCE
        </span>
        {page < 2 && (
          <button
            onClick={() => onStart('direct')}
            className="text-xs font-semibold text-slate-400 hover:text-slate-600 transition-colors py-1.5 px-3 focus-visible:ring-2 focus-visible:ring-orange-500 outline-none rounded-md"
            aria-label="소개 건너뛰고 향수 추천 시작하기"
          >
            건너뛰기
          </button>
        )}
      </header>

      {/* 중앙 콘텐츠 영역 (세 페이지 제목 및 비주얼 가로축/세로 리듬 일관성 적용) */}
      <main className="flex-1 flex flex-col px-6 py-4 justify-start overflow-hidden w-full max-w-[440px] mx-auto">
        <div key={page} className="flex flex-col flex-1 animate-in fade-in duration-300 w-full">
          
          {/* 3개 페이지 공통 타이틀 & 설명 영역 (세로 리듬 통일) */}
          <div className="pt-2 pb-4 space-y-2 shrink-0 min-h-[110px] flex flex-col justify-start">
            <h2
              ref={titleRef}
              tabIndex={-1}
              className="text-[20px] sm:text-[22px] font-extrabold tracking-tight text-slate-900 leading-snug outline-none"
            >
              {page === 0 && (
                <>향수를 고를 때마다<br />뭘 기준으로 봐야 할지 애매했습니다.</>
              )}
              {page === 1 && (
                <>그래서 사주와 향 취향을<br />같이 보기로 했습니다.</>
              )}
              {page === 2 && (
                <>추천 결과만 보여주지 않고<br />왜 잘 맞는지도 설명합니다.</>
              )}
            </h2>
            <p className="text-slate-500 text-[13.5px] leading-relaxed">
              {page === 0 && (
                <>유명한 향인지, 내 취향인지,<br />정작 나와 잘 맞는지는 알기 어려웠습니다.</>
              )}
              {page === 1 && (
                <>오행의 균형을 참고하고,<br />좋아하는 향과 싫어하는 향도 함께 반영합니다.</>
              )}
              {page === 2 && (
                <>오행 분석, 향수 추천, 추천 이유와<br />선택한 향수와의 궁합을 확인할 수 있습니다.</>
              )}
            </p>
          </div>

          {/* 중앙 비주얼 영역 (중앙 정렬 및 적당한 밀도 유지) */}
          <div className="flex-1 flex flex-col justify-center items-center overflow-hidden py-2">
            
            {/* 1페이지 비주얼: 약 30% 확대, 대비 상향 조정 */}
            {page === 0 && (
              <div className="w-full flex items-center justify-center pointer-events-none select-none" aria-hidden="true">
                <div className="relative w-48 h-48 bg-slate-100 rounded-full border-2 border-slate-200 flex items-center justify-center shadow-inner">
                  {/* 향수병 모양 대비 강화 */}
                  <svg className="w-20 h-28 text-slate-400" viewBox="0 0 100 150" fill="currentColor">
                    <rect x="35" y="10" width="30" height="15" rx="3" />
                    <rect x="45" y="25" width="10" height="15" />
                    <rect x="15" y="40" width="70" height="100" rx="15" />
                    <line x1="15" y1="75" x2="85" y2="75" stroke="white" strokeWidth="4" />
                  </svg>
                  {/* 라벨 크기 및 위치 밸런스 조정 */}
                  <div className="absolute top-4 left-4 bg-slate-900 text-white px-2.5 py-1 rounded-md text-[11px] font-bold shadow-sm">
                    Citrus
                  </div>
                  <div className="absolute bottom-8 right-4 bg-slate-900 text-white px-2.5 py-1 rounded-md text-[11px] font-bold shadow-sm">
                    Woody
                  </div>
                  <div className="absolute top-1/2 -translate-y-1/2 right-2 bg-slate-900 text-white px-2.5 py-1 rounded-md text-[11px] font-bold shadow-sm">
                    Musk
                  </div>
                </div>
              </div>
            )}

            {/* 2페이지 비주얼: 폭 확대, 문구 변경 */}
            {page === 1 && (
              <div className="w-full flex flex-col items-center justify-center pointer-events-none select-none" aria-hidden="true">
                <div className="flex items-center justify-between w-full max-w-[320px] bg-slate-50 border-2 border-slate-100 p-5 rounded-3xl shadow-sm">
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-12 h-12 rounded-full bg-slate-200 flex items-center justify-center text-slate-700">
                      <Compass className="w-6 h-6" />
                    </div>
                    <span className="text-[12px] font-extrabold text-slate-700">사주 오행</span>
                  </div>
                  <span className="text-slate-400 font-bold text-xl">+</span>
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-12 h-12 rounded-full bg-orange-50 flex items-center justify-center text-orange-500">
                      <Heart className="w-6 h-6" />
                    </div>
                    <span className="text-[12px] font-extrabold text-orange-500">향 취향</span>
                  </div>
                  <span className="text-slate-400 font-bold text-xl">→</span>
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center text-white">
                      <Sparkles className="w-6 h-6" />
                    </div>
                    <span className="text-[12px] font-extrabold text-slate-200">추천 결과</span>
                  </div>
                </div>
                <p className="text-[12px] text-slate-400 font-semibold mt-5">
                  사주만으로 향수를 정하지 않습니다.
                </p>
              </div>
            )}

            {/* 3페이지 비주얼: 정적 리스트 박스 소폭 마진 조정 */}
            {page === 2 && (
              <div className="w-full py-1 space-y-2 pointer-events-none select-none" aria-hidden="true">
                <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 space-y-2.5">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                      <Compass className="w-3.5 h-3.5 text-slate-700" />
                    </div>
                    <span className="text-xs font-bold text-slate-800">오행 분석</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
                      <Heart className="w-3.5 h-3.5 text-orange-600" />
                    </div>
                    <span className="text-xs font-bold text-slate-800">취향을 반영한 향수 추천</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                      <Sparkles className="w-3.5 h-3.5 text-slate-700" />
                    </div>
                    <span className="text-xs font-bold text-slate-800">추천 이유</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                      <Award className="w-3.5 h-3.5 text-slate-700" />
                    </div>
                    <span className="text-xs font-bold text-slate-800">선택한 향수와의 궁합</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 3페이지 하단 기능 진입 버튼 */}
          {page === 2 && (
            <div className="space-y-2 pt-3 shrink-0 pb-1">
              <button
                onClick={() => onStart('direct')}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold text-[15px] py-3.5 rounded-xl shadow-md transition-transform active:scale-[0.98] flex items-center justify-center gap-2 focus-visible:ring-2 focus-visible:ring-orange-500 outline-none"
              >
                향수 추천 시작하기
              </button>
              <button
                onClick={() => onStart('compat')}
                className="w-full bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 font-bold text-[14px] py-3.5 rounded-xl transition-transform active:scale-[0.98] flex items-center justify-center focus-visible:ring-2 focus-visible:ring-slate-300 outline-none"
              >
                향수 궁합 확인하기
              </button>
            </div>
          )}

        </div>
      </main>

      {/* 하단 내비게이션 바 */}
      <footer className="px-6 py-6 border-t border-slate-100 flex flex-col items-center space-y-4 shrink-0 pb-safe h-28 justify-center">
        {/* 진행 상태 인디케이터 */}
        <div 
          className="flex items-center justify-center space-x-2"
          role="img"
          aria-label={`소개 ${page + 1}/3`}
        >
          {[0, 1, 2].map((idx) => (
            <div
              key={idx}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                page === idx ? 'bg-orange-500 w-4' : 'bg-slate-200'
              }`}
            />
          ))}
        </div>

        {/* 이전/다음 네비게이션 버튼 (일관된 레이아웃 유지) */}
        <div className="flex items-center justify-between w-full max-w-sm">
          {page > 0 ? (
            <button
              onClick={handlePrev}
              className="flex items-center gap-1.5 text-sm font-bold text-slate-500 hover:text-slate-700 transition-colors py-2 px-3 focus-visible:ring-2 focus-visible:ring-slate-300 outline-none rounded-md"
              aria-label="이전 페이지로 이동"
            >
              <ArrowLeft className="w-4 h-4" /> 이전
            </button>
          ) : (
            <div className="w-16" />
          )}

          {page < 2 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-1.5 text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 transition-colors py-2 px-4 rounded-lg focus-visible:ring-2 focus-visible:ring-slate-500 outline-none"
              aria-label="다음 페이지로 이동"
            >
              다음 <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <div className="w-16" />
          )}
        </div>
      </footer>
    </div>
  );
}
