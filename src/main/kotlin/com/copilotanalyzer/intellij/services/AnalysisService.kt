package com.copilotanalyzer.intellij.services

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.copilotanalyzer.intellij.events.EventPublisher
import com.copilotanalyzer.intellij.analysis.CodeAnalyzer
import java.util.concurrent.ConcurrentHashMap

@Service
class AnalysisService(private val project: Project) {
    
    private val analyzer = CodeAnalyzer()
    private val sessionMetrics = ConcurrentHashMap<String, Any>()
    private var isMonitoringEnabled = true
    
    init {
        initializeService()
    }
    
    private fun initializeService() {
        // Load configuration from IDE settings
        val settings = AnalysisSettings.getInstance()
        
        if (settings.apiEndpoint.isNotEmpty() && settings.apiKey.isNotEmpty()) {
            EventPublisher.configure(
                settings.apiEndpoint,
                settings.apiKey,
                settings.batchSize
            )
        }
        
        recordSessionStart()
    }
    
    fun analyzeAndPublish(filePath: String, content: String, fileExtension: String) {
        if (!isMonitoringEnabled) return
        
        try {
            val analysisResult = analyzer.analyzeContent(content, fileExtension)
            
            val event = createAnalysisEvent(filePath, analysisResult, "real_time_analysis")
            EventPublisher.publishEvent(event)
            
            updateSessionMetrics(analysisResult)
            
        } catch (e: Exception) {
            println("Analysis error: ${e.message}")
        }
    }
    
    fun analyzeProject() {
        recordSessionEvent("project_analysis_started")
        // Implementation for full project analysis
    }
    
    fun toggleMonitoring(): Boolean {
        isMonitoringEnabled = !isMonitoringEnabled
        recordSessionEvent(if (isMonitoringEnabled) "monitoring_enabled" else "monitoring_disabled")
        return isMonitoringEnabled
    }
    
    fun getSessionMetrics(): Map<String, Any> {
        return sessionMetrics.toMap()
    }
    
    private fun createAnalysisEvent(
        filePath: String,
        analysisResult: Map<String, Any>,
        eventType: String
    ): Map<String, Any> {
        return mapOf(
            "timestamp" to System.currentTimeMillis(),
            "event_type" to eventType,
            "project_name" to project.name,
            "project_path" to (project.basePath ?: "unknown"),
            "file_path" to filePath,
            "analysis_result" to analysisResult,
            "developer_id" to System.getProperty("user.name"),
            "session_id" to getSessionId(),
            "ide_info" to getIdeInfo()
        )
    }
    
    private fun updateSessionMetrics(analysisResult: Map<String, Any>) {
        val currentCount = sessionMetrics.getOrDefault("files_analyzed", 0) as Int
        sessionMetrics["files_analyzed"] = currentCount + 1
        
        val confidence = analysisResult["copilot_confidence"] as? Double ?: 0.0
        if (confidence > 0.7) {
            val aiCount = sessionMetrics.getOrDefault("high_ai_confidence_files", 0) as Int
            sessionMetrics["high_ai_confidence_files"] = aiCount + 1
        }
        
        sessionMetrics["last_analysis_time"] = System.currentTimeMillis()
    }
    
    private fun recordSessionStart() {
        sessionMetrics["session_start"] = System.currentTimeMillis()
        sessionMetrics["session_id"] = getSessionId()
        
        val sessionEvent = mapOf(
            "timestamp" to System.currentTimeMillis(),
            "event_type" to "session_started",
            "project_name" to project.name,
            "developer_id" to System.getProperty("user.name"),
            "session_id" to getSessionId(),
            "ide_info" to getIdeInfo()
        )
        
        EventPublisher.publishEvent(sessionEvent)
    }
    
    private fun recordSessionEvent(eventType: String) {
        val event = mapOf(
            "timestamp" to System.currentTimeMillis(),
            "event_type" to eventType,
            "project_name" to project.name,
            "developer_id" to System.getProperty("user.name"),
            "session_id" to getSessionId()
        )
        
        EventPublisher.publishEvent(event)
    }
    
    private fun getSessionId(): String {
        return sessionMetrics.getOrPut("session_id") {
            "${System.currentTimeMillis()}-${System.getProperty("user.name")}-${project.name}"
        } as String
    }
    
    private fun getIdeInfo(): Map<String, String> {
        val appInfo = com.intellij.openapi.application.ApplicationInfo.getInstance()
        return mapOf(
            "ide_name" to "IntelliJ IDEA",
            "ide_version" to appInfo.fullVersion,
            "build_number" to appInfo.build.asString()
        )
    }
}

// Settings data class
data class AnalysisSettings(
    var apiEndpoint: String = "",
    var apiKey: String = "",
    var batchSize: Int = 10,
    var monitoringEnabled: Boolean = true,
    var analysisInterval: Long = 2000L
) {
    companion object {
        fun getInstance(): AnalysisSettings {
            // In a real implementation, this would load from IDE persistent settings
            return AnalysisSettings()
        }
    }
}