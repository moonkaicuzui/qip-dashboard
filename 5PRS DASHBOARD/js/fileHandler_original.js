import { state } from './state.js';
import { processData } from './dataProcessor.js';
import { initializeDashboard } from './uiController.js';

// 서버에서 데이터를 자동으로 가져오는 함수
export async function loadDataFromServer() {
    console.log('🔄 서버에서 5PRS 데이터를 가져오는 중...');
    
    // 로딩 인디케이터 표시
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'flex';
    }
    
    try {
        // API 엔드포인트에서 데이터 가져오기 (상대 경로 사용)
        const response = await fetch('/api/5prs-data');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success' && result.data && result.data.length > 0) {
            console.log(`✅ ${result.data.length}개의 레코드를 성공적으로 불러왔습니다.`);
            
            // 데이터가 이미 표준화되어 있으므로 바로 사용
            state.rawData = result.data;
            processData();
            initializeDashboard();
            
            // 업로드 섹션 숨기고 대시보드 표시
            const uploadSection = document.getElementById('uploadSection');
            const dashboardSection = document.getElementById('dashboardSection');
            
            if (uploadSection) uploadSection.style.display = 'none';
            if (dashboardSection) dashboardSection.style.display = 'block';
            
        } else {
            throw new Error('서버에서 데이터를 찾을 수 없습니다.');
        }
    } catch (error) {
        console.error('❌ 데이터 로딩 중 오류 발생:', error);
        
        // 오류 메시지 표시
        const errorContainer = document.getElementById('errorContainer');
        const errorText = document.getElementById('errorText');
        
        if (errorContainer && errorText) {
            errorText.textContent = `데이터를 불러올 수 없습니다: ${error.message}`;
            errorContainer.style.display = 'block';
        }
        
        // 대체 메시지 표시
        const uploadSection = document.getElementById('uploadSection');
        if (uploadSection) {
            uploadSection.innerHTML = `
                <div class="upload-area" style="cursor: default;">
                    <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <div class="upload-text">데이터를 불러올 수 없습니다</div>
                    <div class="upload-subtext">서버 연결을 확인해주세요</div>
                    <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 1rem;">
                        새로고침
                    </button>
                </div>
            `;
        }
    } finally {
        // 로딩 인디케이터 숨기기
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
}

// 데이터 새로고침 함수
export async function refreshData() {
    console.log('🔄 데이터를 새로고침합니다...');
    await loadDataFromServer();
}

// 기존 파일 업로드 함수들은 보관 (필요시 사용)
export function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) readExcelFile(file);
}

export function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.remove('dragover');
    const file = event.dataTransfer.files[0];
    if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
        readExcelFile(file);
    } else {
        alert('엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.');
    }
}

export function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.add('dragover');
}

export function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.remove('dragover');
}

function readExcelFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array', cellDates: true });
            const worksheet = workbook.Sheets[workbook.SheetNames[0]];
            const rawJsonData = XLSX.utils.sheet_to_json(worksheet, { 
                raw: false,
                dateNF: 'yyyy-mm-dd',
                defval: ''
            });

            if (rawJsonData.length > 0) {
                state.rawData = mapColumnNames(rawJsonData);
                processData();
                initializeDashboard();
            } else {
                alert('엑셀 파일에 데이터가 없습니다.');
            }
        } catch (error) {
            console.error('파일 처리 중 오류 발생:', error);
            alert(`파일을 읽는 중 오류가 발생했습니다: ${error.message}`);
        }
    };
    reader.onerror = function(error) {
        console.error('FileReader 오류:', error);
        alert('파일을 읽을 수 없습니다.');
    };
    reader.readAsArrayBuffer(file);
}

function mapColumnNames(data) {
    const columnMapping = {
        'Inspection Date': ['Inspection Date', 'inspection date', 'Date'],
        'Inspector ID': ['Inspector ID', 'inspector id', 'Auditor ID'],
        'Inspector Name': ['Inspector Name', 'inspector name', 'Auditor Name'],
        'Time': ['Time', 'time', 'Shift'],
        'Building': ['Building', 'building', 'Area'],
        'Line': ['Line', 'line', 'Production Line'],
        'PO No': ['PO No', 'PO Number', 'po no', 'PO'],
        'PO Item': ['PO Item', 'po item'],
        'Model': ['Model', 'model', 'Style'],
        'TQC ID': ['TQC ID', 'tqc id', 'QC ID'],
        'TQC Name': ['TQC Name', 'tqc name', 'QC Name'],
        'Validation Qty': ['Validation Qty', 'Valiation Qty', 'validation qty', 'Validated Qty'],
        'Pass Qty': ['Pass Qty', 'pass qty', 'Passed Qty'],
        'Reject Qty': ['Reject Qty', 'reject qty', 'Rejected Qty'],
        'Error': ['Error', 'error', 'Defect', 'Defect Type']
    };

    const findKeyInRow = (rowObject, possibleNames) => {
        for (const key in rowObject) {
            if (Object.prototype.hasOwnProperty.call(rowObject, key)) {
                const trimmedKey = key.trim();
                if (possibleNames.includes(trimmedKey)) {
                    return key;
                }
            }
        }
        return null;
    };

    return data.map(row => {
        const newRow = {};
        for (const [standardName, possibleNames] of Object.entries(columnMapping)) {
            const key = findKeyInRow(row, possibleNames);
            if (key) {
                newRow[standardName] = row[key];
            }
        }
        return newRow;
    });
}