# 👥 QIP 인센티브 대시보드 사용자 접속 가이드

## 📊 시스템 구성 (사용자 관점)

```
                    🌐 인터넷
                         ↓
        ┌────────────────┴────────────────┐
        │                                 │
   👤 일반 직원                      👨‍💼 관리자
        │                                 │
        ↓                                 ↓
┌─────────────────┐              ┌─────────────────┐
│  GitHub Pages   │              │  GitHub Pages   │
│  (대시보드 조회) │              │  (시스템 관리)   │
└─────────────────┘              └─────────────────┘
        │                                 │
        ↓                                 ↓
  selector.html                     admin.html
  비밀번호: qip                      비밀번호: hwk
        │                                 │
        ↓                                 ↓
  월별 대시보드                     Vercel 연동
  (조회만 가능)                     (재계산 실행 가능)
```

---

## 🔐 접속 방법

### 1️⃣ 일반 직원 (대시보드 조회)

**접속 URL**:
```
https://moonkaicuzui.github.io/qip-dashboard/
```

**접속 흐름**:
```
1. 위 URL 접속
   ↓
2. 자동으로 selector.html로 리다이렉트
   ↓
3. 비밀번호 입력: qip
   ↓
4. 월 선택 (7월, 8월, 9월, 10월, 11월)
   ↓
5. 인센티브 대시보드 확인
   - 개인 인센티브 금액
   - 10가지 조건 충족 여부
   - 팀 통계
```

**권한**:
- ✅ 대시보드 조회
- ✅ 월별 전환
- ❌ 데이터 수정 불가
- ❌ 재계산 불가

---

### 2️⃣ 관리자 (시스템 관리)

**접속 URL**:
```
https://moonkaicuzui.github.io/qip-dashboard/admin.html
```
⚠️ **중요**: 이 URL은 직접 입력해야 합니다 (첫 화면에 링크 없음!)

**접속 흐름**:
```
1. admin.html URL 직접 입력
   ↓
2. 비밀번호 입력: hwk
   ↓
3. 관리자 대시보드 표시
   ↓
4. Quick Actions 사용 가능
   - 🔄 Run Recalculation Now
   - 📊 Check Execution Status
```

**권한**:
- ✅ 시스템 상태 모니터링
- ✅ 인센티브 재계산 실행
- ✅ GitHub Actions 워크플로우 트리거
- ✅ 실시간 로그 확인

---

## 🚨 현재 상태: 관리자 링크 없음!

**문제점**:
- auth.html, selector.html, index.html 어디에도 admin.html 링크가 없음
- 관리자는 URL을 **외워서** 직접 입력해야 함

**해결 방안** (선택 가능):

### 옵션 1: 숨겨진 링크 추가
auth.html 하단에 작은 링크 추가:
```html
<a href="admin.html" style="font-size: 0.7rem; color: #999;">Admin</a>
```

### 옵션 2: 특정 키 조합
Ctrl + Shift + A 누르면 admin.html로 이동:
```javascript
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey && e.key === 'A') {
    window.location.href = 'admin.html';
  }
});
```

### 옵션 3: 현재대로 유지
- URL 직접 입력 (보안상 더 안전)
- 관리자에게 북마크 전달

---

## 📱 모바일 접속

### 일반 직원
```
1. 스마트폰 브라우저로 접속
2. https://moonkaicuzui.github.io/qip-dashboard/
3. 비밀번호: qip
4. 월 선택 → 대시보드 확인
```

### 관리자
```
1. 스마트폰 브라우저로 접속
2. https://moonkaicuzui.github.io/qip-dashboard/admin.html
   (직접 입력 또는 북마크)
3. 비밀번호: hwk
4. 재계산 실행 가능
```

---

## 🔄 Vercel의 역할

**Vercel은 대시보드가 아닙니다!**

Vercel은 **백엔드 서버**로:
- admin.html의 "Run Recalculation Now" 버튼 작동
- GitHub Token 안전하게 보관
- GitHub Actions 워크플로우 트리거

**실제 대시보드는 GitHub Pages**:
- https://moonkaicuzui.github.io/qip-dashboard/
- HTML 파일 호스팅
- 정적 웹사이트

**관계**:
```
GitHub Pages (프론트엔드)
    ↓ API 호출
Vercel (백엔드)
    ↓ GitHub API 호출
GitHub Actions (자동화)
    ↓ 결과 저장
GitHub Pages (업데이트된 대시보드)
```

---

## 📊 사용자 시나리오

### 시나리오 1: 직원이 자기 인센티브 확인
```
1. 스마트폰으로 https://moonkaicuzui.github.io/qip-dashboard/ 접속
2. 비밀번호: qip
3. 11월 선택
4. 자기 이름 검색
5. 인센티브 금액 + 조건 확인
```

### 시나리오 2: 관리자가 데이터 업데이트 후 재계산
```
1. Google Drive에 새 CSV 업로드
2. PC에서 https://moonkaicuzui.github.io/qip-dashboard/admin.html 접속
3. 비밀번호: hwk
4. "Run Recalculation Now" 클릭
5. 5-10분 대기
6. 대시보드 자동 업데이트 확인
```

### 시나리오 3: 매시간 자동 업데이트
```
1. (관리자 작업 없음)
2. GitHub Actions 자동 실행 (매시간)
3. Google Drive 동기화
4. 변경 감지 시 자동 재계산
5. 대시보드 자동 갱신
```

---

## 🔐 보안 요약

| URL | 비밀번호 | 세션 | 권한 |
|-----|---------|------|------|
| `/` | qip | 30분 | 조회만 |
| `/admin.html` | hwk | 60분 | 관리 + 재계산 |

**비밀번호 변경 방법**:
- auth.html: Line ~250
- admin.html: Line 416
- SHA-256 해시로 저장됨

---

## ❓ FAQ

**Q: 관리자 페이지는 어디 있나요?**
A: https://moonkaicuzui.github.io/qip-dashboard/admin.html (직접 입력)

**Q: 일반 직원도 재계산할 수 있나요?**
A: 아니요. admin.html 비밀번호(hwk) 필요

**Q: Vercel이 뭔가요?**
A: 백엔드 서버. Admin 페이지의 재계산 버튼 작동시킴

**Q: 대시보드는 자동 업데이트되나요?**
A: 네. 매시간 자동 확인, 변경 시 자동 재계산

**Q: 모바일에서도 되나요?**
A: 네. 모든 기능 모바일 최적화됨
