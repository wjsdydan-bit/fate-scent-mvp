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
      <header className="w-full flex items-center justify-between px-6 py-4 border-b border-slate-50 shrink-0">
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

      {/* 중앙 콘텐츠 영역 (Fade-in 효과 포함) */}
      <main className="flex-1 flex flex-col justify-center px-6 py-4 overflow-hidden">
        <div key={page} className="flex flex-col flex-1 justify-center animate-in fade-in duration-300 max-w-sm mx-auto w-full">
          
          {/* 1페이지: 만든 이유 */}
          {page === 0 && (
            <div className="flex flex-col h-full justify-between py-2">
              <div className="space-y-3">
                <h2
                  ref={titleRef}
                  tabIndex={-1}
                  className="text-[20px] sm:text-[22px] font-extrabold tracking-tight text-slate-900 leading-snug outline-none"
                >
                  향수는 직접 맡아보기 전까지<br />
                  나와 잘 맞을지 알기 어렵습니다.
                </h2>
                <p className="text-slate-500 text-[14px] leading-relaxed">
                  그래서 향 취향 외에<br />
                  참고할 기준을 하나 더 만들어봤습니다.
                </p>
              </div>

              {/* 정적 비주얼: 클릭 불가 */}
              <div 
                className="my-auto py-4 flex items-center justify-center pointer-events-none select-none"
                aria-hidden="true"
              >
                <div className="relative w-36 h-36 bg-slate-50 rounded-full border border-slate-100 flex items-center justify-center">
                  {/* 향수병 모양의 간단한 추상 벡터 */}
                  <svg className="w-16 h-24 text-slate-300" viewBox="0 0 100 150" fill="currentColor">
                    <rect x="35" y="10" width="30" height="15" rx="3" />
                    <rect x="45" y="25" width="10" height="15" />
                    <rect x="15" y="40" width="70" height="100" rx="15" />
                    <line x1="15" y1="75" x2="85" y2="75" stroke="white" strokeWidth="4" />
                  </svg>
                  {/* 향 노트 텍스트 배치 */}
                  <div className="absolute top-2 left-2 bg-white px-2 py-1 rounded-md text-[10px] text-slate-400 font-bold border border-slate-100">
                    Citrus
                  </div>
                  <div className="absolute bottom-6 right-2 bg-white px-2 py-1 rounded-md text-[10px] text-slate-400 font-bold border border-slate-100">
                    Woody
                  </div>
                  <div className="absolute top-1/2 -translate-y-1/2 right-0 bg-white px-2 py-1 rounded-md text-[10px] text-slate-400 font-bold border border-slate-100">
                    Musk
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2페이지: 작동 방식 */}
          {page === 1 && (
            <div className="flex flex-col h-full justify-between py-2">
              <div className="space-y-3">
                <h2
                  ref={titleRef}
                  tabIndex={-1}
                  className="text-[20px] sm:text-[22px] font-extrabold tracking-tight text-slate-900 leading-snug outline-none"
                >
                  사주와 향 취향을<br />
                  함께 반영합니다.
                </h2>
                <p className="text-slate-500 text-[14px] leading-relaxed">
                  오행의 균형을 살펴보고,<br />
                  좋아하는 향과 피하고 싶은 향을 입력받습니다.
                </p>
              </div>

              {/* 중앙 시각화: 클릭 불가 */}
              <div 
                className="my-auto py-4 flex flex-col items-center justify-center pointer-events-none select-none"
                aria-hidden="true"
              >
                <div className="flex items-center justify-between w-full max-w-[280px] bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                  <div className="flex flex-col items-center space-y-1">
                    <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600">
                      <Compass className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-extrabold text-slate-600">사주 오행</span>
                  </div>
                  <span className="text-slate-300 font-bold text-lg">+</span>
                  <div className="flex flex-col items-center space-y-1">
                    <div className="w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center text-orange-500">
                      <Heart className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-extrabold text-orange-500">향 취향</span>
                  </div>
                  <span className="text-slate-400 font-bold">→</span>
                  <div className="flex flex-col items-center space-y-1">
                    <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-white">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-extrabold text-slate-800">추천 매칭</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 font-medium mt-4">
                  사주만으로 향수를 정하지 않습니다.
                </p>
              </div>
            </div>
          )}

          {/* 3페이지: 받을 수 있는 결과 */}
          {page === 2 && (
            <div className="flex flex-col h-full justify-between py-2">
              <div className="space-y-3">
                <h2
                  ref={titleRef}
                  tabIndex={-1}
                  className="text-[20px] sm:text-[22px] font-extrabold tracking-tight text-slate-900 leading-snug outline-none"
                >
                  어울리는 향수와<br />
                  추천 이유를 보여드립니다.
                </h2>
                <p className="text-slate-500 text-[14px] leading-relaxed">
                  입력한 정보를 향수 데이터와 비교해<br />
                  추천 결과와 이유를 정리합니다.
                </p>
              </div>

              {/* 결과 항목 리스트: 클릭 불가 */}
              <div 
                className="my-auto py-3 space-y-2 pointer-events-none select-none"
                aria-hidden="true"
              >
                <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 space-y-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-5 h-5 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                      <Compass className="w-3 h-3 text-slate-600" />
                    </div>
                    <span className="text-xs font-bold text-slate-700">오행 분석</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <div className="w-5 h-5 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
                      <Heart className="w-3 h-3 text-orange-600" />
                    </div>
                    <span className="text-xs font-bold text-slate-700">취향을 반영한 향수 추천</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <div className="w-5 h-5 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                      <Sparkles className="w-3 h-3 text-slate-600" />
                    </div>
                    <span className="text-xs font-bold text-slate-700">추천 이유</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <div className="w-5 h-5 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                      <Award className="w-3 h-3 text-slate-600" />
                    </div>
                    <span className="text-xs font-bold text-slate-700">선택한 향수와의 궁합</span>
                  </div>
                </div>
              </div>

              {/* 최종 기능 진입 버튼: 조건부 렌더링 */}
              <div className="space-y-2.5 pt-2 shrink-0">
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
            </div>
          )}

        </div>
      </main>

      {/* 하단 내비게이션 바 */}
      <footer className="px-6 py-6 border-t border-slate-100 flex flex-col items-center space-y-4 shrink-0 pb-safe">
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
            <div className="w-16" /> /* 레이아웃 유지를 위한 빈 공간 */
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
            <div className="w-16" /> /* 레이아웃 유지를 위한 빈 공간 */
          )}
        </div>
      </footer>
    </div>
  );
}
