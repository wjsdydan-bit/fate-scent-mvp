import React from 'react';
import { Sparkles, ListOrdered, MessageCircleHeart, Award } from 'lucide-react';

interface ResultsPreviewSectionProps {
  onStart: (flow: 'direct' | 'compat') => void;
}

export default function ResultsPreviewSection({ onStart }: ResultsPreviewSectionProps) {
  return (
    <section className="w-full bg-white pt-20 pb-24 px-6 border-t border-slate-100 flex flex-col items-center">
      
      {/* 1. 결과 프리뷰 헤더 */}
      <div className="mb-14 w-full animate-in fade-in slide-in-from-bottom-8 duration-1000">
        <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-4 leading-[1.35] text-slate-900">
          추천만 하지 않고,<br />
          왜 어울리는지도 알려드려요.
        </h2>
        <p className="text-slate-500 text-[15px] leading-[1.7] max-w-[300px]">
          나의 오행과 향 취향을 바탕으로<br />
          어울리는 향의 방향, 추천 향수, 추천 이유를<br />
          한 번에 확인할 수 있어요.
        </p>
      </div>

      {/* 2. 핵심 결과 3가지 */}
      <div className="w-full space-y-4 mb-14">
        {/* A */}
        <div className="flex gap-4 items-start animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-150 fill-mode-both">
          <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center shrink-0 mt-0.5">
            <Sparkles className="w-5 h-5 text-orange-500" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800 mb-1">나의 오행과 향 성향</h3>
            <p className="text-sm text-slate-500 leading-relaxed">
              강한 기운과 부족한 기운을 바탕으로<br />
              나에게 어울리는 향의 방향을 보여줘요.
            </p>
          </div>
        </div>

        {/* B */}
        <div className="flex gap-4 items-start animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300 fill-mode-both">
          <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center shrink-0 mt-0.5">
            <ListOrdered className="w-5 h-5 text-slate-600" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800 mb-1">추천 향수</h3>
            <p className="text-sm text-slate-500 leading-relaxed">
              사주와 실제 향 취향을 함께 반영해<br />
              어울리는 향수를 순위별로 추천해요.
            </p>
          </div>
        </div>

        {/* C */}
        <div className="flex gap-4 items-start animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500 fill-mode-both">
          <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center shrink-0 mt-0.5">
            <MessageCircleHeart className="w-5 h-5 text-slate-600" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800 mb-1">추천 이유와 향수 궁합</h3>
            <p className="text-sm text-slate-500 leading-relaxed">
              왜 어울리는지 쉽게 설명하고,<br />
              궁금한 향수와의 궁합도 확인할 수 있어요.
            </p>
          </div>
        </div>
      </div>

      {/* 3. 실제 결과 느낌의 대표 프리뷰 */}
      <div className="w-full mb-8 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-700 fill-mode-both">
        <div className="w-full bg-slate-50 border border-slate-100 rounded-3xl p-6 shadow-sm relative overflow-hidden">
          <div className="absolute -left-4 -bottom-4 w-24 h-24 bg-orange-100/40 rounded-full blur-2xl"></div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold text-slate-400 tracking-wide uppercase">
                결과 미리보기 (예시)
              </span>
            </div>
            
            <h4 className="text-2xl font-bold text-slate-800 mb-2">
              차분한 나무의 온도
            </h4>
            <p className="text-sm text-slate-500 font-medium mb-6">
              Woody · Musk · Iris
            </p>
            
            <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm mb-4">
              <div className="flex items-center gap-1.5 mb-2">
                <Award className="w-4 h-4 text-orange-500" aria-hidden="true" />
                <span className="text-[11px] font-bold text-orange-500 tracking-wider">
                  BEST MATCH
                </span>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed font-medium">
                차분한 기운을 보완하면서도<br />
                선호하는 포근한 향의 인상을 유지해요.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 4. 신뢰 및 안내 문구 */}
      <p className="text-xs text-slate-400 text-center mb-16 animate-in fade-in duration-1000 delay-1000 fill-mode-both">
        추천 결과는 향수 선택을 돕는 개인화 참고 정보입니다.
      </p>

      {/* 5. 최종 CTA 영역 */}
      <div className="w-full flex flex-col items-center pt-8 border-t border-slate-100 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-[1200ms] fill-mode-both">
        <h3 className="text-xl sm:text-2xl font-extrabold tracking-tight mb-8 text-slate-900 text-center leading-snug">
          아직 만나지 못한<br />
          나의 향을 찾아보세요.
        </h3>
        
        <div className="w-full space-y-3 mb-2">
          <button
            onClick={() => onStart('direct')}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold text-[17px] min-h-[52px] rounded-2xl shadow-lg shadow-orange-500/25 transition-transform active:scale-95 flex items-center justify-center gap-2"
          >
            나만의 향수 찾기
          </button>
          
          <button
            onClick={() => onStart('compat')}
            className="w-full bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 font-bold text-[15px] min-h-[52px] rounded-2xl transition-transform active:scale-95 flex items-center justify-center"
          >
            내가 고른 향수와 궁합 보기
          </button>
        </div>
        
        <p className="text-center text-xs text-slate-400 pt-2 font-medium">
          약 2분 · 회원가입 없이 이용
        </p>
      </div>

    </section>
  );
}
