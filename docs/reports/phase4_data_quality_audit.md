# Perfumance Phase 4-1 데이터 품질 진단 보고서

본 문서는 추천 알고리즘 정밀화를 위해 마스터 데이터베이스 내의 오차 요인을 상세 진단하고 분류한 감사 보고서입니다.

## 1. 품질 핵심 통계 요약

- **전체 향수 수**: 4298개
- **향조 데이터 결측 (Notes/Top/Middle/Base가 모두 빈 것)**: 79개 (전체 대비 1.84%)
- **성별 Unknown (알 수 없음) 향수**: 2217개 (전체 대비 51.58%)
- **정규화 후 이름이 중복되는 그룹**: 78개
  - *오병합 위험이 높은 제품 (EDT/EDP, Intense 등)*: 69개
  - *단순 중복/병합 안전 제품*: 9개
- **브랜드 표기 불일치 종류**: 17건
- **한글 포함 향조 데이터 수**: 59개

## 2. 오병합 위험도가 높은 중복 사례 (Intense, Absolu, Elixir, EDT/EDP 등)

> [!IMPORTANT]
> 아래 향수들은 정규화 시 이름이 같아져 중복 필터링될 위험이 있으나, 실제로는 완전히 다른 제품군(농도, 한정판, 리뉴얼 등)으로 향조와 용도가 다른 경우입니다.

| 브랜드 | 정규화 이름 | 원본 이름들 | 향조 차이 개수 | 주요 상이 향조 | 분류 |
|---|---|---|---|---|---|
| Aesop | `hwyl` | Hwyl, Hwyl Eau de Parfum | 12 | thyme cypress, thyme, smoky, woody notes vetiver, frankincense | **수동 검토 (병합 금지)** |
| Aesop | `rozu` | Rozu, Rozu Eau de Parfum | 18 | green, guaiac, vetiver, bitter orange rose, ylang ylang sandalowood | **수동 검토 (병합 금지)** |
| Aesop | `tacit` | Tacit, Tacit Eau de Parfum | 9 | citrus notes, green, herbal, clove, citruses basil vetiver | **수동 검토 (병합 금지)** |
| armaf | `clubdenuitintenseman` | club-de-nuit-intense-man-parfum, club-de-nuit-intense-man | 0 | 없음 | **수동 검토 (병합 금지)** |
| armand-basi | `inred` | in-red-edp, in-red | 14 | vanilla, cardamom jasmine, rose woody notes, palisander rosewood, oakmoss | **수동 검토 (병합 금지)** |
| azzaro | `themostwanted` | the-most-wanted-parfum, the-most-wanted | 8 | ginger, cardamom toffee amberwood, ginger woodsy notes bourbon vanilla, toffee, cardamom | **수동 검토 (병합 금지)** |
| burberry | `thebeat` | the-beat-edt, the-beat | 6 | bellflower white musk, bellflower musk, white musk, bergamot tea, musk | **수동 검토 (병합 금지)** |
| Byredo | `bal dafrique` | Bal d'Afrique, Bal d'Afrique Eau de Parfum | 20 | neroli, tagetes, black amber, african orange flower violet, jasmine vetiver | **수동 검토 (병합 금지)** |
| byredo | `bibliotheque` | bibliotheque, Bibliotheque Eau de Parfum | 2 | peach violet, peony leather | **수동 검토 (병합 금지)** |
| Byredo | `blanche` | Blanche, Blanche Eau de Parfum | 14 | african orange flower musk, woodsy notes, neroli, african orange flower, rose | **수동 검토 (병합 금지)** |
| Byredo | `eleventh hour` | Eleventh Hour, Eleventh Hour Eau de Parfum | 19 | plum, cashmere wood, carrot seeds cedar, carrot seed, cashmere woods | **수동 검토 (병합 금지)** |
| Byredo | `gypsy water` | Gypsy Water, Gypsy Water Eau de Parfum | 10 | pine, pepper pine needles, juniper berries, orris, powdery | **수동 검토 (병합 금지)** |
| byredo | `inflorescence` | inflorescence, Inflorescence Eau de Parfum | 6 | rose, rose petals, magnolia jasmine, fresh jasmine, jasmine | **수동 검토 (병합 금지)** |
| Byredo | `la tulipe` | La Tulipe, La Tulipe Eau de Parfum | 15 | green, rhubarb, rhuburb pink tulip green notes, pink tulip, vetiver | **수동 검토 (병합 금지)** |
| Byredo | `mojave ghost` | Mojave Ghost, Mojave Ghost Eau de Parfum | 10 | ambrette musk mallow, ambrette musk mallow magnolia, clean, floral, ambrette | **수동 검토 (병합 금지)** |

