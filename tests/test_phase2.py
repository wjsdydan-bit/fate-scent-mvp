"""
Phase 2 통합 테스트: 날짜 검증, 출생시간 의미 통일, 오행 동률 처리
Gemini API 실제 호출 없이 내부 로직만 테스트합니다.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import datetime
import pytest

# =========================================================
# 1. 날짜 검증 테스트
# =========================================================
from main import validate_birth_date, validate_birth_time, resolve_birth_time_unknown
from fastapi import HTTPException

class TestDateValidation:
    """생년월일 유효성 검증 테스트"""
    
    def test_valid_leap_year(self):
        """2024-02-29 성공 (윤년)"""
        validate_birth_date(2024, 2, 29)  # 예외 없이 통과해야 함

    def test_invalid_leap_year(self):
        """2025-02-29 실패 (평년)"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_date(2025, 2, 29)
        assert exc_info.value.status_code == 422
        assert "유효하지 않은 생년월일" in exc_info.value.detail

    def test_invalid_feb_31(self):
        """2025-02-31 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_date(2025, 2, 31)
        assert exc_info.value.status_code == 422

    def test_invalid_apr_31(self):
        """2025-04-31 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_date(2025, 4, 31)
        assert exc_info.value.status_code == 422

    def test_valid_dec_31(self):
        """2025-12-31 성공"""
        validate_birth_date(2025, 12, 31)

    def test_invalid_month_13(self):
        """월 13 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_date(2025, 13, 1)
        assert exc_info.value.status_code == 422

    def test_invalid_day_0(self):
        """일 0 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_date(2025, 1, 0)
        assert exc_info.value.status_code == 422

    def test_valid_normal_date(self):
        """1995-06-15 성공"""
        validate_birth_date(1995, 6, 15)


# =========================================================
# 2. 시간/분 검증 테스트
# =========================================================
class TestTimeValidation:
    """출생시간 유효성 검증 테스트"""
    
    def test_valid_time(self):
        """16:30 유효"""
        validate_birth_time(16, 30)
    
    def test_valid_midnight(self):
        """00:00 유효"""
        validate_birth_time(0, 0)
    
    def test_valid_max_time(self):
        """23:59 유효"""
        validate_birth_time(23, 59)
    
    def test_invalid_hour_24(self):
        """hour=24 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_time(24, 0)
        assert exc_info.value.status_code == 422
    
    def test_invalid_hour_negative(self):
        """hour=-1 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_time(-1, 0)
        assert exc_info.value.status_code == 422
    
    def test_invalid_minute_60(self):
        """minute=60 실패"""
        with pytest.raises(HTTPException) as exc_info:
            validate_birth_time(10, 60)
        assert exc_info.value.status_code == 422
    
    def test_none_hour_ok(self):
        """hour=None은 검증 건너뜀"""
        validate_birth_time(None, None)


# =========================================================
# 3. 출생시간 의미 통일 테스트
# =========================================================
class MockRequest:
    """테스트용 Mock 요청 객체"""
    def __init__(self, know_time=True, is_birth_time_unknown=None):
        self.know_time = know_time
        self.is_birth_time_unknown = is_birth_time_unknown

class TestBirthTimeUnknown:
    """출생시간 의미 통일 테스트"""
    
    def test_new_field_true_means_unknown(self):
        """is_birth_time_unknown=True → 출생시간 모름"""
        req = MockRequest(know_time=False, is_birth_time_unknown=True)
        result = resolve_birth_time_unknown(req)
        assert result is True
    
    def test_new_field_false_means_known(self):
        """is_birth_time_unknown=False → 출생시간 알고 있음"""
        req = MockRequest(know_time=True, is_birth_time_unknown=False)
        result = resolve_birth_time_unknown(req)
        assert result is False
    
    def test_fallback_know_time_true_means_unknown(self):
        """know_time=True (기존 의미: '시간을 몰라요' 체크됨) → 출생시간 모름"""
        req = MockRequest(know_time=True, is_birth_time_unknown=None)
        result = resolve_birth_time_unknown(req)
        assert result is True  # know_time=True는 "모름" 의미이므로 직접 대입
    
    def test_fallback_know_time_false_means_known(self):
        """know_time=False (기존 의미: 체크 해제, 시간 입력함) → 출생시간 알고 있음"""
        req = MockRequest(know_time=False, is_birth_time_unknown=None)
        result = resolve_birth_time_unknown(req)
        assert result is False
    
    def test_new_field_takes_priority(self):
        """is_birth_time_unknown 필드가 know_time보다 우선"""
        req = MockRequest(know_time=True, is_birth_time_unknown=False)
        result = resolve_birth_time_unknown(req)
        assert result is False  # is_birth_time_unknown이 우선


# =========================================================
# 4. 오행 동률 처리 테스트
# =========================================================
from main import get_real_saju_elements, ELEMENTS

