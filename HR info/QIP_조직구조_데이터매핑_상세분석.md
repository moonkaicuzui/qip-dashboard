# QIP 조직 구조 데이터 매핑 상세 분석 보고서
*작성일: 2025-08-28*
*분석 기준: team_structure.json 파일 (/Users/ksmoon/Downloads/5pr back to basic/dashboard/team_structure.json)*

## 📊 데이터 구조 및 매핑 관계

### 핵심 데이터 파일 구조
1. **ATTENDANCE.xlsx**: 출결 데이터
   - `ID No` (int64): 직원 고유 ID
   - `Department` (object): PRGMRQI1 또는 PRGOFQI1
   - `Last name` (object): 직원 이름

2. **OUTPUT_INCENTIVE.xlsx**: 직급 및 팀 정보
   - `Employee No` (int64): 직원 고유 ID (= ATTENDANCE의 ID No)
   - `QIP POSITION 1ST NAME`: 1차 직급명
   - `QIP POSITION 2ND NAME`: 2차 직급명  
   - `QIP POSITION 3RD NAME`: 3차 직급명
   - `FINAL QIP POSITION NAME CODE`: 최종 직급 코드
   - `ROLE TYPE STD`: TYPE-1, TYPE-2, TYPE-3

3. **team_structure.json**: 팀 매핑 규칙
   - `position_1st`: 1차 직급 → 팀 매핑
   - `position_2nd`: 2차 직급 → 팀 매핑
   - `position_3rd`: 3차 직급 → 팀 매핑
   - `final_code`: 최종 코드 → 팀 매핑
   - `team_name`: 소속 팀명
   - `role_category`: 역할 카테고리

---

## 1. 팀 매핑 규칙 (team_name 결정 로직)