## 3. 단순 중복 및 안전 병합 대상 사례

| 브랜드 | 정규화 이름 | 원본 이름들 | 향조 차이 개수 | 분류 |
|---|---|---|---|---|
| antonio-banderas | `blueseduction` | blue-seduction, blue-seduction | 24 | **자동 병합/삭제 가능** |
| clinique | `cliniquehappy` | clinique-happy, clinique-happy | 24 | **자동 병합/삭제 가능** |
| davidoff | `coolwater` | cool-water, cool-water | 34 | **자동 병합/삭제 가능** |
| Diptyque | `eau des sens` | Eau des Sens Eau de Toilette, Eau des Sens | 13 | **자동 병합/삭제 가능** |
| Diptyque | `eau rose` | Eau Rose, Eau Rose Eau de Toilette | 16 | **자동 병합/삭제 가능** |
| Diptyque | `oyedo` | Oyedo Eau de Toilette, Oyedo | 16 | **자동 병합/삭제 가능** |
| giorgio-armani | `armanimania` | armani-mania, armani-mania | 21 | **자동 병합/삭제 가능** |
| paco-rabanne | `ultraviolet` | ultraviolet, ultraviolet | 20 | **자동 병합/삭제 가능** |
| penhaligon-s | `sartorial` | sartorial, Sartorial Eau de Toilette | 20 | **자동 병합/삭제 가능** |

## 4. 동일 브랜드 내 이름이 유사한 실제 별도 제품

| 브랜드 | 기본 제품명 | 유사 하위 제품명 | 분류 |
|---|---|---|---|
| Aesop | Tacit | Tacit Eau de Parfum | **유지 (독립 제품)** |
| By Kilian | Love Eau de Parfum | Rolling in Love Eau de Parfum | **유지 (독립 제품)** |
| Comme des Garcons | 3 Eau de Toilette | Odeur 53 Eau de Toilette | **유지 (독립 제품)** |
| Creed | Aventus | Aventus Eau de Parfum | **유지 (독립 제품)** |
| Creed | Aventus | Aventus For Her Eau de Parfum | **유지 (독립 제품)** |
| Creed | Aventus | Aventus Cologne Eau de Parfum | **유지 (독립 제품)** |
| Creed | Green Irish Tweed | Green Irish Tweed Eau de Parfum ... | **유지 (독립 제품)** |
| Creed | Millesime Imperial | Millesime Imperial Eau de Parfum ... | **유지 (독립 제품)** |
| Creed | Silver Mountain Water | Silver Mountain Water Eau de Parfum ... | **유지 (독립 제품)** |
| Dior | Sauvage | Sauvage Eau de Toilette | **유지 (독립 제품)** |
| Diptyque | Oyedo | Oyedo Eau de Toilette | **유지 (독립 제품)** |
| Diptyque | Do Son | Do Son - Eau de Parfum | **유지 (독립 제품)** |
| Diptyque | Do Son | Do Son - Eau de Toilette | **유지 (독립 제품)** |
| Diptyque | Tam Dao | Tam Dao - Eau de Parfum | **유지 (독립 제품)** |
| Diptyque | Tam Dao | Tam Dao - Eau de Toilette | **유지 (독립 제품)** |

## 5. 브랜드명 표기 불일치 리스트

| 정규화 브랜드명 | 데이터 상의 실제 브랜드 표기 종류 | 분류 |
|---|---|---|
| `houbigant` | houbigant, Houbigant | **자동 수정 가능 (정합화)** |
| `penhaligons` | Penhaligons, penhaligon-s | **자동 수정 가능 (정합화)** |
| `frapin` | frapin, Frapin | **자동 수정 가능 (정합화)** |
| `amouage` | amouage, Amouage | **자동 수정 가능 (정합화)** |
| `nishane` | nishane, Nishane | **자동 수정 가능 (정합화)** |
| `chanel` | chanel, Chanel | **자동 수정 가능 (정합화)** |
| `nasomatto` | nasomatto, Nasomatto | **자동 수정 가능 (정합화)** |
| `mancera` | mancera, Mancera | **자동 수정 가능 (정합화)** |
| `diptyque` | Diptyque, diptyque | **자동 수정 가능 (정합화)** |
| `dior` | dior, Dior | **자동 수정 가능 (정합화)** |
| `montale` | Montale, montale | **자동 수정 가능 (정합화)** |
| `clean` | Clean, clean | **자동 수정 가능 (정합화)** |
| `xerjoff` | xerjoff, Xerjoff | **자동 수정 가능 (정합화)** |
| `byredo` | Byredo, byredo, BYREDO | **자동 수정 가능 (정합화)** |
| `creed` | Creed, creed | **자동 수정 가능 (정합화)** |

