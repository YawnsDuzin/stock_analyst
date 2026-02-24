# 클로드 기반 증권 애널리스트 시스템 - 문서 목차

> **목표**: 대형 기관이 주목하지 않는 틈새에서 정보 비대칭성을 활용하여 알파를 발굴하는 AI 애널리스트 시스템 구축

---

## 문서 구성

| 번호 | 문서명 | 파일 | 설명 |
|------|--------|------|------|
| 01 | [핵심 철학 및 전략 방향](./01_core_philosophy.md) | `01_core_philosophy.md` | 시스템의 근본 철학과 알파 원천 정의 |
| 02 | [차별화된 데이터 소스 전략](./02_data_sources.md) | `02_data_sources.md` | 9가지 대안 데이터 소스 상세 가이드 |
| 03 | [분석 방법론 상세](./03_analysis_methodology.md) | `03_analysis_methodology.md` | 멀티 레이어 분석 프레임워크 |
| 04 | [기술 스택 및 아키텍처](./04_tech_stack.md) | `04_tech_stack.md` | 시스템 구성, 백엔드/프론트엔드/인프라 |
| 05 | [Claude 연동 설계](./05_claude_integration.md) | `05_claude_integration.md` | Tool Use, 멀티 에이전트 설계 |
| 06 | [통합 스코어링 시스템](./06_scoring_system.md) | `06_scoring_system.md` | AlphaScorer 설계 및 대시보드 |
| 07 | [바이브 코딩 개발 로드맵](./07_development_roadmap.md) | `07_development_roadmap.md` | Phase 1~4 개발 단계별 계획 |
| 08 | [백테스팅 및 검증](./08_backtesting.md) | `08_backtesting.md` | 신호 검증 방법 및 편향 주의사항 |
| 09 | [리스크 관리 및 법적 주의사항](./09_risk_management.md) | `09_risk_management.md` | 법적 준수사항 및 포지션 관리 |
| 10 | [우선순위 실행 계획](./10_execution_plan.md) | `10_execution_plan.md` | 단계별 실행 계획 및 참고 자료 |

---

## 프로젝트 구조

```
stock_analyst/
├── docs/                          # 문서 (현재 디렉토리)
│   ├── 00_index.md               # 문서 목차 (이 파일)
│   ├── 01_core_philosophy.md     # 핵심 철학
│   ├── 02_data_sources.md        # 데이터 소스
│   ├── 03_analysis_methodology.md # 분석 방법론
│   ├── 04_tech_stack.md          # 기술 스택
│   ├── 05_claude_integration.md  # Claude 연동
│   ├── 06_scoring_system.md      # 스코어링
│   ├── 07_development_roadmap.md # 로드맵
│   ├── 08_backtesting.md         # 백테스팅
│   ├── 09_risk_management.md     # 리스크 관리
│   └── 10_execution_plan.md      # 실행 계획
├── src/                           # 소스 코드
│   └── stock_analyst/
│       ├── __init__.py
│       ├── config.py             # 설정 관리
│       ├── data_sources/         # 데이터 수집 모듈
│       ├── analysis/             # 분석 엔진
│       ├── scoring/              # 스코어링 시스템
│       └── utils/                # 유틸리티
├── tests/                         # 유닛 테스트
│   ├── test_config.py
│   ├── test_data_sources/
│   ├── test_analysis/
│   └── test_scoring/
├── README.md
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## 빠른 시작

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 설정

# 3. 테스트 실행
pytest tests/ -v

# 4. 개발 서버 실행
uvicorn src.stock_analyst.main:app --reload
```

---

> **면책 고지**: 본 문서는 시스템 구축 참고용이며 투자 조언이 아닙니다.
> 모든 투자 결정은 개인 책임이며, 반드시 백테스팅과 소액 실험 후 점진적으로 확대하시기 바랍니다.
