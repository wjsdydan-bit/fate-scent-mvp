/**
 * 날짜 관련 공통 유틸리티 함수
 * InputForm.tsx와 DirectRecommendForm.tsx에서 공유 사용
 */

/**
 * 주어진 연도와 월에 해당하는 마지막 날짜를 반환합니다.
 * 윤년을 정확히 처리합니다.
 * @param year 연도 (예: 2024)
 * @param month 월 (1~12)
 * @returns 해당 월의 마지막 날짜 (28, 29, 30, 31)
 */
export function getDaysInMonth(year: number, month: number): number {
    // new Date(year, month, 0)은 해당 월의 마지막 날을 반환
    // month는 1-based이므로 그대로 사용 (JS Date의 month는 0-based이므로 month를 넘기면 다음달의 0일 = 이번달 마지막일)
    return new Date(year, month, 0).getDate();
}

/**
 * 연도나 월이 변경되었을 때, 현재 선택된 day가 유효 범위를 넘으면
 * 해당 월의 마지막 날짜로 자동 조정합니다.
 * @param currentDay 현재 선택된 일
 * @param year 연도
 * @param month 월 (1~12)
 * @returns 유효한 일 (조정된 경우 마지막 날, 아니면 원래 값)
 */
export function clampDay(currentDay: number, year: number, month: number): number {
    const maxDay = getDaysInMonth(year, month);
    if (currentDay > maxDay) {
        return maxDay;
    }
    if (currentDay < 1) {
        return 1;
    }
    return currentDay;
}
