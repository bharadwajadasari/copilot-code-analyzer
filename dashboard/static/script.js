/**
 * Copilot Code Analysis Dashboard - Frontend JavaScript
 * Handles dashboard interactions, data visualization, and real-time updates
 */

class Dashboard {
    constructor() {
        this.currentSection = 'overview';
        this.refreshInterval = null;
        this.charts = {};
        this.data = {
            repositories: [],
            overview: {},
            activity: []
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupFeatherIcons();
        this.loadInitialData();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Navigation
        document.getElementById('overview-tab').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSection('overview');
        });
        
        document.getElementById('repositories-tab').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSection('repositories');
        });
        
        document.getElementById('activity-tab').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSection('activity');
        });
        
        // Activity refresh
        const refreshBtn = document.getElementById('refresh-activity');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadRecentActivity();
            });
        }
        
        // Activity filter
        const activityFilter = document.getElementById('activity-filter');
        if (activityFilter) {
            activityFilter.addEventListener('change', () => {
                this.loadRecentActivity();
            });
        }
    }
    
    setupFeatherIcons() {
        // Initialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    async loadInitialData() {
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadRepositories(),
                this.loadRecentActivity()
            ]);
            
            this.showSection('overview');
        } catch (error) {
            this.showError('Failed to load dashboard data: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadOverviewStats() {
        try {
            const response = await fetch('/api/stats/overview');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.data.overview = result.stats;
                this.updateOverviewDisplay();
            } else {
                throw new Error(result.message || 'Failed to load overview stats');
            }
        } catch (error) {
            console.error('Error loading overview stats:', error);
            throw error;
        }
    }
    
    async loadRepositories() {
        try {
            const response = await fetch('/api/repositories');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.data.repositories = result.repositories;
                this.updateRepositoriesDisplay();
            } else {
                throw new Error(result.message || 'Failed to load repositories');
            }
        } catch (error) {
            console.error('Error loading repositories:', error);
            throw error;
        }
    }
    
    async loadRecentActivity() {
        try {
            const hours = document.getElementById('activity-filter')?.value || 24;
            const response = await fetch(`/api/activity?hours=${hours}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                this.data.activity = result.activity;
                this.updateActivityDisplay();
            } else {
                throw new Error(result.message || 'Failed to load activity');
            }
        } catch (error) {
            console.error('Error loading activity:', error);
            this.showError('Failed to load recent activity: ' + error.message);
        }
    }
    
    updateOverviewDisplay() {
        const stats = this.data.overview;
        
        // Update summary cards
        this.updateElement('total-repositories', stats.total_repositories || 0);
        this.updateElement('total-files', this.formatNumber(stats.total_files || 0));
        this.updateElement('total-lines', this.formatNumber(stats.total_lines || 0));
        this.updateElement('copilot-percentage', `${stats.copilot_percentage || 0}%`);
        
        // Update charts
        this.updateDistributionChart(stats);
        this.updateLanguageChart(stats);
    }
    
    updateRepositoriesDisplay() {
        const tableBody = document.getElementById('repositories-table');
        if (!tableBody) return;
        
        if (this.data.repositories.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="empty-state">
                            <i data-feather="folder"></i>
                            <p>No repositories found</p>
                            <small class="text-muted">Start monitoring repositories to see data here</small>
                        </div>
                    </td>
                </tr>
            `;
            this.setupFeatherIcons();
            return;
        }
        
        tableBody.innerHTML = this.data.repositories.map(repo => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <i data-feather="folder" class="me-2"></i>
                        <div>
                            <div class="fw-semibold">${this.escapeHtml(repo.name)}</div>
                            <small class="text-muted">${this.escapeHtml(repo.path)}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-secondary">${repo.total_files || 0}</span>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="confidence-bar me-2" style="width: 60px;">
                            <div class="confidence-fill ${this.getConfidenceClass(repo.copilot_percentage)}" 
                                 style="width: ${repo.copilot_percentage || 0}%"></div>
                        </div>
                        <span>${repo.copilot_percentage || 0}%</span>
                    </div>
                </td>
                <td>
                    <span>${repo.human_percentage || 0}%</span>
                </td>
                <td>
                    <small>${this.formatTimestamp(repo.last_analysis)}</small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="dashboard.showRepositoryDetails('${this.escapeHtml(repo.path)}')">
                        <i data-feather="eye"></i>
                        View
                    </button>
                </td>
            </tr>
        `).join('');
        
        this.setupFeatherIcons();
    }
    
    updateActivityDisplay() {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;
        
        if (this.data.activity.length === 0) {
            activityList.innerHTML = `
                <div class="empty-state">
                    <i data-feather="activity"></i>
                    <p>No recent activity</p>
                    <small class="text-muted">File changes and analyses will appear here</small>
                </div>
            `;
            this.setupFeatherIcons();
            return;
        }
        
        activityList.innerHTML = this.data.activity.map(item => `
            <div class="activity-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center mb-1">
                            <i data-feather="${this.getEventIcon(item.event_type)}" class="me-2"></i>
                            <span class="fw-semibold">${this.getEventLabel(item.event_type)}</span>
                            <span class="badge badge-language language-${item.language?.toLowerCase() || 'unknown'} ms-2">
                                ${item.language || 'Unknown'}
                            </span>
                        </div>
                        <div class="text-truncate">
                            <small class="text-muted">${this.escapeHtml(item.file_path)}</small>
                        </div>
                        <div class="mt-1">
                            <small class="text-muted">
                                Repository: ${this.escapeHtml(item.repository_path)}
                            </small>
                        </div>
                        ${item.copilot_confidence !== undefined ? `
                            <div class="mt-2">
                                <div class="d-flex align-items-center">
                                    <small class="text-muted me-2">Copilot confidence:</small>
                                    <div class="confidence-bar me-2" style="width: 100px;">
                                        <div class="confidence-fill ${this.getConfidenceClass(item.copilot_confidence * 100)}" 
                                             style="width: ${(item.copilot_confidence * 100) || 0}%"></div>
                                    </div>
                                    <small>${Math.round((item.copilot_confidence * 100) || 0)}%</small>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="text-end">
                        <div class="activity-time">${this.formatTimestamp(item.timestamp)}</div>
                        ${item.code_lines ? `<small class="text-muted">${item.code_lines} lines</small>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
        
        this.setupFeatherIcons();
    }
    
    updateDistributionChart(stats) {
        const ctx = document.getElementById('distribution-chart');
        if (!ctx) return;
        
        if (this.charts.distribution) {
            this.charts.distribution.destroy();
        }
        
        const copilotLines = stats.total_copilot_lines || 0;
        const humanLines = stats.total_human_lines || 0;
        const total = copilotLines + humanLines;
        
        if (total === 0) {
            ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
            return;
        }
        
        this.charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Copilot Generated', 'Human Written'],
                datasets: [{
                    data: [copilotLines, humanLines],
                    backgroundColor: ['#f59e0b', '#10b981'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${this.formatNumber(context.raw)} lines (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    updateLanguageChart(stats) {
        const ctx = document.getElementById('language-chart');
        if (!ctx) return;
        
        if (this.charts.language) {
            this.charts.language.destroy();
        }
        
        const languages = stats.languages || [];
        
        if (languages.length === 0) {
            ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
            return;
        }
        
        const colors = [
            '#3776ab', '#f7df1e', '#3178c6', '#ed8b00', 
            '#00599c', '#00add8', '#ce422b', '#239120'
        ];
        
        this.charts.language = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: languages,
                datasets: [{
                    label: 'Languages',
                    data: new Array(languages.length).fill(1),
                    backgroundColor: colors.slice(0, languages.length),
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `${context.label}: Used in project`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    async showRepositoryDetails(repositoryPath) {
        try {
            const response = await fetch(`/api/repository/${encodeURIComponent(repositoryPath)}/summary`);
            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayRepositoryModal(result);
            } else {
                throw new Error(result.message || 'Failed to load repository details');
            }
        } catch (error) {
            this.showError('Failed to load repository details: ' + error.message);
        }
    }
    
    displayRepositoryModal(repoData) {
        const modalBody = document.getElementById('repository-details');
        if (!modalBody) return;
        
        const summary = repoData.summary || {};
        const languageBreakdown = repoData.language_breakdown || {};
        const gitInfo = repoData.git_info || {};
        
        modalBody.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-12">
                    <h6>Repository Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Path:</strong></td>
                            <td>${this.escapeHtml(repoData.repository_path)}</td>
                        </tr>
                        <tr>
                            <td><strong>Last Analysis:</strong></td>
                            <td>${this.formatTimestamp(repoData.timestamp)}</td>
                        </tr>
                        ${gitInfo.current_branch ? `
                            <tr>
                                <td><strong>Branch:</strong></td>
                                <td>${this.escapeHtml(gitInfo.current_branch)}</td>
                            </tr>
                        ` : ''}
                        ${gitInfo.last_commit ? `
                            <tr>
                                <td><strong>Last Commit:</strong></td>
                                <td>${this.escapeHtml(gitInfo.last_commit)}</td>
                            </tr>
                        ` : ''}
                    </table>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <h6>Code Statistics</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Total Files:</strong></td>
                            <td>${summary.total_files || 0}</td>
                        </tr>
                        <tr>
                            <td><strong>Total Lines:</strong></td>
                            <td>${this.formatNumber(summary.total_lines || 0)}</td>
                        </tr>
                        <tr>
                            <td><strong>Code Lines:</strong></td>
                            <td>${this.formatNumber(summary.total_code_lines || 0)}</td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>AI Analysis</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Copilot Lines:</strong></td>
                            <td>${this.formatNumber(summary.copilot_lines || 0)} (${summary.copilot_percentage || 0}%)</td>
                        </tr>
                        <tr>
                            <td><strong>Human Lines:</strong></td>
                            <td>${this.formatNumber(summary.human_lines || 0)} (${summary.human_percentage || 0}%)</td>
                        </tr>
                        <tr>
                            <td><strong>Avg Confidence:</strong></td>
                            <td>${Math.round((summary.average_confidence || 0) * 100)}%</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            ${Object.keys(languageBreakdown).length > 0 ? `
                <div class="row">
                    <div class="col-md-12">
                        <h6>Language Breakdown</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Language</th>
                                        <th>Files</th>
                                        <th>Lines</th>
                                        <th>Copilot %</th>
                                        <th>Human %</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(languageBreakdown).map(([lang, stats]) => `
                                        <tr>
                                            <td>
                                                <span class="badge badge-language language-${lang.toLowerCase()}">${lang}</span>
                                            </td>
                                            <td>${stats.files || 0}</td>
                                            <td>${this.formatNumber(stats.code_lines || 0)}</td>
                                            <td>${stats.copilot_percentage || 0}%</td>
                                            <td>${stats.human_percentage || 0}%</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            ` : ''}
        `;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('repositoryModal'));
        modal.show();
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Show selected section
        const section = document.getElementById(`${sectionName}-section`);
        if (section) {
            section.classList.remove('d-none');
        }
        
        // Add active class to selected nav link
        const navLink = document.getElementById(`${sectionName}-tab`);
        if (navLink) {
            navLink.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // Refresh charts if showing overview
        if (sectionName === 'overview') {
            setTimeout(() => {
                this.updateDistributionChart(this.data.overview);
                this.updateLanguageChart(this.data.overview);
            }, 100);
        }
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.toggle('d-none', !show);
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        
        if (errorDiv && errorText) {
            errorText.textContent = message;
            errorDiv.classList.remove('d-none');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorDiv.classList.add('d-none');
            }, 5000);
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (this.currentSection === 'overview') {
                this.loadOverviewStats();
            } else if (this.currentSection === 'repositories') {
                this.loadRepositories();
            } else if (this.currentSection === 'activity') {
                this.loadRecentActivity();
            }
        }, 30000);
    }
    
    // Utility functions
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp) return 'Unknown';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    getConfidenceClass(percentage) {
        if (percentage >= 70) return 'confidence-high';
        if (percentage >= 40) return 'confidence-medium';
        return 'confidence-low';
    }
    
    getEventIcon(eventType) {
        const iconMap = {
            'created': 'plus',
            'modified': 'edit',
            'analysis': 'search',
            'batch_analysis': 'layers',
            'deleted': 'minus'
        };
        return iconMap[eventType] || 'file';
    }
    
    getEventLabel(eventType) {
        const labelMap = {
            'created': 'File Created',
            'modified': 'File Modified',
            'analysis': 'File Analyzed',
            'batch_analysis': 'Batch Analysis',
            'deleted': 'File Deleted'
        };
        return labelMap[eventType] || 'File Event';
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});
