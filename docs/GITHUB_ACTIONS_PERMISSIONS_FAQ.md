# GitHub Actions 권한 및 외부 Cron 설정 FAQ
## Frequently Asked Questions about Manual Triggers and External Services

**작성일**: 2025-11-25

---

## 질문 1: 외부 Cron 서비스 설정을 자동으로 할 수 없나요?

### 답변: **불가능합니다** (보안상의 이유)

외부 cron 서비스(cron-job.org) 설정은 **반드시 사용자가 수동으로** 해야 합니다.

### 이유:

#### 1. **GitHub Personal Access Token (PAT) 생성**
```
❌ Claude Code가 할 수 없는 것:
  - GitHub 계정에 로그인
  - Personal Access Token 생성
  - Token에 권한(scope) 부여

✅ 사용자만 할 수 있는 것:
  - GitHub 로그인 (사용자 인증)
  - Settings → Developer settings → Personal access tokens
  - Token 생성 및 scope 선택 (actions)
```

**왜 자동화 불가?**
- GitHub PAT는 **사용자의 GitHub 계정 전체 권한**을 가짐
- 보안상 사용자 본인만 생성 가능
- 2FA(Two-Factor Authentication) 필요할 수 있음

#### 2. **cron-job.org 계정 생성**
```
❌ Claude Code가 할 수 없는 것:
  - 외부 서비스에 계정 등록
  - 이메일 인증 완료
  - 로그인 세션 유지

✅ 사용자만 할 수 있는 것:
  - cron-job.org 회원 가입
  - 이메일 인증 완료
  - 대시보드 접속
```

#### 3. **Cron Job 설정**
```
❌ Claude Code가 할 수 없는 것:
  - cron-job.org UI에 로그인
  - Cron job 생성 양식 작성
  - GitHub PAT를 cron-job.org에 입력

✅ 사용자만 할 수 있는 것:
  - 웹 브라우저로 cron-job.org 접속
  - "Create cronjob" 버튼 클릭
  - URL, Headers, Schedule 설정
  - GitHub PAT를 Authorization header에 입력
```

### 대안: **스크립트로 일부 자동화 가능**

cron-job.org API를 사용하면 일부 자동화가 가능하지만, **여전히 사용자의 cron-job.org API key가 필요합니다**:

```bash
# cron-job.org API 사용 예시 (사용자 API key 필요)
curl -X POST "https://api.cron-job.org/jobs" \
  -H "Authorization: Bearer YOUR_CRONJOB_ORG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "url": "https://api.github.com/repos/moonkaicuzui/qip-dashboard/actions/workflows/auto-update-enhanced.yml/dispatches",
      "enabled": true,
      "schedule": {
        "minutes": [0, 30]
      }
    }
  }'
```

**결론**: 초기 설정은 사용자가 15분 정도 투자하여 수동으로 해야 합니다.

---

## 질문 2: "Run workflow" 버튼은 누가 사용할 수 있나요?

### 답변: **GitHub Repository Collaborator with Write Access만 가능**

대시보드에 비밀번호로 접속한 일반 사용자는 **사용할 수 없습니다**.

### 권한 구조:

#### ❌ **사용 불가능한 사람들**:
```
1. 대시보드 비밀번호만 아는 일반 직원
   - 권한: 대시보드 웹 페이지 조회만 가능
   - 제한: GitHub repository 접근 불가

2. GitHub 계정은 있지만 Repository 권한이 없는 사람
   - 권한: GitHub에 로그인 가능
   - 제한: "Run workflow" 버튼이 보이지 않음

3. Repository Read 권한만 있는 사람
   - 권한: GitHub repository 코드 조회 가능
   - 제한: "Run workflow" 버튼 비활성화
```

#### ✅ **사용 가능한 사람들**:
```
1. Repository Owner (moonkaicuzui)
   - 권한: 모든 권한 보유
   - 가능: Run workflow, Push, Settings 변경 등

2. Repository Collaborator with Write Access
   - 권한: Repository 관리자가 부여한 Write 권한
   - 가능: Run workflow, Push, Pull request 등
   - 추가 방법: Settings → Collaborators → Add people
```

