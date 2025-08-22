/**
 * 🌐 專業多語系支援系統
 * 基於最佳實踐的混合式多語言架構
 * 參考：Drift i18n-Architecture.md
 */

class LanguageSwitcher {
    constructor() {
        this.currentLanguage = localStorage.getItem('qubic_language') || 'zh-tw';
        this.translations = {};
        this.isLoading = false;
        
        // 語言查找表 - 用於動態數字和複雜邏輯
        this.languageLookupTable = {
            'zh-tw': {
                units: { tick: 'Tick', ticks: 'Ticks', second: '秒', seconds: '秒' },
                labels: { current: '當前', last: '最後', next: '下一個' },
                status: { excellent: '極佳', good: '良好', normal: '正常', warning: '警告' },
                actions: { analyzing: '分析中', loading: '載入中', updating: '更新中' }
            },
            'en': {
                units: { tick: 'Tick', ticks: 'Ticks', second: 'second', seconds: 'seconds' },
                labels: { current: 'Current', last: 'Last', next: 'Next' },
                status: { excellent: 'Excellent', good: 'Good', normal: 'Normal', warning: 'Warning' },
                actions: { analyzing: 'Analyzing', loading: 'Loading', updating: 'Updating' }
            }
        };
        
        this.init();
    }
    
    async loadTranslations(language) {
        if (this.translations[language]) {
            return this.translations[language];
        }
        
        try {
            const response = await fetch(`/locales/${language}/common.json`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Failed to load ${language} translations`);
            }
            const translations = await response.json();
            
            // ✅ 驗證翻譯檔案完整性
            if (!translations || typeof translations !== 'object') {
                throw new Error(`Invalid translation file format for ${language}`);
            }
            
            this.translations[language] = translations;
            console.log(`✅ 成功載入 ${language} 翻譯檔案`);
            return translations;
        } catch (error) {
            console.error(`❌ 翻譯檔案載入失敗 (${language}):`, error);
            
            // ✅ 多層 fallback 機制
            // 1. 嘗試載入預設語言 (zh-tw)
            if (language !== 'zh-tw' && !this.translations['zh-tw']) {
                console.log(`🔄 嘗試載入預設語言 (zh-tw) 作為 fallback`);
                try {
                    await this.loadTranslations('zh-tw');
                } catch (fallbackError) {
                    console.error('❌ 預設語言載入也失敗:', fallbackError);
                }
            }
            
            // 2. 使用已載入的任何語言
            if (language !== 'zh-tw' && this.translations['zh-tw']) {
                console.log(`🔄 使用預設語言 (zh-tw) 作為 fallback`);
                return this.translations['zh-tw'];
            }
            
            // 3. 使用空物件並記錄錯誤
            console.warn(`⚠️ 無法載入任何翻譯檔案，使用空 fallback`);
            return {};
        }
    }
    
    async init() {
        this.createLanguageSwitcher();
        await this.loadTranslations(this.currentLanguage);
        this.updateInterface();
        this.bindEvents();
    }
    
    createLanguageSwitcher() {
        // 使用現有的 HTML 語言切換器，不創建新的
        const existingDropdown = document.getElementById('languageDropdown');
        if (existingDropdown) {
            console.log('✅ 使用現有的 HTML 語言切換器');
            return;
        }
        
        // 如果沒有現有的，則創建新的（備用方案）
        const switcher = document.createElement('div');
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <button id="lang-toggle" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-globe"></i>
                <span id="current-lang">${this.currentLanguage === 'zh-tw' ? '中文' : 'EN'}</span>
            </button>
        `;
        
        // 添加到頁面右上角
        document.body.appendChild(switcher);
    }
    
    bindEvents() {
        // 綁定備用的動態創建按鈕事件
        const toggleBtn = document.getElementById('lang-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleLanguage();
            });
        }
        
        // 綁定 HTML 下拉選單事件
        const dropdownItems = document.querySelectorAll('.dropdown-item[data-lang]');
        dropdownItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const targetLang = e.target.getAttribute('data-lang');
                if (targetLang && targetLang !== this.currentLanguage) {
                    this.switchLanguage(targetLang);
                }
            });
        });
    }
    
    async toggleLanguage() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        const toggleBtn = document.getElementById('lang-toggle');
        if (toggleBtn) {
            toggleBtn.disabled = true;
            toggleBtn.querySelector('span').textContent = '...';
        }
        
        this.currentLanguage = this.currentLanguage === 'zh-tw' ? 'en' : 'zh-tw';
        localStorage.setItem('qubic_language', this.currentLanguage);
        
        try {
            await this.loadTranslations(this.currentLanguage);
            this.updateInterface();
            
            // 通知其他組件語言已變更
            document.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language: this.currentLanguage }
            }));
        } catch (error) {
            console.error('Language switch failed:', error);
            // 還原語言設定
            this.currentLanguage = this.currentLanguage === 'zh-tw' ? 'en' : 'zh-tw';
            localStorage.setItem('qubic_language', this.currentLanguage);
        } finally {
            this.isLoading = false;
            if (toggleBtn) {
                toggleBtn.disabled = false;
            }
        }
    }
    
    async switchLanguage(targetLang) {
        if (this.isLoading || targetLang === this.currentLanguage) return;
        
        this.isLoading = true;
        console.log(`🌐 切換語言：${this.currentLanguage} → ${targetLang}`);
        
        this.currentLanguage = targetLang;
        localStorage.setItem('qubic_language', this.currentLanguage);
        
        try {
            await this.loadTranslations(this.currentLanguage);
            this.updateInterface();
            
            // 通知其他組件語言已變更
            document.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language: this.currentLanguage }
            }));
            
            console.log(`✅ 語言切換完成：${this.currentLanguage}`);
        } catch (error) {
            console.error('語言切換失敗:', error);
        } finally {
            this.isLoading = false;
        }
    }
    
    updateInterface() {
        const translations = this.translations[this.currentLanguage];
        
        // 更新語言切換按鈕文字（動態創建的按鈕）
        const currentLangSpan = document.getElementById('current-lang');
        if (currentLangSpan) {
            const langText = this.getNestedValue(translations, 'language.current') || 
                           (this.currentLanguage === 'zh-tw' ? '中文' : 'EN');
            currentLangSpan.textContent = langText;
        }
        
        // 更新 HTML 下拉選單中的當前語言顯示
        const currentLanguageSpan = document.getElementById('currentLanguage');
        if (currentLanguageSpan) {
            currentLanguageSpan.textContent = this.currentLanguage === 'zh-tw' ? '繁體中文' : 'English';
        }
        
        // 更新所有帶有 data-i18n 屬性的元素
        const i18nElements = document.querySelectorAll('[data-i18n]');
        console.log(`🌐 更新 ${i18nElements.length} 個翻譯元素 (語言: ${this.currentLanguage})`);
        
        i18nElements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const text = this.getNestedValue(translations, key);
            if (text) {
                element.textContent = text;
                console.log(`✅ 翻譯更新: "${key}" = "${text}"`);
            } else {
                console.warn(`⚠️ 翻譯缺失: "${key}" (${this.currentLanguage})`);
            }
        });
        
        // 更新所有帶有 data-i18n-placeholder 屬性的元素
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const text = this.getNestedValue(translations, key);
            if (text) {
                element.placeholder = text;
            }
        });
        
        // ✅ 更新快速問題按鈕的問題文字
        document.querySelectorAll('.quick-question').forEach(button => {
            const questionAttr = this.currentLanguage === 'zh-tw' ? 'data-question-zh' : 'data-question-en';
            const questionText = button.getAttribute(questionAttr);
            if (questionText) {
                button.setAttribute('data-question', questionText);
            }
        });

    }
    
    /**
     * 獲取嵌套物件的值 (支援 "ai.analysis.title" 格式)
     */
    getNestedValue(obj, path) {
        if (!obj || !path) return null;
        
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : null;
        }, obj);
    }
    
    /**
     * 翻譯函數 - 支援嵌套路徑和參數插值
     */
    t(key, params = {}) {
        const translations = this.translations[this.currentLanguage];
        let text = this.getNestedValue(translations, key);
        
        if (!text) {
            console.warn(`Translation missing for key: ${key} (${this.currentLanguage})`);
            return key;
        }
        
        // 參數插值 (簡單版本，避免複雜的參數處理)
        if (typeof text === 'string' && Object.keys(params).length > 0) {
            Object.keys(params).forEach(param => {
                text = text.replace(`{${param}}`, params[param]);
            });
        }
        
        return text;
    }
    
    /**
     * 語言查找表模式 - 用於動態內容 (參考文件建議)
     */
    getStatsText() {
        const statsTexts = {
            'zh-tw': { 
                word: '字', 
                line: '行', 
                words: '字', 
                lines: '行',
                second: '秒',
                seconds: '秒'
            },
            'en': { 
                word: 'word', 
                line: 'line', 
                words: 'words', 
                lines: 'lines',
                second: 'second',
                seconds: 'seconds'
            }
        };
        return statsTexts[this.currentLanguage] || statsTexts['zh-tw'];
    }
    
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    // ✅ 語言查找表模式 - 最佳實踐
    getLookupText(category, key, fallback = '') {
        const lookup = this.languageLookupTable[this.currentLanguage] || this.languageLookupTable['zh-tw'];
        return lookup[category]?.[key] || fallback;
    }
    
    // 動態數字顯示 - 處理單複數
    formatCount(count, singularKey, pluralKey = null) {
        const lookup = this.languageLookupTable[this.currentLanguage] || this.languageLookupTable['zh-tw'];
        
        // 中文沒有單複數概念
        if (this.currentLanguage === 'zh-tw') {
            return `${count} ${lookup.units[singularKey] || singularKey}`;
        }
        
        // 英文需要單複數判斷
        const unitKey = count === 1 ? singularKey : (pluralKey || singularKey + 's');
        return `${count} ${lookup.units[unitKey] || unitKey}`;
    }
    
    // 狀態文字格式化
    formatStatus(statusKey) {
        return this.getLookupText('status', statusKey, statusKey);
    }
    
    // 動作文字格式化  
    formatAction(actionKey) {
        return this.getLookupText('actions', actionKey, actionKey);
    }
    
    // ✅ 獲取當前語言的翻譯（用於 JSON 翻譯檔案）- 包含錯誤處理
    getTranslation(keyPath, fallback = '') {
        try {
            const translations = this.translations[this.currentLanguage];
            if (!translations) {
                console.warn(`⚠️ 翻譯不存在: ${this.currentLanguage}, 使用 fallback: "${fallback}"`);
                return fallback;
            }
            
            const result = this.getNestedValue(translations, keyPath);
            if (result === null || result === undefined) {
                console.warn(`⚠️ 翻譯 key 不存在: "${keyPath}" (${this.currentLanguage}), 使用 fallback: "${fallback}"`);
                
                // 嘗試從預設語言獲取
                if (this.currentLanguage !== 'zh-tw' && this.translations['zh-tw']) {
                    const fallbackResult = this.getNestedValue(this.translations['zh-tw'], keyPath);
                    if (fallbackResult) {
                        console.log(`🔄 從預設語言獲取翻譯: "${keyPath}" = "${fallbackResult}"`);
                        return fallbackResult;
                    }
                }
                
                return fallback;
            }
            
            return result;
        } catch (error) {
            console.error(`❌ 翻譯獲取錯誤 ("${keyPath}"):`, error);
            return fallback;
        }
    }
}

// 全域語言切換器實例
window.languageSwitcher = new LanguageSwitcher();
