# Trading Agent

**자동 주식 거래 에이전트 시스템** - KIS(한국투자증권) REST API 를 활용하여 정보 수집, 타겟 필터링, 지표 분석, 거래 실행, 결과 평가, 파라미터 최적화를 자동으로 수행하는 투자 에이전트입니다.

## 🚀 Core Features

### 1. Information Collector (정보 수집 모듈)
- **역할**: KIS MCP Server 를 통해 실시간 시세, 뉴스, 재무 데이터 수집
- **입력**: 타겟 종목 목록, 데이터 타입
- **출력**: 정제된 시장 데이터
- **의존성**: trading.kis_api

### 2. Target Filter (타겟 필터링 모듈)
- **역할**: 수집된 데이터에서 투자 기준에 맞는 종목 선별
- **입력**: 시장 데이터, 필터링 기준
- **출력**: 타겟 종목 리스트
- **의존성**: data.db, data.models

### 3. Indicator Analyzer (지표 분석 모듈)
- **역할**: 기술적/기본적 지표 분석 (RSI, MACD, 이동평균 등)
- **입력**: 타겟 종목 리스트
- **출력**: 분석 결과 및 거래 신호
- **의존성**: data.history

### 4. Trader (거래 실행 모듈)
- **역할**: KIS API 를 통해 실제 주문 실행
- **입력**: 거래 신호 (매수/매도), 종목, 수량, 가격
- **출력**: 주문 결과
- **의존성**: trading.order_manager, trading.kis_api

### 5. Evaluator (결과 평가 모듈)
- **역할**: 거래 결과 분석 및 정확도 계산
- **입력**: 주문 결과, 시장 데이터
- **출력**: 성과 지표 (PnL, 승률, 손익비 등)
- **의존성**: data.db

### 6. Learner (플로우 최적화 모듈)
- **역할**: 평가 결과를 바탕으로 필터링/분석 파라미터 최적화
- **입력**: 성과 지표, 과거 거래 내역
- **출력**: 업데이트된 파라미터 설정
- **의존성**: data.history

---

## 🔄 Agent Flow Diagram

```
[Agent Orchestrator]
        │
        ├─→ [Information Collector] → 시장 데이터 수집
        │
        ├─→ [Target Filter] → 투자 기준에 맞는 종목 선별
        │      ↓
        │   [Evaluator: 1 차 평가]
        │      ↓ (부정확 시 재집)
        │
        ├─→ [Indicator Analyzer] → 기술적/기본적 분석
        │      ↓
        │   [Evaluator: 2 차 평가]
        │      ↓ (부정확 시 재분석)
        │
        ├─→ [Trader] → 실제 주문 실행
        │      ↓
        │   [Evaluator: 거래 결과 평가]
        │      ↓
        │
        └─→ [Learner] → 파라미터 최적화
               ↓
        └─────── (다음 주기 적용) ────────┘
```

---

## 📁 Project Structure

```
trading_agent/
├── .sisyphus/plans/        # 개발 계획 문서
├── src/
│   ├── modules/            # 모듈 단위 기능
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py      # 에이전트 오케스트레이터
│   │   │   ├── information_collector.py  # 정보 수집 모듈
│   │   │   ├── target_filter.py      # 타겟 필터링 모듈
│   │   │   ├── indicator_analyzer.py  # 지표 분석 모듈
│   │   │   ├── trader.py             # 거래 실행 모듈
│   │   │   ├── evaluator.py          # 결과 평가 모듈
│   │   │   └── learner.py            # 플로우 최적화 모듈
│   │   ├── trading/
│   │   │   ├── __init__.py
│   │   │   ├── kis_api.py          # KIS REST API 래퍼
│   │   │   ├── order_manager.py    # 주문 관리
│   │   │   └── portfolio.py        # 포트폴리오 관리
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── db.py              # SQLite 데이터베이스
│   │   │   ├── models.py          # 데이터 모델
│   │   │   └── history.py         # 거래 내역 분석
│   │   └── shared/
│   │       ├── __init__.py
│   │       ├── config.py          # 환경 설정
│   │       └── utils.py           # 공통 유틸리티
│   └── main.py                 # 메인 진입점
├── tests/
│   ├── unit/
│   │   ├── test_orchestrator.py
│   │   ├── test_information_collector.py
│   │   ├── test_target_filter.py
│   │   ├── test_indicator_analyzer.py
│   │   ├── test_trader.py
│   │   ├── test_evaluator.py
│   │   └── test_learner.py
│   ├── integration/
│   │   ├── test_kis_api.py
│   │   ├── test_order_flow.py
│   │   └── test_data_persistence.py
│   └── e2e/
│       └── test_full_trading_flow.py
├── .env                      # 환경 변수 (Gitignore)
├── .env.example              # 환경 변수 예시
├── AGENTS.md                # 개발 행동 강령
├── open-trading-api/         # Git submodule
│   └── MCP/
│       └── Kis Trading MCP/
│           ├── tools/
│           ├── configs/
│           └── ...
└── k_is_mcp/                 # Git submodule
    ├── server.py
    ├── example.py
    └── ...
```

### Git Submodules
- **open-trading-api/**: 기존 KIS Trading MCP (open_trading_api/MCP 레퍼런스)
- **k_is_mcp/**: KIS MCP Server (Korean Investment Securities REST API MCP)

두 submodule 은 모두 KIS API 통합을 제공하며, 통합할 때 상호 호환성을 확인합니다.

---

## ⚙️ Environment Configuration

### .env.example
```bash
# OpenAI API Configuration
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o

# KIS Trading API Configuration
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCOUNT_TYPE=VIRTUAL
KIS_CANO=your_account_number

# Agent Configuration
AGENT_INTERVAL_HOURS=24  # 최소 단위: 하루
AGGRESSIVENESS=0.5       # 0.0 (conservative) ~ 1.0 (aggressive)
RISK_TOLERANCE=0.1       # 허용 손실률 (10%)

# Database
DB_PATH=./data/trading.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/trading.log
```

---

## 📖 Development Protocol

개발 행동 강령은 [AGENTS.md](AGENTS.md) 를 참조하세요.

---

## Version History

- **v1.0** (2026-03-19): Initial protocol creation
- **v1.1** (2026-03-19): Added agent-based workflow, project structure, env configuration

---

> **Remember**: This system automates stock trading with KIS API. Test thoroughly with demo account before live trading.
