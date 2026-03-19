# Trading Agent - Development Protocol

## Core Principles

### 1. Plan-First Development (계획 중심 개발)
- 모든 기능 개발 전 **상세한 계획**을 수립해야 합니다
- 계획은 `.sisyphus/plans/` 디렉토리에 `.md` 파일로 저장합니다
- 계획 수행 과정을 Todo List 가 시계로 추적하며 진행합니다
- 계획 수정 시 반드시 기존 계획 파일을 업데이트합니다

### 2. Test-Driven Modular Development (모듈 단위 테스트 주도 개발)
- 각 기능은 **독립적인 모듈**으로 개발되어야 합니다
- 모듈 개발 순서:
  1. 모듈 인터페이스 설계
  2. 테스트 케이스 작성 (unit test)
  3. 구현 코드 작성
  4. 테스트 통과 확인
- 모듈 간 의존성은 명확하게 정의하고 문서화합니다

### 3. Complete Test Coverage (완전한 테스트 커버리지)
- **모든 기능**에 대한 테스트가 완료되어야 개발이 종료됩니다
- 테스트 유형:
  - Unit Tests: 개별 함수/클래스 검증
  - Integration Tests: 모듈 간 연동 검증
  - E2E Tests: 전체 기능 흐름 검증 (필요시)
- 테스트 실패 시 개발을 완료한 것으로 간주하지 않습니다

### 4. Atomic Commits & Pushes (원자적 커밋 및 푸시)
- 각 모듈 개발 완료 시 **즉시 커밋**합니다
- 커밋 메시지 형식:
  ```
  feat: [모듈명] 기능 설명
  fix: [모듈명] 버그 수정 내용
  test: [모듈명] 테스트 추가/수정
  docs: [모듈명] 문서화
  refactor: [모듈명] 리팩토링
  ```
- 커밋 후 **즉시 푸시**하여 원격 저장소에서 동기화합니다
- 다른 모듈의 변경사항과混在하지 않도록 주의합니다

### 5. Agent-Based Workflow (에이전틱 플로우)
- 모든 거래 활동은 **에이전트 오케스트레이터**가 통제합니다
- 각 단계는 **독립적인 모듈**으로 실행되며, 평가를 거쳐 다음 단계로 진행합니다
- 중간 평가 결과가 부정확하면 이전 단계로 돌아가 재분석합니다

---

## Development Workflow

### Stage 1: Planning
```
1. 요구사항 분석
2. 아키텍처 설계 (필요시)
3. 모듈 단위로 작업 분해
4. .sisyphus/plans/{feature-name}.md 에 계획 문서화
5. Todo List 생성
```

### Stage 2: Implementation (per module)
```
1. Todo 에서 하나의 모듈을 in_progress 로 변경
2. 모듈 인터페이스 정의
3. 테스트 케이스 작성
4. 구현 코드 작성
5. 테스트 실행 및 통과 확인
6. lsp_diagnostics 로 에러 확인
7. 커밋 + 푸시
8. Todo 를 completed 로 변경
```

### Stage 3: Verification
```
1. 모든 Todo 항목 completed 확인
2. 전체 테스트 스위트 실행
3. Build 검증
4. LSP diagnostics clean 확인
```

### Stage 4: Completion
```
1. 모든 테스트 통과
2. 모든 커밋 푸시 완료
3. 관련 문서 업데이트
```

---

## Core Modules (Agent Flow)

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

### Agent Flow Diagram
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

## Environment Configuration

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

## Project Structure

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
├── AGENTS.md                # 이 문서
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

## Quality Gates

### Before Marking Todo as Completed:
- [ ] 코드 작성 완료
- [ ] Unit 테스트 통과
- [ ] LSP diagnostics clean
- [ ] 관련 문서 업데이트

### Before Finishing Feature:
- [ ] 모든 Todo 항목 completed
- [ ] 모든 관련 모듈 테스트 통과
- [ ] 통합 테스트 통과 (적용 시)
- [ ] 빌드 성공
- [ ] 모든 커밋 푸시

### Before Closing Issue/PR:
- [ ] Stage 4 Completion 체크리스트 전체 통과
- [ ] 코드 리뷰 (협업 시)
- [ ] 성능 테스트 (고성능 모듈인 경우)

---

## Git Workflow

### Commit Message Standard
```
<type>: [scope] <description>

[optional body]

[optional footer]
```

**Types**:
- `feat:` 새로운 기능
- `fix:` 버그 수정
- `test:` 테스트 추가/수정
- `docs:` 문서 변경
- `refactor:` 코드 리팩토링
- `chore:` 개발 환경/빌드 관련

**Example**:
```bash
feat: [information-collector] KIS 시세 조회 기능 추가

- KIS MCP 서버与现实 통합
- 현재가, 호가, 거래량 데이터 수집
- 관련 unit test 작성

Test Plan:
- test/unit/test_information_collector.py (15 tests)
All tests passed.
```

### Branch Naming
```
feature/{module-name}
fix/{issue-number}
refactor/{module-name}
test/{module-name}
```

---

## Tools & Agents

### Planning Phase
- Use `planning-architect` agent for initial architecture
- Use `metis` agent for complex requirement analysis
- Use `momus` agent for plan review/validation

### Implementation Phase
- `visual-engineering` category for UI/UX work
- `ultrabrain` category for complex logic
- `deep` category for autonomous problem-solving
- `quick` category for trivial changes

### Testing Phase
- Use `qa-test-validator` agent for validation
- Run `lsp_diagnostics` on all changed files
- Execute project's test suite

### Delegation Rules
- ALWAYS load relevant skills before task delegation
- Parallelize independent work (background=true)
- Use session_id for continuation
- Never delegate without clear scope and acceptance criteria

---

## Korean Reminders (한글 요약)

### 개발 원칙
1. **계획 없이 개발하지 않는다** - 모든 작업은 계획 문서화
2. **테스트 없이 코드를 쓰지 않는다** - TDD 로 개발
3. **테스트 미통과=미완료** - 테스트가 통과해야 완료
4. **모듈 하나 = 커밋 하나** - 작고 자주 푸시

### 진행 체크리스트
- [ ] 계획 문서 (.md) 작성 완료
- [ ] Todo List 생성
- [ ] 모듈 단위 개발 및 테스트
- [ ] 각 모듈당 커밋 + 푸시
- [ ] 전체 테스트 통과
- [ ] 빌드 성공

---

## Version History

- **v1.0** (2026-03-19): Initial protocol creation
- **v1.1** (2026-03-19): Added agent-based workflow, project structure, env configuration

---

> **Remember**: This protocol ensures consistent, testable, and maintainable development.
> Follow it religiously. Deviate only with explicit justification.


