package com.copilotanalyzer.intellij.analysis

import java.util.regex.Pattern

class CodeAnalyzer {
    
    private val copilotIndicators = listOf(
        "copilot", "ai", "generated", "auto-complete", "auto-generated",
        "github copilot", "artificial intelligence", "machine learning"
    )
    
    private val aiPatterns = listOf(
        Pattern.compile("//\\s*(generated|copilot|ai)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("#\\s*(generated|copilot|ai)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("/\\*.*?(generated|copilot|ai).*?\\*/", Pattern.CASE_INSENSITIVE or Pattern.DOTALL)
    )

    fun analyzeContent(content: String, fileExtension: String): Map<String, Any> {
        val lines = content.split("\n")
        
        val commentAnalysis = analyzeComments(content)
        val structureAnalysis = analyzeCodeStructure(content, fileExtension)
        val syntaxAnalysis = analyzeSyntaxQuality(content, fileExtension)
        val patternAnalysis = analyzePatterns(content)
        
        val overallConfidence = calculateOverallConfidence(
            commentAnalysis, structureAnalysis, syntaxAnalysis, patternAnalysis
        )
        
        val indicators = mapOf(
            "explicit_ai_comments" to (commentAnalysis > 0.3),
            "perfect_syntax" to (syntaxAnalysis > 0.7),
            "structured_patterns" to (structureAnalysis > 0.6),
            "boilerplate_code" to (patternAnalysis > 0.5)
        )
        
        return mapOf(
            "copilot_confidence" to overallConfidence,
            "human_confidence" to (1.0 - overallConfidence),
            "analysis_details" to mapOf(
                "comment_score" to commentAnalysis,
                "structure_score" to structureAnalysis,
                "syntax_score" to syntaxAnalysis,
                "pattern_score" to patternAnalysis
            ),
            "indicators" to indicators,
            "risk_level" to getRiskLevel(overallConfidence),
            "file_stats" to mapOf(
                "lines_of_code" to lines.size,
                "non_empty_lines" to lines.count { it.trim().isNotEmpty() },
                "comment_lines" to countCommentLines(content, fileExtension)
            )
        )
    }
    
    private fun analyzeComments(content: String): Double {
        var score = 0.0
        val lowerContent = content.lowercase()
        
        // Check for explicit AI indicators
        copilotIndicators.forEach { indicator ->
            if (lowerContent.contains(indicator)) {
                score += 0.3
            }
        }
        
        // Check for pattern matches
        aiPatterns.forEach { pattern ->
            if (pattern.matcher(content).find()) {
                score += 0.4
            }
        }
        
        return minOf(score, 1.0)
    }
    
    private fun analyzeCodeStructure(content: String, fileExtension: String): Double {
        var score = 0.0
        
        // Check for consistent indentation
        if (hasConsistentIndentation(content)) score += 0.2
        
        // Check for complete function implementations
        if (hasCompleteFunctions(content, fileExtension)) score += 0.2
        
        // Check for proper error handling
        if (hasProperErrorHandling(content, fileExtension)) score += 0.2
        
        // Check for documentation
        if (hasGoodDocumentation(content, fileExtension)) score += 0.2
        
        return score
    }
    
    private fun analyzeSyntaxQuality(content: String, fileExtension: String): Double {
        var score = 0.0
        
        when (fileExtension.lowercase()) {
            "java", "kt" -> {
                if (hasProperJavaKotlinSyntax(content)) score += 0.8
            }
            "py" -> {
                if (hasProperPythonSyntax(content)) score += 0.8
            }
            "js", "ts" -> {
                if (hasProperJavaScriptSyntax(content)) score += 0.8
            }
            else -> {
                if (hasGeneralGoodSyntax(content)) score += 0.6
            }
        }
        
        return score
    }
    
    private fun analyzePatterns(content: String): Double {
        var score = 0.0
        
        // Check for boilerplate patterns
        if (content.contains("try {") && content.contains("catch")) score += 0.3
        if (content.contains("public static void main")) score += 0.2
        if (content.contains("@Override") || content.contains("override")) score += 0.2
        if (content.contains("TODO") || content.contains("FIXME")) score -= 0.2
        
        return maxOf(score, 0.0)
    }
    
    private fun calculateOverallConfidence(
        comment: Double, structure: Double, syntax: Double, pattern: Double
    ): Double {
        return (comment * 0.4 + structure * 0.3 + syntax * 0.2 + pattern * 0.1).coerceIn(0.0, 1.0)
    }
    
    private fun getRiskLevel(confidence: Double): String {
        return when {
            confidence >= 0.7 -> "high"
            confidence >= 0.4 -> "medium"
            else -> "low"
        }
    }
    
    // Helper methods
    private fun hasConsistentIndentation(content: String): Boolean {
        val lines = content.split("\n").filter { it.trim().isNotEmpty() }
        val indentations = lines.map { line ->
            line.takeWhile { it == ' ' || it == '\t' }.length
        }.distinct()
        return indentations.size <= 3 // Consistent indentation levels
    }
    
    private fun hasCompleteFunctions(content: String, extension: String): Boolean {
        return when (extension.lowercase()) {
            "java", "kt" -> content.contains("{") && content.contains("}")
            "py" -> content.contains("def ") && content.contains(":")
            else -> true
        }
    }
    
    private fun hasProperErrorHandling(content: String, extension: String): Boolean {
        return content.contains("try") || content.contains("catch") || content.contains("except")
    }
    
    private fun hasGoodDocumentation(content: String, extension: String): Boolean {
        return when (extension.lowercase()) {
            "java", "kt" -> content.contains("/**") || content.contains("//")
            "py" -> content.contains("\"\"\"") || content.contains("#")
            else -> content.contains("//") || content.contains("/*")
        }
    }
    
    private fun hasProperJavaKotlinSyntax(content: String): Boolean {
        return content.contains("public") || content.contains("private") || 
               content.contains("class") || content.contains("fun")
    }
    
    private fun hasProperPythonSyntax(content: String): Boolean {
        return content.contains("def ") || content.contains("class ") || 
               content.contains("import ")
    }
    
    private fun hasProperJavaScriptSyntax(content: String): Boolean {
        return content.contains("function") || content.contains("=>") || 
               content.contains("const ") || content.contains("let ")
    }
    
    private fun hasGeneralGoodSyntax(content: String): Boolean {
        return content.trim().isNotEmpty() && !content.contains("syntax error")
    }
    
    private fun countCommentLines(content: String, extension: String): Int {
        val lines = content.split("\n")
        return when (extension.lowercase()) {
            "java", "kt", "js", "ts" -> lines.count { 
                it.trim().startsWith("//") || it.trim().startsWith("/*") 
            }
            "py" -> lines.count { it.trim().startsWith("#") }
            else -> lines.count { 
                it.trim().startsWith("//") || it.trim().startsWith("#") 
            }
        }
    }
}