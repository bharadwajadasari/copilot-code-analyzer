package com.copilotanalyzer.intellij.listeners

import com.intellij.openapi.editor.Document
import com.intellij.openapi.editor.event.DocumentEvent
import com.intellij.openapi.editor.event.DocumentListener
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import com.copilotanalyzer.intellij.services.AnalysisService
import com.copilotanalyzer.intellij.analysis.CodeAnalyzer
import com.copilotanalyzer.intellij.events.EventPublisher
import java.util.concurrent.ConcurrentHashMap
import java.util.Timer
import java.util.TimerTask

class CodeChangeListener : DocumentListener {
    private val pendingAnalysis = ConcurrentHashMap<Document, Long>()
    private val debounceDelay = 2000L // 2 seconds
    private val timer = Timer(true)

    override fun documentChanged(event: DocumentEvent) {
        val document = event.document
        val file = FileDocumentManager.getInstance().getFile(document)
        
        if (file != null && shouldAnalyzeFile(file)) {
            scheduleAnalysis(document, file)
        }
    }

    private fun shouldAnalyzeFile(file: VirtualFile): Boolean {
        val supportedExtensions = setOf(
            "java", "kt", "py", "js", "ts", "cpp", "c", "cs", "go", "rs", "php", "rb", "swift"
        )
        return file.extension?.lowercase() in supportedExtensions
    }

    private fun scheduleAnalysis(document: Document, file: VirtualFile) {
        val currentTime = System.currentTimeMillis()
        pendingAnalysis[document] = currentTime
        
        timer.schedule(object : TimerTask() {
            override fun run() {
                val lastModification = pendingAnalysis[document]
                if (lastModification != null && lastModification == currentTime) {
                    pendingAnalysis.remove(document)
                    analyzeFile(document, file)
                }
            }
        }, debounceDelay)
    }

    private fun analyzeFile(document: Document, file: VirtualFile) {
        try {
            val content = document.text
            val analyzer = CodeAnalyzer()
            val analysisResult = analyzer.analyzeContent(content, file.extension ?: "")
            
            val event = createAnalysisEvent(file, analysisResult, "code_change")
            EventPublisher.publishEvent(event)
            
        } catch (e: Exception) {
            // Log error but don't interrupt user workflow
            println("Analysis error for file ${file.name}: ${e.message}")
        }
    }

    private fun createAnalysisEvent(
        file: VirtualFile, 
        analysisResult: Map<String, Any>, 
        eventType: String
    ): Map<String, Any> {
        return mapOf(
            "timestamp" to System.currentTimeMillis(),
            "event_type" to eventType,
            "file_path" to file.path,
            "file_name" to file.name,
            "file_extension" to (file.extension ?: ""),
            "analysis_result" to analysisResult,
            "project_name" to (file.parent?.name ?: "unknown"),
            "developer_id" to System.getProperty("user.name"),
            "ide_version" to com.intellij.openapi.application.ApplicationInfo.getInstance().fullVersion
        )
    }
}