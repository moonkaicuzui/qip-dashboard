export const state = {
    // 엑셀에서 읽어온 원본 데이터 배열
    rawData: [],

    // 가공 및 분석이 완료된 데이터 객체
    processedData: {
        // --- 전체 현황 (Overview) ---
        totalValidation: 0,
        totalReject: 0,
        totalRejectRate: 0,
        avgDailyValidation: 0,
        
        // --- 분석 차원별 데이터 ---
        tqcData: {},
        inspectorData: {},
        defectTypes: {},
        buildingData: {},
        poData: {},
        lineData: {},
        modelData: {},
        
        // --- 필터링 및 차트용 마스터 데이터 ---
        buildings: [],
        models: [],
        
        // --- 일별 집계 데이터 ---
        dailyData: {},

        // --- TQC 불량 유출 분석용 데이터 ---
        tqcMissingDefects: {},
        
        // --- (신규) 지속성 탭을 위한 상세 분석 데이터 ---
        // dataProcessor.js에서 계산된 CV, 변동성 점수, 추세 데이터 등이
        // 각 tqcData, buildingData 등에 'sustainability' 속성으로 추가될 예정입니다.
        // 감사관(Auditor) 데이터는 별도로 관리합니다.
        auditorSustainability: {},
    },

    // 동적으로 생성된 Chart.js 인스턴스들을 관리
    charts: {},

    // 현재 선택된 언어와 기간
    currentLanguage: 'ko',
    currentPeriod: 'all',

    // --- (신규) UI 로직에서 사용할 임시 데이터 ---
    
    // TQC 분석 탭의 '교육 우선순위' 차트 데이터
    trainingDefectData: [],
    
    // 업무 지시 탭의 '어딧터별 추천업무' 팝업을 위한 상세 데이터
    auditorDetailInfo: {},
};