### 1.1 Assembly Team (조립팀) - 145명
**매핑 규칙**: 
```json
{
  "position_1st": "ASSEMBLY INSPECTOR" AND
  "position_3rd": contains("ASSEMBLY LINE") 
  → "team_name": "assembly"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| ASSEMBLY INSPECTOR | SHOES INSPECTOR | ASSEMBLY LINE TQC | A1A | 91명 | assembly |
| ASSEMBLY INSPECTOR | SHOES INSPECTOR | ASSEMBLY LINE RQC | A1B | 23명 | assembly |
| ASSEMBLY INSPECTOR | QIP PACKING TEAM | ASSEMBLY LINE PO COMPLETION QUALITY | A4 | 9명 | assembly |
| (V) SUPERVISOR | (V) SUPERVISOR | 1 ASSEMBLY BUILDING QUALITY IN CHARGE | GG | 1명 | assembly |
| (V) SUPERVISOR | (V) SUPERVISOR | 2 ASSEMBLY BUILDING QUALITY IN CHARGE | G | 2명 | assembly |
| A.MANAGER | A.MANAGER | ALL ASSEMBLY QUALITY IN CHARGE | H | 1명 | assembly |
| LINE LEADER | LINE LEADER | 12 ASSEMBLY LINE QUALITY IN CHARGE | E | 8명 | assembly |
| CUTTING | CUTTING | 1 ASSEMBLY BUILDING QUALITY IN CHARGE | F | 2명 | assembly |

### 1.2 Stitching Team (재봉팀) - 99명
**매핑 규칙**:
```json
{
  "position_1st": "STITCHING INSPECTOR" 
  → "team_name": "stitching"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| STITCHING INSPECTOR | STITCHING INSPECTOR | STITCHING LINE TQC | XY1 | 67명 | stitching |
| STITCHING INSPECTOR | STITCHING INSPECTOR | STITCHING LINE RQC | XY2 | 21명 | stitching |
| STITCHING INSPECTOR | STITCHING INSPECTOR | CUTTING TQC | XY3 | 3명 | stitching |
| STITCHING INSPECTOR | HAPPO MTL TEAM LEADER | STITCHING QUALITY ANALYST | XY4 | 4명 | stitching |
| (V) SUPERVISOR | (V) SUPERVISOR | 1 STITCHING BUILDING QUALITY IN CHARGE | GGG | 4명 | stitching |

### 1.3 New Member Team (신입팀) - 44명
**매핑 규칙**:
```json
{
  "position_1st": "NEW QIP MEMBER"
  → "team_name": "new member"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| NEW QIP MEMBER | NEW QIP MEMBER | NEW QIP MEMBER | 0 | 44명 | new member |

### 1.4 Bottom Team (밑창팀) - 42명
**매핑 규칙**:
```json
{
  "position_1st": "BOTTOM INSPECTOR"
  → "team_name": "bottom"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| BOTTOM INSPECTOR | BOTTOM INSPECTOR | BOTTOM INSPECTION TQC | BTS2B | 31명 | bottom |
| BOTTOM INSPECTOR | BOTTOM INSPECTOR | BOTTOM INSPECTION RQC | BTS2A | 5명 | bottom |
| BOTTOM INSPECTOR | BOTTOM INSPECTOR | BOTTOM PU ROOM CFA | BTS2C | 2명 | bottom |
| MODEL MASTER | MODEL MASTER | MODEL MASTER | D | 2명 | bottom |
| LINE LEADER | LINE LEADER | BOTTOM LINE QUALITY IN CHARGE | BTS1 | 2명 | bottom |

### 1.5 MTL Team (자재팀) - 33명
**매핑 규칙**:
```json
{
  "position_1st": "MTL INSPECTOR" OR
  "position_3rd": contains("MTL")
  → "team_name": "MTL"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| MTL INSPECTOR | MTL INSPECTOR | TEXTILE TQC | NK1 | 10명 | MTL |
| MTL INSPECTOR | MTL INSPECTOR | SUBSI TQC | NK2 | 9명 | MTL |
| MTL INSPECTOR | MTL INSPECTOR | LEATHER TQC | NK3 | 8명 | MTL |
| MTL INSPECTOR | MTL INSPECTOR | HP MATERIAL TQC | NK4 | 3명 | MTL |
| MTL INSPECTOR | MTL INSPECTOR | CHEMICAL TQC | NK5 | 2명 | MTL |
| GROUP LEADER | HAPPO MTL TEAM LEADER | HAPPO MTL TEAM LEADER | OFG | 1명 | MTL |

### 1.6 OSC Team (아웃소싱팀) - 26명
**매핑 규칙**:
```json
{
  "position_1st": "OSC INSPECTOR"
  → "team_name": "OSC"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| OSC INSPECTOR | OSC INSPECTOR | INCOMING WH OSC INSPECTION TQC | OS1 | 11명 | OSC |
| OSC INSPECTOR | OSC INSPECTOR | INHOUSE HF/NO-SEW INSPECTION TQC | OS2 | 10명 | OSC |
| OSC INSPECTOR | OSC INSPECTOR | OUTSOURCE AND CUT PART TQC | OS3 | 3명 | OSC |
| OSC INSPECTOR | OSC INSPECTOR | OSC RQC | OS4 | 2명 | OSC |

### 1.7 AQL Team (품질검사팀) - 24명
**매핑 규칙**:
```json
{
  "position_1st": "AQL INSPECTOR" AND
  "position_3rd": NOT contains("REPACKING")
  → "team_name": "AQL"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| AQL INSPECTOR | AQL INSPECTOR | AQL INSPECTOR | B | 6명 | AQL |
| AQL INSPECTOR | QIP PACKING TEAM | AQL ROOM PACKING TQC | B1 | 6명 | AQL |
| AQL INSPECTOR | QIP PACKING TEAM | FG WH INPUT-OUTPUT CARTON TQC | B2 | 6명 | AQL |
| AQL INSPECTOR | SHOES INSPECTOR | AFTER UVC LINE CFA | B3 | 3명 | AQL |
| AQL INSPECTOR | UPPER INSPECTOR | SPECIAL CFA | B4 | 3명 | AQL |

### 1.8 Repacking Team (재포장팀) - 24명
**매핑 규칙**:
```json
{
  "position_3rd": contains("REPACKING")
  → "team_name": "Repacking"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| ASSEMBLY INSPECTOR | QIP PACKING TEAM | REPACKING LINE PACKING TQC | A2 | 9명 | Repacking |
| ASSEMBLY INSPECTOR | QIP PACKING TEAM | REPACKING LINE REPAIRING TQC | A3 | 6명 | Repacking |
| ASSEMBLY INSPECTOR | SHOES INSPECTOR | REPACKING LINE TQC | A1C | 3명 | Repacking |
| AQL INSPECTOR | QIP PACKING TEAM | REPACKING ROOM CFA | B5 | 3명 | Repacking |
| AQL INSPECTOR | QIP PACKING TEAM | REPACKING LINE QC LEADER | B6 | 3명 | Repacking |

### 1.9 AUDIT & TRAINING TEAM (감사/교육팀) - 8명
**매핑 규칙**:
```json
{
  "position_1st": "AUDIT & TRAINING TEAM"
  → "team_name": "AUDIT & TRAINING TEAM"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| AUDIT & TRAINING TEAM | AUDIT & TRAINING TEAM | AUDITOR & TRAINER | QA2B | 7명 | AUDIT & TRAINING TEAM |
| AUDIT & TRAINING TEAM | AUDIT & TRAINING TEAM | AUDIT & TRAINING TEAM LEADER | QA2A | 1명 | AUDIT & TRAINING TEAM |

### 1.10 QA Team (품질보증팀) - 8명
**매핑 규칙**:
```json
{
  "position_3rd": contains("QUALITY ANALYST") AND
  NOT contains("STITCHING")
  → "team_name": "QA"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| QC TECHNICAL TEAM | QC TECHNICAL TEAM | QUALITY ANALYST | QA1 | 4명 | QA |
| QC TECHNICAL TEAM | QC TECHNICAL TEAM | SENIOR QUALITY ANALYST | QA1A | 4명 | QA |

### 1.11 Report Team (보고팀) - 3명
**매핑 규칙**:
```json
{
  "position_1st": "GROUP LEADER" AND
  "position_2nd": "REPORT TEAM"
  → "team_name": "report"
}
```

**구체적 매핑**:
| position_1st | position_2nd | position_3rd | final_code | 인원 | team_name |
|-------------|--------------|--------------|------------|------|-----------|
| GROUP LEADER | REPORT TEAM | TEAM OPERATION MANAGEMENT | OF2 | 3명 | report |

### 1.12-1.16 기타 소규모 팀
- **OCPT Team**: 2명 (특수 검사)
- **Scan Pack Team**: 2명 (스캔/포장)
- **Cutting Team**: 3명 (재단)
- **QIP Team**: 1명 (총괄)

---

## 2. 역할 카테고리 매핑 규칙 (role_category 결정 로직)

### 2.1 Management Team (관리팀)
**매핑 규칙**:
```json
{
  "position_1st": IN ["(V) SUPERVISOR", "A.MANAGER", "GROUP LEADER", "LINE LEADER", "CUTTING"]
  → "role_category": "management team"
}
```

### 2.2 TQC (전수 품질 검사)
**매핑 규칙**:
```json
{
  "position_3rd": contains("TQC")
  → "role_category": "TQC"
}
```
- 총 인원: 약 250명 (전체의 54%)

### 2.3 RQC (무작위 품질 검사)
**매핑 규칙**:
```json
{
  "position_3rd": contains("RQC")
  → "role_category": "RQC"
}
```
- 총 인원: 약 50명 (전체의 11%)

### 2.4 CFA (최종 검사)
**매핑 규칙**:
```json
{
  "position_3rd": contains("CFA")
  → "role_category": "CFA"
}
```

### 2.5 LEADER (팀장)
**매핑 규칙**:
```json
{
  "position_3rd": contains("LEADER") AND
  NOT "position_1st": IN ["GROUP LEADER", "LINE LEADER"]
  → "role_category": "LEADER"
}
```

### 2.6 AUDIT & TRAINER (감사/교육담당)
**매핑 규칙**:
```json
{
  "position_3rd": contains("AUDITOR") OR contains("TRAINER")
  → "role_category": "AUDIT & TRAINER"
}
```

### 2.7 Support Team (지원팀)
**매핑 규칙**:
```json
{
  특정 support 관련 직급
  → "role_category": "support team"
}
```

### 2.8 Staff (일반 직원)
**매핑 규칙**:
```json
{
  기본 검사 직원
  → "role_category": "staff"
}
```

### 2.9 New Member (신입)
**매핑 규칙**:
```json
{
  "position_1st": "NEW QIP MEMBER"
  → "role_category": "new member"
}
```

---

## 3. Department 매핑 (ATTENDANCE.xlsx)

### PRGMRQI1 (스탭 및 관리자)
**포함 직급**:
- Management team 전체
- LEADER 직급
- AUDIT & TRAINER
- Support team

### PRGOFQI1 (작업자) - 다수
**포함 직급**:
- TQC 검사원
- RQC 검사원
- CFA 검사원
- New Member
- 일반 Staff

---

## 4. ROLE TYPE STD 매핑 (인센티브 계산)

### TYPE-1 (관리자급)
**매핑 규칙**:
```json
{
  "role_category": "management team" OR
  "position_1st": contains("MANAGER") OR "SUPERVISOR"
  → "ROLE TYPE STD": "TYPE-1"
}
```
- 높은 책임도, 높은 인센티브

### TYPE-2 (중간 관리자 및 숙련 검사원)
**매핑 규칙**:
```json
{
  "role_category": IN ["TQC", "RQC", "LEADER", "AUDIT & TRAINER"]
  → "ROLE TYPE STD": "TYPE-2"
}
```
- 275명 (59.3%)
- 중간 책임도, 중간 인센티브

### TYPE-3 (일반 검사원)
**매핑 규칙**:
```json
{
  "role_category": IN ["staff", "new member", "support team"]
  → "ROLE TYPE STD": "TYPE-3"
}
```
- 기본 책임도, 기본 인센티브

---

## 5. 데이터 조인 방법

### 출결 데이터와 직급 데이터 연결
```python
# ATTENDANCE.xlsx의 ID No와 OUTPUT_INCENTIVE.xlsx의 Employee No 조인
merged_data = pd.merge(
    attendance_df,
    incentive_df,
    left_on='ID No',
    right_on='Employee No',
    how='left'
)

# team_structure.json으로 팀 정보 추가
for row in merged_data:
    position_key = f"{row['QIP POSITION 1ST NAME']}_{row['QIP POSITION 3RD NAME']}"
    team_info = team_structure.get(position_key)
    row['team_name'] = team_info['team_name']
    row['role_category'] = team_info['role_category']
```

---

## 6. 데이터 일관성 체크 포인트

1. **ID 매칭**: ATTENDANCE의 407명 중 OUTPUT_INCENTIVE와 매칭되는 인원 확인
2. **직급 코드 검증**: FINAL QIP POSITION NAME CODE의 고유성 확인
3. **팀 배정 검증**: 모든 직원이 16개 팀 중 하나에 배정되었는지 확인
4. **역할 카테고리 검증**: 9개 카테고리 완전성 확인
5. **ROLE TYPE 검증**: TYPE-1, 2, 3 분류 완전성 확인

---

## 7. 핵심 데이터 관계도

```
ATTENDANCE.xlsx
    ├── ID No ─────────────┐
    ├── Department         │
    └── Last name          │
                          ↓ (JOIN)
OUTPUT_INCENTIVE.xlsx      │
    ├── Employee No ←──────┘
    ├── QIP POSITION 1ST NAME ─┐
    ├── QIP POSITION 2ND NAME  │
    ├── QIP POSITION 3RD NAME  │
    ├── FINAL CODE             │
    └── ROLE TYPE STD          │
                              ↓ (MAPPING)
team_structure.json           │
    ├── position_1st ←─────────┘
    ├── position_2nd
    ├── position_3rd
    ├── final_code
    ├── team_name (결과)
    └── role_category (결과)
```

---

*본 문서는 2025년 8월 28일 기준 QIP 조직 구조의 데이터 매핑 관계를 상세히 분석한 것입니다.*