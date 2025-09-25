import { state } from './state.js';
import { processData } from './dataProcessor.js';
import { initializeDashboard } from './uiController.js';

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