## 6. 향조 데이터 누락 (Notes 결측) 주요 사례

| 브랜드 | 향수명 | 분류 |
|---|---|---|
| Comme des Garcons | Concrete Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Comme des Garcons: Olfactory Library | Eau de Cologne Eau de Toilette | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Filippo Sorcinelli - SAUF | Unda Maris 8 Extrait de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Filippo Sorcinelli - SAUF | Violon Basse 16 Extrait de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Mad et Len | Red Musc Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Mad et Len | Vetyver Bucolique Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Mad et Len | Fuego Flores Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Mad et Len | Black Afghan Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Floris London | Bergamotto di Positano Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |
| Tauerville | Fruitchouli Eau de Parfum | **수동 보완 필요 (Gemini 오프라인 정제)** |

## 7. TAG_TO_KEYWORDS 미사용 키워드 리스트

| 태그 종류 | 미사용 키워드 리스트 | 분류 |
|---|---|---|
| 포근한(머스크) | soft musk | **유지 또는 대체** |

## 8. 한글 향조 포함 주요 사례 (매칭 공백 발생)

| 브랜드 | 향수명 | 한글 포함 향조 데이터 | 분류 |
|---|---|---|---|
| Anthologie de Grands Crus | Vanille d'Amine Eau de Parfum | ` Madagascan vanilla ol챕or챕sin, Somalian Olibanum, Madagascan Clove bud oil` | **수동 번역/정제 필요** |
| Les Indemodables | Oriental Velours Eau de Parfum | ` Indian jasmine alcoolat 밎rand Cru뵝 5%, Madagascan vanilla 밎rand Cru뵝 2.5%, Somalian myrrh 15%, Haitian vetiver밎rand Cru뵝 10%, Alpine spruce oil` | **수동 번역/정제 필요** |
| Les Indemodables | Cuir de Chine Eau de Parfum | ` Chinese osmanthus absolute 1%, Chinese osmanthus밶lcoolat뵝 Grand Cru 10%, Turkish뱓abac blond뵝 absolute .2%, Alpine clary sage` | **수동 번역/정제 필요** |
| TOM FORD Signature | Ombre Leather Eau de Parfum | ` Violet leaf, cardamom, jasmine sambac, black leather, white moss, patchouli Click Here For Ingredients 횞Close Ombre Leather by TOM FORD Signature Ingredients Please be aware that ingredient lists may change or vary from time to time.  Please refer to the ingredient list on the product package you receive for the most up to date list of ingredients.` | **수동 번역/정제 필요** |
| Roja Parfums | Qatar Extrait de parfum | ` Citrus notes, rose de mai, jasmine from Grasse, violet, pear, peach, clove, saffron, patchouli, cedarwood, casmir wood, sandalwood, oud, candyfloss accord, benzoin, vanilla, orris sur c챔dre, orris, styrax, birch, labdanum, ambergris, musk` | **수동 번역/정제 필요** |
| Perris Monte Carlo | Rose de Taif Eau de Parfum | ` Lemon, nutmeg, geranium, Ta챦f rose essential oil, rose Damas absolute, rose musk` | **수동 번역/정제 필요** |
| MEMO | Kedu Eau de Parfum | ` Grapefruit, neroli, mandarin, mat챕 absolute, freesia, rose, peony, sesame absolute, white musk, moss.` | **수동 번역/정제 필요** |
| MEMO | Irish Leather Eau de Parfum | ` Pink pepper, clary sage, juniper berry, green mat챕 absolute, flouve, iris concrete, tonka bean absolute, leather, birch, amber accord.` | **수동 번역/정제 필요** |
| MEMO | Granada Eau de Parfum | ` Oil of bergamot, pomegranate, orange blossom, jasmine sambac, h챕liotrope, musk, amber wood accord.` | **수동 번역/정제 필요** |
| Stephane Humbert Lucas 777 | Une Nuit a Doha Eau de Parfum | ` Fennel, crystallized mandarin, ginger, immortelle flower from Corsica, vetiver from Ha챦ti, brown tobacco, absolute of vanilla.` | **수동 번역/정제 필요** |
