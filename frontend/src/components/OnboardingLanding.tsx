import React, { useState, useRef, useEffect } from 'react';
import { Compass, Heart, Sparkles, Award, ArrowRight, ArrowLeft, ArrowDown } from 'lucide-react';

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
      <header className="w-full flex items-center justify-between px-6 py-4 border-b border-slate-50 shrink-0 h-14 z-10 bg-white">
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

      {/* 중앙 콘텐츠 영역 */}
      <main className="flex-1 flex flex-col px-6 py-4 justify-start overflow-hidden w-full max-w-[540px] mx-auto relative">
        <div key={page} className="flex flex-col flex-1 animate-in fade-in duration-300 w-full z-10">
          
          {/* 공통 타이틀 & 설명 영역 (세로 리듬 통일) */}
          <div className="pt-2 pb-4 space-y-2 shrink-0 min-h-[120px] flex flex-col justify-start">
            <h2
              ref={titleRef}
              tabIndex={-1}
              className="text-[21px] sm:text-[23px] font-extrabold tracking-tight text-slate-900 leading-snug outline-none"
            >
              {page === 0 && (
                <>매일 보는 운세가<br />상품 추천으로 이어질 수 있을까?</>
              )}
              {page === 1 && (
                <>사주만으로<br />향수를 고르지는 않습니다.</>
              )}
              {page === 2 && (
                <>추천 향수와<br />그 이유를 함께 보여드립니다.</>
              )}
            </h2>
            <p className="text-slate-500 text-[14px] leading-relaxed">
              {page === 0 && (
                <>익숙한 사주를 활용해<br />향수를 추천하는 서비스를 만들어봤습니다.</>
              )}
              {page === 1 && (
                <>오행의 균형과 실제 향 취향을 함께 반영해<br />향수 데이터에서 어울리는 후보를 찾습니다.</>
              )}
              {page === 2 && (
                <>오행 분석과 향수 추천, 추천 이유,<br />궁금한 향수와의 궁합을 확인할 수 있습니다.</>
              )}
            </p>
          </div>

          {/* 중앙 대표 비주얼 영역 (중앙 정렬 및 비율 안정 배분) */}
          <div className="flex-1 flex flex-col justify-center items-center overflow-hidden py-4 relative">
            
            {/* 1페이지 대표 비주얼: 오늘의 기운 카드 -> 향수 추천 연결 대형 일러스트 */}
            {page === 0 && (
              <div className="w-full flex items-center justify-center pointer-events-none select-none relative" aria-hidden="true">
                {/* 비주얼 배경 옅은 살구/아이보리색 그라데이션 원 */}
                <div className="absolute w-56 h-56 rounded-full bg-gradient-to-tr from-orange-50/50 to-amber-50/60 blur-xl"></div>
                
                <div className="relative flex items-center justify-center gap-6 w-full max-w-[340px]">
                  {/* 운세 카드 */}
                  <div className="w-24 h-36 bg-white border border-slate-200/80 rounded-2xl shadow-md p-3 flex flex-col justify-between items-center shrink-0">
                    <span className="text-[10px] font-extrabold text-slate-400 tracking-wider">FORTUNE</span>
                    <div className="w-10 h-10 rounded-full bg-amber-50 flex items-center justify-center text-amber-500 my-2">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-black text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
                      오늘의 기운
                    </span>
                  </div>

                  {/* 연결선/화살표 */}
                  <div className="flex flex-col items-center justify-center">
                    <div className="flex items-center text-orange-400 animate-pulse">
                      <span className="text-lg font-bold">→</span>
                    </div>
                  </div>

                  {/* 향수병 일러스트 */}
                  <div className="w-24 h-36 bg-slate-900 text-white rounded-2xl shadow-lg p-3 flex flex-col justify-between items-center shrink-0 relative overflow-hidden">
                    <div className="absolute -right-4 -bottom-4 w-12 h-12 bg-orange-500/20 rounded-full blur-xl"></div>
                    <span className="text-[9px] font-extrabold text-slate-500 tracking-wider">SCENT</span>
                    
                    <svg className="w-8 h-12 text-slate-300 my-1" viewBox="0 0 100 150" fill="currentColor">
                      <rect x="35" y="10" width="30" height="15" rx="3" />
                      <rect x="45" y="25" width="10" height="15" />
                      <rect x="15" y="40" width="70" height="100" rx="15" />
                    </svg>

                    <span className="text-[10px] font-extrabold text-orange-400 tracking-tighter">
                      Woody · Citrus
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* 2페이지 대표 비주얼: 대형 분석 다이어그램 */}
            {page === 1 && (
              <div className="w-full flex flex-col items-center justify-center pointer-events-none select-none relative" aria-hidden="true">
                {/* 2페이지 배경 추상 면 (위치가 다른 베이지 원형) */}
                <div className="absolute w-60 h-60 rounded-full bg-slate-100/70 blur-xl -top-6 -left-6"></div>
                
                <div className="relative flex flex-col items-center justify-center w-full max-w-[340px] bg-white border border-slate-200/80 p-6 rounded-3xl shadow-sm">
                  {/* 상단 두 입력 요소 */}
                  <div className="flex items-center justify-between w-full mb-4">
                    <div className="flex flex-col items-center p-3 bg-slate-50 rounded-2xl w-[100px] border border-slate-100">
                      <Compass className="w-6 h-6 text-slate-600 mb-1" />
                      <span className="text-[11px] font-extrabold text-slate-700">오행의 균형</span>
                    </div>
                    
                    <span className="text-slate-400 font-bold text-lg">+</span>
                    
                    <div className="flex flex-col items-center p-3 bg-orange-50/50 rounded-2xl w-[100px] border border-orange-100/50">
                      <Heart className="w-6 h-6 text-orange-500 mb-1" />
                      <span className="text-[11px] font-extrabold text-slate-700">향 취향</span>
                    </div>
                  </div>

                  {/* 아래 방향 연결 */}
                  <ArrowDown className="w-4 h-4 text-slate-300 mb-3" />

                  {/* 향수 데이터 비교 영역 */}
                  <div className="w-full bg-slate-900 text-white p-3 rounded-2xl flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4 text-orange-400 animate-pulse" />
                    <span className="text-[12px] font-black tracking-wide">향수 데이터 비교</span>
                  </div>
                </div>

                <p className="text-[11.5px] text-slate-400 font-bold mt-4">
                  사주와 취향을 함께 봅니다.
                </p>
              </div>
            )}

            {/* 3페이지 대표 비주얼: 실제 결과 화면 축약 패널 */}
            {page === 2 && (
              <div className="w-full flex items-center justify-center pointer-events-none select-none relative py-1" aria-hidden="true">
                <div className="w-full max-w-[320px] bg-slate-50 border border-slate-200/80 rounded-3xl p-5 shadow-sm space-y-4">
                  {/* 결과 예시 패널 내부 */}
                  <div className="flex justify-between items-center border-b border-slate-200/50 pb-2">
                    <span className="text-[10px] font-extrabold text-slate-400">결과 예시</span>
                    <span className="text-[10px] font-extrabold text-orange-500 bg-orange-50 px-2 py-0.5 rounded-full">BEST</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="p-2.5 bg-white rounded-xl border border-slate-100">
                      <span className="text-slate-400 block mb-0.5">오행 분석</span>
                      <strong className="text-slate-800 font-extrabold">목(木) 기운 보완</strong>
                    </div>
                    <div className="p-2.5 bg-white rounded-xl border border-slate-100">
                      <span className="text-slate-400 block mb-0.5">향수 추천</span>
                      <strong className="text-slate-800 font-extrabold">차분한 우디 향수</strong>
                    </div>
                  </div>

                  <div className="p-2.5 bg-white rounded-xl border border-slate-100 text-[11px]">
                    <span className="text-slate-400 block mb-0.5">추천 이유</span>
                    <p className="text-slate-700 font-medium leading-relaxed">
                      "부족한 목의 기운을 보완하며 안정감을 줍니다."
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-[11px] bg-white p-2.5 rounded-xl border border-slate-100">
                    <span className="text-slate-400">향수 궁합</span>
                    <strong className="text-slate-800 font-extrabold">좋은 궁합 (85점)</strong>
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
      <footer className="px-6 py-6 border-t border-slate-100 flex flex-col items-center space-y-4 shrink-0 pb-safe h-28 justify-center z-10 bg-white">
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
