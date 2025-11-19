# 🔒 QIP Dashboard 보안 작업 이력

## 📅 타임라인

### 2025-08-21 ~ 2025-08-23 ❌ **보안 사고**
**커밋**: `ecb0e34`, `95d525f`
- `credentials/service-account-key.json` **public 저장소에 커밋됨**
- Google Drive API Service Account 인증키 노출
- **영향**: 무단 Google Drive 접근 가능
- **상태**: ⚠️ **Git 히스토리에 여전히 존재** (추적만 해제됨)

---

### 2025-11-15 09:18 ✅ **대시보드 접근 보안 강화**
**커밋**: `10ebad1` - Comprehensive security enhancement

#### 구현된 보안 기능
1. **인증 시스템** (`docs/auth.html`)
   - SHA-256 비밀번호 해싱
   - 30분 세션 타임아웃
   - Brute-force 보호 (5회 시도, 5분 잠금)
   - sessionStorage 기반 세션 관리

2. **검색 엔진 차단**
   - `docs/robots.txt` 추가 (모든 크롤러 차단)
   - 모든 페이지에 noindex/nofollow 메타 태그

3. **접근 제어**
   - 모든 페이지에서 세션 검증
   - 미인증 시 auth.html로 자동 리다이렉트
   - 1분마다 세션 유효성 재검증

4. **데이터 보호**
   - 우클릭 방지
   - 복사 감지 및 경고
   - Ctrl+S/Ctrl+P 차단 (저장/인쇄 방지)
   - 개발자 도구 감지 및 경고

**기본 비밀번호**: `admin`
**SHA-256 해시**: `8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918`

---

### 2025-11-15 09:30 🔐 **비밀번호 변경**
**커밋**: `ad5fcfd` - Enhanced security

- **비밀번호 변경**: `admin` → `qip`
- **새 SHA-256 해시**: `19e49d5a0a97333a704097653034a76eaddb6cff5aeff18e4efec4c871d4caae`
- 최소한의 범용 디자인 적용 (기호만 사용, 언어 무관)

---

### 2025-11-17 09:40 🧹 **Git 저장소 보안 정리**
**커밋**: `36a4ea9` - 보안 개선 및 Git 저장소 정리

#### 조치 사항
1. **민감 파일 추적 제거**
   - `credentials/service-account-key.json` Git 추적 해제
   - `.gitignore` 업데이트 (`.cache/`, `logs/` 추가)
   - 110개 캐시/로그 파일 제거

2. **보안 가이드 문서 생성**
   - `SECURITY_URGENT.md` 추가
   - Google Cloud 키 폐기 및 Git 히스토리 정리 가이드

3. **제한 사항**
   - ⚠️ Git 추적만 해제, **히스토리에는 여전히 존재**
   - 완전 제거를 위해 BFG Repo-Cleaner 필요

---

## 🚨 현재 보안 상태

### ✅ 보호됨
- 대시보드 접근: 비밀번호 인증 (`qip`)
- 검색 엔진: 완전 차단
- 데이터 보호: 복사/저장/인쇄 방지
- 세션 관리: 30분 타임아웃

### ⚠️ 미해결
- **Google Service Account 키**: Git 히스토리에 남아있음
  - 2025-08-23 커밋 (`95d525f`)에서 public 저장소에 노출
  - 현재 추적만 해제된 상태 (파일 접근 불가, 히스토리 접근 가능)

---

## 📋 후속 조치 필요

### 최우선 (CRITICAL)
1. **Google Cloud Console에서 키 폐기**
   - https://console.cloud.google.com/iam-admin/serviceaccounts
   - 노출된 Service Account 키 삭제
   - 새 키 생성 → GitHub Secrets에 저장

2. **Git 히스토리에서 완전 제거**
   ```bash
   # BFG Repo-Cleaner 사용 (권장)
   brew install bfg
   bfg --delete-files service-account-key.json
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push origin --force --all
   ```

### 권장 (HIGH)
3. **비밀번호 변경**
   - 현재: `qip` (팀 내부용)
   - 권장: 강력한 비밀번호로 변경
   - 파일: `docs/auth.html` Line ~250

4. **GitHub Secrets 설정**
   - Repository Settings → Secrets → Actions
   - `GOOGLE_CREDENTIALS` 추가 (새 Service Account 키)
   - GitHub Actions에서만 사용

---

## 📖 참고 문서
- `SECURITY_URGENT.md` - 긴급 조치 가이드
- `docs/auth.html` - 인증 시스템
- `docs/robots.txt` - 검색 엔진 차단
