"use client";

import { useState, useEffect } from "react";
import InputForm from "@/components/InputForm";
import LoadingStep1 from "@/components/LoadingStep1";
import CompatibilityResult from "@/components/CompatibilityResult";
import RecommendationForm from "@/components/RecommendationForm";
import LoadingStep2 from "@/components/LoadingStep2";
import RecommendationResult from "@/components/RecommendationResult";
import DirectRecommendForm from "@/components/DirectRecommendForm";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function Home() {
  const [step, setStep] = useState<number>(0);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [step]);

  const [userInfo, setUserInfo] = useState<any>(null);
  const [compatData, setCompatData] = useState<any>(null);
  const [recommendData, setRecommendData] = useState<any>(null);
  const [apiError, setApiError] = useState<string>("");

  const handleInputSubmit = async (data: any) => {
    setApiError("");
    setUserInfo(data);
    setStep(2); // Loading 1

    try {
      const res = await fetch(`${API_BASE}/api/compatibility`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("API 연동 오류");
      const result = await res.json();
      setCompatData(result);
      setStep(3); // Result 1
    } catch (error) {
      console.error(error);
      setApiError("분석 중 일시적인 오류가 발생했습니다. 입력 정보를 확인하고 다시 시도해주세요.");
      setStep(1);
    }
  };

  const handleDirectRecommendSubmit = async (data: any) => {
    setApiError("");
    setUserInfo(data);
    setStep(5); // Loading 2 (바로 추천용 로딩)

    try {
      const res = await fetch(`${API_BASE}/api/recommend_direct`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) throw new Error("API 연동 오류");
      const result = await res.json();
      setRecommendData(result);
      setStep(6); // Result 2
    } catch (error) {
      console.error("Direct Recommend API Error:", error);
      setApiError("추천 중 일시적인 오류가 발생했습니다. 잠시 후 다시 버튼을 눌러주세요.");
      setStep(1);
    }
  };

  const handleRecommendSubmit = async (recommendRequestData: any) => {
    setApiError("");
    setUserInfo((prev: any) => ({
      ...prev,
      interests: recommendRequestData.interests || [],
      saju_data: compatData?.saju_data
    }));
    setStep(5); // Loading 2
    try {
      const payload = {
        user_name: userInfo.user_name,
        gender: userInfo.gender,
        saju_data: compatData.saju_data,
        ...recommendRequestData
      };

      const res = await fetch(`${API_BASE}/api/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("API 연동 오류");
      const result = await res.json();
      setRecommendData(result);
      setStep(6); // Result 2
    } catch (error) {
      console.error("Recommend API Error:", error);
      setApiError("결과를 가져오는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.");
      setStep(4);
    }
  };

  const resetAll = () => {
    setApiError("");
    setStep(0);
    setUserInfo(null);
    setCompatData(null);
    setRecommendData(null);
  };

  return (
    <main className="min-h-screen max-w-md mx-auto bg-white relative overflow-hidden flex flex-col items-center justify-start p-0 sm:border-x border-slate-100 shadow-2xl shadow-slate-200/50">
      <div className="w-full h-full min-h-screen flex flex-col">


        {step === 0 && (
          <div className="flex flex-col flex-1 h-screen relative bg-white text-slate-900 animate-in fade-in duration-1000">
            <div className="flex-1 flex flex-col items-center justify-center -mt-10">
              <h1 className="text-4xl sm:text-5xl font-black tracking-tighter mb-4 text-center text-slate-900">
                PERFUMANCE
              </h1>
              <p className="text-slate-400 text-sm text-center">
                사주로 보는 향수 케미
              </p>
            </div>

            <div className="absolute bottom-0 w-full p-6 pb-12">
              <button
                onClick={() => setStep(1)}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold text-lg py-4 rounded-2xl shadow-lg transition-transform active:scale-95 flex items-center justify-center gap-2"
              >
                향수와 케미 알아보기
              </button>
            </div>
          </div>
        )}

        <div className="w-full p-4 sm:p-6">
          {step === 1 && (
            <div className="w-full">
              <div className="flex border-b border-slate-200 mb-6 bg-slate-50/50 rounded-xl p-1">
                <button
                  onClick={() => setUserInfo({ ...userInfo, flow: 'compat' })}
                  className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all ${(!userInfo || userInfo.flow !== 'direct') ? 'bg-white shadow-sm text-orange-600' : 'text-slate-500 hover:text-slate-700'}`}
                >
                  향수와의 케미
                </button>
                <button
                  onClick={() => setUserInfo({ ...userInfo, flow: 'direct' })}
                  className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all ${(userInfo && userInfo.flow === 'direct') ? 'bg-white shadow-sm text-orange-600' : 'text-slate-500 hover:text-slate-700'}`}
                >
                  나에 맞는 향수 추천
                </button>
              </div>

              {(!userInfo || userInfo.flow !== 'direct') ? (
                <InputForm onSubmit={handleInputSubmit} userInfo={userInfo} apiError={apiError} />
              ) : (
                <DirectRecommendForm onSubmit={handleDirectRecommendSubmit} userInfo={userInfo} apiError={apiError} />
              )}
            </div>
          )}
          {step === 2 && <LoadingStep1 />}
          {step === 3 && (
            <CompatibilityResult
              data={compatData}
              userInfo={userInfo}
              onNext={() => { setApiError(""); setStep(4); }}
              onReset={resetAll}
            />
          )}
          {step === 4 && (
            <RecommendationForm
              userInfo={userInfo}
              onNext={handleRecommendSubmit}
              onReset={() => setStep(3)}
              apiError={apiError}
            />
          )}
          {step === 5 && <LoadingStep2 />}
          {step === 6 && (
            <RecommendationResult
              data={recommendData}
              userInfo={userInfo}
              onReset={resetAll}
            />
          )}
        </div>
      </div>
    </main>
  );
}
