import React from 'react';
import { Compass, Heart } from 'lucide-react';

export default function WhyPerfumanceSection() {
  return (
    <section className="w-full bg-slate-50 pt-20 pb-24 px-6 border-t border-slate-100 flex flex-col items-center">
      
      {/* 1. 문제 정의 영역 */}
      <div className="mb-16 w-full animate-in fade-in slide-in-from-bottom-8 duration-1000">
        <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-5 leading-[1.35] text-slate-900">
          향수를 고를 때,<br />
          인기만으로는 부족하니까.
        </h2>
        <p className="text-slate-500 text-[15px] leading-[1.7] max-w-[300px]">
          같은 향수도 누구에게는 편안하고,<br />
          누구에게는 무겁거나 낯설게 느껴질 수 있어요.<br />
          <br />
          Perfumance는 유행이나 성별 구분만 따르지 않고,<br />
          나의 기질과 실제 향 취향을 함께 살펴봅니다.
        </p>
      </div>

      {/* 2. 두 가지 분석 기준 */}
      <div className="w-full space-y-4 mb-14">
        {/* 기준 A */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-150 fill-mode-both">
          <div className="w-10 h-10 rounded-2xl bg-slate-50 flex items-center justify-center mb-4 text-slate-600">
            <Compass className="w-5 h-5" aria-hidden="true" />
          </div>
          <h3 className="text-lg font-bold text-slate-800 mb-2">기질을 살펴봐요</h3>
          <p className="text-sm text-slate-500 leading-relaxed">
            생년월일을 바탕으로 오행의 강약과 균형을 살펴봐요.
          </p>
        </div>

        {/* 기준 B */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300 fill-mode-both">
          <div className="w-10 h-10 rounded-2xl bg-orange-50 flex items-center justify-center mb-4 text-orange-500">
            <Heart className="w-5 h-5" aria-hidden="true" />
          </div>
          <h3 className="text-lg font-bold text-slate-800 mb-2">취향을 놓치지 않아요</h3>
          <p className="text-sm text-slate-500 leading-relaxed">
            좋아하는 향과 피하고 싶은 향을 함께 반영해요.
          </p>
        </div>
      </div>

      {/* 3. 분석 구조 시각화 */}
      <div className="w-full flex flex-col items-center mb-20 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500 fill-mode-both">
        <div className="flex items-center justify-center gap-3 w-full">
          <div className="bg-slate-800 text-white text-xs font-bold px-4 py-2.5 rounded-full shadow-md">
            사주 오행
          </div>
          <span className="text-slate-300 font-bold text-lg">+</span>
          <div className="bg-orange-500 text-white text-xs font-bold px-4 py-2.5 rounded-full shadow-md">
            실제 향 취향
          </div>
        </div>
        
        <div className="h-8 w-[2px] bg-gradient-to-b from-slate-200 to-slate-400 my-3"></div>
        
        <div className="bg-white border-2 border-slate-800 text-slate-800 text-sm font-black px-6 py-3 rounded-2xl shadow-sm">
          균형 잡힌 향수 추천
        </div>
      </div>

      {/* 4. 핵심 브랜드 문장 */}
      <div className="w-full text-center pb-8 animate-in fade-in duration-1000 delay-700 fill-mode-both">
        <p className="text-lg font-extrabold text-slate-800 leading-[1.4] tracking-tight">
          사주보다 취향을 무시하지 않고,<br />
          취향보다 새로운 가능성을 놓치지 않아요.
        </p>
      </div>

    </section>
  );
}
