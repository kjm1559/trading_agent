# Initial Setup Plan

## Overview

이 계획은 Trading Agent 프로젝트의 초기 개발 환경을 설정하고 첫 번째 기능 모듈 (Information Collector) 을 구현하는 것을 목표로 합니다.

**목표**: KIS MCP Server 를 통한 주식 정보 수집 모듈 구현 및 테스트 완료

---

## Phase 1: Project Initialization (Day 1)

### Module 1.1: Project Structure Setup

**Scope**:
- `.sisyphus/plans/` 디렉토리 구조 생성 (현재 작업)
- 기본 Python 프로젝트 구조 설정
- Git configuration

**Deliverables**:
```
.sisyphus/plans/          # 계획 문서 저장소
src/                      # 소스 코드
├── modules/__init__.py   # 패키지 루트
└── shared/__init__.py    # 공유 유틸리티
tests/                    # 테스트 코드
├── unit/
└── integration/
```

**Acceptance Criteria**:
- [ ] 디렉토리 구조가 README.md 에 정의된 대로 생성됨
- [ ] Python 패키지 구조 (`__init__.py`) 적절히 설정됨
- [ ] Git submodule 이 올바르게 초기화됨

---

### Module 1.2: Environment & Configuration

**Scope**:
- `.env.example` 파일 작성
- `pyproject.toml` 또는 `requirements.txt` 설정
- pipenv/venv 설정

**Deliverables**:
- `.env.example` - 환경 변수 템플릿
- `pyproject.toml` - 프로젝트 의존성 관리
- `.gitignore` 업데이트 (`.env`, `__pycache__`, etc.)

**Dependencies**:
- `python-dotenv` - 환경 변수 로드
- `openai` - OpenAI API 클라이언트
- `pytest` - 테스트 프레임워크
- `pytest-cov` - 테스트 커버리지

**Acceptance Criteria**:
- [ ] `pip install -e .` 실행 가능
- [ ] `.env.example` 에 모든 필수 변수 정의됨
- [ ] `pytest .` 실행 가능 (빈 테스트라도)

---

### Module 1.3: Data Layer (Foundation)

**Scope**:
- SQLite 데이터베이스 초기화
- SQLAlchemy/Alembic migration 설정
- 기본 데이터 모델 정의

**Deliverables**:
- `src/modules/data/db.py` - DB 연결 및 세션 관리
- `src/modules/data/models.py` - 데이터 모델
  - `StockInfo` - 종목 기본 정보
  - `MarketData` - 시세 데이터
  - `Trade` - 거래 내역
  - `Performance` - 성과 지표
- `tests/unit/test_db.py` - DB 연결 test
- `tests/unit/test_models.py` - 모델 test

**Acceptance Criteria**:
- [ ] SQLite DB 생성/연결 테스트 통과
- [ ] 모든 모델에 unit test 작성
- [ ] CRUD 기본 작업 테스트 완료

**Model Specifications**:

```python
# StockInfo
- stock_code: str (PK)
- stock_name: str
- market_type: str (KOSPI/KOSDAQ)
- sector: str

# MarketData
- id: int (PK)
- stock_code: str (FK → StockInfo)
- timestamp: datetime
- current_price: float
- volume: int
- change_rate: float

# Trade
- id: int (PK)
- stock_code: str
- timestamp: datetime
- side: str (BUY/SELL)
- price: float
- quantity: int
- status: str (PENDING/COMPLETED/CANCELLED)

# Performance
- id: int (PK)
- timestamp: datetime
- total_pnl: float
- win_rate: float
- profit_factor: float
```

---

### Module 1.4: Shared Utilities

**Scope**:
- 공통 유틸리티 함수
- 로그 설정
- 에러 처리

**Deliverables**:
- `src/modules/shared/config.py` - 환경 설정 관리
- `src/modules/shared/utils.py` - 유틸리티 함수
- `logs/` 디렉토리 및 로깅 설정

**Acceptance Criteria**:
- [ ] 환경 변수 로드 및 검증
- [ ] 로깅 구조 설정 (INFO, DEBUG, ERROR)
- [ ] 에러 처리 공통 패턴 정의

---

## Phase 2: Core Trading Infrastructure (Day 2)

### Module 2.1: KIS API Wrapper

**Scope**:
- KIS REST API 기본 래퍼
- 인증 및 요청 관리
- MCP Server 통합

**Deliverables**:
- `src/modules/trading/kis_api.py` - KIS API 래퍼 클래스
- `tests/unit/test_kis_api.py` - API 래퍼 test
- `tests/integration/test_kis_api.py` - 실제 API 연동 test

**API Endpoints** (from KIS docs):
- `OHLC 정보 받기`
- `현재가 받기`
- "주식(일별/시가총액순/상한하한) 조회"

**Acceptance Criteria**:
- [ ] KIS API 인증 성공
- [ ] 현재가 조회 테스트 통과
- [ ] OHLC 데이터 조회 테스트 통과
- [ ] 에러 처리 (rate limit, network) 테스트 통과

---

### Module 2.2: Order Manager

**Scope**:
- 주문 관리 로직
- 포트폴리오 상태 추적

**Deliverables**:
- `src/modules/trading/order_manager.py` - 주문 관리
- `src/modules/trading/portfolio.py` - 포트폴리오 관리
- `tests/unit/test_order_manager.py`
- `tests/unit/test_portfolio.py`

**Acceptance Criteria**:
- [ ] 주문 생성/조회/취소 로직
- [ ] 보유 주식 조회
- [ ] 가산가 calculation

---

## Phase 3: Information Collector Module (Day 3-4)

### Module 3.1: Information Collector Interface

**Scope**:
- Collector 모듈 인터페이스 정의
- 데이터 수집 전략 정의