### 실제 시나리오:

#### **시나리오 1: 일반 직원이 최신 데이터 원함**
```
문제:
  - 직원이 대시보드에서 오래된 데이터를 발견
  - "최신 데이터로 업데이트" 버튼 클릭
  - GitHub Actions 페이지로 이동
  - "Run workflow" 버튼이 보이지 않거나 비활성화됨

해결 방법:
  1. 외부 Cron 서비스(cron-job.org) 사용 → 자동 업데이트
  2. Repository 관리자에게 요청 (전화, 이메일, Slack 등)
  3. Write access 권한 부여 받기 (보안 고려 필요)
```

#### **시나리오 2: 관리자가 즉시 업데이트 원함**
```
방법:
  1. GitHub repository 페이지 접속
  2. Actions 탭 클릭
  3. "Enhanced Auto Update Dashboard" workflow 선택
  4. "Run workflow" 버튼 클릭
  5. Branch: main 선택
  6. "Run workflow" 녹색 버튼 클릭
  7. 5-10분 후 대시보드 새로고침
```

### 권한 부여 방법:

#### **옵션 1: Collaborator 추가 (권장하지 않음)**
```
장점:
  ✅ 해당 직원이 직접 "Run workflow" 실행 가능
  ✅ 코드 수정 및 Push 가능

단점:
  ⚠️ Repository 전체에 대한 Write 권한 부여
  ⚠️ 실수로 코드 삭제 또는 잘못된 수정 가능
  ⚠️ 보안 위험 (민감한 설정 파일 접근 가능)

적합한 대상:
  - IT 팀원
  - 기술 관리자
  - DevOps 엔지니어
```

#### **옵션 2: 외부 Cron 서비스 사용 (권장)**
```
장점:
  ✅ 자동화 (30분마다 자동 실행)
  ✅ 직원들이 수동 트리거 불필요
  ✅ Repository 권한 불필요
  ✅ 보안 위험 최소화

단점:
  ⚠️ 초기 설정 15분 필요
  ⚠️ 외부 서비스 의존성

적합한 상황:
  - 대부분의 경우 (가장 권장)
  - 직원들이 기술적 배경이 없을 때
  - 보안을 중요시할 때
```

#### **옵션 3: GitHub Organization 사용 (엔터프라이즈)**
```
방법:
  1. GitHub Organization 생성 (무료 또는 유료)
  2. Repository를 Organization으로 이전
  3. Team 생성 (예: "Dashboard Admins")
  4. Team에 필요한 직원 추가
  5. Team에 Actions 실행 권한만 부여

장점:
  ✅ 세밀한 권한 관리 가능
  ✅ Actions 실행 권한만 부여 (코드 수정 불가)
  ✅ 여러 관리자 관리 용이

단점:
  ⚠️ GitHub Organization 설정 필요 (복잡)
  ⚠️ 무료 플랜에서는 제한적
  ⚠️ 엔터프라이즈 요금제 필요할 수 있음 (월 $4/user)

적합한 상황:
  - 대규모 조직 (직원 50명 이상)
  - 여러 관리자 필요
  - 세밀한 권한 관리 필요
```

---

## 권장 솔루션 (우선순위 순)

### 1. **외부 Cron 서비스 (cron-job.org)** ✅ **최우선 권장**

**설정 시간**: 15분 1회
**유지 비용**: $0
**보안**: 높음 (Repository 권한 불필요)
**자동화**: 완전 자동 (30분마다)

**적합한 경우**:
- 대부분의 경우 (90% 이상)
- 직원들이 기술적 배경 없음
- 자동 업데이트를 원함
- 보안을 중요시함

**설정 가이드**: `docs/EXTERNAL_CRON_SETUP.md`

---

### 2. **선별적 Collaborator 추가** ⚠️ **신중하게 사용**

**설정 시간**: 5분 (초대 후 수락)
**보안**: 중간 (Write 권한 필요)
**자동화**: 없음 (수동 트리거)

**적합한 경우**:
- IT 팀원 또는 기술 관리자만
- 즉시 업데이트가 가끔 필요할 때
- 외부 서비스 사용 불가능할 때

