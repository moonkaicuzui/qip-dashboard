# 🚨 긴급 보안 조치 필요

## 발견된 문제
`credentials/service-account-key.json`이 GitHub public 저장소에 노출됨 (2025-08-23 커밋)

## 즉시 조치해야 할 사항

### 1단계: Google Cloud Console에서 키 폐기
1. https://console.cloud.google.com/iam-admin/serviceaccounts 접속
2. 해당 Service Account 선택
3. "키" 탭에서 노출된 키 삭제
4. 새 키 생성 및 안전한 위치에 저장

### 2단계: Git 히스토리에서 완전히 제거
```bash
# BFG Repo-Cleaner 사용 (권장)
brew install bfg  # Mac
bfg --delete-files service-account-key.json
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 또는 git filter-branch (수동)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch credentials/service-account-key.json' \
  --prune-empty --tag-name-filter cat -- --all
```

### 3단계: Force push (주의!)
```bash
git push origin --force --all
git push origin --force --tags
```

### 4단계: .gitignore 확인
이미 설정되어 있음:
- Line 25: `service_account_key.json`
- Line 26: `config_files/service_account_key.json`

## 참고
- 이 파일은 절대 커밋되어서는 안됩니다
- GitHub Secrets에 저장하고 CI/CD에서만 사용해야 합니다