**Deliverables**:
- `src/modules/agent/information_collector.py` - Collector 클래스 스켈레톤
- 인터페이스 문서

**Interface Specification**:
```python
class InformationCollector:
    def collect_stock_list(self, market_type: str) -> List[StockInfo]
    def collect_market_data(self, stock_codes: List[str]) -> Dict[str, MarketData]
    def collect_news(self, stock_codes: List[str]) -> List[NewsItem]
    def validate_data(self, data: Any) -> ValidationResult
```

**Acceptance Criteria**:
- [ ] 인터페이스 정의 완료
- [ ] 문서화 완료

---

### Module 3.2: Information Collector Implementation

**Scope**:
- 실제 구현 (TDD)
- 테스트 우선 개발

**Deliverables**:
1. **테스트 작성**: `tests/unit/test_information_collector.py`
   - test_collect_stock_list_valid_market
   - test_collect_market_data_valid_codes
   - test_collect_market_data_with_kis_api_integration
   - test_validate_data_success
   - test_validate_data_missing_fields
   - ... (15+ tests)

2. **구현 코드**: `src/modules/agent/information_collector.py`
   - KIS API 를 통한 종목 목록 수집
   - 현재가/거래량/변동률 수집
   - 데이터 검증 로직

**Acceptance Criteria**:
- [ ] 모든 unit test 통과
- [ ] LSP diagnostics clean
- [ ] 코드 커밋 및 푸시

---

### Module 3.3: Integration Tests

**Scope**:
- 실제 KIS API 와의 연동 테스트
- E2E 테스트 (Demo 계정으로)

**Deliverables**:
- `tests/integration/test_collector_integration.py`
- Demo 환경 설정 가이드

**Acceptance Criteria**:
- [ ] Demo 계정과 연동测试 통과
- [ ] 실제 시장 데이터 수집 확인

---

## Phase 4: Documentation & Handoff (Day 5)

### Module 4.1: Documentation

**Deliverables**:
- README.md 업데이트 (구현된 기능 추가)
- AGENTS.md 에 Phase 1 완료 기록
- `docs/` 디렉토리에 기술 문서

**Acceptance Criteria**:
- [ ] README 업데이트
- [ ] Version History 업데이트

---

## Test Coverage Plan

| Module | Test Type | Test Count | Coverage Target |
|--------|-----------|------------|----------------|
| data.db | Unit | 10 | 90% |
| data.models | Unit | 15 | 95% |
| shared.config | Unit | 8 | 90% |
| trading.kis_api | Unit + Integration | 20 | 85% |
| trading.order_manager | Unit | 15 | 90% |
| agent.information_collector | Unit + Integration | 25 | 90% |

**Total Tests**: ~110 tests
**Target Coverage**: 90%+

---

## Module Breakdown Summary (Todo List)

### Phase 1: Project Initialization
- [ ] **TODO-1**: `.sisyphus/plans/` 디렉토리 구조 생성
- [ ] **TODO-2**: Python 패키지 구조 설정 (`__init__.py` files)
- [ ] **TODO-3**: `.env.example` 작성 및 환경 변수 정의
- [ ] **TODO-4**: `pyproject.toml` 의존성 설정
- [ ] **TODO-5**: `src/modules/data/db.py` 구현 + unit test
- [ ] **TODO-6**: `src/modules/data/models.py` 구현 + unit test
- [ ] **TODO-7**: `src/modules/shared/config.py` 구현 + unit test
- [ ] **TODO-8**: `src/modules/shared/utils.py` 구현 + unit test

### Phase 2: Core Trading Infrastructure
- [ ] **TODO-9**: `src/modules/trading/kis_api.py` 구현 + unit test
- [ ] **TODO-10**: `src/modules/trading/order_manager.py` 구현 + unit test
- [ ] **TODO-11**: `src/modules/trading/portfolio.py` 구현 + unit test
- [ ] **TODO-12**: KIS API integration test 작성

### Phase 3: Information Collector
- [ ] **TODO-13**: `InformationCollector` 인터페이스 정의
- [ ] **TODO-14**: `tests/unit/test_information_collector.py` 작성 (TDD)
- [ ] **TODO-15**: `information_collector.py` 구현
- [ ] **TODO-16**: Integration tests 작성
- [ ] **TODO-17**: 모든 테스트 통과 확인

### Phase 4: Documentation
- [ ] **TODO-18**: README.md 업데이트
- [ ] **TODO-19**: Version History 업데이트
- [ ] **TODO-20**: 커밋 및 푸시 완료

---

## Development Checklist

### Pre-Development
- [ ] 계획 문서 검토
- [ ] Git submodule 확인
- [ ] 환경 변수 준비

### Per Module
- [ ] 테스트 먼저 작성 (TDD)
- [ ] 구현 코드 작성
- [ ] 테스트 통과
- [ ] LSP diagnostics clean
- [ ] 커밋 + 푸시

### Post-Phase
- [ ] 모든 테스트 통과
- [ ] 문서화 완료
- [ ] 다음 Phase 계획

---

## Metrics & Success Criteria

**Phase 1 Success**:
- ✅ 모든 Phase 1 모듈 테스트 통과
- ✅ Coverage > 90%
- ✅ LSP diagnostics clean
- ✅ 모든 커밋 푸시 완료

**Quality Gates**:
```
Before committing:
- All tests pass: pytest -v
- LSP clean: lsp_diagnostics
- No linting errors

Before finishing:
- All modules completed
- All tests passing
- Documentation updated
```

---

## Notes

- submodule 초기화 필요시: `git submodule update --init --recursive`
- Demo 계정 필수 (실제 거래 전 테스트)
- KIS API rate limit 고려 (최대 20 회/분)

---

**Created**: 2026-03-20
**Author**: Sisyphus-Junior
**Status**: Planning Phase