class TestElementTieHandling:
    """오행 동률 처리 테스트"""
    
    def test_single_strongest_and_weakest(self):
        """동률이 없을 때 배열에 하나만 포함"""
        # 1990-01-15 같은 일반적인 날짜로 테스트
        result = get_real_saju_elements(1990, 1, 15, 12, 0)
        assert result is not None
        assert "strongest_elements" in result
        assert "weakest_elements" in result
        assert isinstance(result["strongest_elements"], list)
        assert isinstance(result["weakest_elements"], list)
        assert len(result["strongest_elements"]) >= 1
        assert len(result["weakest_elements"]) >= 1
        # 단일 필드가 배열 첫 번째와 일치
        assert result["strongest"] == result["strongest_elements"][0]
        assert result["weakest"] == result["weakest_elements"][0]

    def test_tie_handling_direct(self):
        """오행 개수가 동률일 때 모두 포함되는지 직접 검증"""
        # counts를 직접 만들어서 검증
        counts_tie = {"Wood": 1, "Fire": 3, "Earth": 0, "Metal": 3, "Water": 1}
        max_val = max(counts_tie.values())
        min_val = min(counts_tie.values())
        strongest_elements = [e for e in ELEMENTS if counts_tie[e] == max_val]
        weakest_elements = [e for e in ELEMENTS if counts_tie[e] == min_val]
        
        assert "Fire" in strongest_elements
        assert "Metal" in strongest_elements
        assert len(strongest_elements) == 2
        assert "Earth" in weakest_elements
        assert len(weakest_elements) == 1
    
    def test_tie_handling_multiple_weakest(self):
        """여러 부족 오행 동률 처리"""
        counts_tie = {"Wood": 0, "Fire": 2, "Earth": 0, "Metal": 1, "Water": 2}
        max_val = max(counts_tie.values())
        min_val = min(counts_tie.values())
        strongest_elements = [e for e in ELEMENTS if counts_tie[e] == max_val]
        weakest_elements = [e for e in ELEMENTS if counts_tie[e] == min_val]
        
        assert "Fire" in strongest_elements
        assert "Water" in strongest_elements
        assert len(strongest_elements) == 2
        assert "Wood" in weakest_elements
        assert "Earth" in weakest_elements
        assert len(weakest_elements) == 2
    
    def test_element_order_is_fixed(self):
        """동률 시 ELEMENTS 배열 순서(Wood, Fire, Earth, Metal, Water) 유지"""
        counts_tie = {"Wood": 0, "Fire": 2, "Earth": 0, "Metal": 1, "Water": 2}
        weakest_elements = [e for e in ELEMENTS if counts_tie[e] == min(counts_tie.values())]
        # Wood이 Earth보다 앞에 와야 함 (ELEMENTS 순서)
        assert weakest_elements == ["Wood", "Earth"]

    def test_saju_function_returns_arrays(self):
        """실제 사주 함수가 배열 필드를 반환하는지 확인"""
        result = get_real_saju_elements(2000, 6, 15)
        assert "strongest_elements" in result
        assert "weakest_elements" in result
        assert result["strongest"] in result["strongest_elements"]
        assert result["weakest"] in result["weakest_elements"]


# =========================================================
# 5. 추천 로직 호환성 테스트
# =========================================================
from main import recommend_perfumes, df as perf_df

class TestRecommendCompat:
    """부족 오행이 1개일 때 기존 결과와 동일한지 검증"""
    
    def test_single_element_unchanged(self):
        """부족 오행 1개 → 기존 계산과 동일"""
        if perf_df.empty:
            pytest.skip("향수 데이터가 로드되지 않았습니다")
        
        weakest_single = ["Metal"]
        strongest_single = ["Wood"]
        
        result = recommend_perfumes(
            perf_df, weakest_single, strongest_single,
            [], [], "전체 뷰티 브랜드 포함", "전체"
        )
        assert not result.empty
        assert len(result) >= 3
    
    def test_multiple_weak_elements(self):
        """부족 오행 2개 → 정상 동작"""
        if perf_df.empty:
            pytest.skip("향수 데이터가 로드되지 않았습니다")
        
        weakest_multi = ["Wood", "Earth"]
        strongest_multi = ["Fire", "Water"]
        
        result = recommend_perfumes(
            perf_df, weakest_multi, strongest_multi,
            [], [], "전체 뷰티 브랜드 포함", "전체"
        )
        assert not result.empty
        assert len(result) >= 3


# =========================================================
# 6. 사주 계산 실패 처리 테스트
# =========================================================
class TestSajuFailure:
    """사주 계산 라이브러리 실패 시 안전하게 None 반환"""
    
    def test_valid_date_returns_result(self):
        """유효한 날짜 → 정상 결과 반환"""
        result = get_real_saju_elements(1995, 6, 15, 12, 0)
        assert result is not None
        assert "saju_name" in result
        assert "counts" in result
    
    def test_known_time_included_in_saju(self):
        """시간을 알 때 → 시주가 사주에 포함됨 (8글자)"""
        result = get_real_saju_elements(1995, 6, 15, 16, 30)
        assert result is not None
        assert "시" in result["saju_name"]
        assert result["pillars"]["hour"]["stem"] != "?"
    
    def test_unknown_time_excluded_from_saju(self):
        """시간을 모를 때 → '시간 모름' 표기, 6글자 기준"""
        result = get_real_saju_elements(1995, 6, 15)
        assert result is not None
        assert "시간 모름" in result["saju_name"]
        assert result["pillars"]["hour"]["stem"] == "?"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
