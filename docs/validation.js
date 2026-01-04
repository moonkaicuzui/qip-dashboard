// ============================================
// QIP Incentive Validation System
// Independent JavaScript Validation Engine
// ============================================

const ValidationEngine = {
    // Global state
    state: {
        selectedMonth: null,
        selectedYear: null,
        previousMonthData: null,
        currentMonthData: {
            attendance: null,
            aql: null,
            prs: null,
            basicInfo: null,
            config: null,
            positionMatrix: null,
            dashboardOutput: null
        },
        validationResults: null
    },

    // ================================================
    // Module 1: File Loaders & Template Generator
    // ================================================
    FileLoader: {
        /**
         * Generate blank Excel template for Previous Month data
         * Only 2 columns: Employee ID, Previous_Incentive
         * No pre-filled data - user pastes their own
         */
        generatePreviousMonthTemplate(monthKey) {
            const wb = XLSX.utils.book_new();

            // Create worksheet with headers only
            const wsData = [
                ['Employee ID', 'Previous_Incentive'],
                ['', ''],  // Empty row 1
                ['', ''],  // Empty row 2
                ['', ''],  // Empty row 3
                // ... add more empty rows for user convenience
            ];

            // Add 100 empty rows
            for (let i = 0; i < 100; i++) {
                wsData.push(['', '']);
            }

            const ws = XLSX.utils.aoa_to_sheet(wsData);

            // Set column widths
            ws['!cols'] = [
                { wch: 15 },  // Employee ID
                { wch: 20 }   // Previous_Incentive
            ];

            XLSX.utils.book_append_sheet(wb, ws, 'Previous Month Data');

            return wb;
        },

        /**
         * Trigger download of template Excel file
         */
        downloadTemplate(monthKey, fileName) {
            const wb = this.generatePreviousMonthTemplate(monthKey);
            XLSX.writeFile(wb, fileName);
        },

        /**
         * Load and parse user-uploaded Excel file
         */
        async loadPreviousMonthExcel(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();

                reader.onload = (e) => {
                    try {
                        const data = new Uint8Array(e.target.result);
                        const workbook = XLSX.read(data, { type: 'array' });

                        // Get first sheet
                        const sheetName = workbook.SheetNames[0];
                        const worksheet = workbook.Sheets[sheetName];

                        // Convert to JSON
                        const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: '' });

                        resolve(jsonData);
                    } catch (error) {
                        reject(new Error('Failed to parse Excel file: ' + error.message));
                    }
                };

                reader.onerror = () => reject(new Error('Failed to read file'));
                reader.readAsArrayBuffer(file);
            });
        },

        /**
         * Validate uploaded Previous Month file
         */
        validateUploadedFile(fileData) {
            const errors = [];
            const warnings = [];

            // Check required columns
            if (!fileData || fileData.length === 0) {
                errors.push('파일이 비어있습니다 (File is empty)');
                return { valid: false, errors, warnings };
            }

            const firstRow = fileData[0];
            if (!firstRow.hasOwnProperty('Employee ID')) {
                errors.push('필수 컬럼 누락: Employee ID');
            }
            if (!firstRow.hasOwnProperty('Previous_Incentive')) {
                errors.push('필수 컬럼 누락: Previous_Incentive');
            }

            if (errors.length > 0) {
                return { valid: false, errors, warnings };
            }

            // Validate data ranges
            fileData.forEach((row, idx) => {
                const empId = row['Employee ID'];
                const incentive = row['Previous_Incentive'];

                // Skip empty rows
                if (!empId && !incentive) return;

                // Validate Employee ID
                if (!empId || empId === '') {
                    warnings.push(`Row ${idx + 2}: Employee ID가 비어있습니다`);
                }

                // Validate Previous_Incentive
                if (incentive === '' || incentive === null || incentive === undefined) {
                    warnings.push(`Row ${idx + 2}: Previous_Incentive가 비어있습니다`);
                } else if (isNaN(incentive) || Number(incentive) < 0) {
                    errors.push(`Row ${idx + 2}: Previous_Incentive는 0 이상의 숫자여야 합니다 (${incentive})`);
                }
            });

            return {
                valid: errors.length === 0,
                errors,
                warnings
            };
        },

        /**
         * Reverse-calculate Continuous_Months from Previous_Incentive amount
         * 150,000 → 1 month
         * 250,000 → 2 months
         * ...
         * 1,000,000 → 12+ months (we assume 12, exact number doesn't matter for 12+)
         */
        reverseContinuousMonths(incentive) {
            const progressionTable = {
                0: 0,
                150000: 1,
                250000: 2,
                300000: 3,
                350000: 4,
                400000: 5,
                450000: 6,
                500000: 7,
                650000: 8,
                750000: 9,
                850000: 10,
                950000: 11,
                1000000: 12  // For 12-15 months, all receive 1,000,000
            };

            // Find exact match first
            if (progressionTable.hasOwnProperty(incentive)) {
                return progressionTable[incentive];
            }

            // If 1,000,000 VND, assume 12 months (could be 12-15)
            if (incentive >= 1000000) {
                return 12;
            }

            // If no exact match, find closest lower value
            const amounts = Object.keys(progressionTable).map(Number).sort((a, b) => a - b);
            for (let i = amounts.length - 1; i >= 0; i--) {
                if (incentive >= amounts[i]) {
                    return progressionTable[amounts[i]];
                }
            }

            return 0;  // Default
        },

        /**
         * Load CSV file from URL using PapaParse
         */
        async loadCSVFromURL(url) {
            return new Promise((resolve, reject) => {
                Papa.parse(url, {
                    download: true,
                    header: true,
                    dynamicTyping: true,
                    skipEmptyLines: true,
                    complete: (results) => resolve(results.data),
                    error: (error) => reject(error)
                });
            });
        },

        /**
         * Load JSON file from URL
         */
        async loadJSONFromURL(url) {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed to load ${url}: ${response.statusText}`);
            }
            return await response.json();
        },

        /**
         * Load all required source files for selected month
         * Returns: { attendance, aql, prs, basicInfo, config, positionMatrix }
         */
        async loadAllSources(monthKey) {
            const [monthName, year] = monthKey.split('_');

            // File paths - using validation_data folder (GitHub Pages compatible)
            const basePath = './validation_data';  // Files copied to /docs/validation_data

            const filePaths = {
                attendance: `${basePath}/${monthName}_${year}/attendance data ${monthName}_converted.csv`,
                aql: `${basePath}/${monthName}_${year}/1.HSRG AQL REPORT-${monthName.toUpperCase()}.${year}.csv`,
                prs: `${basePath}/${monthName}_${year}/5prs data ${monthName}.csv`,
                basicInfo: `${basePath}/${monthName}_${year}/basic manpower data ${monthName}.csv`,
                config: `${basePath}/${monthName}_${year}/config_${monthName}_${year}.json`,
                positionMatrix: `${basePath}/${monthName}_${year}/position_condition_matrix.json`,
                dashboardOutput: `${basePath}/${monthName}_${year}/output_QIP_incentive_${monthName}_${year}_Complete_V10.0_Complete.csv`
            };

            try {
                const [attendance, aql, prs, basicInfo, config, positionMatrix, dashboardOutput] = await Promise.all([
                    this.loadCSVFromURL(filePaths.attendance),
                    this.loadCSVFromURL(filePaths.aql),
                    this.loadCSVFromURL(filePaths.prs),
                    this.loadCSVFromURL(filePaths.basicInfo),
                    this.loadJSONFromURL(filePaths.config),
                    this.loadJSONFromURL(filePaths.positionMatrix),
                    this.loadCSVFromURL(filePaths.dashboardOutput)
                ]);

                return {
                    attendance,
                    aql,
                    prs,
                    basicInfo,
                    config,
                    positionMatrix,
                    dashboardOutput
                };
            } catch (error) {
                throw new Error(`Failed to load source files: ${error.message}`);
            }
        }
    },

    // ================================================
    // Module 2: Independent Calculator
    // ================================================
    Calculator: {
        /**
         * Condition 1: Attendance Rate >= 88%
         * Formula: 100 - ((total - actual - approved_leave) / total × 100)
         */
        calculateCondition1_AttendanceRate(employee, attendanceData, config) {
            const totalDays = config.working_days || 0;
            const actualDays = employee.actualWorkingDays || 0;
            const approvedLeaveDays = employee.approvedLeaveDays || 0;

            if (totalDays === 0) return 'FAIL';

            const absenceDays = totalDays - actualDays - approvedLeaveDays;
            const absenceRate = (absenceDays / totalDays) * 100;
            const attendanceRate = 100 - absenceRate;

            return attendanceRate >= 88 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 2: Unapproved Absence <= 2 days
         */
        calculateCondition2_UnapprovedAbsence(employee, attendanceData) {
            const unapprovedAbsence = employee.unapprovedAbsence || 0;
            return unapprovedAbsence <= 2 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 3: Actual Working Days > 0
         */
        calculateCondition3_ActualWorkingDays(employee, attendanceData) {
            const actualDays = employee.actualWorkingDays || 0;
            return actualDays > 0 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 4: Minimum Working Days >= 12
         * Date-dependent: QC Assembly Inspector (15-day cutoff), Others (20-day cutoff)
         */
        calculateCondition4_MinimumDays(employee, attendanceData, currentDate, positionMatrix) {
            const position = employee.position || '';
            const positionCode = employee.positionCode || '';
            const actualDays = employee.actualWorkingDays || 0;

            // Check if QC Assembly Inspector
            const isQCAssembly = position.includes('ASSEMBLY INSPECTOR') || positionCode.startsWith('A');
            const cutoffDay = isQCAssembly ? 15 : 20;

            const currentDay = currentDate.getDate();
            const isInterimReport = currentDay < cutoffDay;

            if (isInterimReport) {
                return 'NOT_APPLICABLE';
            }

            return actualDays >= 12 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 5: Personal AQL Failure = 0 (current month)
         */
        calculateCondition5_PersonalAQLFailure(employee, aqlData) {
            // Filter AQL data for this employee in current month
            // Employee No column in basic info vs employee_id in AQL data
            const empNo = employee['Employee No'];
            const empAQL = aqlData.filter(row => row.employee_id === empNo);

            if (empAQL.length === 0) return 'PASS';  // No AQL tests = pass

            const failCount = empAQL.filter(row => row.result === 'FAIL' || row.result === 'F').length;
            return failCount === 0 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 6: No 3-month Consecutive Personal AQL Failures
         * (This requires historical data - simplified for now)
         */
        calculateCondition6_AQL3MonthConsecutive(employee, aqlData) {
            // Placeholder - requires historical AQL data
            // For now, check Continuous_FAIL column if available
            return employee.continuousFail === 'YES_3MONTHS' ? 'FAIL' : 'PASS';
        },

        /**
         * Condition 7: No 3-month Consecutive Team/Area AQL Failures
         */
        calculateCondition7_TeamAreaAQL(employee, aqlData) {
            // Placeholder - requires team/area aggregation
            return 'PASS';  // Simplified
        },

        /**
         * Condition 8: Area Reject Rate < 3%
         */
        calculateCondition8_AreaRejectRate(employee, aqlData) {
            // Placeholder - requires area-level calculation
            return 'PASS';  // Simplified
        },

        /**
         * Condition 9: 5PRS Pass Rate >= 95%
         */
        calculateCondition9_5PRSPassRate(employee, prsData) {
            const empNo = employee['Employee No'];
            const empPRS = prsData.filter(row => row.employee_id === empNo);

            if (empPRS.length === 0) return 'PASS';  // No PRS tests = pass

            const totalTests = empPRS.length;
            const passCount = empPRS.filter(row => row.result === 'PASS' || row.result === 'P').length;
            const passRate = (passCount / totalTests) * 100;

            return passRate >= 95 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 10: 5PRS Inspection Quantity >= 100
         */
        calculateCondition10_5PRSInspectionQty(employee, prsData) {
            const empNo = employee['Employee No'];
            const empPRS = prsData.filter(row => row.employee_id === empNo);

            const totalQty = empPRS.reduce((sum, row) => sum + (row.inspection_qty || 0), 0);

            return totalQty >= 100 ? 'PASS' : 'FAIL';
        },

        /**
         * Calculate Continuous_Months based on previous month and condition pass
         */
        calculateContinuousMonths(employee, previousMonthData, allConditionsPass) {
            if (!previousMonthData) {
                // New employee - no previous month data
                return allConditionsPass ? 1 : 0;
            }

            const empNo = employee['Employee No'];
            const prevData = previousMonthData.find(row => row['Employee ID'] === empNo);

            if (!prevData) {
                // Employee not in previous month
                return allConditionsPass ? 1 : 0;
            }

            const prevIncentive = prevData['Previous_Incentive'] || 0;
            const prevContinuousMonths = ValidationEngine.FileLoader.reverseContinuousMonths(prevIncentive);

            if (allConditionsPass) {
                return Math.min(prevContinuousMonths + 1, 15);  // Max 15 months
            } else {
                return 0;  // Reset on failure
            }
        },

        /**
         * Calculate incentive amount based on TYPE and continuous months
         */
        calculateIncentiveAmount(employee, continuousMonths, employeeType, allConditionsPass, positionMatrix) {
            if (!allConditionsPass) {
                return 0;  // 100% Rule: no partial incentives
            }

            const progressionTable = positionMatrix.progression_table || {};

            if (employeeType === 'TYPE-1') {
                return progressionTable[continuousMonths] || 0;
            } else if (employeeType === 'TYPE-2') {
                // TYPE-2 uses TYPE-1 average (simplified - would need full TYPE-1 calculation)
                return progressionTable[continuousMonths] || 0;
            } else if (employeeType === 'TYPE-3') {
                return 0;  // TYPE-3 always 0
            }

            return 0;
        },

        /**
         * Master validation function - validates single employee
         */
        validateEmployee(empId, allData, previousMonthData, currentDate) {
            const { attendance, aql, prs, basicInfo, config, positionMatrix } = allData;

            // Find employee in basicInfo
            // CSV column is "Employee No" (with space), not "emp_no"
            const employee = basicInfo.find(row => row['Employee No'] === empId);
            if (!employee) {
                return null;  // Employee not found
            }

            // Get position config
            const positionCode = employee['FINAL QIP POSITION NAME CODE'] || '';
            const positionConfig = positionMatrix.position_matrix[positionCode] || {};
            const applicableConditions = positionConfig.applicable_conditions || [];
            const employeeType = positionConfig.type || 'TYPE-3';

            // Calculate all 10 conditions
            const conditionResults = {
                condition_1: this.calculateCondition1_AttendanceRate(employee, attendance, config),
                condition_2: this.calculateCondition2_UnapprovedAbsence(employee, attendance),
                condition_3: this.calculateCondition3_ActualWorkingDays(employee, attendance),
                condition_4: this.calculateCondition4_MinimumDays(employee, attendance, currentDate, positionMatrix),
                condition_5: this.calculateCondition5_PersonalAQLFailure(employee, aql),
                condition_6: this.calculateCondition6_AQL3MonthConsecutive(employee, aql),
                condition_7: this.calculateCondition7_TeamAreaAQL(employee, aql),
                condition_8: this.calculateCondition8_AreaRejectRate(employee, aql),
                condition_9: this.calculateCondition9_5PRSPassRate(employee, prs),
                condition_10: this.calculateCondition10_5PRSInspectionQty(employee, prs)
            };

            // Check if all applicable conditions pass
            const passedConditions = applicableConditions.filter(condNum =>
                conditionResults[`condition_${condNum}`] === 'PASS'
            ).length;

            const allConditionsPass = (passedConditions === applicableConditions.length);

            // Calculate Continuous_Months
            const continuousMonths = this.calculateContinuousMonths(employee, previousMonthData, allConditionsPass);

            // Calculate Incentive Amount
            const incentiveAmount = this.calculateIncentiveAmount(
                employee,
                continuousMonths,
                employeeType,
                allConditionsPass,
                positionMatrix
            );

            return {
                emp_no: empId,
                name: employee['Full Name'] || '',
                position: employee['QIP POSITION 1ST  NAME'] || '',
                employeeType,
                conditionResults,
                applicableConditions,
                passedConditions,
                allConditionsPass,
                continuousMonths,
                incentiveAmount
            };
        }
    },

    // ================================================
    // Module 3: Comparator
    // ================================================
    Comparator: {
        /**
         * Compare expected vs actual for single employee
         */
        compareEmployees(expected, actual) {
            const mismatches = [];

            // Dashboard CSV column names
            const actualIncentive = actual['December_Incentive'] || 0;
            const actualContinuousMonths = actual['Continuous_Months'] || 0;

            // Compare incentive amount
            if (expected.incentiveAmount !== actualIncentive) {
                mismatches.push({
                    field: 'Incentive Amount',
                    expected: expected.incentiveAmount,
                    actual: actualIncentive,
                    difference: expected.incentiveAmount - actualIncentive,
                    severity: 'CRITICAL'
                });
            }

            // Compare continuous months
            if (expected.continuousMonths !== actualContinuousMonths) {
                mismatches.push({
                    field: 'Continuous Months',
                    expected: expected.continuousMonths,
                    actual: actualContinuousMonths,
                    difference: expected.continuousMonths - actualContinuousMonths,
                    severity: 'HIGH'
                });
            }

            // Compare condition results (CSV uses cond_1, cond_2, etc.)
            for (let i = 1; i <= 10; i++) {
                const expectedCond = expected.conditionResults[`condition_${i}`];
                const actualCond = actual[`cond_${i}`];  // CSV column name

                if (expectedCond !== actualCond && expected.applicableConditions.includes(i)) {
                    mismatches.push({
                        field: `Condition ${i}`,
                        expected: expectedCond,
                        actual: actualCond,
                        difference: null,
                        severity: 'MEDIUM'
                    });
                }
            }

            return mismatches;
        },

        /**
         * Generate comprehensive validation report
         */
        generateValidationReport(expectedResults, actualData) {
            const report = {
                totalEmployees: expectedResults.length,
                matched: 0,
                mismatched: 0,
                mismatches: [],
                expectedTotalIncentive: 0,
                actualTotalIncentive: 0
            };

            expectedResults.forEach(expected => {
                // Dashboard CSV uses "Employee No" column
                const actual = actualData.find(row => row['Employee No'] === expected.emp_no);

                if (!actual) {
                    report.mismatches.push({
                        emp_no: expected.emp_no,
                        name: expected.name,
                        issue: 'Employee not found in dashboard output',
                        severity: 'CRITICAL'
                    });
                    report.mismatched++;
                    return;
                }

                const employeeMismatches = this.compareEmployees(expected, actual);

                if (employeeMismatches.length > 0) {
                    report.mismatches.push({
                        emp_no: expected.emp_no,
                        name: expected.name,
                        position: expected.position,
                        mismatches: employeeMismatches
                    });
                    report.mismatched++;
                } else {
                    report.matched++;
                }

                report.expectedTotalIncentive += expected.incentiveAmount;
                report.actualTotalIncentive += actual.incentive_amount || 0;
            });

            return report;
        }
    },

    // ================================================
    // Module 4: UI Controller
    // ================================================
    UIController: {
        /**
         * Display summary statistics
         */
        displaySummary(validationReport) {
            document.getElementById('totalEmployees').textContent = validationReport.totalEmployees;
            document.getElementById('matchedCount').textContent = validationReport.matched;
            document.getElementById('mismatchedCount').textContent = validationReport.mismatched;

            const matchPercent = ((validationReport.matched / validationReport.totalEmployees) * 100).toFixed(2);
            const mismatchPercent = ((validationReport.mismatched / validationReport.totalEmployees) * 100).toFixed(2);

            document.getElementById('matchedPercent').textContent = `(${matchPercent}%)`;
            document.getElementById('mismatchedPercent').textContent = `(${mismatchPercent}%)`;

            document.getElementById('expectedTotal').textContent =
                `Expected: ₫${validationReport.expectedTotalIncentive.toLocaleString()}`;
            document.getElementById('actualTotal').textContent =
                `Actual: ₫${validationReport.actualTotalIncentive.toLocaleString()}`;

            // Show summary section
            document.getElementById('summary').classList.remove('hidden');
            document.getElementById('searchFilter').classList.remove('hidden');
            document.getElementById('mismatchTable').classList.remove('hidden');
        },

        /**
         * Display mismatch table
         */
        displayMismatchTable(mismatches) {
            const tbody = document.getElementById('mismatchBody');
            tbody.innerHTML = '';

            if (mismatches.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No mismatches found ✅</td></tr>';
                return;
            }

            mismatches.forEach(mismatch => {
                mismatch.mismatches.forEach(detail => {
                    const row = document.createElement('tr');
                    row.classList.add('mismatch-row');

                    row.innerHTML = `
                        <td>${mismatch.emp_no}</td>
                        <td>${mismatch.name}</td>
                        <td>${detail.field}</td>
                        <td>${detail.expected}</td>
                        <td>${detail.actual}</td>
                        <td>${detail.difference !== null ? detail.difference : '-'}</td>
                        <td><span class="severity-badge severity-${detail.severity.toLowerCase()}">${detail.severity}</span></td>
                    `;

                    tbody.appendChild(row);
                });
            });
        },

        /**
         * Export mismatches to Excel
         */
        exportToExcel(mismatches) {
            const wb = XLSX.utils.book_new();

            // Prepare data for export
            const exportData = [];
            mismatches.forEach(mismatch => {
                mismatch.mismatches.forEach(detail => {
                    exportData.push({
                        'Employee ID': mismatch.emp_no,
                        'Name': mismatch.name,
                        'Position': mismatch.position,
                        'Field': detail.field,
                        'Expected': detail.expected,
                        'Actual': detail.actual,
                        'Difference': detail.difference !== null ? detail.difference : '-',
                        'Severity': detail.severity
                    });
                });
            });

            const ws = XLSX.utils.json_to_sheet(exportData);
            XLSX.utils.book_append_sheet(wb, ws, 'Mismatches');

            const fileName = `Validation_Mismatches_${ValidationEngine.state.selectedMonth}_${new Date().toISOString().slice(0, 10)}.xlsx`;
            XLSX.writeFile(wb, fileName);
        }
    },

    // ================================================
    // Module 5: Main Workflow
    // ================================================
    async runValidation(monthKey, previousMonthFile) {
        try {
            // Update progress
            const progressBar = document.querySelector('#progressBar .progress-bar');
            progressBar.style.width = '10%';
            progressBar.textContent = 'Loading files...';

            // Load all source files
            const allData = await this.FileLoader.loadAllSources(monthKey);
            this.state.currentMonthData = allData;

            progressBar.style.width = '30%';
            progressBar.textContent = 'Loading previous month data...';

            // Load and validate previous month file
            if (previousMonthFile) {
                const fileData = await this.FileLoader.loadPreviousMonthExcel(previousMonthFile);
                const validation = this.FileLoader.validateUploadedFile(fileData);

                if (!validation.valid) {
                    throw new Error('Previous Month file validation failed:\n' + validation.errors.join('\n'));
                }

                this.state.previousMonthData = fileData;
            }

            progressBar.style.width = '50%';
            progressBar.textContent = 'Calculating...';

            // Calculate expected results for all employees
            const currentDate = new Date();  // Or get from config
            const expectedResults = [];

            allData.basicInfo.forEach(employee => {
                const result = this.Calculator.validateEmployee(
                    employee['Employee No'],  // CSV column name with space
                    allData,
                    this.state.previousMonthData,
                    currentDate
                );

                if (result) {
                    expectedResults.push(result);
                }
            });

            progressBar.style.width = '70%';
            progressBar.textContent = 'Comparing results...';

            // Compare with dashboard output
            const validationReport = this.Comparator.generateValidationReport(
                expectedResults,
                allData.dashboardOutput
            );

            this.state.validationResults = validationReport;

            progressBar.style.width = '90%';
            progressBar.textContent = 'Displaying results...';

            // Display results
            this.UIController.displaySummary(validationReport);
            this.UIController.displayMismatchTable(validationReport.mismatches);

            progressBar.style.width = '100%';
            progressBar.textContent = 'Complete ✅';

            setTimeout(() => {
                document.getElementById('progressBar').classList.add('hidden');
            }, 2000);

        } catch (error) {
            console.error('Validation failed:', error);
            alert(`검증 실패: ${error.message}`);
            document.getElementById('progressBar').classList.add('hidden');
        }
    }
};

// ================================================
// Event Handlers & Initialization
// ================================================
document.addEventListener('DOMContentLoaded', () => {
    // Month selector change
    document.getElementById('monthSelector').addEventListener('change', (e) => {
        const monthKey = e.target.value;
        if (monthKey) {
            ValidationEngine.state.selectedMonth = monthKey;

            // Update template download button
            const [monthName, year] = monthKey.split('_');
            const prevMonthName = getPreviousMonthName(monthName);
            document.getElementById('downloadTemplate').textContent =
                `📄 ${prevMonthName} ${year} 양식 다운로드`;
        }
    });

    // Template download button
    document.getElementById('downloadTemplate').addEventListener('click', () => {
        const monthKey = ValidationEngine.state.selectedMonth;
        if (!monthKey) {
            alert('먼저 검증 월을 선택하세요 (Please select validation month first)');
            return;
        }

        const [monthName, year] = monthKey.split('_');
        const prevMonthName = getPreviousMonthName(monthName);
        const fileName = `${prevMonthName}_${year}_Template.xlsx`;

        ValidationEngine.FileLoader.downloadTemplate(monthKey, fileName);
    });

    // File upload
    document.getElementById('previousMonthFile').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const uploadStatus = document.getElementById('uploadStatus');
        uploadStatus.classList.remove('hidden', 'success', 'error', 'warning');
        uploadStatus.textContent = 'Uploading...';

        try {
            const fileData = await ValidationEngine.FileLoader.loadPreviousMonthExcel(file);
            const validation = ValidationEngine.FileLoader.validateUploadedFile(fileData);

            if (validation.valid) {
                uploadStatus.classList.add('success');
                const t = translations[currentLang];
                uploadStatus.textContent = `✅ ${t.uploadSuccess}: ${fileData.length}${t.uploadEmployees}`;
                document.getElementById('startValidation').disabled = false;
            } else {
                uploadStatus.classList.add('error');
                uploadStatus.textContent = '❌ ' + validation.errors.join(', ');
            }

            if (validation.warnings.length > 0) {
                uploadStatus.classList.add('warning');
                uploadStatus.textContent += '\n⚠️ ' + validation.warnings.join(', ');
            }
        } catch (error) {
            uploadStatus.classList.add('error');
            uploadStatus.textContent = '❌ ' + error.message;
        }
    });

    // Start validation button
    document.getElementById('startValidation').addEventListener('click', async () => {
        const monthKey = ValidationEngine.state.selectedMonth;
        const fileInput = document.getElementById('previousMonthFile');

        const t = translations[currentLang];

        if (!monthKey) {
            alert(t.selectMonth);
            return;
        }

        if (!fileInput.files[0]) {
            alert(t.uploadFile);
            return;
        }

        // Show progress bar
        document.getElementById('progressBar').classList.remove('hidden');

        await ValidationEngine.runValidation(monthKey, fileInput.files[0]);
    });

    // Export to Excel button
    document.getElementById('exportExcel').addEventListener('click', () => {
        if (ValidationEngine.state.validationResults) {
            ValidationEngine.UIController.exportToExcel(ValidationEngine.state.validationResults.mismatches);
        }
    });

    // Language switcher
    const translations = {
        ko: {
            title: '인센티브 검증 시스템',
            subtitle: '독립적인 계산 엔진으로 인센티브 금액을 검증합니다',
            configSection: '검증 설정',
            monthSelect: '검증 월 선택',
            monthPlaceholder: '-- 월 선택 --',
            step1Title: 'Step 1: 전월 데이터 양식 다운로드',
            step1Desc: '실제 지급된 전월 인센티브 데이터를 입력할 Excel 양식을 다운로드하세요.',
            downloadBtn: '양식 다운로드 (Previous Month Template)',
            templateInfo: '양식 안내:',
            step2Title: 'Step 2: 작성한 양식 업로드',
            step2Label: '전월 실제 지급 파일 (Previous Month Actual Payment)',
            startBtn: '검증 시작 (Start Validation)',
            summaryTitle: '검증 요약',
            totalEmployees: '총 직원 수',
            matched: '일치',
            mismatched: '불일치',
            totalIncentive: '총 인센티브',
            mismatchTitle: 'Validation Mismatches',
            uploadSuccess: '업로드 성공',
            uploadEmployees: '명의 데이터',
            selectMonth: '먼저 검증 월을 선택하세요',
            uploadFile: '먼저 전월 데이터 파일을 업로드하세요'
        },
        en: {
            title: 'Incentive Validation System',
            subtitle: 'Independently validates incentive calculations with dedicated calculation engine',
            configSection: 'Validation Settings',
            monthSelect: 'Select Validation Month',
            monthPlaceholder: '-- Select Month --',
            step1Title: 'Step 1: Download Previous Month Template',
            step1Desc: 'Download the Excel template to enter actual payment data for previous month.',
            downloadBtn: 'Download Template (Previous Month)',
            templateInfo: 'Template Guide:',
            step2Title: 'Step 2: Upload Completed Template',
            step2Label: 'Previous Month Actual Payment File',
            startBtn: 'Start Validation',
            summaryTitle: 'Validation Summary',
            totalEmployees: 'Total Employees',
            matched: 'Matched',
            mismatched: 'Mismatched',
            totalIncentive: 'Total Incentive',
            mismatchTitle: 'Validation Mismatches',
            uploadSuccess: 'Upload Success',
            uploadEmployees: 'employees',
            selectMonth: 'Please select validation month first',
            uploadFile: 'Please upload previous month data file first'
        },
        vi: {
            title: 'Hệ thống Xác thực Thưởng',
            subtitle: 'Xác thực độc lập việc tính toán thưởng với công cụ tính toán chuyên dụng',
            configSection: 'Cài đặt Xác thực',
            monthSelect: 'Chọn Tháng Xác thực',
            monthPlaceholder: '-- Chọn Tháng --',
            step1Title: 'Bước 1: Tải Mẫu Tháng Trước',
            step1Desc: 'Tải mẫu Excel để nhập dữ liệu thanh toán thực tế cho tháng trước.',
            downloadBtn: 'Tải Mẫu (Tháng Trước)',
            templateInfo: 'Hướng dẫn Mẫu:',
            step2Title: 'Bước 2: Tải Mẫu Đã Hoàn Thành',
            step2Label: 'Tệp Thanh Toán Thực Tế Tháng Trước',
            startBtn: 'Bắt đầu Xác thực',
            summaryTitle: 'Tóm tắt Xác thực',
            totalEmployees: 'Tổng Nhân viên',
            matched: 'Khớp',
            mismatched: 'Không khớp',
            totalIncentive: 'Tổng Thưởng',
            mismatchTitle: 'Sai lệch Xác thực',
            uploadSuccess: 'Tải lên Thành công',
            uploadEmployees: 'nhân viên',
            selectMonth: 'Vui lòng chọn tháng xác thực trước',
            uploadFile: 'Vui lòng tải lên tệp dữ liệu tháng trước trước'
        }
    };

    let currentLang = 'ko';

    function switchLanguage(lang) {
        currentLang = lang;
        const t = translations[lang];

        // Update header
        document.querySelector('header h1').innerHTML = `<i class="fas fa-search-dollar"></i> ${t.title}`;
        document.querySelector('header .lead').textContent = t.subtitle;

        // Update config section
        const configSection = document.querySelector('.input-section h3');
        if (configSection) configSection.innerHTML = `<i class="fas fa-cog"></i> ${t.configSection}`;

        // Update month selector
        const monthLabel = document.querySelector('label[for="monthSelector"] strong');
        if (monthLabel) monthLabel.textContent = t.monthSelect;

        const monthPlaceholder = document.querySelector('#monthSelector option[value=""]');
        if (monthPlaceholder) monthPlaceholder.textContent = t.monthPlaceholder;

        // Update Step 1
        const step1Title = document.querySelector('.template-section h4');
        if (step1Title) step1Title.innerHTML = `<i class="fas fa-download"></i> ${t.step1Title}`;

        const step1Desc = document.querySelector('.template-section p');
        if (step1Desc) step1Desc.textContent = t.step1Desc;

        const downloadBtn = document.getElementById('downloadTemplate');
        if (downloadBtn) downloadBtn.innerHTML = `<i class="fas fa-file-excel"></i> ${t.downloadBtn}`;

        const templateInfo = document.querySelector('.template-info strong');
        if (templateInfo) templateInfo.innerHTML = `<i class="fas fa-info-circle"></i> ${t.templateInfo}`;

        // Update Step 2
        const step2Title = document.querySelector('.file-upload h4');
        if (step2Title) step2Title.innerHTML = `<i class="fas fa-upload"></i> ${t.step2Title}`;

        const step2Label = document.querySelector('.file-upload label');
        if (step2Label) step2Label.textContent = t.step2Label;

        // Update Start button
        const startBtn = document.getElementById('startValidation');
        if (startBtn) startBtn.innerHTML = `<i class="fas fa-check-circle"></i> ${t.startBtn}`;

        // Update Summary section
        const summaryTitle = document.querySelector('#summary h3');
        if (summaryTitle) summaryTitle.innerHTML = `<i class="fas fa-chart-bar"></i> ${t.summaryTitle}`;

        // Update KPI cards
        const kpiTitles = document.querySelectorAll('#summary .card-title');
        if (kpiTitles[0]) kpiTitles[0].textContent = t.totalEmployees;
        if (kpiTitles[1]) kpiTitles[1].textContent = t.matched;
        if (kpiTitles[2]) kpiTitles[2].textContent = t.mismatched;
        if (kpiTitles[3]) kpiTitles[3].textContent = t.totalIncentive;

        // Update Mismatch table
        const mismatchTitle = document.querySelector('#mismatchTable h3');
        if (mismatchTitle) mismatchTitle.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${t.mismatchTitle}`;

        // Update language selector buttons
        document.querySelectorAll('.lang-selector .btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
    }

    // Language selector buttons
    document.querySelectorAll('.lang-selector .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchLanguage(btn.dataset.lang);
        });
    });

    // Initialize with default language (Korean)
    switchLanguage('ko');
});

// Helper function to get previous month name
function getPreviousMonthName(monthName) {
    const months = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ];

    const monthIndex = months.findIndex(m => m === monthName.toLowerCase());
    const prevIndex = monthIndex === 0 ? 11 : monthIndex - 1;

    return months[prevIndex].charAt(0).toUpperCase() + months[prevIndex].slice(1);
}
