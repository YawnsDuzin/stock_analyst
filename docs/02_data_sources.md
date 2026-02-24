# 02. 차별화된 데이터 소스 전략

> **이 문서의 목적**: 시스템이 활용하는 9가지 차별화된 데이터 소스를 상세히 설명하고, 각 소스의 활용법, API 접근 방법, 코드 예시를 제공합니다.

---

## 목차

- [2.1 정부 공공 데이터](#21-정부-공공-데이터)
- [2.2 채용공고 역발상 분석](#22-채용공고-역발상-분석)
- [2.3 해외 공개 데이터의 국내 역이용](#23-해외-공개-데이터의-국내-역이용)
- [2.4 텍스트 마이닝 기반 언어 변화 감지](#24-텍스트-마이닝-기반-언어-변화-감지)
- [2.5 크로스 에셋 / 비전통 선행지표](#25-크로스-에셋--비전통-선행지표)
- [2.6 소셜/커뮤니티 감성 역발상 전략](#26-소셜커뮤니티-감성-역발상-전략)
- [2.7 규제/정책 변화 조기 포착](#27-규제정책-변화-조기-포착)
- [2.8 공급망 역추적 분석](#28-공급망-역추적-분석)
- [2.9 이상 거래 패턴 감지](#29-이상-거래-패턴-감지)
- [데이터 소스 요약 매트릭스](#데이터-소스-요약-매트릭스)

---

## 2.1 정부 공공 데이터 (가장 강력한 공개 정보)

정부 공공 데이터는 무료이면서도 가장 강력한 선행 지표를 제공합니다. 대부분 API를 통해 자동화된 수집이 가능합니다.

---

### 2.1.1 나라장터 (조달청) 낙찰 데이터 ⭐⭐⭐

대형 계약 낙찰이 IR 공시보다 평균 **2~4주 먼저** 나라장터에 공개됩니다. 이는 가장 강력한 선행 신호 중 하나입니다.

#### 핵심 정보

- **수혜 섹터**: IT 서비스, 방산, 의료기기, 환경, 에너지
- **분석 포인트**: 계약금액 / 시가총액 비율이 **10% 초과** 시 중요 이벤트
- **API**: 공공데이터포털 `나라장터 낙찰결과정보` (무료)
- **선행성**: IR 공시 대비 2~4주

#### API 호출 예시

```python
import requests
from datetime import datetime, timedelta

def get_procurement_data(company_name: str, days_back: int = 30) -> dict:
    """
    나라장터에서 특정 기업의 최근 낙찰 데이터를 조회합니다.

    Args:
        company_name: 검색할 기업명
        days_back: 조회 기간 (일)

    Returns:
        낙찰 결과 리스트
    """
    url = "https://apis.data.go.kr/1230000/ScsbidInfoService/getOpengResultListInfoServcPPSSrch"

    date_to = datetime.now().strftime("%Y%m%d")
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

    params = {
        "ServiceKey": "YOUR_API_KEY",  # 공공데이터포털에서 발급
        "numOfRows": 100,
        "pageNo": 1,
        "inqryDiv": 1,
        "type": "json",
        "bidNtceNm": company_name,
        "inqryBgnDt": date_from,
        "inqryEndDt": date_to
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

#### 분석 전략

1. **계약금액 임계값**: 시가총액 대비 10% 이상 계약은 "매우 강한 신호"
2. **반복 낙찰 패턴**: 동일 기관에서 반복 수주 = 안정적 매출 기반
3. **신규 분야 진출**: 기존과 다른 분야 낙찰 = 사업 확장 신호
4. **계약 규모 추이**: 분기별 낙찰 규모 증가 추세 = 실적 모멘텀

---

### 2.1.2 건강보험심사평가원 (HIRA) 의약품 청구 데이터 ⭐⭐⭐

분기별로 의약품 청구 실적이 공개되어 제약/바이오 기업의 실제 처방 트렌드를 재무제표보다 먼저 확인할 수 있습니다.

#### 활용 시나리오

| 시나리오 | 분석 방법 | 투자 시그널 |
|---------|----------|-----------|
| 신약 출시 후 처방 확산 | 청구 건수 추이 추적 | 확산 속도 > 예상 → Buy |
| 특정 성분 시장 점유율 | 성분별 청구 비율 변화 | 점유율 급증 기업 → Buy |
| 제네릭 진입 영향 | 오리지널 청구 감소율 | 급감 시 오리지널 기업 → Sell |

#### 데이터 접근 방법

```python
# HIRA 공개 데이터 활용 구조
class HIRADataCollector:
    BASE_URL = "https://opendata.hira.or.kr/op/opc/olapDiagBhvInfo.do"

    def get_prescription_trend(self, drug_name: str, period: str) -> dict:
        """특정 약물의 처방 트렌드를 조회합니다."""
        # API 또는 데이터 다운로드 방식으로 접근
        pass

    def compare_market_share(self, ingredient: str) -> dict:
        """특정 성분의 제조사별 시장 점유율을 비교합니다."""
        pass
```

---

### 2.1.3 특허청 KIPRIS 출원 데이터 ⭐⭐

특허 출원은 공개까지 18개월이 걸리지만, **출원 건수 급증 자체**가 R&D 집중 신호입니다.

#### 핵심 기술 키워드 필터링

| 기술 영역 | 키워드 | 관련 섹터 |
|----------|--------|----------|
| 비만치료제 | GLP-1, 세마글루타이드 | 바이오/제약 |
| 차세대 배터리 | 전고체, 리튬메탈 | 2차전지 |
| 태양전지 | 페로브스카이트, 탠덤 | 에너지 |
| AI 반도체 | HBM, PIM, NPU | 반도체 |

#### 분석 포인트

1. **섹터 내 기술력 격차**: 경쟁사 대비 출원 속도 비교
2. **신규 진출 영역**: 기존 사업과 다른 분야 출원 = 사업 다각화 신호
3. **해외 출원**: PCT 국제 출원은 글로벌 사업 의지의 지표
4. **공동 출원**: 대학/연구소와 공동 출원 = R&D 파이프라인 강화

---

### 2.1.4 금융감독원 DART 전자공시 ⭐⭐⭐

DART는 가장 기본적이면서도, 깊이 있게 분석하면 강력한 선행 지표를 제공합니다.

#### 핵심 공시 유형

| 공시 유형 | 분석 포인트 | 선행성 |
|----------|-----------|--------|
| **대량보유 보고 (5% 룰)** | 기관/외인 지분 변동 조기 감지 | 1~2주 |
| **임원 주식 매매 보고** | 내부자 거래 패턴 분석 | 수일 |
| **정정 공시** | 정정 횟수가 많은 기업 = 리스크 신호 | 즉시 |
| **사업보고서 YoY 비교** | 언어/톤 변화 감지 | 1~2분기 |

#### DART API 활용

```python
import dart_fss

# DART API 키 설정
dart_fss.set_api_key("YOUR_DART_API_KEY")

def get_major_shareholder_changes(corp_code: str) -> list:
    """대량보유 보고 변동 내역을 조회합니다."""
    reports = dart_fss.api.filings.get_corp_code(corp_code)
    # 5% 보고서 필터링 및 변동 추이 분석
    return reports

def get_insider_trading(corp_code: str) -> list:
    """임원 주식 매매 내역을 조회합니다."""
    # 임원 매수/매도 패턴 분석
    pass
```

---

## 2.2 채용공고 역발상 분석 ⭐⭐⭐

월가 헤지펀드들이 실제로 사용하는 방법이지만, 국내에서 체계적으로 하는 곳이 거의 없습니다.

### 2.2.1 신규 채용 포지션으로 사업방향 예측

| 채용 패턴 | 해석 | 관련 섹터 |
|-----------|------|-----------|
| AI/ML 엔지니어 급증 | AI 사업 피벗 준비 | AI 인프라, SaaS |
| 해외영업팀 채용 | 수출 확대 전략 | 수출주 전반 |
| 임상 CRA 채용 급증 | 파이프라인 가속 | 바이오 |
| 물류/SCM 담당자 | 공급망 확대 | 물류, 유통 |
| 보안/컴플라이언스 | 규제 대응 준비 | 핀테크, 플랫폼 |

### 2.2.2 퇴사/위기 신호 탐지 (역발상)

- **Blind, 잡플래닛 리뷰 점수 급락**: 내부 문제 선행 신호
- **임원급 LinkedIn 프로필 회사 변경**: 경영진 이탈 감지
- **핵심 기술인력의 경쟁사 이직 패턴**: 기술 경쟁력 약화 신호

### 2.2.3 채용 동결 = 실적 악화 선행

채용공고가 갑자기 사라지는 시점은 실적 하향 조정보다 평균 **1~2분기 빠릅니다**.

#### 코드 구조

```python
class HiringSignalTracker:
    """채용공고 변화에서 투자 신호를 추출하는 트래커"""

    def track(self, company_list: list[str]) -> list[dict]:
        """기업 목록의 채용 변화를 추적합니다."""
        results = []

        for company in company_list:
            current_jobs = self.crawl_job_postings(company)
            prev_jobs = self.db.get_last_week(company)

            delta = len(current_jobs) - len(prev_jobs)
            new_categories = self.extract_new_categories(current_jobs, prev_jobs)

            results.append({
                "company": company,
                "volume_change": delta,          # 채용 증감
                "new_directions": new_categories, # 새 사업방향
                "signal_strength": self.score(delta, new_categories)
            })

        return results

    def crawl_job_postings(self, company: str) -> list[dict]:
        """채용 사이트에서 현재 공고를 크롤링합니다."""
        # 사람인, 잡코리아, 원티드, 링크드인 등
        pass

    def extract_new_categories(self, current: list, previous: list) -> list[str]:
        """새로 등장한 직무 카테고리를 추출합니다."""
        current_cats = set(job["category"] for job in current)
        prev_cats = set(job["category"] for job in previous)
        return list(current_cats - prev_cats)

    def score(self, delta: int, new_categories: list) -> float:
        """채용 변화의 투자 신호 강도를 0~100으로 산출합니다."""
        volume_score = min(abs(delta) * 5, 50)  # 변화량 기반
        category_score = min(len(new_categories) * 15, 50)  # 새 방향 기반
        return volume_score + category_score
```

---

## 2.3 해외 공개 데이터의 국내 역이용 ⭐⭐⭐

한국 투자자들이 국내 데이터만 보는 동안, 해외에서 공개되는 한국 연관 데이터를 먼저 활용합니다.

### 2.3.1 미국 FDA / EMA 임상 데이터베이스

| 데이터 소스 | 활용 | URL |
|------------|------|-----|
| ClinicalTrials.gov | 국내 바이오 해외 임상 현황 | clinicaltrials.gov |
| FDA CDER | 신약 승인 심사 현황 | fda.gov/drugs |
| EMA 유럽의약품청 | 유럽 시장 진출 현황 | ema.europa.eu |

#### 분석 시나리오

1. **임상 3상 완료 → 승인 신청**: 국내 공시보다 먼저 파악
2. **임상 중단/철회 등록**: 주가 급락 전 포지션 정리 가능
3. **경쟁 약물 임상 결과**: 경쟁 구도 변화 조기 감지

### 2.3.2 미국 SEC EDGAR

- **반도체 고객사 분석**: NVIDIA, TSMC, Micron의 10-K/10-Q에서 재고/수요 전망 확인
- **한국 기업 미국 자회사**: 개별 공시에서 현지 사업 실적 추적
- **밸류체인 선행지표**: 해외 대형 고객의 CAPEX 변화 → 국내 장비/소재주 영향

```python
# SEC EDGAR API 예시
def get_sec_filing(company: str, filing_type: str = "10-K") -> dict:
    """SEC EDGAR에서 특정 기업의 공시를 조회합니다."""
    url = f"https://efts.sec.gov/LATEST/search-index?q={company}&dateRange=custom&startdt=2024-01-01&forms={filing_type}"
    headers = {"User-Agent": "StockAnalyst research@example.com"}
    response = requests.get(url, headers=headers)
    return response.json()
```

### 2.3.3 중국 해관총서 수출입 데이터

- 한-중 교역 데이터 매월 공개
- **중국의 한국산 특정 소재 수입 급증** → 화학/소재주 선행 신호
- **중국 내 특정 제품 수요 변화** → 국내 연관 기업 영향 예측

### 2.3.4 일본 기업 결산 발표

- 일본 소재/장비 기업 실적 → 국내 고객사(삼성, SK) 투자 사이클 예측
- **핵심 모니터링 기업**: 도쿄 일렉트론, 신에츠화학, SUMCO, 히타치
- 가이던스 변화에 주목 → 국내 장비 서브 벤더 주가 연동 패턴 분석

---

## 2.4 텍스트 마이닝 기반 언어 변화 감지 ⭐⭐⭐

**핵심 통찰**: 숫자보다 말이 먼저 바뀝니다. CEO와 IR 담당자의 언어 패턴 변화를 추적합니다.

### 2.4.1 실적 발표 컨퍼런스콜 NLP 분석

#### 감성 신호 키워드 사전

```python
# 긍정 신호 키워드
POSITIVE_SIGNALS = [
    "가시성이 높아지고", "수주 파이프라인이 견조", "초과 달성",
    "기대 이상", "상향 조정", "신규 계약 체결", "시장 점유율 확대",
    "사상 최대", "흑자 전환", "성장 가속화"
]

# 부정 신호 키워드
NEGATIVE_SIGNALS = [
    "불확실성을 모니터링", "보수적으로 접근", "일회성 비용",
    "시장 환경이 어렵", "수요 둔화", "재고 조정", "가이던스 하향",
    "구조조정", "비용 절감 노력", "점진적 회복 기대"
]

# 회피 신호 (가장 중요한 경고 신호)
EVASION_SIGNALS = [
    # 특정 사업부 언급 횟수 급감
    # 구체적 수치 대신 "노력하겠습니다"
    # 질문 회피 패턴
    # "자세한 것은 추후 공개"
]
```

### 2.4.2 애널리스트 리포트 컨센서스 이탈 감지

모두 "Buy"인데 목표주가를 조금씩 낮추는 패턴은 사실상 부정적 전망의 소프트한 표현입니다. 이런 **언어적 위장**을 NLP로 탐지합니다.

### 2.4.3 DART 사업보고서 YoY 문구 변화 비교

```python
def compare_annual_reports(company_id: str, year: int) -> dict:
    """전년도 vs 올해 사업보고서의 문구 변화를 분석합니다."""
    current = get_dart_report(company_id, year)
    previous = get_dart_report(company_id, year - 1)

    changes = {
        "risk_factors_added": find_new_risks(current, previous),
        "strengths_removed": find_removed_strengths(current, previous),
        "tone_shift": measure_sentiment_delta(current, previous),
        "keyword_frequency_change": compare_keywords(current, previous)
    }
    return changes
```

---

## 2.5 크로스 에셋 / 비전통 선행지표 ⭐⭐

### 2.5.1 위성 이미지 데이터 분석

| 데이터 | 활용 | 관련 종목 |
|--------|------|----------|
| 주차장 차량 수 | 유통 매장 매출 추정 | 이마트, 롯데쇼핑 |
| 항만 컨테이너 적재량 | 수출 선행지표 | 수출주 전반 |
| 공장 굴뚝 연기/조명 | 제조업 가동률 추정 | 제조업 |

- **데이터 소스**: Planet.com, Google Earth Engine (무료/저가 티어)

### 2.5.2 선박 AIS 추적 데이터

- **MarineTraffic** 무료 API로 특정 항구 입출항 추적
- 철광석/석탄 벌크선 동향 → 포스코 원가 선행
- LNG 탱커 움직임 → 가스 기업 마진 예측
- 한국 수출 항구(부산, 인천) 선박 밀도 변화

### 2.5.3 전력/에너지 소비 데이터

- 한국전력 통계월보에서 산업용 전력 소비 추적
- 가스공사 공개 데이터로 제조업 가동률 선행 파악
- 특정 지역 전력 수요 급증 → 신규 공장/데이터센터 착공 신호

### 2.5.4 구글 트렌드 + 네이버 데이터랩

- 소비재/플랫폼 기업은 검색량이 실적의 **1~2개월 선행지표**
- 경쟁사 대비 검색점유율 변화로 시장 점유율 이동 조기 감지
- **중요**: 계절성 조정 후 YoY 변화율에 집중

---

## 2.6 소셜/커뮤니티 감성 역발상 전략 ⭐⭐

일반적 감성분석과 반대로 **과도한 낙관/비관 구간**을 역이용합니다.

### 극단치 탐지 알고리즘

```python
class SentimentExtremeDetector:
    """커뮤니티 감성의 극단치를 감지하여 역발상 신호를 생성합니다."""

    BULLISH_THRESHOLD = 0.92   # 매수 글 92% 이상 = 버블 신호
    BEARISH_THRESHOLD = 0.08   # 매수 글 8% 이하 = 반등 신호

    def detect_extreme(self, ticker: str) -> str:
        sentiment_ratio = self.get_community_sentiment(ticker)
        volume_spike = self.detect_volume_anomaly(ticker)

        if sentiment_ratio > self.BULLISH_THRESHOLD and volume_spike:
            return "CONTRARIAN_SELL"   # 역발상 매도
        elif sentiment_ratio < self.BEARISH_THRESHOLD:
            return "CONTRARIAN_BUY"    # 역발상 매수
        return "NEUTRAL"
```

### 해외 커뮤니티의 한국 종목 언급

- Reddit r/investing, r/stocks, r/ValueInvesting에서 한국 반도체/배터리 언급 급증
- 외국인 자금 유입 1~2주 전 선행 신호로 활용
- StockTwits 한국 관련 ETF(EWY) 감성 변화 추적

---

## 2.7 규제/정책 변화 조기 포착 ⭐⭐⭐

### 2.7.1 국회 법안 발의 자동 추적

법안 발의부터 통과까지 수개월이 걸리는 동안 선행 포지셔닝이 가능합니다.

```python
# 규제-섹터 매핑 사전
REGULATION_SECTOR_MAP = {
    "탄소중립": ["OCI", "한화솔루션", "SK이노베이션"],
    "의료기기": ["인바디", "뷰웍스", "오스테오닉"],
    "게임 셧다운제": ["넷마블", "엔씨소프트", "크래프톤"],
    "플랫폼 규제": ["카카오", "네이버", "쿠팡"],
    "전기차 보조금": ["에코프로", "포스코퓨처엠", "LG에너지솔루션"]
}
```

### 2.7.2 중앙부처 예고 고시 분석

- 환경부, 산업부, 복지부 행정예고 → 수혜/피해 섹터 자동 매핑
- **예고 단계에서 포지션 진입 → 확정 후 차익 실현**

### 2.7.3 지방선거/대선 공약 분석

- 대선 후보 공약 → 집권 후 정책 방향 예측
- 공약 수혜 섹터 미리 파악 (SOC, 복지, 에너지 전환 등)

---

## 2.8 공급망 역추적 분석 ⭐⭐

대기업 실적은 이미 알려져 있지만, 그 대기업의 **2차, 3차 협력사**는 아무도 보지 않습니다.

### 밸류체인 매핑 자동화

```python
def extract_supply_chain(company_id: str) -> dict:
    """DART 사업보고서에서 주요 매출처/공급처를 추출합니다."""
    report = get_dart_full_report(company_id)

    # Claude로 "주요 매출처" 섹션 파싱
    customers = claude_extract(report, "주요 매출처 및 의존도")
    suppliers = claude_extract(report, "주요 원재료 공급처")

    return build_supply_chain_graph(customers, suppliers)
```

### 활용 전략

| 대기업 이벤트 | 추적 대상 | 투자 신호 |
|-------------|----------|----------|
| 삼성전자 스마트폰 출하량 증가 | 2~3차 부품 협력사 | 선행 매수 |
| 현대차 전기차 생산 계획 | 와이어링 하네스, 파워모듈 | 수혜 기업 매수 |
| 대형 고객사 매출 의존도 70% 이상 | 해당 중소형주 | 집중 모니터링 |

---

## 2.9 이상 거래 패턴 감지 ⭐⭐

### 2.9.1 공시 전 비정상 거래량 탐지

```python
def detect_unusual_volume(ticker: str, lookback_days: int = 60) -> str:
    """거래량 이상 패턴을 감지합니다."""
    avg_volume = get_avg_volume(ticker, lookback_days)
    today_volume = get_today_volume(ticker)

    volume_ratio = today_volume / avg_volume
    price_change = get_price_change(ticker)

    # 거래량 급증 + 주가 변화 미미 = 정보 선점 의심
    if volume_ratio > 3.0 and abs(price_change) < 0.02:
        return "PRE_EVENT_SIGNAL"

    return "NORMAL"
```

### 2.9.2 옵션/선물 시장 역이용

- 주식 옵션 풋/콜 비율 급변화 → 기관의 헤지 포지션 변화 감지
- 공매도 잔고 급증 종목의 반대 포지션 검토
- ELW 발행사의 헤지 거래로 기관 방향성 추정

---

## 데이터 소스 요약 매트릭스

| # | 데이터 소스 | 차별화 | 난이도 | 선행성 | 비용 | 우선순위 |
|---|-----------|--------|--------|--------|------|---------|
| 1 | 나라장터 낙찰 | ⭐⭐⭐ | 낮음 | 2~4주 | 무료 | 최우선 |
| 2 | HIRA 의약품 | ⭐⭐⭐ | 중간 | 1~2분기 | 무료 | 섹터별 |
| 3 | KIPRIS 특허 | ⭐⭐ | 중간 | 장기 | 무료 | 보조 |
| 4 | DART 공시 | ⭐⭐⭐ | 낮음 | 즉시~2주 | 무료 | 최우선 |
| 5 | 채용공고 | ⭐⭐⭐ | 중간 | 1~2분기 | 무료 | 높음 |
| 6 | 해외 공시 | ⭐⭐⭐ | 중간 | 1~4주 | 무료 | 높음 |
| 7 | NLP 분석 | ⭐⭐⭐ | 높음 | 1~2분기 | 무료 | 높음 |
| 8 | 위성/AIS | ⭐⭐ | 높음 | 1~2주 | 유료 | 중간 |
| 9 | 커뮤니티 감성 | ⭐⭐ | 중간 | 수일 | 무료 | 보조 |
| 10 | 규제/정책 | ⭐⭐⭐ | 낮음 | 수개월 | 무료 | 높음 |
| 11 | 공급망 역추적 | ⭐⭐ | 높음 | 1~2분기 | 무료 | 중간 |
| 12 | 이상 거래 | ⭐⭐ | 중간 | 수일 | 무료 | 보조 |

---

> **다음 문서**: [03. 분석 방법론 상세](./03_analysis_methodology.md)
