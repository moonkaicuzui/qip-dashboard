# 🚀 Vercel Serverless Function 배포 가이드

이 가이드는 Admin 페이지의 "Run Recalculation Now" 버튼이 **진짜 자동으로 작동**하도록 Vercel을 설정하는 방법을 안내합니다.

---

## 📋 사전 준비

### 1. GitHub Personal Access Token 생성

GitHub Token은 **서버에서만 사용**되므로 절대 노출되지 않습니다.

1. GitHub 접속: https://github.com/settings/tokens
2. **"Generate new token"** → **"Generate new token (classic)"** 클릭
3. Note: `QIP Dashboard Workflow Trigger`
4. Expiration: **No expiration** (또는 1년)
5. 권한 선택:
   - ✅ `repo` (전체 체크)
   - ✅ `workflow` (체크)
6. **"Generate token"** 클릭
7. ⚠️ **토큰을 복사해서 안전한 곳에 저장** (다시 볼 수 없음!)

**생성된 토큰 예시**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🔧 Vercel 배포 단계

### Step 1: Vercel 계정 생성

1. https://vercel.com 접속
2. **"Sign Up"** 클릭
3. **"Continue with GitHub"** 선택
4. GitHub 계정으로 로그인

---

### Step 2: 프로젝트 Import

1. Vercel 대시보드에서 **"Add New..."** → **"Project"** 클릭
2. GitHub에서 `qip-dashboard` 저장소 선택
3. **"Import"** 클릭

---

### Step 3: 환경 변수 설정 (중요!)

**프로젝트 설정 화면에서:**

1. **"Environment Variables"** 섹션 찾기
2. 다음 두 개의 환경변수 추가:

#### 환경변수 1: GITHUB_TOKEN
- **Name**: `GITHUB_TOKEN`
- **Value**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (Step 1에서 생성한 토큰)
- **Environment**: Production, Preview, Development (모두 체크)

#### 환경변수 2: ADMIN_PASSWORD_HASH
- **Name**: `ADMIN_PASSWORD_HASH`
- **Value**: `85a84e034c5b9248758c500f6c1f2b8bb99c9818ce7902ee5bc702c07ecda5a0`
- **Environment**: Production, Preview, Development (모두 체크)

**⚠️ 중요**: 환경변수 값에 공백이나 따옴표가 없어야 합니다!

---

### Step 4: 배포

1. **"Deploy"** 버튼 클릭
2. 약 1-2분 대기
3. 배포 완료 시 **"Visit"** 버튼 클릭

---

### Step 5: 도메인 확인

배포 완료 후 Vercel이 자동으로 도메인을 생성합니다:
- **예시**: `qip-dashboard-xxx.vercel.app`

이 도메인을 기억하세요! (또는 Vercel 대시보드에서 확인 가능)

---

### Step 6: admin.html 업데이트 (선택사항)

**현재 설정**으로도 작동하지만, Vercel 도메인을 명시적으로 설정하려면:

1. `docs/admin.html` 파일 열기
2. 420-425번 줄 근처 찾기:
```javascript
const API_ENDPOINT = window.location.hostname === 'localhost'
    ? 'http://localhost:3000/api/trigger-workflow'
    : '/api/trigger-workflow';
```

3. 다음과 같이 수정 (선택사항):
```javascript
const API_ENDPOINT = 'https://your-project.vercel.app/api/trigger-workflow';
```

4. `your-project.vercel.app`를 실제 Vercel 도메인으로 변경

**참고**: 이 단계는 선택사항입니다. 현재 설정으로도 정상 작동합니다.

---

## ✅ 테스트

### 1. Admin 페이지 접속
```
https://moonkaicuzui.github.io/qip-dashboard/admin.html
```

### 2. 로그인
- Password: `hwk`

### 3. "Run Recalculation Now" 버튼 클릭

### 4. 성공 확인
Activity Log에 다음과 같은 메시지가 표시되어야 합니다:
```
[시간] Requesting recalculation...
[시간] ✅ Recalculation started! GitHub Actions running...
[시간] Triggered at: 2025-11-15T...
[시간] Downloading CSV...
```

---

## 🔍 문제 해결

### ❌ "Network error" 또는 "Server error" 발생

**원인**: 환경변수가 제대로 설정되지 않았거나 GitHub Token이 잘못됨

**해결 방법**:
1. Vercel 대시보드 → 프로젝트 선택
2. **"Settings"** → **"Environment Variables"** 확인
3. `GITHUB_TOKEN`과 `ADMIN_PASSWORD_HASH` 값 재확인
4. 값이 정확하지 않으면 수정 후 **"Redeploy"**

---

### ❌ "Authentication failed" 발생

**원인**: `ADMIN_PASSWORD_HASH`가 잘못됨

**해결 방법**:
1. 환경변수 값이 정확한지 확인:
   ```
   85a84e034c5b9248758c500f6c1f2b8bb99c9818ce7902ee5bc702c07ecda5a0
   ```
2. 공백이나 따옴표가 없는지 확인
3. Vercel에서 환경변수 수정 후 **"Redeploy"**

---

### ❌ "GitHub API error" 발생

**원인**: GitHub Token 권한이 부족하거나 만료됨

**해결 방법**:
1. GitHub Token 재생성 (권한: `repo`, `workflow`)
2. Vercel 환경변수 `GITHUB_TOKEN` 업데이트
3. **"Redeploy"** 클릭

---

## 🎉 성공!

이제 Admin 페이지에서 버튼 클릭만으로 **즉시 재계산**이 시작됩니다!

**작동 방식**:
1. 버튼 클릭 → Vercel Serverless Function 호출
2. Vercel Function → GitHub Token으로 API 인증
3. GitHub Actions 워크플로우 즉시 실행
4. 5-10분 후 대시보드 업데이트 완료

**보안**:
- ✅ GitHub Token은 Vercel 서버에만 저장 (절대 노출되지 않음)
- ✅ Admin Password Hash로 이중 보안
- ✅ CORS 설정으로 허가된 도메인만 접근 가능

---

## 📚 추가 정보

### Vercel 로그 확인
- Vercel 대시보드 → 프로젝트 → **"Deployments"** → 최신 배포 클릭
- **"Functions"** 탭에서 API 호출 로그 확인

### 환경변수 변경 시
- Vercel 대시보드 → **"Settings"** → **"Environment Variables"**
- 변경 후 반드시 **"Redeploy"** 필요

### 비용
- Vercel **무료 플랜**: 월 100GB 대역폭, 100,000 함수 호출
- QIP Dashboard: 월 예상 사용량 < 1GB (완전 무료)

---

**문제가 해결되지 않으면?**
- Vercel 로그 확인: https://vercel.com/[your-username]/qip-dashboard/deployments
- GitHub Actions 로그 확인: https://github.com/moonkaicuzui/qip-dashboard/actions
