# Perfumance Phase 4-2 안전 데이터 정제 완료 보고서

본 보고서는 마스터 데이터베이스에서 안전하게 자동으로 클렌징할 수 있는 범위의 데이터 정제를 완수하고 변경 내역을 요약 기술한 보고서입니다.

## 1. 정제 핵심 지표

- **정제 전 행 수**: 4298개
- **정제 후 행 수**: 4292개
- **제거된 단순 중복 레코드**: 6개
- **브랜드 정합화 자동 수정 건수**: 360건
- **오염 데이터 수동 검토 대상 분리**: 57개

## 2. 제거된 주요 중복 사례 (안전 병합)

| 브랜드 | 향수명 | 분류 | 사유 |
|---|---|---|---|
| paco-rabanne | ultraviolet | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |
| giorgio-armani | armani-mania | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |
| giorgio-armani | acqua-di-gio | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |
| davidoff | cool-water | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |
| clinique | clinique-happy | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |
| antonio-banderas | blue-seduction | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |

## 3. 별도 독립 제품으로 안전하게 보존한 대표 사례

> [!TIP]
> 이름 뒤에 EDT/EDP, Intense 등이 붙었거나 향조 구성이 달라 함부로 병합하지 않고 개별 추천될 수 있도록 독립 유지한 제품들입니다.

| 브랜드 | 기본 정규화 이름 | 보존된 개별 원본 이름군 |
|---|---|---|
| Xerjoff | `uden` | uden, Uden Eau de Parfum |
| Xerjoff | `nio` | nio, Nio Eau de Parfum |
| versace | `eros` | eros-parfum, eros |
| tom-ford | `noirextreme` | noir-extreme-parfum, noir-extreme |
| tom-ford | `blackorchid` | black-orchid-parfum, black-orchid |
| roja-dove | `enigmapourhomme` | enigma-pour-homme-parfum-cologne, enigma-pour-homme |
| Penhaligons | `sartorial` | sartorial, Sartorial Eau de Toilette |
| Penhaligons | `halfeti` | halfeti, Halfeti Eau de Parfum |
| Penhaligons | `endymion` | endymion, Endymion Cologne |
| Penhaligons | `artemisia` | artemisia, Artemisia Eau de Parfum |

- **독립 보존된 다중 규격 제품군 그룹 수**: 10개 브랜드별 그룹
