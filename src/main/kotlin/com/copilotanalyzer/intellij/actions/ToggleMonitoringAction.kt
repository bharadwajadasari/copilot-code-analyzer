package com.copilotanalyzer.intellij.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.copilotanalyzer.intellij.services.AnalysisService

class ToggleMonitoringAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project: Project? = e.project
        if (project != null) {
            val service = project.getService(AnalysisService::class.java)
            val isEnabled = service.toggleMonitoring()
            
            val message = if (isEnabled) "Code monitoring enabled" else "Code monitoring disabled"
            // Show notification to user
            com.intellij.notification.NotificationGroupManager.getInstance()
                .getNotificationGroup("Copilot Analyzer")
                ?.createNotification(message, com.intellij.notification.NotificationType.INFORMATION)
                ?.notify(project)
        }
    }
}