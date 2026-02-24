# 09. 리스크 관리 및 법적 주의사항

> **이 문서의 목적**: 시스템 운용 시 반드시 준수해야 할 법적 사항과 포지션 리스크 관리 규칙을 명확히 정의합니다.

---

## 목차

- [9.1 법적 주의사항](#91-법적-주의사항)
- [9.2 데이터 수집 법적 가이드라인](#92-데이터-수집-법적-가이드라인)
- [9.3 포지션 리스크 관리](#93-포지션-리스크-관리)
- [9.4 시스템 리스크 관리](#94-시스템-리스크-관리)
- [9.5 운영 리스크 체크리스트](#95-운영-리스크-체크리스트)

---

## 9.1 법적 주의사항

### 반드시 준수해야 할 사항

```
✅ 허용 사항:
  - 공개된 데이터만 활용 (나라장터, DART, 공공API 등)
  - 크롤링 시 robots.txt 준수 및 서버 부하 최소화
  - 수집 데이터 개인정보보호법 준수
  - 공개 API의 이용약관 준수
  - 학술/개인 연구 목적의 데이터 분석

❌ 금지 사항:
  - 미공개 중요 정보(MNPI) 활용 → 자본시장법 위반
  - 기업 내부자로부터 취득한 미공개 정보 사용 → 내부자 거래
  - 해킹, 무단 접근으로 취득한 데이터 사용 → 형법 위반
  - 시세조종, 부정거래 행위 → 자본시장법 위반
  - AI 분석 결과를 투자 조언으로 제3자에게 유료 배포 → 금융투자업 허가 필요
```

### 관련 법률

| 법률 | 관련 조항 | 핵심 내용 |
|------|----------|----------|
| **자본시장법** | 제174조 | 미공개 중요정보 이용행위 금지 |
| **자본시장법** | 제176조 | 시세조종 행위 금지 |
| **자본시장법** | 제178조 | 부정거래 행위 금지 |
| **개인정보보호법** | 전반 | 개인정보 수집/이용/저장 규정 |
| **정보통신망법** | 제48조 | 정보통신망 침해행위 금지 |
| **금융투자업법** | 제6조 | 투자자문업 인가 요건 |

### 면책 고지 문구 (필수 포함)

시스템이 생성하는 모든 분석 결과에 반드시 포함해야 할 문구:

```
본 분석은 AI 기반 자동 분석 결과이며, 투자 조언이 아닙니다.
모든 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다.
과거의 신호 성과가 미래의 수익을 보장하지 않습니다.
본 시스템은 공개된 데이터만을 활용하며, 미공개 정보를 사용하지 않습니다.
```

---

## 9.2 데이터 수집 법적 가이드라인

### 크롤링 윤리 규칙

```python
class CrawlingPolicy:
    """웹 크롤링 시 준수해야 할 정책"""

    # robots.txt 준수
    RESPECT_ROBOTS_TXT = True

    # 요청 간격 (서버 부하 방지)
    MIN_REQUEST_INTERVAL_SECONDS = 2.0

    # User-Agent 명시 (봇임을 투명하게 표시)
    USER_AGENT = "StockAnalystBot/1.0 (research purpose; contact@example.com)"

    # 일일 최대 요청 수 (사이트별)
    MAX_DAILY_REQUESTS_PER_SITE = 5000

    # 비즈니스 시간 외 크롤링 선호
    PREFERRED_CRAWL_HOURS = (0, 6)  # 자정~오전 6시
```

### API 이용약관 준수 체크리스트

| 데이터 소스 | API 키 필요 | 일일 제한 | 상업적 이용 | 비고 |
|------------|-----------|----------|-----------|------|
| 공공데이터포털 | O | 1,000건 | 허용 | 서비스 활용 신청 필요 |
| DART | O | 일반 10,000건 | 허용 | 이용약관 동의 |
| KIPRIS | O | 제한적 | 조건부 허용 | 학술/연구 우선 |
| HIRA | O/X | 제한적 | 확인 필요 | 데이터별 상이 |
| ClinicalTrials.gov | X | 제한적 | 허용 | 미국 공공 데이터 |
| SEC EDGAR | X | 10req/sec | 허용 | User-Agent 필수 |

### 개인정보 처리 규칙

```python
# 수집 금지 대상
PROHIBITED_DATA = [
    "주민등록번호",
    "전화번호",
    "이메일 (개인)",
    "주소 (개인)",
    "금융계좌 정보",
    "의료 정보 (개인 식별 가능)",
]

# 수집 시 즉시 익명화 처리
def anonymize_data(data: dict) -> dict:
    """개인 식별 가능 정보를 제거합니다."""
    for field in PROHIBITED_DATA:
        if field in data:
            del data[field]
    return data
```

---

## 9.3 포지션 리스크 관리

### RiskManager 핵심 규칙

```python
class RiskManager:
    """포지션 리스크를 관리하는 핵심 모듈"""

    # === 포지션 한도 ===
    MAX_SINGLE_POSITION = 0.10    # 단일 종목 최대 10%
    MAX_SECTOR_EXPOSURE = 0.30    # 섹터 최대 30%
    MAX_TOTAL_INVESTED = 0.80     # 총 투자 비율 최대 80% (현금 20% 유지)

    # === 손절 기준 ===
    STOP_LOSS_THRESHOLD = -0.08   # 8% 하락 시 손절
    TRAILING_STOP = -0.10         # 고점 대비 10% 하락 시 트레일링 스톱

    # === 신호 기준 ===
    MIN_SIGNAL_SCORE = 65         # 최소 신호 강도 기준
    MIN_CROSS_VALIDATION = 3     # 최소 교차 검증 소스 수

    def approve_trade(
        self,
        ticker: str,
        signal_score: float,
        portfolio: "Portfolio"
    ) -> dict:
        """매매 승인 여부를 결정합니다."""

        checks = {
            "signal_strength": signal_score >= self.MIN_SIGNAL_SCORE,
            "single_position": (
                portfolio.get_weight(ticker) < self.MAX_SINGLE_POSITION
            ),
            "sector_exposure": (
                portfolio.get_sector_weight(ticker) < self.MAX_SECTOR_EXPOSURE
            ),
            "total_invested": (
                portfolio.get_total_invested_ratio() < self.MAX_TOTAL_INVESTED
            ),
            "liquidity": self.check_liquidity(ticker),
        }

        approved = all(checks.values())
        failed_checks = [k for k, v in checks.items() if not v]

        return {
            "approved": approved,
            "checks": checks,
            "failed": failed_checks,
            "reason": f"거부 사유: {', '.join(failed_checks)}" if not approved else "승인"
        }

    def check_liquidity(self, ticker: str) -> bool:
        """유동성 충분 여부를 확인합니다."""
        avg_volume = self.get_avg_daily_volume(ticker, days=20)
        # 일 거래대금 10억원 이상
        avg_turnover = avg_volume * self.get_current_price(ticker)
        return avg_turnover >= 1_000_000_000

    def check_stop_loss(self, position: dict) -> dict:
        """손절 조건 충족 여부를 확인합니다."""
        current_price = self.get_current_price(position["ticker"])
        entry_price = position["entry_price"]
        highest_price = position.get("highest_price", entry_price)

        # 절대 손절
        pnl = (current_price - entry_price) / entry_price
        if pnl <= self.STOP_LOSS_THRESHOLD:
            return {
                "action": "STOP_LOSS",
                "reason": f"절대 손절: {pnl:.1%} (기준: {self.STOP_LOSS_THRESHOLD:.1%})",
                "urgency": "HIGH"
            }

        # 트레일링 스톱
        from_high = (current_price - highest_price) / highest_price
        if from_high <= self.TRAILING_STOP:
            return {
                "action": "TRAILING_STOP",
                "reason": f"트레일링 스톱: 고점 대비 {from_high:.1%}",
                "urgency": "HIGH"
            }

        return {"action": "HOLD", "reason": "정상 범위", "urgency": "LOW"}
```

### 포지션 사이징 규칙

```python
def calculate_position_size(
    signal_score: float,
    confidence: float,
    portfolio_value: float,
    volatility: float
) -> float:
    """
    Kelly Criterion 변형으로 포지션 사이즈를 계산합니다.

    Args:
        signal_score: 신호 점수 (0~100)
        confidence: 신호 신뢰도 (0~1)
        portfolio_value: 총 포트폴리오 가치
        volatility: 종목의 연간 변동성

    Returns:
        투자 금액
    """
    # 기본 배분: 점수에 비례 (최대 10%)
    base_pct = (signal_score / 100) * 0.10

    # 신뢰도 반영
    adjusted_pct = base_pct * confidence

    # 변동성 반비례 (변동성 높은 종목은 적게)
    vol_adjustment = 0.20 / max(volatility, 0.10)  # 20% 변동성 기준
    final_pct = adjusted_pct * min(vol_adjustment, 1.5)

    # 최대/최소 제한
    final_pct = max(0.02, min(final_pct, 0.10))  # 2% ~ 10%

    return portfolio_value * final_pct
```

---

## 9.4 시스템 리스크 관리

### API 장애 대응

```python
class SystemRiskManager:
    """시스템 수준의 리스크를 관리합니다."""

    def handle_api_failure(self, api_name: str, error: Exception):
        """API 장애 시 대응 프로세스"""

        # 1. 알림 전송
        self.send_alert(
            level="WARNING",
            message=f"API 장애 감지: {api_name} - {str(error)}"
        )

        # 2. 대체 데이터 소스 활용
        fallback = self.get_fallback_source(api_name)
        if fallback:
            return fallback.collect()

        # 3. 해당 신호 제외하고 분석 계속
        return None  # 해당 신호를 50 (중립)으로 처리

    def validate_data_integrity(self, data: dict) -> bool:
        """수집된 데이터의 무결성을 검증합니다."""
        checks = [
            data is not None,
            len(data) > 0,
            self.check_date_range(data),
            self.check_value_range(data),
            not self.detect_anomaly(data),
        ]
        return all(checks)
```

### 모니터링 대상

| 구분 | 모니터링 항목 | 임계값 | 알림 채널 |
|------|-------------|--------|----------|
| API | 응답 시간 | > 30초 | 텔레그램 |
| API | 연속 실패 | > 3회 | 텔레그램 + 이메일 |
| 데이터 | 수집 누락 | > 1일 | 텔레그램 |
| 분석 | 점수 급변 | 1일 > 30점 변동 | 텔레그램 |
| 포지션 | 손절 임계값 | -8% | 즉시 텔레그램 |
| 시스템 | 디스크 사용률 | > 85% | 이메일 |

---

## 9.5 운영 리스크 체크리스트

### 일간 체크리스트

```
□ 데이터 수집 정상 완료 확인
□ 신호 스코어 급변 종목 검토
□ 보유 종목 손절 조건 점검
□ API 사용량 모니터링
□ 시스템 로그 이상 여부 확인
```

### 주간 체크리스트

```
□ 주간 성과 리뷰 (예측 vs 실제)
□ 신호별 적중률 추이 확인
□ 포트폴리오 섹터 집중도 점검
□ 데이터 소스 변동사항 확인 (API 변경 등)
□ 채용공고 스냅샷 비교
```

### 월간 체크리스트

```
□ 월간 성과 종합 리포트
□ 가중치 재최적화 필요성 검토
□ 신규 데이터 소스 탐색
□ API 비용 검토 (예산 내 운용 확인)
□ 법적/규제 변화 확인
□ 시스템 보안 점검
```

---

## 핵심 요약

```
1. 법적 준수 = 공개 데이터만 사용, MNPI 절대 금지, 면책 고지 필수
2. 크롤링 윤리 = robots.txt 준수, 요청 간격 유지, User-Agent 명시
3. 포지션 관리 = 단일 종목 10%, 섹터 30%, 현금 20% 유지
4. 손절 규칙 = 절대 -8%, 트레일링 -10%
5. 시스템 모니터링 = API 장애 대응, 데이터 무결성, 일/주/월간 체크리스트
```

---

> **다음 문서**: [10. 우선순위 실행 계획](./10_execution_plan.md)