**주의사항**:
- 신뢰할 수 있는 사람만 추가
- GitHub 계정 보안 강화 (2FA 필수)
- 정기적으로 권한 검토

---

### 3. **GitHub Organization + Teams** 🏢 **엔터프라이즈 전용**

**설정 시간**: 1-2시간 (초기 설정)
**비용**: $4/user/month (유료 플랜)
**보안**: 매우 높음 (세밀한 권한 관리)
**자동화**: 설정 가능

**적합한 경우**:
- 대규모 조직 (50명 이상)
- 여러 팀/부서 관리 필요
- 엔터프라이즈급 보안 요구
- 예산이 있음

---

## 현재 시스템 권한 구조

```
┌─────────────────────────────────────────┐
│  웹 대시보드 (Public)                    │
│  - URL: https://moonkaicuzui.github.io/... │
│  - 인증: 비밀번호 (auth.html)            │
│  - 접근: 비밀번호 아는 모든 직원         │
│  - 권한: 조회만 가능                     │
└─────────────────────────────────────────┘
              ↓ (조회만)
┌─────────────────────────────────────────┐
│  GitHub Pages (Public Hosting)          │
│  - HTML, CSS, JS 파일 서빙              │
│  - 자동 배포 (Push 후 1-2분)            │
└─────────────────────────────────────────┘
              ↑ (배포)
┌─────────────────────────────────────────┐
│  GitHub Repository (Private)            │
│  - Owner: moonkaicuzui                  │
│  - Collaborators: Write access 필요     │
│  - "Run workflow": Write access만 가능  │
└─────────────────────────────────────────┘
              ↑ (트리거)
┌─────────────────────────────────────────┐
│  GitHub Actions (Automation)            │
│  - Cron: */30 * * * * (불안정)          │
│  - Manual: workflow_dispatch (제한적)   │
└─────────────────────────────────────────┘
              ↑ (안정적 트리거)
┌─────────────────────────────────────────┐
│  외부 Cron 서비스 (cron-job.org)        │
│  - 30분마다 정확한 실행                 │
│  - GitHub API 호출                      │
│  - Repository 권한 불필요 (PAT 사용)    │
└─────────────────────────────────────────┘
```

---

## 보안 베스트 프랙티스

### GitHub Personal Access Token (PAT)

```yaml
권장 설정:
  Expiration: 90 days (정기적으로 갱신)
  Scopes:
    - actions (GitHub Actions 트리거만)

금지 사항:
  ❌ repo (전체 repository 접근)
  ❌ admin:org (조직 관리)
  ❌ 무제한 만료 (never expire)

보관:
  ✅ 비밀번호 관리자 (1Password, LastPass)
  ✅ GitHub Secrets (다른 Actions에서 사용 시)
  ❌ 코드에 하드코딩
  ❌ 이메일, 메신저로 공유
```

### Repository Collaborator 관리

```yaml
주기적 검토:
  - 분기별 권한 감사
  - 퇴사자 즉시 제거
  - 불필요한 권한 강등

권한 부여 기준:
  ✅ 업무상 필요성 명확
  ✅ GitHub 계정 2FA 활성화
  ✅ 기술적 이해도 충분

  ❌ "편의상" 부여
  ❌ 임시 계약직
  ❌ 외부 협력사
```

---

## 요약

### 질문 1: 외부 Cron 자동 설정?
**답변**: ❌ 불가능 (보안상 사용자만 가능)
- GitHub PAT 생성: 사용자 인증 필요
- cron-job.org 계정: 이메일 인증 필요
- **해결**: 15분 투자하여 1회 수동 설정

### 질문 2: "Run workflow" 누가 사용?
**답변**: ✅ Repository Collaborator (Write Access)
- 일반 직원: ❌ 사용 불가
- Repository Owner: ✅ 사용 가능
- Write 권한 Collaborator: ✅ 사용 가능
- **권장**: 외부 Cron 서비스로 자동화

---

**Last Updated**: 2025-11-25
**Related Docs**: `docs/EXTERNAL_CRON_SETUP.md`
**Security Review**: 2025-11-25
