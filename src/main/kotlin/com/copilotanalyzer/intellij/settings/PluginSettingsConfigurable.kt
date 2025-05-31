package com.copilotanalyzer.intellij.settings

import com.intellij.openapi.options.Configurable
import com.intellij.openapi.ui.ComponentContainer
import com.intellij.ui.components.JBLabel
import com.intellij.ui.components.JBTextField
import com.intellij.ui.components.JBCheckBox
import com.intellij.util.ui.FormBuilder
import javax.swing.JComponent
import javax.swing.JPanel

class PluginSettingsConfigurable : Configurable {
    private var apiEndpointField: JBTextField? = null
    private var apiKeyField: JBTextField? = null
    private var batchSizeField: JBTextField? = null
    private var enableMonitoringCheckbox: JBCheckBox? = null
    private var analysisIntervalField: JBTextField? = null

    override fun getDisplayName(): String = "Copilot Code Analyzer"

    override fun createComponent(): JComponent {
        apiEndpointField = JBTextField(40)
        apiKeyField = JBTextField(40)
        batchSizeField = JBTextField("10", 10)
        enableMonitoringCheckbox = JBCheckBox("Enable real-time monitoring", true)
        analysisIntervalField = JBTextField("2000", 10)

        return FormBuilder.createFormBuilder()
            .addLabeledComponent(JBLabel("External API Endpoint:"), apiEndpointField!!, 1, false)
            .addLabeledComponent(JBLabel("API Key:"), apiKeyField!!, 1, false)
            .addLabeledComponent(JBLabel("Batch Size:"), batchSizeField!!, 1, false)
            .addComponent(enableMonitoringCheckbox!!, 1)
            .addLabeledComponent(JBLabel("Analysis Interval (ms):"), analysisIntervalField!!, 1, false)
            .addComponentFillVertically(JPanel(), 0)
            .panel
    }

    override fun isModified(): Boolean {
        val settings = AnalysisSettings.getInstance()
        return apiEndpointField?.text != settings.apiEndpoint ||
               apiKeyField?.text != settings.apiKey ||
               batchSizeField?.text != settings.batchSize.toString() ||
               enableMonitoringCheckbox?.isSelected != settings.monitoringEnabled ||
               analysisIntervalField?.text != settings.analysisInterval.toString()
    }

    override fun apply() {
        val settings = AnalysisSettings.getInstance()
        settings.apiEndpoint = apiEndpointField?.text ?: ""
        settings.apiKey = apiKeyField?.text ?: ""
        settings.batchSize = batchSizeField?.text?.toIntOrNull() ?: 10
        settings.monitoringEnabled = enableMonitoringCheckbox?.isSelected ?: true
        settings.analysisInterval = analysisIntervalField?.text?.toLongOrNull() ?: 2000L
        
        // Reconfigure EventPublisher with new settings
        com.copilotanalyzer.intellij.events.EventPublisher.configure(
            settings.apiEndpoint,
            settings.apiKey,
            settings.batchSize
        )
    }

    override fun reset() {
        val settings = AnalysisSettings.getInstance()
        apiEndpointField?.text = settings.apiEndpoint
        apiKeyField?.text = settings.apiKey
        batchSizeField?.text = settings.batchSize.toString()
        enableMonitoringCheckbox?.isSelected = settings.monitoringEnabled
        analysisIntervalField?.text = settings.analysisInterval.toString()
    }
}