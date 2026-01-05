// ============================================
// QIP Incentive Validation System
// Independent JavaScript Validation Engine
// ============================================

const ValidationEngine = {
    // Global state
    state: {
        selectedMonth: null,
        selectedYear: null,
        fileUploaded: false,
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

            // Cache-busting: Add timestamp to prevent stale cached files
            const cacheBuster = `?v=${Date.now()}`;

            const filePaths = {
                attendance: `${basePath}/${monthName}_${year}/attendance data ${monthName}_converted.csv${cacheBuster}`,
                aql: `${basePath}/${monthName}_${year}/1.HSRG AQL REPORT-${monthName.toUpperCase()}.${year}.csv${cacheBuster}`,
                prs: `${basePath}/${monthName}_${year}/5prs data ${monthName}.csv${cacheBuster}`,
                basicInfo: `${basePath}/${monthName}_${year}/basic manpower data ${monthName}.csv${cacheBuster}`,
                config: `${basePath}/${monthName}_${year}/config_${monthName}_${year}.json${cacheBuster}`,
                positionMatrix: `${basePath}/${monthName}_${year}/position_condition_matrix.json${cacheBuster}`,
                dashboardOutput: `${basePath}/${monthName}_${year}/output_QIP_incentive_${monthName}_${year}_Complete_V10.0_Complete.csv${cacheBuster}`,
                // Phase 2.2: Additional data sources for position-specific calculators
                aqlInspectorConfig: `${basePath}/${monthName}_${year}/aql_inspector_incentive_config.json${cacheBuster}`
            };

            try {
                const [attendance, aql, prs, basicInfo, config, positionMatrix, dashboardOutput, aqlInspectorConfig] = await Promise.all([
                    this.loadCSVFromURL(filePaths.attendance),
                    this.loadCSVFromURL(filePaths.aql),
                    this.loadCSVFromURL(filePaths.prs),
                    this.loadCSVFromURL(filePaths.basicInfo),
                    this.loadJSONFromURL(filePaths.config),
                    this.loadJSONFromURL(filePaths.positionMatrix),
                    this.loadCSVFromURL(filePaths.dashboardOutput),
                    // Phase 2.2: Load AQL Inspector 3-Part configuration (fallback to empty object if not found)
                    this.loadJSONFromURL(filePaths.aqlInspectorConfig).catch(() => ({}))
                ]);

                // DEBUG: Check positionMatrix loading
                console.log('[DEBUG loadAllSources] positionMatrix type:', typeof positionMatrix);
                console.log('[DEBUG loadAllSources] positionMatrix keys:', positionMatrix ? Object.keys(positionMatrix) : 'NULL');
                console.log('[DEBUG loadAllSources] type_2_incentive_calculation exists:', positionMatrix && positionMatrix.type_2_incentive_calculation ? 'YES' : 'NO');
                if (positionMatrix && positionMatrix.type_2_incentive_calculation) {
                    console.log('[DEBUG loadAllSources] type_2_incentive_calculation keys:', Object.keys(positionMatrix.type_2_incentive_calculation));
                }

                return {
                    attendance,
                    aql,
                    prs,
                    basicInfo,
                    config,
                    positionMatrix,
                    dashboardOutput,
                    // Phase 2.2: Additional data sources
                    aqlInspectorConfig  // AQL Inspector 3-Part calculation data
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
         * Get applicable conditions for a position based on position_condition_matrix.json
         * @param {string} position - Employee position (e.g., "ASSEMBLY INSPECTOR")
         * @param {string} employeeType - TYPE-1, TYPE-2, or TYPE-3
         * @param {object} positionMatrix - position_condition_matrix.json data
         * @returns {object} { applicable: [1,2,3,...], excluded: [5,6,7,...] }
         */
        getApplicableConditions(position, employeeType, positionMatrix) {
            if (!positionMatrix || !positionMatrix.position_matrix) {
                // Fallback: 기본 조건 (출근 조건만)
                return {
                    applicable: [1, 2, 3, 4],
                    excluded: [5, 6, 7, 8, 9, 10]
                };
            }

            const typeMatrix = positionMatrix.position_matrix[employeeType];
            if (!typeMatrix) {
                return {
                    applicable: [1, 2, 3, 4],
                    excluded: [5, 6, 7, 8, 9, 10]
                };
            }

            // Find matching position config
            for (const [key, config] of Object.entries(typeMatrix)) {
                if (key === 'default') continue;

                if (config.patterns && config.patterns.some(pattern =>
                    position.toUpperCase().includes(pattern.toUpperCase())
                )) {
                    return {
                        applicable: config.applicable_conditions || [],
                        excluded: config.excluded_conditions || []
                    };
                }
            }

            // No match found → use default
            return {
                applicable: typeMatrix.default?.applicable_conditions || [1, 2, 3, 4],
                excluded: typeMatrix.default?.excluded_conditions || [5, 6, 7, 8, 9, 10]
            };
        },

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
         * FIXED (Issue #41): Use correct CSV column names
         */
        calculateCondition5_PersonalAQLFailure(employee, aqlData) {
            // Filter AQL data for this employee in current month
            // AQL CSV column is "EMPLOYEE NO" (uppercase), not "employee_id"
            const empNo = String(employee['Employee No'] || '').trim();
            const empAQL = aqlData.filter(row =>
                String(row['EMPLOYEE NO'] || '').trim() === empNo
            );

            if (empAQL.length === 0) return 'PASS';  // No AQL tests = pass

            // AQL CSV uses "RESULT" column (PASS/FAIL)
            const failCount = empAQL.filter(row => {
                const result = (row['RESULT'] || '').toString().toUpperCase().trim();
                return result === 'FAIL' || result === 'F';
            }).length;
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
         * FIXED (Issue #41): Use TQC ID column for ASSEMBLY INSPECTOR matching
         * 5PRS CSV structure:
         *   - Inspector ID: Person doing the inspection (AUDIT & TRAINING TEAM)
         *   - TQC ID: Person being inspected (ASSEMBLY INSPECTOR) ← Use this!
         */
        calculateCondition9_5PRSPassRate(employee, prsData) {
            // CRITICAL FIX: Use TQC ID (person being inspected), NOT Inspector ID
            const empNo = String(employee['Employee No'] || '').trim();
            const empPRS = prsData.filter(row =>
                String(row['TQC ID'] || '').trim() === empNo
            );

            // CRITICAL FIX (Issue #41): No 5PRS data = FAIL (to match dashboard behavior)
            // Dashboard marks employees without 5PRS inspections as FAIL for both cond_9 and cond_10
            if (empPRS.length === 0) return 'FAIL';  // No PRS inspections = FAIL

            // Calculate pass rate from Pass Qty and Valiation Qty (note: typo in CSV)
            let totalQty = 0;
            let passQty = 0;
            empPRS.forEach(row => {
                totalQty += parseFloat(row['Valiation Qty'] || row['Validation Qty'] || 0);
                passQty += parseFloat(row['Pass Qty'] || 0);
            });

            if (totalQty === 0) return 'PASS';  // No inspections = pass

            const passRate = (passQty / totalQty) * 100;
            return passRate >= 95 ? 'PASS' : 'FAIL';
        },

        /**
         * Condition 10: 5PRS Inspection Quantity >= 100
         * FIXED (Issue #41): Use TQC ID column for ASSEMBLY INSPECTOR matching
         * Same logic as Condition 9 - use TQC ID (person being inspected)
         */
        calculateCondition10_5PRSInspectionQty(employee, prsData) {
            // CRITICAL FIX: Use TQC ID (person being inspected), NOT Inspector ID
            const empNo = String(employee['Employee No'] || '').trim();
            const empPRS = prsData.filter(row =>
                String(row['TQC ID'] || '').trim() === empNo
            );

            // Sum "Valiation Qty" (typo in CSV) for total inspection quantity
            const totalQty = empPRS.reduce((sum, row) =>
                sum + (parseFloat(row['Valiation Qty'] || row['Validation Qty'] || 0)), 0
            );

            return totalQty >= 100 ? 'PASS' : 'FAIL';
        },

        /**
         * Calculate Continuous_Months based on previous month and condition pass
         * TYPE-1 ONLY - TYPE-2/3 do not use Continuous Months concept
         */
        calculateContinuousMonths(employee, previousMonthData, allConditionsPass, employeeType) {
            // TYPE-2 and TYPE-3 do not use Continuous Months
            if (employeeType !== 'TYPE-1') {
                return null;  // Not applicable
            }

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
         * Phase 2.5: Calculate incentive amount with position-specific logic
         * @param {Object} employee - Employee data from CSV
         * @param {number} continuousMonths - Calculated continuous months
         * @param {string} employeeType - TYPE-1, TYPE-2, or TYPE-3
         * @param {boolean} allConditionsPass - Whether all applicable conditions pass
         * @param {Object} positionMatrix - Position condition matrix JSON
         * @param {Object} context - Additional context for position-specific calculations
         * @param {Map} context.subordinateMap - Map of boss_id -> subordinates
         * @param {Array} context.allValidatedEmployees - All validated employees so far
         * @param {Object} context.aqlConfig - AQL Inspector config (3-part formula)
         * @param {Object} context.type1Averages - TYPE-1 position averages (for TYPE-2)
         * @returns {{amount: number, method: string}} - Incentive amount and calculation method
         */
        calculateIncentiveAmount(employee, continuousMonths, employeeType, allConditionsPass, positionMatrix, context = {}) {
            // 100% Rule: no partial incentives
            if (!allConditionsPass) {
                return { amount: 0, method: '조건 미충족 (0 VND)' };
            }

            const progressionTable = positionMatrix.progression_table || {};
            const position = (employee['QIP POSITION 1ST  NAME'] || '').toUpperCase();

            // TYPE-3: Always 0
            if (employeeType === 'TYPE-3') {
                return { amount: 0, method: 'TYPE-3 (0 VND)' };
            }

            // TYPE-1: Position-specific calculation
            if (employeeType === 'TYPE-1') {
                // Use PositionCalculators if context is available
                if (context.subordinateMap && context.allValidatedEmployees) {
                    const result = ValidationEngine.PositionCalculators.calculatePositionSpecificIncentive(
                        employee,
                        position,
                        continuousMonths,
                        context.subordinateMap,
                        context.allValidatedEmployees,
                        context.aqlConfig
                    );
                    return result;
                }
                // Fallback: Use progression table
                const amount = progressionTable[continuousMonths] || 0;
                return {
                    amount: amount,
                    method: `Progression Table (${continuousMonths}개월 → ${amount.toLocaleString()} VND)`
                };
            }

            // TYPE-2: Use TYPE-1 reference position average with multiplier
            if (employeeType === 'TYPE-2') {
                const type2Mapping = positionMatrix.type_2_incentive_calculation || {};
                // Normalize position name for lookup (try exact match, then pattern matching)
                const normalizedPosition = position.trim().toUpperCase();

                // DEBUG: Log first 3 TYPE-2 employees
                if (!window._type2DebugCount) window._type2DebugCount = 0;
                if (window._type2DebugCount < 3) {
                    console.log('[TYPE-2 DEBUG] Employee:', employee['Employee No'], 'Position:', position);
                    console.log('[TYPE-2 DEBUG] type2Mapping keys:', Object.keys(type2Mapping));
                    console.log('[TYPE-2 DEBUG] _default exists:', !!type2Mapping._default);
                    window._type2DebugCount++;
                }

                // Find matching mapping entry (try exact match first, then patterns)
                let mappingEntry = null;
                let mappingKey = null;

                // Try exact match first
                for (const [key, value] of Object.entries(type2Mapping)) {
                    if (key.startsWith('_')) continue; // Skip meta fields
                    if (normalizedPosition === key.toUpperCase()) {
                        mappingEntry = value;
                        mappingKey = key;
                        break;
                    }
                }

                // Try partial match if no exact match
                if (!mappingEntry) {
                    for (const [key, value] of Object.entries(type2Mapping)) {
                        if (key.startsWith('_')) continue; // Skip meta fields
                        if (normalizedPosition.includes(key.toUpperCase())) {
                            mappingEntry = value;
                            mappingKey = key;
                            break;
                        }
                    }
                }

                // Use default mapping if still no match
                if (!mappingEntry && type2Mapping._default) {
                    mappingEntry = type2Mapping._default;
                    mappingKey = '_default';
                }

                if (!mappingEntry) {
                    // No mapping found - use progression table as fallback
                    const amount = progressionTable[continuousMonths] || 0;
                    return {
                        amount: amount,
                        method: `TYPE-2 매핑 없음 → Progression Table (${continuousMonths}개월)`
                    };
                }

                // Extract reference position and multiplier from mapping entry
                const referencePosition = mappingEntry.reference_type1_position || mappingKey;
                const multiplier = mappingEntry.multiplier || 1.0;

                // Get TYPE-1 average from context
                if (context.type1Averages && context.type1Averages[referencePosition]) {
                    const avg = context.type1Averages[referencePosition];
                    const finalAmount = Math.round(avg.average * multiplier);
                    const methodDesc = multiplier === 1.0
                        ? `TYPE-1 ${referencePosition} 평균 (수령자 ${avg.receivingCount}명, ${avg.average.toLocaleString()} VND)`
                        : `TYPE-1 ${referencePosition} 평균 × ${multiplier} (수령자 ${avg.receivingCount}명, ${avg.average.toLocaleString()} × ${multiplier} = ${finalAmount.toLocaleString()} VND)`;

                    return {
                        amount: finalAmount,
                        method: methodDesc
                    };
                }

                // Fallback: No TYPE-1 average available
                return {
                    amount: 0,
                    method: `TYPE-1 ${referencePosition} 평균 없음 (0 VND)`
                };
            }

            return { amount: 0, method: 'Unknown TYPE' };
        },

        /**
         * Phase 2.5: Master validation function - validates single employee
         * @param {string} empId - Employee ID
         * @param {Object} allData - All loaded data sources
         * @param {Array} previousMonthData - Previous month employee data
         * @param {Date} currentDate - Current date for calculations
         * @param {Object} context - Additional context for position-specific calculations
         * @param {Map} context.subordinateMap - Map of boss_id -> subordinates
         * @param {Array} context.allValidatedEmployees - All validated employees so far (for manager calcs)
         * @param {Object} context.aqlConfig - AQL Inspector config (3-part formula)
         * @param {Object} context.type1Averages - TYPE-1 position averages (for TYPE-2)
         */
        validateEmployee(empId, allData, previousMonthData, currentDate, context = {}) {
            const { attendance, aql, prs, basicInfo, config, positionMatrix } = allData;

            // DEBUG: Check positionMatrix in validateEmployee (first 3 calls only)
            if (!window._validateDebugCount) window._validateDebugCount = 0;
            if (window._validateDebugCount < 3) {
                console.log('[DEBUG validateEmployee] allData.positionMatrix exists:', !!allData.positionMatrix);
                console.log('[DEBUG validateEmployee] positionMatrix (destructured) exists:', !!positionMatrix);
                console.log('[DEBUG validateEmployee] type_2_incentive_calculation exists:', positionMatrix && positionMatrix.type_2_incentive_calculation ? 'YES' : 'NO');
                window._validateDebugCount++;
            }

            // Find employee in basicInfo
            // CSV column is "Employee No" (with space), not "emp_no"
            const employee = basicInfo.find(row => row['Employee No'] === empId);
            if (!employee) {
                return null;  // Employee not found
            }

            // ========== CRITICAL FIX (Issue #41): Merge Attendance Data ==========
            // Problem: basicInfo doesn't contain attendance fields
            // Solution: Find matching attendance record and merge fields
            const attendanceRecord = attendance.find(row =>
                String(row['ID No'] || '').trim() === String(empId || '').trim()
            );

            if (attendanceRecord) {
                // Merge attendance fields with expected property names
                employee.actualWorkingDays = parseFloat(attendanceRecord['ACTUAL WORK DAY']) || 0;
                employee.approvedLeaveDays = parseFloat(attendanceRecord['Approved Leave Days']) || 0;
                employee.unapprovedAbsence = parseFloat(attendanceRecord['Unapproved Absences']) || 0;
                employee.totalWorkingDays = parseFloat(attendanceRecord['TOTAL WORK DAY']) || 0;
                employee.attendanceRate = parseFloat(attendanceRecord['Attendance Rate (%)']) || 0;
            } else {
                // No attendance record found - set defaults
                employee.actualWorkingDays = 0;
                employee.approvedLeaveDays = 0;
                employee.unapprovedAbsence = 0;
                employee.totalWorkingDays = 0;
                employee.attendanceRate = 0;
            }
            // ========== END CRITICAL FIX ==========

            // Determine employee TYPE from CSV column
            // CSV column name is "ROLE TYPE STD", not "TYPE"
            const typeColumn = employee['ROLE TYPE STD'] || employee['TYPE'] || '';
            const employeeType = typeColumn || 'TYPE-3';

            // Get position name (not code!) and assign to employee object
            const position = employee['QIP POSITION 1ST  NAME'] || '';
            employee.position = position;  // For condition calculators
            employee.positionCode = employee['QIP POSITION CODE'] || '';  // For QC Assembly check

            // Get applicable conditions based on position + TYPE
            const conditionsConfig = this.getApplicableConditions(position, employeeType, positionMatrix);
            const applicableConditions = conditionsConfig.applicable;
            const excludedConditions = conditionsConfig.excluded;

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
            // CRITICAL FIX (Issue #41): 'NOT_APPLICABLE' should count as passing
            // NOT_APPLICABLE means the condition doesn't apply (e.g., interim report)
            const passedConditions = applicableConditions.filter(condNum => {
                const result = conditionResults[`condition_${condNum}`];
                return result === 'PASS' || result === 'NOT_APPLICABLE';
            }).length;

            const allConditionsPass = (passedConditions === applicableConditions.length);

            // Calculate Continuous_Months (TYPE-1 only)
            const continuousMonths = this.calculateContinuousMonths(employee, previousMonthData, allConditionsPass, employeeType);

            // Phase 2.5: Calculate Incentive Amount with position-specific logic
            const incentiveResult = this.calculateIncentiveAmount(
                employee,
                continuousMonths,
                employeeType,
                allConditionsPass,
                positionMatrix,
                context  // Pass context for position-specific calculations
            );

            // Extract amount and method from result
            const incentiveAmount = incentiveResult.amount;
            const calculationMethod = incentiveResult.method;

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
                incentiveAmount,
                calculationMethod  // Phase 2.5: Include calculation method
            };
        }
    },

    // ================================================
    // Module 2.5: Position-Specific Calculator Helpers (Phase 2.3, 2.4)
    // ================================================
    PositionCalculators: {
        /**
         * Phase 2.3: Builds a mapping of boss ID to subordinate employees
         * Uses BOSS ID field from basic manpower data for hierarchy
         * @param {Array} basicInfoData - Basic manpower data with BOSS ID field
         * @returns {Map} Map<bossId, Array<employee>>
         */
        buildSubordinateMapping(basicInfoData) {
            const mapping = new Map();

            // DEBUG: Log first employee's keys and BOSS ID value
            if (basicInfoData.length > 0) {
                const firstEmp = basicInfoData[0];
                console.log('[DEBUG buildSubordinateMapping] First employee keys:', Object.keys(firstEmp));
                console.log('[DEBUG buildSubordinateMapping] MST direct boss name value:', firstEmp['MST direct boss name']);
                console.log('[DEBUG buildSubordinateMapping] BOSS ID value:', firstEmp['BOSS ID']);
            }

            let bossIdCount = 0;
            basicInfoData.forEach(emp => {
                // Try multiple possible column names for BOSS ID
                // CRITICAL FIX (Issue #41): 'MST direct boss name' contains the boss's Employee No (not a name!)
                const bossId = String(emp['MST direct boss name'] || emp['BOSS ID'] || emp['direct boss id'] || emp['Boss ID'] || '').trim();
                if (!bossId || bossId === '-' || bossId === '0' || bossId === '') return;
                bossIdCount++;

                if (!mapping.has(bossId)) {
                    mapping.set(bossId, []);
                }
                mapping.get(bossId).push(emp);
            });

            console.log(`[DEBUG buildSubordinateMapping] Employees with valid boss ID: ${bossIdCount}/${basicInfoData.length}`);
            return mapping;  // Map<bossId, [subordinates]>
        },

        /**
         * Phase 2.4.1: Calculate AQL INSPECTOR incentive (3-Part Formula)
         * Part 1: Progression table (AQL 평가)
         * Part 2: CFA Certification (CFA 자격증) - Fixed 700,000 VND
         * Part 3: HWK Claim Prevention (HWK 클레임 방지)
         */
        calculateAqlInspectorIncentive(emp, continuousMonths, aqlConfig) {
            const PROGRESSION_TABLE = {
                0: 0, 1: 150000, 2: 250000, 3: 350000, 4: 450000,
                5: 550000, 6: 650000, 7: 750000, 8: 850000,
                9: 900000, 10: 950000, 11: 975000, 12: 1000000,
                13: 1000000, 14: 1000000, 15: 1000000
            };

            const empNo = String(emp['Employee No'] || emp.emp_no || '').trim();
            const monthData = aqlConfig[empNo];

            if (!monthData) {
                // Fallback to progression table only (Part 1 only)
                const amount = PROGRESSION_TABLE[Math.min(continuousMonths, 15)] || 0;
                return {
                    amount: amount,
                    method: `Progression Table (${continuousMonths}개월)`
                };
            }

            // Part 1: Progression Table (AQL 평가)
            const part1Months = parseInt(monthData['Part1_Months'] || continuousMonths);
            const part1Amount = parseInt(monthData['Part1_Amount'] || PROGRESSION_TABLE[Math.min(part1Months, 15)] || 0);

            // Part 2: CFA Certification (CFA 자격증)
            const part2Amount = parseInt(monthData['Part2_CFA_Amount'] || 0);

            // Part 3: HWK Claim Prevention (HWK 클레임 방지)
            const part3Months = parseInt(monthData['Part3_Months'] || 0);
            const part3Amount = parseInt(monthData['Part3_Amount'] || 0);

            const totalAmount = part1Amount + part2Amount + part3Amount;

            return {
                amount: totalAmount,
                method: `3-Part: Part1(${part1Months}개월, ${part1Amount.toLocaleString()}) + Part2(CFA, ${part2Amount.toLocaleString()}) + Part3(${part3Months}개월, ${part3Amount.toLocaleString()})`
            };
        },

        /**
         * Phase 2.4.2: Calculate LINE LEADER incentive (Subordinate Formula)
         * Formula: (Total Subordinate Incentive) × 12% × Receiving Ratio
         * FIXED (Issue #41): Filter by TYPE-1 employees, not position name (matches Python logic)
         */
        calculateLineLeaderIncentive(emp, subordinateMap, allValidatedEmployees) {
            const empNo = String(emp['Employee No'] || emp.emp_no || '').trim();
            const subordinates = subordinateMap.get(empNo) || [];

            // FIXED: Filter by TYPE-1 employees (Python uses 'ROLE TYPE STD' == 'TYPE-1')
            // This matches the Python logic in step1_인센티브_계산_개선버전.py:3555
            const type1Subordinates = subordinates.filter(sub => {
                const roleType = (sub['ROLE TYPE STD'] || sub['TYPE'] || '').toUpperCase();
                return roleType === 'TYPE-1';
            });

            if (type1Subordinates.length === 0) {
                return {
                    amount: 0,
                    method: 'No TYPE-1 Subordinates (TYPE-1 부하직원 없음)'
                };
            }

            // Calculate total incentive and receiving count from TYPE-1 subordinates
            let totalSubordinateIncentive = 0;
            let receivingCount = 0;

            type1Subordinates.forEach(sub => {
                const subNo = String(sub['Employee No'] || '').trim();
                const subResult = allValidatedEmployees.find(v =>
                    String(v.emp_no || '').trim() === subNo
                );
                if (!subResult) return;

                const subIncentive = subResult.incentiveAmount || 0;
                totalSubordinateIncentive += subIncentive;
                if (subIncentive > 0) receivingCount++;
            });

            // Formula: Total × 12% × Receiving Ratio
            const receivingRatio = receivingCount / type1Subordinates.length;
            const amount = Math.round(totalSubordinateIncentive * 0.12 * receivingRatio);

            return {
                amount: amount,
                method: `TYPE-1 부하직원 × 12% × 수령비율 (${receivingCount}/${type1Subordinates.length}명 수령, 합계 ${totalSubordinateIncentive.toLocaleString()})`
            };
        },

        /**
         * Phase 2.4.3: Calculate GROUP LEADER incentive (BFS + LINE LEADER avg × 2)
         * Uses BFS to find subordinate LINE LEADERs through hierarchy
         */
        calculateGroupLeaderIncentive(emp, subordinateMap, allValidatedEmployees) {
            const empNo = String(emp['Employee No'] || emp.emp_no || '').trim();

            // BFS to find subordinate LINE LEADERs
            const lineLeaders = [];
            const queue = [empNo];
            const visited = new Set([empNo]);

            while (queue.length > 0) {
                const currentId = queue.shift();
                const subordinates = subordinateMap.get(currentId) || [];

                subordinates.forEach(sub => {
                    const subId = String(sub['Employee No'] || '').trim();
                    if (visited.has(subId)) return;
                    visited.add(subId);

                    const subPos = (sub['Position'] || sub['QIP POSITION 1ST  NAME'] || '').toUpperCase();
                    if (subPos.includes('LINE LEADER')) {
                        lineLeaders.push(sub);
                    } else {
                        queue.push(subId);  // Continue BFS
                    }
                });
            }

            if (lineLeaders.length === 0) {
                return {
                    amount: 0,
                    method: 'No LINE LEADER Subordinates (부하 LINE LEADER 없음)'
                };
            }

            // Calculate TYPE-1 LINE LEADER average (receiving only)
            let totalIncentive = 0;
            let receivingCount = 0;

            lineLeaders.forEach(ll => {
                const llNo = String(ll['Employee No'] || '').trim();
                const llResult = allValidatedEmployees.find(v =>
                    String(v.emp_no || '').trim() === llNo && v.employeeType === 'TYPE-1'
                );
                if (!llResult) return;

                const llIncentive = llResult.incentiveAmount || 0;
                if (llIncentive > 0) {
                    totalIncentive += llIncentive;
                    receivingCount++;
                }
            });

            if (receivingCount === 0) {
                return {
                    amount: 0,
                    method: 'TYPE-1 LINE LEADER 평균 × 2 (수령자 없음)'
                };
            }

            const avg = Math.round(totalIncentive / receivingCount);
            const amount = avg * 2;

            return {
                amount: amount,
                method: `TYPE-1 LINE LEADER 평균 × 2 (${receivingCount}명 수령, 평균 ${avg.toLocaleString()})`
            };
        },

        /**
         * Phase 2.4.4 & 2.4.5: Calculate SUPERVISOR incentive (BFS + Multiplier)
         * SUPERVISOR: LINE LEADER avg × 2.5
         * (V) SUPERVISOR / V.SUPERVISOR: LINE LEADER avg × 2.5 (same as SUPERVISOR per Python engine)
         * FIX (2026-01-05): A.SUPERVISOR was 3.5, corrected to 2.5 to match Python engine
         */
        calculateSupervisorIncentive(emp, subordinateMap, allValidatedEmployees, position) {
            const posUpper = (position || '').toUpperCase();

            // Determine multiplier based on position name
            // All SUPERVISOR variants use 2.5 per Python engine (step1:3699-3700)
            let multiplier = 2.5;  // Default for all SUPERVISOR types

            // Use GROUP LEADER logic to find LINE LEADER average
            const groupLeaderResult = this.calculateGroupLeaderIncentive(emp, subordinateMap, allValidatedEmployees);
            const lineLeaderAvg = groupLeaderResult.amount / 2;  // Reverse the × 2 to get avg

            if (lineLeaderAvg === 0) {
                return {
                    amount: 0,
                    method: `TYPE-1 LINE LEADER 평균 × ${multiplier} (LINE LEADER 평균 0)`
                };
            }

            const amount = Math.round(lineLeaderAvg * multiplier);

            return {
                amount: amount,
                method: `TYPE-1 LINE LEADER 평균 × ${multiplier} (평균 ${Math.round(lineLeaderAvg).toLocaleString()})`
            };
        },

        /**
         * Phase 2.4.6 & 2.4.7: Calculate MANAGER incentive (BFS + Multiplier)
         * S.MANAGER / SENIOR MANAGER: LINE LEADER avg × 4.0
         * MANAGER: LINE LEADER avg × 3.5
         * A.MANAGER / ASSISTANT MANAGER: LINE LEADER avg × 3.0
         * FIX (2026-01-05): Corrected multipliers to match Python engine (step1:3695-3698)
         */
        calculateManagerIncentive(emp, subordinateMap, allValidatedEmployees, position) {
            const posUpper = (position || '').toUpperCase();

            // Determine multiplier based on position name (per Python engine step1:3695-3698)
            let multiplier = 3.5;  // Default for MANAGER
            if (posUpper.includes('S.MANAGER') || posUpper.includes('SENIOR MANAGER')) {
                multiplier = 4.0;
            } else if (posUpper.includes('A.MANAGER') || posUpper.includes('A. MANAGER') || posUpper.includes('ASSISTANT MANAGER')) {
                multiplier = 3.0;
            }

            // Use GROUP LEADER logic to find LINE LEADER average
            const groupLeaderResult = this.calculateGroupLeaderIncentive(emp, subordinateMap, allValidatedEmployees);
            const lineLeaderAvg = groupLeaderResult.amount / 2;  // Reverse the × 2 to get avg

            if (lineLeaderAvg === 0) {
                return {
                    amount: 0,
                    method: `TYPE-1 LINE LEADER 평균 × ${multiplier} (LINE LEADER 평균 0)`
                };
            }

            const amount = Math.round(lineLeaderAvg * multiplier);

            return {
                amount: amount,
                method: `TYPE-1 LINE LEADER 평균 × ${multiplier} (평균 ${Math.round(lineLeaderAvg).toLocaleString()})`
            };
        },

        /**
         * Phase 2.5: Master function to calculate position-specific incentive
         * Routes to appropriate calculator based on position name
         */
        calculatePositionSpecificIncentive(emp, position, continuousMonths, subordinateMap, allValidatedEmployees, aqlConfig) {
            const PROGRESSION_TABLE = {
                0: 0, 1: 150000, 2: 250000, 3: 350000, 4: 450000,
                5: 550000, 6: 650000, 7: 750000, 8: 850000,
                9: 900000, 10: 950000, 11: 975000, 12: 1000000,
                13: 1000000, 14: 1000000, 15: 1000000
            };

            const posUpper = (position || '').toUpperCase();

            // Route to position-specific calculator
            if (posUpper.includes('AQL INSPECTOR')) {
                return this.calculateAqlInspectorIncentive(emp, continuousMonths, aqlConfig);
            } else if (posUpper.includes('LINE LEADER')) {
                return this.calculateLineLeaderIncentive(emp, subordinateMap, allValidatedEmployees);
            } else if (posUpper.includes('GROUP LEADER')) {
                return this.calculateGroupLeaderIncentive(emp, subordinateMap, allValidatedEmployees);
            } else if (posUpper.includes('SUPERVISOR')) {
                return this.calculateSupervisorIncentive(emp, subordinateMap, allValidatedEmployees, position);
            } else if (posUpper.includes('MANAGER')) {
                return this.calculateManagerIncentive(emp, subordinateMap, allValidatedEmployees, position);
            } else {
                // Default: Progression table for ASSEMBLY INSPECTOR, MODEL MASTER, AUDITOR, TRAINER
                const amount = PROGRESSION_TABLE[Math.min(continuousMonths, 15)] || 0;
                return {
                    amount: amount,
                    method: `Progression Table (${continuousMonths}개월)`
                };
            }
        }
    },

    // ================================================
    // Module 3: Comparator
    // ================================================
    Comparator: {
        /**
         * Compare expected vs actual for single employee
         * TYPE별로 다른 검증 로직 적용:
         * - TYPE-1: Incentive + Continuous Months 검증
         * - TYPE-2: Incentive만 검증 (Continuous Months 제외)
         * - TYPE-3: Incentive만 검증 (항상 0)
         */
        compareEmployees(expected, actual) {
            const mismatches = [];

            // Dashboard CSV column names
            const dashboardIncentive = actual['December_Incentive'] || 0;
            const dashboardContinuousMonths = actual['Continuous_Months'] || 0;

            // Compare incentive amount (모든 TYPE 공통)
            if (expected.incentiveAmount !== dashboardIncentive) {
                mismatches.push({
                    field: 'Incentive',
                    validatedIncentive: expected.incentiveAmount,
                    dashboardIncentive: dashboardIncentive,
                    difference: expected.incentiveAmount - dashboardIncentive
                });
            }

            // Compare continuous months (TYPE-1 ONLY)
            // FIX (Issue #41): Use dashboard's Previous_Continuous_Months instead of reverseContinuousMonths
            // This avoids issues with non-standard amounts (AQL 3-part, LINE LEADER, etc.)
            if (expected.employeeType === 'TYPE-1') {
                const prevMonths = parseInt(actual['Previous_Continuous_Months'] || 0);
                let expectedCurrentMonths;

                if (expected.allConditionsPass) {
                    expectedCurrentMonths = Math.min(prevMonths + 1, 15);  // Max 15 months
                } else {
                    expectedCurrentMonths = 0;  // Reset on failure
                }

                if (expectedCurrentMonths !== dashboardContinuousMonths) {
                    mismatches.push({
                        field: 'Continuous Months',
                        validatedIncentive: expectedCurrentMonths,
                        dashboardIncentive: dashboardContinuousMonths,
                        difference: expectedCurrentMonths - dashboardContinuousMonths,
                        previousMonths: prevMonths,
                        allConditionsPass: expected.allConditionsPass
                    });
                }
            }

            // Compare condition results (CSV uses full column names like cond_1_attendance_rate)
            // FIXED (Issue #41): Use correct CSV column names
            const conditionColumnMap = {
                1: 'cond_1_attendance_rate',
                2: 'cond_2_unapproved_absence',
                3: 'cond_3_actual_working_days',
                4: 'cond_4_minimum_days',
                5: 'cond_5_aql_personal_failure',
                6: 'cond_6_aql_continuous',
                7: 'cond_7_aql_team_area',
                8: 'cond_8_area_reject',
                9: 'cond_9_5prs_pass_rate',
                10: 'cond_10_5prs_inspection_qty'
            };

            for (let i = 1; i <= 10; i++) {
                const expectedCond = expected.conditionResults[`condition_${i}`];
                const actualCond = actual[conditionColumnMap[i]];  // Use full column name

                if (expectedCond !== actualCond && expected.applicableConditions.includes(i)) {
                    mismatches.push({
                        field: `Condition ${i}`,
                        validatedIncentive: expectedCond,
                        dashboardIncentive: actualCond,
                        difference: null
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
                actualTotalIncentive: 0,
                allEmployees: []  // NEW: Store all employee data for statistics
            };

            expectedResults.forEach(expected => {
                // Dashboard CSV uses "Employee No" column
                const actual = actualData.find(row => row['Employee No'] === expected.emp_no);

                if (!actual) {
                    report.mismatches.push({
                        emp_no: expected.emp_no,
                        name: expected.name,
                        employeeType: expected.employeeType,
                        issue: 'Employee not found in dashboard output'
                    });
                    report.mismatched++;
                    return;
                }

                const employeeMismatches = this.compareEmployees(expected, actual);

                // Store all employee data for TYPE/Position statistics
                // Phase 2.1 & 2.5: Enhanced data structure with position-specific calculation info
                report.allEmployees.push({
                    emp_no: expected.emp_no,
                    name: expected.name,
                    position: expected.position,
                    employeeType: expected.employeeType,
                    validatedIncentive: expected.incentiveAmount,
                    dashboardIncentive: actual['December_Incentive'] || actual.incentive_amount || 0,
                    validatedConditions: expected.conditionResults,
                    hasMismatch: employeeMismatches.length > 0,
                    mismatches: employeeMismatches,
                    // Phase 2.5: Position-specific calculation display fields
                    continuousMonths: actual['Continuous_Months'] || 0,  // FIX: Use dashboard value instead of calculated
                    calculationMethod: expected.calculationMethod || '',  // Now populated by position-specific calculators
                    // Phase 3.1: New fields for TYPE-2 3-layer validation
                    conditionsPassed: expected.passedConditions || 0,  // FIX: was conditionsPassed, now passedConditions
                    conditionsApplicable: expected.applicableConditions?.length || 0,
                    allConditionsPass: expected.allConditionsPass || false,  // Use already-calculated value
                    stopWorkingDate: actual['Stop working Date'] || null,  // For TYPE-2 Layer 1 resignation check
                    // FIX (Issue #41): Add Previous_Continuous_Months from dashboard for validation
                    previousContinuousMonths: parseInt(actual['Previous_Continuous_Months'] || 0)
                });

                if (employeeMismatches.length > 0) {
                    // Enhanced mismatch object with full validation data for 10-condition display
                    report.mismatches.push({
                        emp_no: expected.emp_no,
                        name: expected.name,
                        position: expected.position,
                        employeeType: expected.employeeType,
                        conditionResults: expected.conditionResults,  // NEW: All 10 condition results
                        applicableConditions: expected.applicableConditions,  // NEW: Which conditions apply
                        continuousMonths: expected.continuousMonths,  // NEW: Continuous months
                        validatedIncentive: expected.incentiveAmount,  // NEW: Validated incentive
                        dashboardIncentive: actual['December_Incentive'] || actual.incentive_amount || 0,  // NEW: Dashboard incentive
                        mismatches: employeeMismatches
                    });
                    report.mismatched++;
                } else {
                    report.matched++;
                }

                report.expectedTotalIncentive += expected.incentiveAmount;
                // FIXED (Issue #41): Use December_Incentive (not November_Incentive)
                report.actualTotalIncentive += parseFloat(actual['December_Incentive']) || 0;
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

            // Generate TYPE별 Position별 통계
            this.generatePositionStatistics(validationReport.allEmployees);

            // Show summary section
            document.getElementById('summary').classList.remove('hidden');
            document.getElementById('positionStats').classList.remove('hidden');
            document.getElementById('searchFilter').classList.remove('hidden');
            document.getElementById('mismatchTable').classList.remove('hidden');
        },

        /**
         * Generate TYPE별 Position별 통계 테이블
         */
        generatePositionStatistics(allEmployees) {
            // Group by TYPE and Position
            const stats = {
                'TYPE-1': {},
                'TYPE-2': {},
                'TYPE-3': {}
            };

            allEmployees.forEach(emp => {
                const type = emp.employeeType || 'TYPE-3';
                const position = emp.position || 'UNKNOWN';

                if (!stats[type][position]) {
                    stats[type][position] = {
                        total: 0,
                        receivingDashboard: 0,
                        receivingValidation: 0,
                        notReceivingDashboard: 0,
                        notReceivingValidation: 0,
                        mismatched: 0,
                        amountMatched: 0,
                        amountMismatched: 0,
                        calculationMethods: new Set()  // Phase 2.7: Collect unique calculation methods
                    };
                }

                const s = stats[type][position];
                s.total++;

                // Phase 2.7: Collect calculation method
                if (emp.calculationMethod) {
                    s.calculationMethods.add(emp.calculationMethod);
                }

                // Receiving status
                const dashboardReceiving = emp.dashboardIncentive > 0;
                const validationReceiving = emp.validatedIncentive > 0;

                if (dashboardReceiving) s.receivingDashboard++;
                else s.notReceivingDashboard++;

                if (validationReceiving) s.receivingValidation++;
                else s.notReceivingValidation++;

                // Receiving mismatch
                if (dashboardReceiving !== validationReceiving) {
                    s.mismatched++;
                }

                // Amount match
                if (emp.dashboardIncentive === emp.validatedIncentive) {
                    s.amountMatched++;
                } else {
                    s.amountMismatched++;
                }
            });

            // Display statistics for each TYPE with analysis
            this.displayTypeStatistics('type1StatsBody', stats['TYPE-1'], allEmployees.filter(e => e.employeeType === 'TYPE-1'));
            this.displayTypeStatistics('type2StatsBody', stats['TYPE-2'], allEmployees.filter(e => e.employeeType === 'TYPE-2'));
            this.displayTypeStatistics('type3StatsBody', stats['TYPE-3'], allEmployees.filter(e => e.employeeType === 'TYPE-3'));
        },

        /**
         * Display statistics table for one TYPE
         */
        displayTypeStatistics(tbodyId, positionStats, typeEmployees) {
            const tbody = document.getElementById(tbodyId);
            tbody.innerHTML = '';

            // Generate position discrepancy analysis
            const analysis = analyzePositionDiscrepancies(positionStats, typeEmployees);

            // Sort positions alphabetically
            const positions = Object.keys(positionStats).sort();

            if (positions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No data</td></tr>';
                return;
            }

            let typeTotal = {
                total: 0,
                receivingDashboard: 0,
                receivingValidation: 0,
                notReceivingDashboard: 0,
                notReceivingValidation: 0,
                mismatched: 0,
                amountMatched: 0,
                amountMismatched: 0
            };

            positions.forEach(position => {
                const s = positionStats[position];
                const row = document.createElement('tr');

                // Check if this position has discrepancies
                const hasDiscrepancy = analysis[position]?.hasDiscrepancy || false;

                // Phase 2.7: Format calculation methods (unique values)
                const methodsArray = s.calculationMethods ? Array.from(s.calculationMethods) : [];
                const methodsDisplay = methodsArray.length > 0
                    ? methodsArray.map(m => `<div class="small">${m}</div>`).join('')
                    : '-';

                // Calculate Match % for this position
                const matchPercent = s.total > 0 ? ((s.amountMatched / s.total) * 100).toFixed(1) : 0;
                const matchPercentClass = matchPercent == 100 ? 'table-success fw-bold' : (matchPercent >= 90 ? 'table-warning' : 'table-danger');

                row.innerHTML = `
                    <td style="white-space: nowrap; font-size: 0.7rem;">
                        ${position}
                        ${hasDiscrepancy ? `
                            <button class="btn btn-sm btn-warning ms-1 py-0 px-1" style="font-size: 0.6rem;"
                                    onclick="displayPositionAnalysis('${position}', ${JSON.stringify(analysis[position]).replace(/"/g, '&quot;')})"
                                    title="차이 원인 분석">
                                <i class="fas fa-search"></i>
                            </button>
                        ` : ''}
                    </td>
                    <td style="font-size: 0.65rem; max-width: 120px; overflow: hidden; text-overflow: ellipsis;">${methodsDisplay}</td>
                    <td>${s.total}</td>
                    <td${s.receivingDashboard !== s.receivingValidation ? ' class="table-danger fw-bold"' : ''}>${s.receivingDashboard}</td>
                    <td${s.receivingDashboard !== s.receivingValidation ? ' class="table-warning fw-bold"' : ''}>${s.receivingValidation}</td>
                    <td>${s.notReceivingDashboard}</td>
                    <td>${s.notReceivingValidation}</td>
                    <td${s.mismatched > 0 ? ' class="table-danger fw-bold"' : ''}>${s.mismatched}</td>
                    <td${s.amountMatched === s.total ? ' class="table-success"' : ''}>${s.amountMatched}</td>
                    <td${s.amountMismatched > 0 ? ' class="table-warning fw-bold"' : ''}>${s.amountMismatched}</td>
                    <td class="${matchPercentClass}">${matchPercent}%</td>
                `;

                tbody.appendChild(row);

                // Accumulate totals
                typeTotal.total += s.total;
                typeTotal.receivingDashboard += s.receivingDashboard;
                typeTotal.receivingValidation += s.receivingValidation;
                typeTotal.notReceivingDashboard += s.notReceivingDashboard;
                typeTotal.notReceivingValidation += s.notReceivingValidation;
                typeTotal.mismatched += s.mismatched;
                typeTotal.amountMatched += s.amountMatched;
                typeTotal.amountMismatched += s.amountMismatched;
            });

            // Add total row with Match %
            const totalMatchPercent = typeTotal.total > 0 ? ((typeTotal.amountMatched / typeTotal.total) * 100).toFixed(1) : 0;
            const totalMatchClass = totalMatchPercent == 100 ? 'table-success' : (totalMatchPercent >= 90 ? 'table-warning' : 'table-danger');

            const totalRow = document.createElement('tr');
            totalRow.classList.add('table-secondary', 'fw-bold');
            totalRow.innerHTML = `
                <td>TOTAL</td>
                <td class="text-muted">-</td>
                <td>${typeTotal.total}</td>
                <td>${typeTotal.receivingDashboard}</td>
                <td>${typeTotal.receivingValidation}</td>
                <td>${typeTotal.notReceivingDashboard}</td>
                <td>${typeTotal.notReceivingValidation}</td>
                <td${typeTotal.mismatched > 0 ? ' class="table-danger"' : ''}>${typeTotal.mismatched}</td>
                <td${typeTotal.amountMatched === typeTotal.total ? ' class="table-success"' : ''}>${typeTotal.amountMatched}</td>
                <td${typeTotal.amountMismatched > 0 ? ' class="table-warning"' : ''}>${typeTotal.amountMismatched}</td>
                <td class="${totalMatchClass}">${totalMatchPercent}%</td>
            `;
            tbody.appendChild(totalRow);
        },

        /**
         * Get human-readable condition name from condition number
         * Maps "Condition 1" to "Attendance Rate >= 88%", etc.
         */
        getConditionName(fieldName) {
            const conditionNames = {
                'Condition 1': 'Attendance Rate >= 88%',
                'Condition 2': 'Unapproved Absence <= 2 days',
                'Condition 3': 'Actual Working Days > 0',
                'Condition 4': 'Minimum Working Days >= 12',
                'Condition 5': 'Personal AQL: Current Month Failures = 0',
                'Condition 6': 'Personal AQL: No 3-month Consecutive Failures',
                'Condition 7': 'Team/Area AQL: No 3-month Consecutive Failures',
                'Condition 8': 'Area Reject Rate < 3%',
                'Condition 9': '5PRS Pass Rate >= 95%',
                'Condition 10': '5PRS Inspection Quantity >= 100',
                'Continuous Months': 'Continuous Months',
                'Incentive': 'Incentive Amount'
            };

            return conditionNames[fieldName] || fieldName;
        },

        /**
         * Get condition display value (PASS/FAIL/N/A)
         */
        getConditionDisplay(conditionResults, conditionNum, applicableConditions) {
            // Check if condition applies to this position
            if (!applicableConditions.includes(conditionNum)) {
                return '<span class="text-muted">N/A</span>';
            }

            const result = conditionResults[`condition_${conditionNum}`];

            if (result === 'PASS') {
                return '<span class="badge bg-success">✓</span>';
            } else if (result === 'FAIL') {
                return '<span class="badge bg-danger">✗</span>';
            } else {
                return '<span class="text-muted">-</span>';
            }
        },

        /**
         * Display mismatch table
         * TYPE-1/2/3별로 그룹화 + 10개 조건을 각각 컬럼으로 표시
         */
        displayMismatchTable(mismatches, allEmployees = []) {
            const tbody = document.getElementById('mismatchBody');
            tbody.innerHTML = '';

            // Store allEmployees for filtering (preserve existing filter/search if set)
            this._allEmployeesData = allEmployees;
            if (this._currentFilter === undefined) {
                this._currentFilter = 'mismatched';
            }
            if (this._searchTerm === undefined) {
                this._searchTerm = '';
            }

            if (mismatches.length === 0 && allEmployees.length === 0) {
                tbody.innerHTML = '<tr><td colspan="18" class="text-center">No data found</td></tr>';
                return;
            }

            // Determine which employees to show based on filter
            const employeesToShow = this._getFilteredEmployees(mismatches, allEmployees);

            if (employeesToShow.length === 0) {
                tbody.innerHTML = '<tr><td colspan="18" class="text-center">No mismatches found ✅</td></tr>';
                return;
            }

            // TYPE별로 그룹화
            const groupedByType = {
                'TYPE-1': [],
                'TYPE-2': [],
                'TYPE-3': []
            };

            employeesToShow.forEach(emp => {
                const type = emp.employeeType || 'TYPE-3';
                if (!groupedByType[type]) groupedByType[type] = [];
                groupedByType[type].push(emp);
            });

            // TYPE-1, TYPE-2, TYPE-3 순서로 표시
            ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(typeKey => {
                const typeGroup = groupedByType[typeKey];
                if (typeGroup.length === 0) return;

                // TYPE 헤더 행 추가
                const headerRow = document.createElement('tr');
                headerRow.classList.add('table-secondary', 'fw-bold');
                headerRow.innerHTML = `
                    <td colspan="18" class="text-center">
                        ${typeKey} (${typeGroup.length}명)
                    </td>
                `;
                tbody.appendChild(headerRow);

                // 각 직원 행 추가 - 10개 조건을 각각 컬럼으로 표시
                typeGroup.forEach(emp => {
                    const row = document.createElement('tr');

                    // Determine if this is a match or mismatch
                    const isMatch = emp.validatedIncentive === emp.dashboardIncentive;
                    row.classList.add(isMatch ? 'table-success-light' : 'mismatch-row');

                    // Generate condition columns (1-10)
                    const conditionCells = [];
                    for (let i = 1; i <= 10; i++) {
                        const display = this.getConditionDisplay(
                            emp.conditionResults || emp.validatedConditions,
                            i,
                            emp.applicableConditions || []
                        );
                        conditionCells.push(`<td class="text-center" style="padding: 2px 4px;">${display}</td>`);
                    }

                    // Match Status column
                    const matchStatus = isMatch
                        ? '<span class="badge bg-success" style="font-size: 0.6rem;">Matching</span>'
                        : '<span class="badge bg-danger" style="font-size: 0.6rem;">No Match</span>';

                    row.innerHTML = `
                        <td style="padding: 2px 4px; font-size: 0.7rem;">${emp.emp_no}</td>
                        <td style="padding: 2px 4px; font-size: 0.7rem; max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${emp.name}</td>
                        <td style="padding: 2px 4px; font-size: 0.7rem;">${typeKey}</td>
                        <td style="padding: 2px 4px; font-size: 0.65rem; max-width: 70px; overflow: hidden; text-overflow: ellipsis;"><strong>${emp.position}</strong></td>
                        ${conditionCells.join('')}
                        <td class="text-center" style="padding: 2px 4px;">${emp.continuousMonths !== null && emp.continuousMonths !== undefined ? emp.continuousMonths : '-'}</td>
                        <td class="text-success fw-bold" style="padding: 2px 4px; font-size: 0.65rem;">₫${(emp.validatedIncentive || 0).toLocaleString()}</td>
                        <td class="text-danger fw-bold" style="padding: 2px 4px; font-size: 0.65rem;">₫${(emp.dashboardIncentive || 0).toLocaleString()}</td>
                        <td class="text-center" style="padding: 2px 4px;">${matchStatus}</td>
                    `;

                    // Store data attributes for filtering
                    row.dataset.empNo = emp.emp_no;
                    row.dataset.name = emp.name;
                    row.dataset.isMatch = isMatch;

                    tbody.appendChild(row);
                });
            });
        },

        /**
         * Get filtered employees based on current filter and search term
         */
        _getFilteredEmployees(mismatches, allEmployees) {
            let result = [];

            // Apply filter
            switch (this._currentFilter) {
                case 'mismatched':
                    result = mismatches;
                    break;
                case 'matched':
                    result = allEmployees.filter(emp => emp.validatedIncentive === emp.dashboardIncentive);
                    break;
                case 'all':
                default:
                    result = allEmployees;
                    break;
            }

            // Apply search term
            if (this._searchTerm) {
                const term = this._searchTerm.toLowerCase();
                result = result.filter(emp =>
                    String(emp.emp_no || '').toLowerCase().includes(term) ||
                    String(emp.name || '').toLowerCase().includes(term)
                );
            }

            return result;
        },

        /**
         * Get condition result text for Excel export
         */
        getConditionResultText(conditionResults, conditionNum, applicableConditions) {
            if (!applicableConditions.includes(conditionNum)) {
                return 'N/A';
            }
            const result = conditionResults[`condition_${conditionNum}`];
            return result === 'PASS' ? '✓ PASS' : (result === 'FAIL' ? '✗ FAIL' : '-');
        },

        /**
         * Export mismatches to Excel
         * TYPE-1/2/3별로 그룹화 + 10개 조건을 각각 컬럼으로 내보내기
         */
        exportToExcel(mismatches) {
            const wb = XLSX.utils.book_new();

            // TYPE별로 그룹화
            const groupedByType = {
                'TYPE-1': [],
                'TYPE-2': [],
                'TYPE-3': []
            };

            mismatches.forEach(mismatch => {
                const type = mismatch.employeeType || 'TYPE-3';
                if (!groupedByType[type]) groupedByType[type] = [];
                groupedByType[type].push(mismatch);
            });

            // TYPE-1, TYPE-2, TYPE-3 순서로 시트 생성
            ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(typeKey => {
                const typeGroup = groupedByType[typeKey];
                if (typeGroup.length === 0) return;

                const exportData = [];
                typeGroup.forEach(mismatch => {
                    exportData.push({
                        'Employee ID': mismatch.emp_no,
                        'Name': mismatch.name,
                        'TYPE': typeKey,
                        'Position': mismatch.position,
                        'Cond1 (출근율≥88%)': this.getConditionResultText(mismatch.conditionResults, 1, mismatch.applicableConditions),
                        'Cond2 (무단≤2일)': this.getConditionResultText(mismatch.conditionResults, 2, mismatch.applicableConditions),
                        'Cond3 (실제>0일)': this.getConditionResultText(mismatch.conditionResults, 3, mismatch.applicableConditions),
                        'Cond4 (최소≥12일)': this.getConditionResultText(mismatch.conditionResults, 4, mismatch.applicableConditions),
                        'Cond5 (개인AQL)': this.getConditionResultText(mismatch.conditionResults, 5, mismatch.applicableConditions),
                        'Cond6 (AQL 3M)': this.getConditionResultText(mismatch.conditionResults, 6, mismatch.applicableConditions),
                        'Cond7 (팀AQL)': this.getConditionResultText(mismatch.conditionResults, 7, mismatch.applicableConditions),
                        'Cond8 (구역불량)': this.getConditionResultText(mismatch.conditionResults, 8, mismatch.applicableConditions),
                        'Cond9 (5PRS율)': this.getConditionResultText(mismatch.conditionResults, 9, mismatch.applicableConditions),
                        'Cond10 (5PRS량)': this.getConditionResultText(mismatch.conditionResults, 10, mismatch.applicableConditions),
                        'Continuous Months': mismatch.continuousMonths !== null && mismatch.continuousMonths !== undefined ? mismatch.continuousMonths : '-',
                        'Validated Incentive': mismatch.validatedIncentive,
                        'Dashboard Incentive': mismatch.dashboardIncentive
                    });
                });

                const ws = XLSX.utils.json_to_sheet(exportData);
                XLSX.utils.book_append_sheet(wb, ws, typeKey);
            });

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

            progressBar.style.width = '40%';
            progressBar.textContent = 'Building hierarchies...';

            // ============================================
            // Phase 2.6: Two-Pass Validation Strategy
            // ============================================
            // CRITICAL FIX (Issue #41): Use config month/year instead of today's date
            // For December 2025 validation, use end-of-month date (2025-12-31)
            // This ensures Condition 4 (Minimum Days) cutoff is correctly applied
            const monthNames = ['january', 'february', 'march', 'april', 'may', 'june',
                               'july', 'august', 'september', 'october', 'november', 'december'];
            const configMonth = allData.config.month || 'december';
            const configYear = allData.config.year || 2025;
            const monthIndex = monthNames.indexOf(configMonth.toLowerCase());
            // Create date for last day of month (day 31 will auto-adjust to correct last day)
            const currentDate = new Date(configYear, monthIndex + 1, 0);  // Last day of month
            console.log(`📅 Validation date set to: ${currentDate.toISOString().slice(0, 10)} (end of ${configMonth} ${configYear})`);
            const expectedResults = [];

            // Build subordinate mapping for manager calculations
            const subordinateMap = this.PositionCalculators.buildSubordinateMapping(allData.basicInfo);
            console.log(`📊 Subordinate mapping built: ${subordinateMap.size} managers with subordinates`);

            // Separate employees by TYPE
            const type1Employees = allData.basicInfo.filter(emp =>
                (emp['ROLE TYPE STD'] || emp['TYPE'] || '') === 'TYPE-1'
            );
            const type2Employees = allData.basicInfo.filter(emp =>
                (emp['ROLE TYPE STD'] || emp['TYPE'] || '') === 'TYPE-2'
            );
            const type3Employees = allData.basicInfo.filter(emp => {
                const empType = emp['ROLE TYPE STD'] || emp['TYPE'] || '';
                return empType !== 'TYPE-1' && empType !== 'TYPE-2';
            });

            console.log(`📊 Employee counts: TYPE-1=${type1Employees.length}, TYPE-2=${type2Employees.length}, TYPE-3=${type3Employees.length}`);

            // ==========================================
            // PASS 1: Validate TYPE-1 employees first
            // (Progressive: managers reference already-validated employees)
            // ==========================================
            // CRITICAL FIX (Issue #41): Order TYPE-1 employees by dependency
            // 1. ASSEMBLY INSPECTOR, MODEL MASTER, AUDITOR, TRAINER (base positions)
            // 2. LINE LEADER (needs ASSEMBLY INSPECTOR results)
            // 3. GROUP LEADER (needs LINE LEADER results)
            // 4. SUPERVISOR (needs LINE LEADER results via GROUP LEADER logic)
            // 5. MANAGER (needs LINE LEADER results via GROUP LEADER logic)
            const positionOrder = {
                'ASSEMBLY INSPECTOR': 1,
                'MODEL MASTER': 1,
                'AUDITOR': 1,
                'TRAINER': 1,
                'LINE LEADER': 2,
                'GROUP LEADER': 3,
                'SUPERVISOR': 4,
                'A.SUPERVISOR': 4,
                'MANAGER': 5,
                'A.MANAGER': 5
            };

            const getPositionPriority = (emp) => {
                const pos = (emp['QIP POSITION 1ST  NAME'] || emp['Position'] || '').toUpperCase();
                for (const [key, priority] of Object.entries(positionOrder)) {
                    if (pos.includes(key)) return priority;
                }
                return 0;  // Unknown positions first
            };

            // Sort TYPE-1 employees by position dependency order
            const sortedType1Employees = [...type1Employees].sort((a, b) =>
                getPositionPriority(a) - getPositionPriority(b)
            );

            console.log(`📊 TYPE-1 position ordering applied (base → LINE LEADER → GROUP LEADER → SUPERVISOR → MANAGER)`);

            progressBar.style.width = '50%';
            progressBar.textContent = 'Validating TYPE-1 employees...';

            const type1Results = [];
            sortedType1Employees.forEach(employee => {
                const context = {
                    subordinateMap: subordinateMap,
                    allValidatedEmployees: type1Results,  // Pass already-validated TYPE-1 employees
                    aqlConfig: allData.aqlInspectorConfig || {}
                };

                const result = this.Calculator.validateEmployee(
                    employee['Employee No'],
                    allData,
                    this.state.previousMonthData,
                    currentDate,
                    context
                );

                if (result) {
                    type1Results.push(result);
                }
            });

            console.log(`✅ TYPE-1 validation complete: ${type1Results.length} employees`);

            // ==========================================
            // Calculate TYPE-1 Position Averages (for TYPE-2)
            // Only include receiving employees (incentive > 0)
            // ==========================================
            progressBar.style.width = '60%';
            progressBar.textContent = 'Calculating TYPE-1 averages...';

            const type1Averages = {};
            type1Results.forEach(emp => {
                const position = emp.position || '';
                if (!type1Averages[position]) {
                    type1Averages[position] = {
                        total: 0,
                        count: 0,
                        receivingSum: 0,
                        receivingCount: 0,
                        average: 0
                    };
                }
                type1Averages[position].total += emp.incentiveAmount || 0;
                type1Averages[position].count++;
                if (emp.incentiveAmount > 0) {
                    type1Averages[position].receivingSum += emp.incentiveAmount;
                    type1Averages[position].receivingCount++;
                }
            });

            // Calculate averages (receiving only)
            Object.keys(type1Averages).forEach(position => {
                const posData = type1Averages[position];
                if (posData.receivingCount > 0) {
                    posData.average = Math.round(posData.receivingSum / posData.receivingCount);
                }
            });

            console.log(`📊 TYPE-1 averages calculated for ${Object.keys(type1Averages).length} positions`);

            // ==========================================
            // PASS 2: Validate TYPE-2 employees
            // (Using TYPE-1 position averages)
            // ==========================================
            progressBar.style.width = '70%';
            progressBar.textContent = 'Validating TYPE-2 employees...';

            const type2Results = [];
            type2Employees.forEach(employee => {
                const context = {
                    subordinateMap: subordinateMap,
                    allValidatedEmployees: [...type1Results, ...type2Results],
                    aqlConfig: allData.aqlInspectorConfig || {},
                    type1Averages: type1Averages  // Pass TYPE-1 averages
                };

                const result = this.Calculator.validateEmployee(
                    employee['Employee No'],
                    allData,
                    this.state.previousMonthData,
                    currentDate,
                    context
                );

                if (result) {
                    type2Results.push(result);
                }
            });

            console.log(`✅ TYPE-2 validation complete: ${type2Results.length} employees`);

            // ==========================================
            // PASS 3: Validate TYPE-3 employees
            // (Always 0 VND)
            // ==========================================
            const type3Results = [];
            type3Employees.forEach(employee => {
                const result = this.Calculator.validateEmployee(
                    employee['Employee No'],
                    allData,
                    this.state.previousMonthData,
                    currentDate,
                    {}  // No special context needed
                );

                if (result) {
                    type3Results.push(result);
                }
            });

            console.log(`✅ TYPE-3 validation complete: ${type3Results.length} employees`);

            // Combine all results
            expectedResults.push(...type1Results, ...type2Results, ...type3Results);
            console.log(`✅ Total validation complete: ${expectedResults.length} employees`);

            progressBar.style.width = '80%';
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

            // Store mismatches for search/filter functionality
            this.state.mismatches = validationReport.mismatches;
            this.state.allEmployees = validationReport.allEmployees;

            this.UIController.displayMismatchTable(validationReport.mismatches, validationReport.allEmployees);

            // Display working days information (NEW - User Request)
            displayWorkingDaysInfo(
                allData.config,
                allData.attendance,
                allData.dashboardOutput
            );

            // Display condition-by-condition validation (NEW - User Request)
            validateConditions(
                allData.attendance,
                allData.aql,
                allData.prs,
                allData.dashboardOutput
            );

            // Display additional validations (NEW - User Request)
            // Phase 3.3: Updated to pass config for 3-layer TYPE-2 validation
            displayAdditionalValidations(
                validationReport.allEmployees,
                allData.attendance,
                allData.dashboardOutput,
                allData.positionMatrix,
                allData.config  // Phase 3: config for month/year info in 3-layer validation
            );

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

            // Enable validation button if file is already uploaded
            const fileInput = document.getElementById('previousMonthFile');
            if (fileInput.files.length > 0 && ValidationEngine.state.fileUploaded) {
                document.getElementById('startValidation').disabled = false;
            }
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

                // Mark file as uploaded
                ValidationEngine.state.fileUploaded = true;

                // Enable button only if month is also selected
                const monthKey = ValidationEngine.state.selectedMonth;
                if (monthKey) {
                    document.getElementById('startValidation').disabled = false;
                } else {
                    uploadStatus.textContent += '\n⚠️ Please select a month first';
                }
            } else {
                uploadStatus.classList.add('error');
                uploadStatus.textContent = '❌ ' + validation.errors.join(', ');
                ValidationEngine.state.fileUploaded = false;
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

    // ============================================
    // Search and Filter Event Handlers
    // ============================================

    // Search box - filter by employee ID or name
    const searchBox = document.getElementById('searchBox');
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            const searchTerm = e.target.value.trim();
            ValidationEngine.UIController._searchTerm = searchTerm;

            // Re-render the table with current filter and new search term
            if (ValidationEngine.state.mismatches && ValidationEngine.state.allEmployees) {
                ValidationEngine.UIController.displayMismatchTable(
                    ValidationEngine.state.mismatches,
                    ValidationEngine.state.allEmployees
                );
            }
        });
    }

    // Filter type dropdown - filter by All/Matched/Mismatched
    const filterType = document.getElementById('filterType');
    if (filterType) {
        filterType.addEventListener('change', (e) => {
            const filterValue = e.target.value;
            ValidationEngine.UIController._currentFilter = filterValue;

            // Re-render the table with new filter
            if (ValidationEngine.state.mismatches && ValidationEngine.state.allEmployees) {
                ValidationEngine.UIController.displayMismatchTable(
                    ValidationEngine.state.mismatches,
                    ValidationEngine.state.allEmployees
                );
            }
        });
    }
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

// ============================================================================
// Working Days Information Display
// ============================================================================

function displayWorkingDaysInfo(config, attendanceData, dashboardData) {
    const section = document.getElementById('workingDaysInfo');
    section.classList.remove('hidden');

    // Config working days
    const configDays = config.working_days;
    document.getElementById('configWorkingDays').textContent = `${configDays}일`;

    // Attendance file working days
    const attendanceDays = attendanceData.length > 0 ? attendanceData[0]['TOTAL WORK DAY'] : null;
    document.getElementById('totalWorkingDays').textContent = attendanceDays ? `${attendanceDays}일` : 'N/A';

    // Working date range
    document.getElementById('workingDateRange').textContent = '2025.12.01 ~ 2025.12.31';

    // Dashboard match check
    let matchStatus = '';
    if (attendanceDays === configDays) {
        matchStatus = `<span class="badge bg-success"><i class="fas fa-check"></i> 일치 (${configDays}일)</span>`;
    } else {
        matchStatus = `<span class="badge bg-danger"><i class="fas fa-times"></i> 불일치 (Config: ${configDays}일 vs Attendance: ${attendanceDays}일)</span>`;
    }
    document.getElementById('dashboardWorkingDaysMatch').innerHTML = matchStatus;
}

// ============================================================================
// Condition Validation Functions
// ============================================================================

function validateConditions(attendanceData, aqlData, prsData, dashboardData) {
    const section = document.getElementById('conditionValidation');
    section.classList.remove('hidden');

    // 조건 정의
    const conditions = [
        {
            id: 1,
            category: 'attendance',
            name: 'Cond1: 출근율 ≥ 88%',
            nameEn: 'Attendance Rate ≥ 88%',
            checkFn: (emp) => emp['Attendance Rate (%)'] >= 88,
            getValueFn: (emp) => emp['Attendance Rate (%)'] ? `${emp['Attendance Rate (%)'].toFixed(1)}%` : 'N/A',
            dashboardCol: 'cond_1_attendance_rate'
        },
        {
            id: 2,
            category: 'attendance',
            name: 'Cond2: 무단결근 ≤ 2일',
            nameEn: 'Unapproved Absence ≤ 2 days',
            checkFn: (emp) => (emp['Unapproved Absences'] || 0) <= 2,
            getValueFn: (emp) => `${emp['Unapproved Absences'] || 0}일`,
            dashboardCol: 'cond_2_unapproved_absence'
        },
        {
            id: 3,
            category: 'attendance',
            name: 'Cond3: 실제근무일 > 0',
            nameEn: 'Actual Working Days > 0',
            checkFn: (emp) => (emp['ACTUAL WORK DAY'] || 0) > 0,
            getValueFn: (emp) => `${emp['ACTUAL WORK DAY'] || 0}일`,
            dashboardCol: 'cond_3_actual_working_days'
        },
        {
            id: 4,
            category: 'attendance',
            name: 'Cond4: 최소근무일 ≥ 12',
            nameEn: 'Minimum Days ≥ 12',
            checkFn: (emp) => (emp['ACTUAL WORK DAY'] || 0) >= 12,
            getValueFn: (emp) => `${emp['ACTUAL WORK DAY'] || 0}일`,
            dashboardCol: 'cond_4_minimum_days'
        },
        {
            id: 5,
            category: 'aql',
            name: 'Cond5: 개인 AQL Fail = 0',
            nameEn: 'Personal AQL Failure = 0',
            checkFn: (emp) => {
                // Use dashboard evaluation as source of truth
                const dashValue = emp.dashboard?.['cond_5_aql_personal_failure'];
                return dashValue === 'PASS' || dashValue === 'NOT_APPLICABLE';
            },
            getValueFn: (emp) => emp.dashboard?.['cond_5_aql_personal_failure'] || 'N/A',
            dashboardCol: 'cond_5_aql_personal_failure'
        },
        {
            id: 6,
            category: 'aql',
            name: 'Cond6: 3개월 연속 AQL FAIL 없음',
            nameEn: 'No 3-Month Consecutive AQL Failures',
            checkFn: (emp) => {
                const dashValue = emp.dashboard?.['cond_6_aql_continuous'];
                return dashValue === 'PASS' || dashValue === 'NOT_APPLICABLE';
            },
            getValueFn: (emp) => emp.dashboard?.['cond_6_aql_continuous'] || 'N/A',
            dashboardCol: 'cond_6_aql_continuous'
        },
        {
            id: 7,
            category: 'aql',
            name: 'Cond7: 팀/구역 AQL 조건',
            nameEn: 'Team/Area AQL Condition',
            checkFn: (emp) => {
                const dashValue = emp.dashboard?.['cond_7_aql_team_area'];
                return dashValue === 'PASS' || dashValue === 'NOT_APPLICABLE';
            },
            getValueFn: (emp) => emp.dashboard?.['cond_7_aql_team_area'] || 'N/A',
            dashboardCol: 'cond_7_aql_team_area'
        },
        {
            id: 8,
            category: 'aql',
            name: 'Cond8: 구역 불량률 < 3%',
            nameEn: 'Area Reject Rate < 3%',
            checkFn: (emp) => {
                const dashValue = emp.dashboard?.['cond_8_area_reject'];
                return dashValue === 'PASS' || dashValue === 'NOT_APPLICABLE';
            },
            getValueFn: (emp) => emp.dashboard?.['cond_8_area_reject'] || 'N/A',
            dashboardCol: 'cond_8_area_reject'
        },
        {
            id: 9,
            category: 'prs',
            name: 'Cond9: 5PRS 통과율 ≥ 95%',
            nameEn: '5PRS Pass Rate ≥ 95%',
            checkFn: (emp) => {
                const dashValue = emp.dashboard?.['cond_9_5prs_pass_rate'];
                return dashValue === 'PASS' || dashValue === 'NOT_APPLICABLE';
            },
            getValueFn: (emp) => emp.dashboard?.['cond_9_5prs_pass_rate'] || 'N/A',
            dashboardCol: 'cond_9_5prs_pass_rate'
        },
        {
            id: 10,
            category: 'prs',
            name: 'Cond10: 5PRS 검사량 ≥ 100',
            nameEn: '5PRS Inspection Qty ≥ 100',
            checkFn: (emp) => {
                const dashValue = emp.dashboard?.['cond_10_5prs_inspection_qty'];
                return dashValue === 'PASS' || dashValue === 'NOT_APPLICABLE';
            },
            getValueFn: (emp) => emp.dashboard?.['cond_10_5prs_inspection_qty'] || 'N/A',
            dashboardCol: 'cond_10_5prs_inspection_qty'
        }
    ];

    // Merge data
    const mergedData = attendanceData.map(attEmp => {
        const empNo = attEmp['ID No'];
        const dashEmp = dashboardData.find(d => String(d['Employee No']) === String(empNo));
        return {
            ...attEmp,
            dashboard: dashEmp || {}
        };
    });

    // Validate each condition
    conditions.forEach(cond => {
        const results = {
            total: mergedData.length,
            failed: 0,
            failedWithIncentive: 0,
            dashboardMismatch: 0,
            failedEmployees: []
        };

        mergedData.forEach(emp => {
            const passed = cond.checkFn(emp);
            const dashboardValue = emp.dashboard[cond.dashboardCol];
            const hasIncentive = (emp.dashboard['December_Incentive'] || 0) > 0;

            if (!passed) {
                results.failed++;
                if (hasIncentive) {
                    results.failedWithIncentive++;
                }

                results.failedEmployees.push({
                    empNo: emp['ID No'],
                    name: emp['Last name'],
                    value: cond.getValueFn(emp),
                    incentive: emp.dashboard['December_Incentive'] || 0,
                    dashboardCheck: dashboardValue
                });
            }

            // Dashboard mismatch check
            if (dashboardValue && dashboardValue !== 'NOT_APPLICABLE') {
                const dashboardPassed = dashboardValue === 'PASS';
                if (passed !== dashboardPassed) {
                    results.dashboardMismatch++;
                }
            }
        });

        // Display condition card
        displayConditionCard(cond, results);
    });
}

function displayConditionCard(condition, results) {
    const containerMap = {
        'attendance': 'attendanceConditions',
        'aql': 'aqlConditions',
        'prs': 'prsConditions'
    };

    const container = document.getElementById(containerMap[condition.category]);
    if (!container) return;

    const cardHtml = `
        <div class="col-md-6 mb-3">
            <div class="card h-100 ${results.failedWithIncentive > 0 ? 'border-danger' : results.dashboardMismatch > 0 ? 'border-warning' : 'border-success'}">
                <div class="card-header ${results.failedWithIncentive > 0 ? 'bg-danger text-white' : results.dashboardMismatch > 0 ? 'bg-warning' : 'bg-light'}">
                    <strong>${condition.name}</strong>
                    <br><small class="text-muted">${condition.nameEn}</small>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-4 text-center">
                            <h6>조건 미달</h6>
                            <p class="display-6 ${results.failed > 0 ? 'text-danger' : 'text-success'}">${results.failed}</p>
                            <small>명</small>
                        </div>
                        <div class="col-4 text-center border-start">
                            <h6>인센티브 수령</h6>
                            <p class="display-6 ${results.failedWithIncentive > 0 ? 'text-danger' : 'text-success'}">${results.failedWithIncentive}</p>
                            <small>명</small>
                        </div>
                        <div class="col-4 text-center border-start">
                            <h6>Dashboard 불일치</h6>
                            <p class="display-6 ${results.dashboardMismatch > 0 ? 'text-warning' : 'text-success'}">${results.dashboardMismatch}</p>
                            <small>명</small>
                        </div>
                    </div>

                    ${results.failedWithIncentive > 0 ? `
                        <div class="alert alert-danger mt-3 mb-0">
                            <strong><i class="fas fa-exclamation-triangle"></i> 오류 발견!</strong><br>
                            조건 미달인데 인센티브를 받은 직원 ${results.failedWithIncentive}명
                        </div>
                    ` : results.dashboardMismatch > 0 ? `
                        <div class="alert alert-warning mt-3 mb-0">
                            <strong><i class="fas fa-exclamation-circle"></i> 검증 필요</strong><br>
                            Dashboard 조건 판정과 불일치 ${results.dashboardMismatch}명
                        </div>
                    ` : results.failed === 0 ? `
                        <div class="alert alert-success mt-3 mb-0">
                            <i class="fas fa-check-circle"></i> 모든 직원이 조건 충족
                        </div>
                    ` : `
                        <div class="alert alert-success mt-3 mb-0">
                            <i class="fas fa-check-circle"></i> 조건 미달자 모두 0 VND
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', cardHtml);
}

// ============================================================================
// 연속월 검증 함수 (Continuous Months Validation)
// ============================================================================
/**
 * Validates continuous months calculation
 * @param {Array} allEmployees - All employees from validation
 * @param {Array} previousMonthData - Previous month data (if available)
 * @param {Object} positionMatrix - Position condition matrix
 * @returns {Object} Validation results with two sub-validations
 */
function validateContinuousMonths(allEmployees, previousMonthData, positionMatrix) {
    // FIX (Issue #41): Removed PROGRESSION_TABLE check - non-standard amounts exist for:
    // - AQL Inspector (3-part formula: Part1 + Part2 + Part3)
    // - LINE LEADER (subordinate-based)
    // - GROUP LEADER/SUPERVISOR/MANAGER (multiplier-based)
    // - TYPE-2 (average-based)

    const results = {
        amountConsistency: { total: 0, correct: 0, mismatched: 0, employees: [] },
        incrementLogic: { total: 0, correct: 0, mismatched: 0, employees: [], skipped: false, skipReason: '' }
    };

    // FIX (Issue #41): Use previousContinuousMonths from allEmployees (dashboard CSV data)
    // instead of trying to get it from previousMonthData (user-uploaded file)

    // FIX (Issue #41 Phase 2): Check if Previous_Continuous_Months data is reliable
    // Python engine bug: always reads july_continuous_months instead of dynamic previous month
    // Detect unreliable data: all values are 0 or empty
    const type1Employees = allEmployees.filter(emp => {
        const position = emp.position || '';
        return ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINER', 'LINE LEADER']
            .some(p => position.toUpperCase().includes(p));
    });

    const prevMonthsValues = type1Employees
        .map(emp => parseInt(emp.previousContinuousMonths || 0))
        .filter(v => !isNaN(v));

    const allZeros = prevMonthsValues.every(v => v === 0);

    // If all Previous_Continuous_Months are 0, skip increment logic validation
    // This indicates Python engine bug: hardcoded july_continuous_months instead of dynamic lookup
    if (allZeros && prevMonthsValues.length > 0) {
        results.incrementLogic.skipped = true;
        results.incrementLogic.skipReason = 'Python 계산 엔진 버그: Previous_Continuous_Months 컬럼이 모두 0입니다 (step1_인센티브_계산_개선버전.py:4682-4683의 july_continuous_months 하드코딩 문제)';
    }

    allEmployees.forEach(emp => {
        const position = emp.position || '';
        // TYPE-1 positions that use continuous months
        const isType1 = ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINER', 'LINE LEADER']
            .some(p => position.toUpperCase().includes(p));

        if (!isType1) return;  // Skip TYPE-2/3

        const empId = String(emp.emp_no || '').trim();  // FIX: was employeeId, now emp_no
        const currentMonths = parseInt(emp.continuousMonths || 0);
        const actualAmount = parseFloat(emp.dashboardIncentive || 0);  // FIX: was incentive, now dashboardIncentive

        // Validation 1: Amount Consistency (skipped - amounts vary by position type)
        // Only increment logic validation is meaningful for continuous months
        results.amountConsistency.total++;
        results.amountConsistency.correct++;  // Skip amount validation (non-standard amounts)

        // Validation 2: Increment Logic
        // Skip if data is unreliable
        if (results.incrementLogic.skipped) {
            results.incrementLogic.total++;
            return;  // Don't count as error or correct
        }

        // FIX (Issue #41): Use previousContinuousMonths from dashboard CSV (via allEmployees)
        const prevMonths = parseInt(emp.previousContinuousMonths || 0);
        const allConditionsPass = emp.allConditionsPass || false;  // FIX: use stored value
        const expected = allConditionsPass ? Math.min(prevMonths + 1, 15) : 0;

        results.incrementLogic.total++;
        if (currentMonths === expected) {
            results.incrementLogic.correct++;
        } else {
            results.incrementLogic.mismatched++;
            results.incrementLogic.employees.push({
                employeeId: empId,
                employeeName: emp.name,  // FIX: was employeeName, now name
                position: position,
                previousMonths: prevMonths,
                currentMonths: currentMonths,
                expected: expected,
                allConditionsPass: allConditionsPass
            });
        }
    });

    return results;
}

// ============================================================================
// 포지션별 차이 분석 함수 (Position-level Discrepancy Analysis)
// ============================================================================
function analyzePositionDiscrepancies(positionStats, allEmployees) {
    const analysis = {};

    Object.keys(positionStats).forEach(position => {
        const stats = positionStats[position];
        const positionEmployees = allEmployees.filter(emp => emp.position === position);

        // 차이 분석
        const receivingMismatch = stats.receivingDashboard !== stats.receivingValidation;
        const amountMismatch = stats.amountMismatched > 0;

        if (!receivingMismatch && !amountMismatch) {
            analysis[position] = {hasDiscrepancy: false};
            return;
        }

        analysis[position] = {
            hasDiscrepancy: true,
            receivingMismatch: receivingMismatch,
            amountMismatch: amountMismatch,
            details: {
                dashboardReceiving: stats.receivingDashboard,
                validationReceiving: stats.receivingValidation,
                amountMatched: stats.amountMatched,
                amountMismatched: stats.amountMismatched
            },
            employees: positionEmployees.filter(emp =>
                emp.dashboardIncentive !== emp.validatedIncentive ||
                (emp.dashboardIncentive > 0) !== (emp.validatedIncentive > 0)
            )
        };
    });

    return analysis;
}

function displayPositionAnalysis(position, analysis) {
    if (!analysis || !analysis.hasDiscrepancy) {
        alert(`${position}: 차이 없음 (No discrepancies)`);
        return;
    }

    let message = `📊 ${position} 차이 분석\n\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n\n`;

    if (analysis.receivingMismatch) {
        message += `⚠️ 수령자 수 불일치:\n`;
        message += `  • Dashboard: ${analysis.details.dashboardReceiving}명\n`;
        message += `  • Validation: ${analysis.details.validationReceiving}명\n`;
        message += `  • 차이: ${Math.abs(analysis.details.dashboardReceiving - analysis.details.validationReceiving)}명\n\n`;
    }

    if (analysis.amountMismatch) {
        message += `💰 금액 불일치:\n`;
        message += `  • 일치: ${analysis.details.amountMatched}명\n`;
        message += `  • 불일치: ${analysis.details.amountMismatched}명\n\n`;
    }

    message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
    message += `불일치 직원 목록 (${analysis.employees.length}명):\n\n`;

    analysis.employees.slice(0, 10).forEach(emp => {
        message += `• ${emp.employeeId} - ${emp.employeeName}\n`;
        message += `  Dashboard: ${emp.dashboardIncentive.toLocaleString()} VND\n`;
        message += `  Validation: ${emp.validatedIncentive.toLocaleString()} VND\n`;
        message += `  차이: ${Math.abs(emp.dashboardIncentive - emp.validatedIncentive).toLocaleString()} VND\n\n`;
    });

    if (analysis.employees.length > 10) {
        message += `... 외 ${analysis.employees.length - 10}명 더 있음\n`;
    }

    alert(message);
}

// ============================================================================
// 기타 조건 검증 함수 (Additional Validation Conditions)
// ============================================================================

/**
 * 퇴사자 인센티브 검증
 * Check if any resigned employees received incentives
 */
function validateResignedEmployees(attendanceData, dashboardData) {
    const results = {
        totalResigned: 0,
        resignedWithIncentive: 0,
        employees: []
    };

    const monthStart = new Date(attendanceData[0]?.Date || '2025-12-01').setDate(1);

    attendanceData.forEach(emp => {
        const stopDate = emp['Stop working Date'];
        if (!stopDate || stopDate === '') return;

        const stopDateTime = new Date(stopDate).getTime();
        if (stopDateTime >= monthStart) return; // 해당월 이후 퇴사는 제외

        results.totalResigned++;

        // Dashboard 인센티브 확인
        const dashboardEmp = dashboardData.find(d => d['Employee No'] === emp['Emp No']);
        const dashboardIncentive = dashboardEmp ? (parseFloat(dashboardEmp['December_Incentive'] || 0)) : 0;

        if (dashboardIncentive > 0) {
            results.resignedWithIncentive++;
            results.employees.push({
                employeeId: emp['Emp No'],
                employeeName: emp['Emp Name'],
                stopDate: stopDate,
                incentive: dashboardIncentive
            });
        }
    });

    return results;
}

/**
 * TYPE-2 3-Layer Validation (Phase 3.2)
 * Layer 1: Resignation Check - Employees resigned before month should have 0 VND
 * Layer 2: 100% Condition Fulfillment Rule - Must pass ALL applicable conditions
 * Layer 3: TYPE-1 Average Match - Should match TYPE-1 reference position average
 *
 * @param {Array} allEmployees - All validated employees with condition results
 * @param {Object} positionMatrix - Position configuration with TYPE-2 mapping
 * @param {Object} config - Monthly config with year, month_num for resignation check
 * @param {Array} attendanceData - Attendance data with Stop working Date (optional, for Layer 1)
 */
function validateType2Averages(allEmployees, positionMatrix, config = {}, attendanceData = []) {
    const results = {
        positions: {},
        totalMismatches: 0,
        // Phase 3.2: New validation error categories
        validationErrors: {
            resignedWithIncentive: 0,       // Layer 1: Resigned but received incentive
            failedConditionsWithIncentive: 0, // Layer 2: Failed conditions but received incentive
            totalValidationFailures: 0       // Total Layer 1 + Layer 2 failures
        },
        problematicEmployees: [],  // Employees with Layer 1/2 issues
        type1Averages: {}          // Expose TYPE-1 averages for UI display
    };

    // Calculate month start date for resignation check (Layer 1)
    const year = config.year || 2025;
    const monthNum = config.month_num || 12;
    const monthStart = new Date(`${year}-${String(monthNum).padStart(2, '0')}-01`).getTime();

    // TYPE-2 positions mapping
    const type2Mapping = positionMatrix?.type_2_incentive_calculation || {};

    // Calculate TYPE-1 averages (receiving only - for Layer 3)
    const type1Averages = {};
    allEmployees.filter(emp => emp.employeeType === 'TYPE-1').forEach(emp => {
        const position = emp.position;
        if (!type1Averages[position]) {
            type1Averages[position] = { total: 0, count: 0, receiving: 0, receivingSum: 0, average: 0 };
        }
        type1Averages[position].total += emp.validatedIncentive || 0;
        type1Averages[position].count++;
        if ((emp.validatedIncentive || 0) > 0) {
            type1Averages[position].receiving++;
            type1Averages[position].receivingSum += emp.validatedIncentive;
        }
    });

    // Calculate averages (receiving only)
    Object.keys(type1Averages).forEach(position => {
        const data = type1Averages[position];
        type1Averages[position].average = data.receiving > 0
            ? Math.round(data.receivingSum / data.receiving)
            : 0;
    });

    results.type1Averages = type1Averages;

    // ===== 3-Layer Validation for TYPE-2 Employees =====
    allEmployees.filter(emp => emp.employeeType === 'TYPE-2').forEach(emp => {
        const position = emp.position || '';
        const normalizedPosition = position.trim().toUpperCase();
        const actualIncentive = emp.validatedIncentive || 0;

        // Find mapping entry (same logic as calculateIncentiveAmount)
        let mappingEntry = null;

        // Try exact match first
        for (const [key, value] of Object.entries(type2Mapping)) {
            if (key.startsWith('_')) continue;
            if (normalizedPosition === key.toUpperCase()) {
                mappingEntry = value;
                break;
            }
        }

        // Try partial match if no exact match
        if (!mappingEntry) {
            for (const [key, value] of Object.entries(type2Mapping)) {
                if (key.startsWith('_')) continue;
                if (normalizedPosition.includes(key.toUpperCase())) {
                    mappingEntry = value;
                    break;
                }
            }
        }

        // Use default mapping if still no match
        if (!mappingEntry && type2Mapping._default) {
            mappingEntry = type2Mapping._default;
        }

        // Extract reference position and multiplier
        const referencePosition = mappingEntry?.reference_type1_position || null;
        const multiplier = mappingEntry?.multiplier || 1.0;

        // ----- Layer 1: Resignation Check -----
        const stopWorkingDate = emp.stopWorkingDate;
        const isResigned = stopWorkingDate &&
            !isNaN(new Date(stopWorkingDate).getTime()) &&
            new Date(stopWorkingDate).getTime() < monthStart;

        if (isResigned && actualIncentive > 0) {
            results.validationErrors.resignedWithIncentive++;
            results.validationErrors.totalValidationFailures++;
            results.problematicEmployees.push({
                emp_no: emp.emp_no,
                name: emp.name,
                position: position,
                issue: 'RESIGNED_WITH_INCENTIVE',
                stopWorkingDate: stopWorkingDate,
                incentive: actualIncentive,
                layer: 1
            });
        }

        // ----- Layer 2: 100% Condition Fulfillment Rule -----
        const allConditionsPass = emp.allConditionsPass || false;
        const conditionsPassed = emp.conditionsPassed || 0;
        const conditionsApplicable = emp.conditionsApplicable || 0;

        if (!allConditionsPass && actualIncentive > 0) {
            results.validationErrors.failedConditionsWithIncentive++;
            results.validationErrors.totalValidationFailures++;
            results.problematicEmployees.push({
                emp_no: emp.emp_no,
                name: emp.name,
                position: position,
                issue: '100%_RULE_VIOLATION',
                conditionsPassed: conditionsPassed,
                conditionsApplicable: conditionsApplicable,
                incentive: actualIncentive,
                layer: 2
            });
        }

        // ----- Layer 3: TYPE-1 Average Match -----
        // Only validate if employee SHOULD receive incentive (passed all conditions & not resigned)
        if (!referencePosition) return;

        if (allConditionsPass && !isResigned) {
            const baseAvg = type1Averages[referencePosition]?.average || 0;
            const expectedAvg = Math.round(baseAvg * multiplier);  // Apply multiplier

            if (!results.positions[position]) {
                results.positions[position] = {
                    referencePosition: referencePosition,
                    multiplier: multiplier,
                    baseAverage: baseAvg,
                    expectedAverage: expectedAvg,
                    type1ReceivingCount: type1Averages[referencePosition]?.receiving || 0,
                    matches: 0,
                    mismatches: 0,
                    employees: []
                };
            }

            const isMatch = actualIncentive === expectedAvg;
            if (isMatch) {
                results.positions[position].matches++;
            } else {
                results.positions[position].mismatches++;
                results.totalMismatches++;
                results.positions[position].employees.push({
                    emp_no: emp.emp_no,
                    name: emp.name,
                    expected: expectedAvg,
                    actual: actualIncentive,
                    difference: actualIncentive - expectedAvg
                });
            }
        }
    });

    return results;
}

/**
 * Display additional validations (퇴사자 인센티브 + TYPE-2 3-Layer 평균)
 * Phase 3.3-3.4: Enhanced to show 3-layer validation results
 */
function displayAdditionalValidations(allEmployees, attendanceData, dashboardData, positionMatrix, config = {}) {
    // 1. 퇴사자 인센티브 검증
    const resignedResults = validateResignedEmployees(attendanceData, dashboardData);

    document.getElementById('totalResigned').textContent = resignedResults.totalResigned;
    document.getElementById('resignedWithIncentive').textContent = resignedResults.resignedWithIncentive;

    const resignedMessage = document.getElementById('resignedValidationMessage');
    if (resignedResults.resignedWithIncentive > 0) {
        resignedMessage.innerHTML = `
            <div class="alert alert-danger mb-0">
                <strong><i class="fas fa-exclamation-triangle"></i> 오류 발견!</strong><br>
                ${resignedResults.resignedWithIncentive}명의 퇴사자가 인센티브를 받았습니다
                <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                    ${resignedResults.employees.map(emp => `
                        <div class="border-bottom py-1">
                            • ${emp.employeeId} - ${emp.employeeName}<br>
                            퇴사일: ${emp.stopDate}, 인센티브: ${emp.incentive.toLocaleString()} VND
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        document.getElementById('resignedEmployeesCard').querySelector('.card-header')
            .classList.add('bg-danger', 'text-white');
    } else {
        resignedMessage.innerHTML = `
            <div class="alert alert-success mb-0">
                <i class="fas fa-check-circle"></i> 모든 퇴사자가 0 VND
            </div>
        `;
        document.getElementById('resignedEmployeesCard').querySelector('.card-header')
            .classList.add('bg-success', 'text-white');
    }

    // 2. TYPE-2 3-Layer 검증 (Phase 3.2-3.4)
    const type2Results = validateType2Averages(allEmployees, positionMatrix, config, attendanceData);

    const type2Total = Object.values(type2Results.positions).reduce((sum, pos) =>
        sum + pos.matches + pos.mismatches, 0);

    document.getElementById('type2TotalEmployees').textContent = type2Total;
    document.getElementById('type2Mismatches').textContent = type2Results.totalMismatches;

    // Phase 3.4: Display Layer 1 & Layer 2 error counts (if elements exist)
    const layer1Element = document.getElementById('type2ResignedErrors');
    const layer2Element = document.getElementById('type2RuleErrors');
    const totalFailuresElement = document.getElementById('type2TotalFailures');

    if (layer1Element) {
        layer1Element.textContent = type2Results.validationErrors.resignedWithIncentive;
    }
    if (layer2Element) {
        layer2Element.textContent = type2Results.validationErrors.failedConditionsWithIncentive;
    }
    if (totalFailuresElement) {
        totalFailuresElement.textContent = type2Results.validationErrors.totalValidationFailures;
    }

    const type2Message = document.getElementById('type2ValidationMessage');
    const hasLayer1Errors = type2Results.validationErrors.resignedWithIncentive > 0;
    const hasLayer2Errors = type2Results.validationErrors.failedConditionsWithIncentive > 0;
    const hasLayer3Errors = type2Results.totalMismatches > 0;

    // Build combined message with all 3 layers
    let messageHTML = '';

    // Layer 1 & 2 Problematic Employees (CRITICAL)
    if (type2Results.problematicEmployees.length > 0) {
        messageHTML += `
            <div class="alert alert-danger mb-2">
                <strong><i class="fas fa-exclamation-triangle"></i> 3-Layer 검증 오류 발견!</strong>
                <div class="mt-2">
                    <span class="badge bg-danger me-2">Layer 1: ${type2Results.validationErrors.resignedWithIncentive}명</span>
                    <span class="badge bg-warning text-dark">Layer 2: ${type2Results.validationErrors.failedConditionsWithIncentive}명</span>
                </div>
                <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                    <table class="table table-sm table-bordered mb-0" style="font-size: 0.85rem;">
                        <thead class="table-dark">
                            <tr>
                                <th>사번</th>
                                <th>이름</th>
                                <th>직급</th>
                                <th>Layer</th>
                                <th>문제</th>
                                <th>인센티브</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${type2Results.problematicEmployees.map(emp => `
                                <tr class="${emp.layer === 1 ? 'table-danger' : 'table-warning'}">
                                    <td>${emp.emp_no}</td>
                                    <td>${emp.name}</td>
                                    <td>${emp.position}</td>
                                    <td><span class="badge ${emp.layer === 1 ? 'bg-danger' : 'bg-warning text-dark'}">Layer ${emp.layer}</span></td>
                                    <td>${emp.issue === 'RESIGNED_WITH_INCENTIVE' ?
                                        `퇴사일: ${emp.stopWorkingDate}` :
                                        `조건 충족: ${emp.conditionsPassed}/${emp.conditionsApplicable}`}</td>
                                    <td class="text-end">${emp.incentive.toLocaleString()} VND</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // Layer 3: TYPE-1 Average Mismatches
    if (hasLayer3Errors) {
        messageHTML += `
            <div class="alert alert-warning mb-0">
                <strong><i class="fas fa-exclamation-circle"></i> Layer 3: 평균 불일치</strong><br>
                ${type2Results.totalMismatches}명의 TYPE-2 직원 금액이 TYPE-1 평균과 다릅니다
                <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                    ${Object.entries(type2Results.positions).map(([position, data]) => {
                        if (data.mismatches === 0) return '';
                        return `
                            <div class="border-bottom py-2">
                                <strong>${position}</strong> (참조: ${data.referencePosition}, TYPE-1 수령자 ${data.type1ReceivingCount}명)<br>
                                예상 평균: ${data.expectedAverage.toLocaleString()} VND<br>
                                불일치: ${data.mismatches}명
                                ${data.employees.slice(0, 3).map(emp => `
                                    <div class="ms-3 text-muted small">
                                        • ${emp.emp_no}: ${emp.actual.toLocaleString()} VND
                                        (차이: ${emp.difference > 0 ? '+' : ''}${emp.difference.toLocaleString()} VND)
                                    </div>
                                `).join('')}
                                ${data.employees.length > 3 ? `<div class="ms-3 text-muted small">... 외 ${data.employees.length - 3}명</div>` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // All layers passed
    if (!hasLayer1Errors && !hasLayer2Errors && !hasLayer3Errors) {
        messageHTML = `
            <div class="alert alert-success mb-0">
                <i class="fas fa-check-circle"></i> 3-Layer 검증 통과!<br>
                <small class="text-muted">
                    ✅ Layer 1: 퇴사자 인센티브 없음<br>
                    ✅ Layer 2: 100% 조건 충족 규칙 준수<br>
                    ✅ Layer 3: TYPE-1 평균과 일치
                </small>
            </div>
        `;
    }

    type2Message.innerHTML = messageHTML;

    // Update card header color based on overall status
    const type2CardHeader = document.getElementById('type2AverageCard')?.querySelector('.card-header');
    if (type2CardHeader) {
        type2CardHeader.classList.remove('bg-success', 'bg-warning', 'bg-danger', 'text-white');
        if (hasLayer1Errors || hasLayer2Errors) {
            type2CardHeader.classList.add('bg-danger', 'text-white');
        } else if (hasLayer3Errors) {
            type2CardHeader.classList.add('bg-warning');
        } else {
            type2CardHeader.classList.add('bg-success', 'text-white');
        }
    }

    // 3. 연속월 검증 (Continuous Months Validation)
    const previousMonthData = ValidationEngine.state.previousMonthData || [];
    const continuousResults = validateContinuousMonths(allEmployees, previousMonthData, positionMatrix);

    // Display amount consistency
    document.getElementById('amountConsistencyTotal').textContent = continuousResults.amountConsistency.total;
    document.getElementById('amountConsistencyCorrect').textContent = continuousResults.amountConsistency.correct;
    document.getElementById('amountConsistencyMismatched').textContent = continuousResults.amountConsistency.mismatched;

    // Display increment logic (with skip handling for Python engine bug)
    const incrementLogicContainer = document.getElementById('incrementLogicTotal')?.closest('.row');
    if (continuousResults.incrementLogic.skipped) {
        // Show warning instead of numbers when skipped
        document.getElementById('incrementLogicTotal').textContent = continuousResults.incrementLogic.total;
        document.getElementById('incrementLogicCorrect').textContent = '-';
        document.getElementById('incrementLogicMismatched').innerHTML = '<span class="text-warning">건너뜀</span>';

        // Add warning alert below increment logic section
        const warningDiv = document.createElement('div');
        warningDiv.className = 'alert alert-warning mt-2';
        warningDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>증가 로직 검증 건너뜀</strong><br>
            <small>${continuousResults.incrementLogic.skipReason}</small>
        `;
        incrementLogicContainer?.insertAdjacentElement('afterend', warningDiv);
    } else {
        document.getElementById('incrementLogicTotal').textContent = continuousResults.incrementLogic.total;
        document.getElementById('incrementLogicCorrect').textContent = continuousResults.incrementLogic.correct;
        document.getElementById('incrementLogicMismatched').textContent = continuousResults.incrementLogic.mismatched;
    }
}
