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
- **각 모듈 개발 완료 시 즉시 커밋하고 푸시합니다**
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
- **하나의 커밋 = 하나의 모듈 완성**

### 5. Agent-Based Workflow (에이전틱 플로우)
- 모든 거래 활동은 **에이전트 오케스트레이터**가 통제합니다
- 각 단계는 **독립적인 모듈**로 실행되며, 평가를 거쳐 다음 단계로 진행합니다
- 중간 평가 결과가 부정확하면 이전 단계로 돌아가 재분석합니다

---

## Stage 2: Implementation (per module)

**각 모듈별 개발 절차**:

```
1. Todo 에서 하나의 모듈을 in_progress 로 변경
2. 모듈 인터페이스 정의
3. 테스트 케이스 작성 (TDD: 테스트 먼저!)
4. 구현 코드 작성
5. 테스트 실행 및 통과 확인
6. lsp_diagnostics 로 에러 확인
7. ⚡ 커밋 + 푸시 (즉시!)
8. Todo 를 completed 로 변경
9. 다음 모듈로 이동
```

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
- [ ] **모든 커밋 푸시 완료**

### Before Closing Issue/PR:
- [ ] Quality Gates 전체 통과
- [ ] 코드 리뷰 (협업 시)
- [ ] 성능 테스트 (고성능 모듈인 경우)

---

## Git Workflow

### Commit Message Standard
```
<type>: [scope] <description>

[optional body with test results]

[optional footer]
```

**Types**:
- `feat:` 새로운 기능
- `fix:` 버그 수정
- `test:` 테스트 추가/수정
- `docs:` 문서 변경
- `refactor:` 코드 리팩토링
- `chore:` 개발 환경/билд 관련

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
4. **모듈 하나 = 커밋 하나 = 푸시 하나** - 작고 자주!

### 진행 체크리스트
- [ ] 계획 문서 (.md) 작성 완료
- [ ] Todo List 생성
- [ ] 모듈 단위 개발 및 테스트
- [ ] **각 모듈당 즉시 커밋 + 푸시** ⚡
- [ ] 전체 테스트 통과
- [ ] 빌드 성공

---

> **🚀 Remember: 각 모듈 구현 후 즉시 git commit & push!**
> **⚡ One module = One commit = One push = One completed Todo**
> **📖 프로젝트 구조는 [README.md](README.md) 참조**


