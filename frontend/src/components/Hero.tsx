import React from 'react';
import { Sparkles, Award } from 'lucide-react';

interface HeroProps {
  onStart: (flow: 'direct' | 'compat') => void;
}

export default function Hero({ onStart }: HeroProps) {
  return (
    <div className="flex flex-col flex-1 h-full min-h-screen relative bg-white text-slate-900 overflow-y-auto">
      {/* 1. 상단 헤더 */}
      <header className="w-full flex items-center justify-between p-4 sm:p-6 pb-2">
        <h1 className="text-xl font-black tracking-tighter text-slate-900">
          PERFUMANCE
        </h1>
        <button
          onClick={() => onStart('compat')}
          className="text-sm font-bold text-slate-500 hover:text-slate-800 transition-colors py-2 px-3 rounded-md"
        >
          향수 궁합
        </button>
      </header>

      <div className="flex-1 flex flex-col px-6 pt-8 pb-32">
        {/* 2. 메인 카피 */}
        <div className="mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-5 leading-[1.3] text-slate-900">
            나의 기질과 취향을 담은<br />
            향수를 찾아보세요.
          </h2>
          <p className="text-slate-500 text-[15px] leading-relaxed max-w-[280px]">
            사주 오행과 실제 향 취향을 함께 분석해 나에게 어울리는 향수와 추천 이유를 알려드려요.
          </p>
        </div>

        {/* 3. 주요 CTA & 보조 CTA */}
        <div className="space-y-3 mb-10 w-full animate-in fade-in slide-in-from-bottom-6 duration-1000 delay-150 fill-mode-both">
          <button
            onClick={() => onStart('direct')}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold text-[17px] min-h-[52px] rounded-2xl shadow-lg shadow-orange-500/25 transition-transform active:scale-95 flex items-center justify-center gap-2"
          >
            내 향수 찾기
          </button>
          
          <button
            onClick={() => onStart('compat')}
            className="w-full bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 font-bold text-[15px] min-h-[52px] rounded-2xl transition-transform active:scale-95 flex items-center justify-center"
          >
            내가 고른 향수와 궁합 보기
          </button>
          
          {/* 5. 이용 안내 */}
          <p className="text-center text-xs text-slate-400 pt-2 font-medium">
            약 2분 · 회원가입 없이 이용
          </p>
        </div>

        {/* 6. 하단 결과 미리보기 */}
        <div className="mt-auto w-full animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300 fill-mode-both">
          <p className="text-xs text-slate-400 font-medium text-center mb-3 tracking-wide">
            결과 미리보기
          </p>
          <div className="w-full bg-slate-50 border border-slate-100 rounded-3xl p-5 shadow-sm relative overflow-hidden">
            <div className="absolute -right-4 -top-4 w-20 h-20 bg-orange-100/50 rounded-full blur-2xl"></div>
            
            <div className="relative z-10">
              <div className="flex items-center gap-1.5 mb-2">
                <Sparkles className="w-3.5 h-3.5 text-orange-400" />
                <span className="text-xs font-bold text-orange-500 tracking-wider">
                  당신의 향 성향
                </span>
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-1">
                차분한 나무의 온도
              </h3>
              <p className="text-sm text-slate-500 font-medium mb-4">
                Woody · Musk · Iris
              </p>
              
              <div className="flex items-center gap-2 bg-white px-3 py-2.5 rounded-xl border border-slate-100 shadow-sm">
                <div className="w-8 h-8 rounded-full bg-orange-50 flex items-center justify-center shrink-0">
                  <Award className="w-4 h-4 text-orange-500" />
                </div>
                <div>
                  <div className="text-[10px] font-bold text-slate-400">BEST MATCH</div>
                  <div className="text-xs font-bold text-slate-700">당신을 닮은 차분한 우디향</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
