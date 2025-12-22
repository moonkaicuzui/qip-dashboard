#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter State Manager for Dashboard
===================================
@FrontendArchitect & @UXResearcher 협업 개발

대시보드 필터 상태 localStorage 저장 기능

이 스크립트는 대시보드에 주입할 JavaScript 코드를 생성합니다.
"""


def get_filter_state_js():
    """
    필터 상태 관리 JavaScript 코드 반환

    기능:
    - 필터 상태 localStorage 저장
    - 페이지 로드 시 상태 복원
    - 빌딩 필터, 직원 필터, 정렬 상태 관리
    """
    return """
    // ========================================
    // Filter State Manager
    // @FrontendArchitect & @UXResearcher
    // ========================================

    const FilterStateManager = {
        STORAGE_KEY: 'qip_dashboard_filter_state',
        VERSION: '1.0',

        // 기본 상태
        defaultState: {
            version: '1.0',
            timestamp: null,
            filters: {
                building: 'all',
                position: 'all',
                incentiveStatus: 'all',
                search: ''
            },
            sorting: {
                column: 'incentive',
                direction: 'desc'
            },
            ui: {
                language: 'ko',
                activeTab: 'summary'
            }
        },

        // 상태 저장
        saveState: function(partialState) {
            try {
                const currentState = this.loadState();
                const newState = {
                    ...currentState,
                    ...partialState,
                    timestamp: new Date().toISOString()
                };
                localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newState));
                console.log('🔄 Filter state saved:', partialState);
                return true;
            } catch (e) {
                console.warn('⚠️ Failed to save filter state:', e);
                return false;
            }
        },

        // 상태 로드
        loadState: function() {
            try {
                const stored = localStorage.getItem(this.STORAGE_KEY);
                if (!stored) return { ...this.defaultState };

                const state = JSON.parse(stored);
                if (state.version !== this.VERSION) {
                    console.log('🔄 Filter state version mismatch, resetting');
                    return { ...this.defaultState };
                }
                return state;
            } catch (e) {
                console.warn('⚠️ Failed to load filter state:', e);
                return { ...this.defaultState };
            }
        },

        // 필터 저장
        saveFilter: function(filterName, value) {
            const state = this.loadState();
            state.filters = state.filters || {};
            state.filters[filterName] = value;
            return this.saveState({ filters: state.filters });
        },

        // 정렬 저장
        saveSorting: function(column, direction) {
            return this.saveState({
                sorting: { column, direction }
            });
        },

        // UI 상태 저장
        saveUI: function(uiState) {
            const state = this.loadState();
            state.ui = { ...state.ui, ...uiState };
            return this.saveState({ ui: state.ui });
        },

        // 상태 복원
        restoreState: function() {
            const state = this.loadState();
            console.log('🔙 Restoring filter state:', state);

            // 빌딩 필터 복원
            if (state.filters?.building) {
                const buildingFilter = document.getElementById('orgBuildingFilter');
                if (buildingFilter) {
                    buildingFilter.value = state.filters.building;
                    // 이벤트 트리거
                    buildingFilter.dispatchEvent(new Event('change'));
                }
            }

            // 검색 필터 복원
            if (state.filters?.search) {
                const searchInput = document.getElementById('searchInput') ||
                                   document.querySelector('input[type="search"]');
                if (searchInput) {
                    searchInput.value = state.filters.search;
                    searchInput.dispatchEvent(new Event('input'));
                }
            }

            // 언어 복원
            if (state.ui?.language && typeof switchLanguage === 'function') {
                // switchLanguage는 이미 로드된 경우에만
                // switchLanguage(state.ui.language);
            }

            return state;
        },

        // 상태 초기화
        clearState: function() {
            try {
                localStorage.removeItem(this.STORAGE_KEY);
                console.log('🗑️ Filter state cleared');
                return true;
            } catch (e) {
                console.warn('⚠️ Failed to clear filter state:', e);
                return false;
            }
        },

        // 이벤트 리스너 초기화
        initEventListeners: function() {
            const self = this;

            // 빌딩 필터 변경 감지
            const buildingFilter = document.getElementById('orgBuildingFilter');
            if (buildingFilter) {
                buildingFilter.addEventListener('change', function() {
                    self.saveFilter('building', this.value);
                });
            }

            // 검색 입력 감지 (디바운스 적용)
            const searchInputs = document.querySelectorAll('input[type="search"], #searchInput');
            searchInputs.forEach(input => {
                let debounceTimer;
                input.addEventListener('input', function() {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        self.saveFilter('search', this.value);
                    }, 500);
                });
            });

            // 탭 변경 감지
            const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
            tabButtons.forEach(tab => {
                tab.addEventListener('shown.bs.tab', function(e) {
                    const targetId = e.target.getAttribute('href') ||
                                    e.target.getAttribute('data-bs-target');
                    if (targetId) {
                        self.saveUI({ activeTab: targetId.replace('#', '') });
                    }
                });
            });

            console.log('✅ Filter state listeners initialized');
        },

        // 초기화
        init: function() {
            console.log('🚀 Initializing FilterStateManager');

            // DOM 로드 후 이벤트 리스너 초기화
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.initEventListeners();
                    // 약간의 딜레이 후 상태 복원 (다른 초기화 완료 대기)
                    setTimeout(() => this.restoreState(), 100);
                });
            } else {
                this.initEventListeners();
                setTimeout(() => this.restoreState(), 100);
            }

            return this;
        }
    };

    // 자동 초기화
    window.FilterStateManager = FilterStateManager.init();
    """


def inject_filter_state_js(html_content):
    """
    HTML 콘텐츠에 필터 상태 관리 JavaScript 주입

    Args:
        html_content: 원본 HTML 문자열

    Returns:
        수정된 HTML 문자열
    """
    js_code = get_filter_state_js()

    # </body> 태그 앞에 스크립트 삽입
    insert_point = html_content.rfind('</body>')
    if insert_point > 0:
        script_tag = f'\n<script>\n{js_code}\n</script>\n'
        return html_content[:insert_point] + script_tag + html_content[insert_point:]

    return html_content


if __name__ == '__main__':
    print("Filter State Manager JavaScript Generator")
    print("=" * 50)
    print(get_filter_state_js()[:500] + "...")
    print("=" * 50)
    print("✅ Use inject_filter_state_js() to add to dashboard HTML")
