# 05. Claude 연동 설계

> **이 문서의 목적**: Claude API의 Tool Use와 멀티 에이전트 구조를 활용한 증권 분석 시스템의 AI 연동 설계를 상세히 설명합니다.

---

## 목차

- [5.1 Claude API 기본 설정](#51-claude-api-기본-설정)
- [5.2 시스템 프롬프트 설계](#52-시스템-프롬프트-설계)
- [5.3 Tool Use 설계](#53-tool-use-설계)
- [5.4 RAG (Retrieval Augmented Generation)](#54-rag-retrieval-augmented-generation)
- [5.5 멀티 에이전트 구조](#55-멀티-에이전트-구조)
- [5.6 프롬프트 엔지니어링 팁](#56-프롬프트-엔지니어링-팁)
- [5.7 비용 최적화](#57-비용-최적화)

---

## 5.1 Claude API 기본 설정

### 의존성 설치

```bash
pip install anthropic
```

### 기본 클라이언트 설정

```python
import anthropic
import os

# 클라이언트 초기화
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# 모델 선택 가이드
MODELS = {
    "analysis": "claude-sonnet-4-20250514",   # 일반 분석 (비용 효율)
    "deep_analysis": "claude-opus-4-20250514",     # 심층 분석 (최고 품질)
    "quick_check": "claude-haiku-4-20250514",  # 빠른 확인 (저비용)
}
```

---

## 5.2 시스템 프롬프트 설계

### 메인 애널리스트 시스템 프롬프트

```python
SYSTEM_PROMPT = """
당신은 대안 데이터 전문 시니어 증권 애널리스트입니다.

## 분석 원칙
1. 공시/뉴스보다 1~2단계 앞선 선행 지표를 반드시 찾는다
2. 기관이 주목하지 않는 중소형주 틈새를 발굴한다
3. 규제 변화를 가장 먼저 수혜/피해 섹터로 매핑한다
4. 모든 의견에는 반드시 근거 데이터를 명시한다
5. 손절 기준과 구체적 리스크를 항상 함께 제시한다
6. 가설이 틀릴 수 있는 반론을 스스로 검토한다

## 리포트 형식
- 투자의견: Buy / Hold / Sell (근거 3가지 이상)
- 목표가: 현재가 대비 상승여력
- 핵심 catalyst: 주가 움직임의 트리거 이벤트
- 리스크 요인: 가설이 틀릴 경우의 시나리오
- 모니터링 지표: 지속 추적할 데이터 포인트

## 제약사항
- 미공개 정보는 절대 활용하지 않는다
- 확실하지 않은 내용은 반드시 불확실성을 명시한다
- 투자는 개인 책임임을 항상 고지한다
"""
```

### Devil's Advocate (리스크 검토) 프롬프트

```python
RISK_REVIEWER_PROMPT = """
당신은 투자 가설의 약점을 찾는 전문 리스크 분석가입니다.
어떤 투자 아이디어가 제시되면, 반드시 반론을 제시해야 합니다.

## 검토 관점
1. 이 정보가 이미 주가에 반영되었을 가능성은?
2. 데이터 해석에 편향이 있지는 않은가?
3. 반대 방향의 신호는 없는가?
4. 최악의 시나리오에서 손실 규모는?
5. 유사한 과거 사례에서 실패한 경우는?

## 출력 형식
각 반론에 대해:
- 반론 제목
- 상세 설명
- 발생 확률: 높음/중간/낮음
- 영향도: 높음/중간/낮음
- 대응 방안 제안
"""
```

---

## 5.3 Tool Use 설계

### 도구(Tool) 정의

```python
TOOLS = [
    {
        "name": "get_procurement_signals",
        "description": "나라장터에서 특정 기업의 최근 낙찰 데이터를 조회합니다. "
                       "대형 계약 낙찰은 IR 공시보다 2~4주 먼저 확인할 수 있는 선행 지표입니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "검색할 기업명 (예: '삼성SDS', 'LG CNS')"
                },
                "days_back": {
                    "type": "integer",
                    "description": "조회 기간(일), 기본값 30일",
                    "default": 30
                }
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "get_hiring_signals",
        "description": "채용공고 변화에서 사업 방향 신호를 추출합니다. "
                       "신규 채용 포지션은 사업 피벗이나 확장의 선행 지표입니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "기업명"
                },
                "signal_type": {
                    "type": "string",
                    "enum": ["expansion", "new_business", "risk", "all"],
                    "description": "신호 유형 필터"
                }
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "analyze_dart_changes",
        "description": "DART 공시 문서의 전년 대비 언어 변화를 분석합니다. "
                       "사업보고서의 톤 변화, 리스크 추가/제거, 키워드 빈도 변화를 감지합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_id": {
                    "type": "string",
                    "description": "DART 고유번호"
                },
                "report_type": {
                    "type": "string",
                    "enum": ["annual", "quarterly", "material"],
                    "description": "보고서 유형"
                }
            },
            "required": ["company_id"]
        }
    },
    {
        "name": "get_alternative_signals",
        "description": "위성, AIS, 전력 등 대안 데이터에서 신호를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "signal_source": {
                    "type": "string",
                    "enum": ["satellite", "ais", "power", "search_trend"],
                    "description": "데이터 소스 유형"
                },
                "target": {
                    "type": "string",
                    "description": "기업명 또는 섹터"
                }
            },
            "required": ["signal_source", "target"]
        }
    },
    {
        "name": "calculate_alpha_score",
        "description": "모든 신호를 통합하여 투자 알파 스코어를 계산합니다. "
                       "각 데이터 소스의 점수를 가중 평균하여 0~100 사이의 점수를 산출합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "종목 코드 (예: '005930')"
                },
                "weights": {
                    "type": "object",
                    "description": "각 신호 가중치 (선택사항, 기본값 사용 가능)",
                    "properties": {
                        "government_contract": {"type": "number"},
                        "hiring_signal": {"type": "number"},
                        "language_change": {"type": "number"},
                        "alternative_data": {"type": "number"},
                        "sentiment_extreme": {"type": "number"},
                        "supply_chain": {"type": "number"}
                    }
                }
            },
            "required": ["ticker"]
        }
    }
]
```

### Tool Use 실행 루프

```python
async def run_analyst(user_query: str) -> str:
    """Claude Tool Use 루프를 실행합니다."""
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model=MODELS["analysis"],
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        # 텍스트 응답이면 종료
        if response.stop_reason == "end_turn":
            return extract_text(response)

        # Tool Use 요청 처리
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})


async def execute_tool(name: str, inputs: dict) -> dict:
    """도구를 실행하고 결과를 반환합니다."""
    tool_map = {
        "get_procurement_signals": procurement_collector.collect,
        "get_hiring_signals": hiring_tracker.track,
        "analyze_dart_changes": dart_analyzer.compare,
        "get_alternative_signals": alt_data_collector.collect,
        "calculate_alpha_score": alpha_scorer.calculate_score,
    }

    handler = tool_map.get(name)
    if handler:
        return await handler(**inputs)
    return {"error": f"Unknown tool: {name}"}
```

---

## 5.4 RAG (Retrieval Augmented Generation)

### RAG 파이프라인

```python
from sentence_transformers import SentenceTransformer
import chromadb

class RAGPipeline:
    """분석 시 관련 문맥을 자동으로 검색하여 Claude에게 제공합니다."""

    def __init__(self):
        self.embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection("analyst_knowledge")

    def add_document(self, doc_id: str, text: str, metadata: dict):
        """문서를 벡터 DB에 추가합니다."""
        embedding = self.embedder.encode(text).tolist()
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )

    def retrieve(self, query: str, n_results: int = 5) -> list[str]:
        """쿼리와 관련된 문서를 검색합니다."""
        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results["documents"][0] if results["documents"] else []

    def augmented_prompt(self, query: str) -> str:
        """RAG로 강화된 프롬프트를 생성합니다."""
        contexts = self.retrieve(query)
        context_text = "\n---\n".join(contexts)

        return f"""
다음은 관련 참고 자료입니다:

{context_text}

---

위 참고 자료를 바탕으로 다음 질문에 답하세요:
{query}
"""
```

### 저장할 문서 유형

| 문서 유형 | 업데이트 주기 | 메타데이터 |
|----------|-------------|----------|
| DART 사업보고서 | 분기/연간 | company_id, year, report_type |
| 컨퍼런스콜 전문 | 분기 | company_id, quarter, date |
| 뉴스 기사 | 일간 | company_id, date, source |
| 애널리스트 리포트 | 수시 | company_id, analyst, date |
| 과거 분석 결과 | 수시 | ticker, analysis_date, score |

---

## 5.5 멀티 에이전트 구조

### 3개 전문 에이전트 협력 구조

```python
class AnalystSystem:
    """3개의 전문 에이전트가 협력하는 분석 시스템"""

    def __init__(self):
        self.data_agent = DataCollectorAgent()    # 데이터 수집 전담
        self.analyst_agent = AnalystAgent()       # Claude: 분석 전담
        self.risk_agent = RiskManagerAgent()       # Claude: 리스크 검토 전담

    async def analyze(self, ticker: str) -> dict:
        # Step 1: 데이터 수집 (비동기 병렬)
        data = await self.data_agent.collect_all(ticker)

        # Step 2: 분석 생성 (Claude 애널리스트)
        analysis = await self.analyst_agent.analyze(data)

        # Step 3: 리스크 검토 (Claude Devil's Advocate)
        risk_review = await self.risk_agent.challenge(analysis)

        # Step 4: 최종 리포트 통합
        return self.merge_report(analysis, risk_review)

    def merge_report(self, analysis: dict, risk_review: dict) -> dict:
        """분석과 리스크 검토를 통합합니다."""
        # 리스크 검토 결과에 따라 최종 점수 조정
        adjusted_score = analysis["score"]
        for risk in risk_review["risks"]:
            if risk["probability"] == "높음" and risk["impact"] == "높음":
                adjusted_score *= 0.7  # 고위험 항목 시 30% 하향

        return {
            "analysis": analysis,
            "risk_review": risk_review,
            "adjusted_score": adjusted_score,
            "final_recommendation": self.get_recommendation(adjusted_score)
        }
```

### DataCollectorAgent (데이터 수집)

```python
class DataCollectorAgent:
    """모든 데이터 소스에서 병렬로 데이터를 수집합니다."""

    async def collect_all(self, ticker: str) -> dict:
        import asyncio

        tasks = [
            self.collect_dart(ticker),
            self.collect_procurement(ticker),
            self.collect_hiring(ticker),
            self.collect_news(ticker),
            self.collect_sentiment(ticker),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "dart": results[0] if not isinstance(results[0], Exception) else None,
            "procurement": results[1] if not isinstance(results[1], Exception) else None,
            "hiring": results[2] if not isinstance(results[2], Exception) else None,
            "news": results[3] if not isinstance(results[3], Exception) else None,
            "sentiment": results[4] if not isinstance(results[4], Exception) else None,
        }
```

### AnalystAgent (분석)

```python
class AnalystAgent:
    """Claude를 사용하여 수집된 데이터를 분석합니다."""

    async def analyze(self, data: dict) -> dict:
        prompt = self._build_analysis_prompt(data)

        response = client.messages.create(
            model=MODELS["analysis"],
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_analysis(response)

    def _build_analysis_prompt(self, data: dict) -> str:
        return f"""
다음 데이터를 기반으로 종합 분석 리포트를 작성하세요:

## 수집된 데이터
### DART 공시: {json.dumps(data.get('dart'), ensure_ascii=False)}
### 나라장터: {json.dumps(data.get('procurement'), ensure_ascii=False)}
### 채용 신호: {json.dumps(data.get('hiring'), ensure_ascii=False)}
### 뉴스 감성: {json.dumps(data.get('news'), ensure_ascii=False)}
### 커뮤니티: {json.dumps(data.get('sentiment'), ensure_ascii=False)}

리포트 형식을 따라 분석해주세요.
"""
```

### RiskManagerAgent (리스크 검토)

```python
class RiskManagerAgent:
    """분석 결과에 대한 반론을 생성합니다."""

    async def challenge(self, analysis: dict) -> dict:
        prompt = f"""
다음 투자 분석에 대해 Devil's Advocate 관점에서 검토하세요:

## 분석 결과
{json.dumps(analysis, ensure_ascii=False)}

반드시 5가지 이상의 반론을 제시하고,
각 반론의 발생 확률과 영향도를 평가하세요.
"""

        response = client.messages.create(
            model=MODELS["analysis"],
            max_tokens=2048,
            system=RISK_REVIEWER_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_risk_review(response)
```

---

## 5.6 프롬프트 엔지니어링 팁

### 한국어 금융 분석에 특화된 팁

1. **구체적 수치 요구**: "대략적으로"가 아닌 "구체적 수치와 근거를 포함하여" 요청
2. **한국 시장 맥락 제공**: 한국 주식시장의 특성(외인 매매 영향, 코스피/코스닥 차이 등) 명시
3. **출력 형식 명시**: JSON, Markdown 등 원하는 출력 형식을 명확히 지정
4. **반론 의무화**: "이 분석이 틀릴 수 있는 경우를 반드시 포함"

### 프롬프트 템플릿

```python
ANALYSIS_TEMPLATE = """
## 분석 대상
- 종목: {ticker} ({company_name})
- 현재가: {current_price}원
- 시가총액: {market_cap}억원

## 요청 사항
{analysis_request}

## 출력 형식
반드시 다음 JSON 형식으로 응답하세요:
{{
    "recommendation": "BUY|HOLD|SELL",
    "target_price": <number>,
    "score": <0-100>,
    "catalysts": [<string>, ...],
    "risks": [<string>, ...],
    "stop_loss": <number>,
    "monitoring_indicators": [<string>, ...]
}}
"""
```

---

## 5.7 비용 최적화

### 모델 선택 전략

| 작업 유형 | 추천 모델 | 이유 |
|----------|----------|------|
| 간단한 데이터 분류 | Haiku | 저비용, 빠른 응답 |
| 일반 분석 리포트 | Sonnet | 비용/품질 균형 |
| 심층 분석, 복합 판단 | Opus | 최고 품질 (비용 높음) |
| 임베딩 생성 | Sentence Transformers | 무료 (로컬) |

### 캐싱 전략

```python
import hashlib

def get_cached_analysis(prompt: str, ttl: int = 3600) -> str | None:
    """동일한 프롬프트의 분석 결과를 캐싱합니다."""
    cache_key = f"claude:{hashlib.md5(prompt.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    if cached:
        return cached.decode()
    return None

def cache_analysis(prompt: str, result: str, ttl: int = 3600):
    """분석 결과를 캐싱합니다."""
    cache_key = f"claude:{hashlib.md5(prompt.encode()).hexdigest()}"
    redis_client.setex(cache_key, ttl, result)
```

### Prompt Caching 활용

```python
# 시스템 프롬프트 캐싱으로 반복 비용 절감
response = client.messages.create(
    model=MODELS["analysis"],
    max_tokens=4096,
    system=[
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}  # 프롬프트 캐싱
        }
    ],
    messages=messages
)
```

---

## 핵심 요약

```
1. Tool Use = Claude가 직접 데이터를 조회하고 분석하는 에이전트 구조
2. RAG = ChromaDB + 한국어 임베딩으로 맥락 강화
3. 멀티 에이전트 = 데이터 수집 + 분석 + 리스크 검토 3단계
4. 비용 최적화 = 모델 선택 + 캐싱 + 프롬프트 캐싱
```

---

> **다음 문서**: [06. 통합 스코어링 시스템](./06_scoring_system.md)
