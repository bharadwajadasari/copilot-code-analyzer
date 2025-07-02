#!/usr/bin/env python3
"""
Test Java Evasion-Resistant AI Detection
Demonstrates how the enhanced detector handles Java code processed through formatters like Spotless, Google Java Format
"""

import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.java_evasion_detector import JavaEvasionDetector

def create_java_test_samples():
    """Create Java test samples showing original AI vs formatted versions"""
    
    # Original AI-generated Java code
    original_ai_java = '''
package com.example.service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * User data processing service with comprehensive validation and transformation capabilities.
 * 
 * This service provides methods for processing user data with various validation options
 * and transformation capabilities for different data formats.
 */
public class UserDataProcessor {
    
    private static final String DEFAULT_FORMAT = "JSON";
    private final Map<String, Object> configurationMap;
    
    /**
     * Constructor for UserDataProcessor with configuration options.
     * 
     * @param configurationMap Configuration parameters for data processing
     * @throws IllegalArgumentException if configuration is invalid
     */
    public UserDataProcessor(Map<String, Object> configurationMap) throws Exception {
        if (configurationMap == null) {
            throw new IllegalArgumentException("Configuration map cannot be null");
        }
        this.configurationMap = configurationMap;
    }
    
    /**
     * Process user data with validation and transformation.
     * 
     * @param userData The user data to process
     * @param validateInput Whether to validate input data
     * @param outputFormat The desired output format
     * @return Processed user data
     * @throws Exception if processing fails
     */
    public Map<String, Object> processUserData(List<Map<String, Object>> userData, 
                                             boolean validateInput, 
                                             String outputFormat) throws Exception {
        if (userData == null || userData.isEmpty()) {
            return new HashMap<>();
        }
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            if (validateInput) {
                userData = validateUserData(userData);
            }
            
            List<Map<String, Object>> processedData = userData.stream()
                .filter(item -> item != null && !item.isEmpty())
                .map(this::transformUserItem)
                .collect(Collectors.toList());
            
            result.put("processedData", processedData);
            result.put("totalCount", processedData.size());
            result.put("format", outputFormat != null ? outputFormat : DEFAULT_FORMAT);
            
        } catch (Exception e) {
            e.printStackTrace();
            throw new Exception("Failed to process user data: " + e.getMessage());
        }
        
        return result;
    }
    
    /**
     * Validate user data according to business rules.
     * 
     * @param userData List of user data items to validate
     * @return Validated user data
     * @throws IllegalArgumentException if validation fails
     */
    private List<Map<String, Object>> validateUserData(List<Map<String, Object>> userData) {
        List<Map<String, Object>> validatedData = new ArrayList<>();
        
        for (Map<String, Object> item : userData) {
            if (isValidUserItem(item)) {
                validatedData.add(item);
            }
        }
        
        return validatedData;
    }
    
    /**
     * Check if user item is valid according to business rules.
     * 
     * @param item User item to validate
     * @return true if item is valid, false otherwise
     */
    private boolean isValidUserItem(Map<String, Object> item) {
        if (item == null || item.isEmpty()) {
            return false;
        }
        
        return item.containsKey("id") && item.containsKey("name") && 
               item.get("id") != null && item.get("name") != null;
    }
    
    /**
     * Transform individual user item.
     * 
     * @param item User item to transform
     * @return Transformed user item
     */
    private Map<String, Object> transformUserItem(Map<String, Object> item) {
        Map<String, Object> transformedItem = new HashMap<>();
        
        item.forEach((key, value) -> {
            if (value != null) {
                transformedItem.put(key.toLowerCase(), value.toString().trim());
            }
        });
        
        return transformedItem;
    }
}
'''

    # Same code after Google Java Format + Spotless + manual obfuscation
    formatted_ai_java = '''
package com.example.service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

// Data processing service
public class UserDataProcessor {
  private static final String DEF_FMT = "JSON";
  private final Map<String, Object> cfg;

  public UserDataProcessor(Map<String, Object> cfg) throws Exception {
    if (cfg == null) {
      throw new IllegalArgumentException("Config null");
    }
    this.cfg = cfg;
  }

  public Map<String, Object> processUserData(
      List<Map<String, Object>> data, boolean val, String fmt) throws Exception {
    if (data == null || data.isEmpty()) {
      return new HashMap<>();
    }

    Map<String, Object> res = new HashMap<>();

    try {
      if (val) {
        data = validateUserData(data);
      }

      List<Map<String, Object>> processed =
          data.stream()
              .filter(i -> i != null && !i.isEmpty())
              .map(this::transformUserItem)
              .collect(Collectors.toList());

      res.put("processedData", processed);
      res.put("totalCount", processed.size());
      res.put("format", fmt != null ? fmt : DEF_FMT);

    } catch (Exception ex) {
      ex.printStackTrace();
      throw new Exception("Processing failed: " + ex.getMessage());
    }

    return res;
  }

  private List<Map<String, Object>> validateUserData(List<Map<String, Object>> data) {
    List<Map<String, Object>> valid = new ArrayList<>();

    for (Map<String, Object> i : data) {
      if (isValidUserItem(i)) {
        valid.add(i);
      }
    }

    return valid;
  }

  private boolean isValidUserItem(Map<String, Object> i) {
    if (i == null || i.isEmpty()) {
      return false;
    }

    return i.containsKey("id") && i.containsKey("name") && i.get("id") != null && i.get("name") != null;
  }

  private Map<String, Object> transformUserItem(Map<String, Object> i) {
    Map<String, Object> t = new HashMap<>();

    i.forEach(
        (k, v) -> {
          if (v != null) {
            t.put(k.toLowerCase(), v.toString().trim());
          }
        });

    return t;
  }
}
'''

    # Human-written Java equivalent
    human_java = '''
package com.example.service;

import java.util.*;
import java.util.stream.Collectors;

// Quick user processor I wrote for the customer management module
public class UserDataProcessor {
    private static final String JSON_FORMAT = "JSON";
    private Map<String, Object> settings;
    
    public UserDataProcessor(Map<String, Object> configuration) throws Exception {
        if (configuration == null) throw new IllegalArgumentException("Need configuration");
        this.settings = configuration;
    }
    
    // Main processing method - handles user data validation and transformation
    public Map<String, Object> processUserData(List<Map<String, Object>> users, 
                                             boolean shouldValidate, String format) throws Exception {
        if (users == null || users.size() == 0) return new HashMap<>();
        
        Map<String, Object> output = new HashMap<>();
        
        try {
            // Validate first if requested
            if (shouldValidate) {
                users = validateUsers(users);
            }
            
            // Transform the data
            List<Map<String, Object>> transformed = users.stream()
                .filter(user -> user != null && user.size() > 0)
                .map(user -> transformUser(user))
                .collect(Collectors.toList());
            
            output.put("processedData", transformed);
            output.put("totalCount", transformed.size());
            output.put("format", format == null ? JSON_FORMAT : format);
            
        } catch (Exception error) {
            // Log the error for debugging
            System.err.println("Error processing users: " + error.getMessage());
            throw new Exception("User processing failed", error);
        }
        
        return output;
    }
    
    // Validate user data - checks required fields
    private List<Map<String, Object>> validateUsers(List<Map<String, Object>> userList) {
        ArrayList<Map<String, Object>> validUsers = new ArrayList<>();
        
        for (Map<String, Object> user : userList) {
            if (isUserValid(user)) {
                validUsers.add(user);
            }
        }
        
        return validUsers;
    }
    
    // Check if user has required fields
    private boolean isUserValid(Map<String, Object> user) {
        return user != null && 
               user.containsKey("id") && user.get("id") != null &&
               user.containsKey("name") && user.get("name") != null;
    }
    
    // Transform user data to standard format
    private Map<String, Object> transformUser(Map<String, Object> originalUser) {
        HashMap<String, Object> cleanUser = new HashMap<>();
        
        // Clean up each field
        originalUser.entrySet().forEach(entry -> {
            String key = entry.getKey();
            Object value = entry.getValue();
            if (value != null) {
                cleanUser.put(key.toLowerCase(), value.toString().trim());
            }
        });
        
        return cleanUser;
    }
}
'''

    return {
        'original_ai_java': original_ai_java,
        'formatted_ai_java': formatted_ai_java,
        'human_java': human_java
    }

def test_java_evasion_resistance():
    """Test Java evasion-resistant detection"""
    
    print("Testing Java Evasion-Resistant AI Detection")
    print("=" * 55)
    
    # Initialize Java detector
    config = {
        'ai_indicators': {
            'strong_indicators': [],
            'moderate_indicators': [],
            'weak_indicators': []
        }
    }
    
    detector = JavaEvasionDetector(config)
    
    # Get Java test samples
    samples = create_java_test_samples()
    
    # Test each sample
    results = {}
    
    for sample_name, java_code in samples.items():
        print(f"\nAnalyzing {sample_name.replace('_', ' ').title()}:")
        print("-" * 40)
        
        analysis = detector.analyze_content(java_code, '.java')
        results[sample_name] = analysis
        
        print(f"AI Confidence: {analysis['copilot_confidence']:.2%}")
        print(f"Risk Level: {analysis['risk_level']}")
        
        # Show Java-specific analysis
        java_analysis = analysis['java_analysis']
        print(f"Semantic Score: {java_analysis.get('semantic_score', 0):.2f}")
        print(f"Structure Score: {java_analysis.get('structure_score', 0):.2f}")
        print(f"Naming Score: {java_analysis.get('naming_score', 0):.2f}")
        print(f"API Usage Score: {java_analysis.get('api_score', 0):.2f}")
        
        # Show evasion detection
        evasion_data = analysis['evasion_resistance']
        if evasion_data['evasion_detected']:
            print(f"⚠️  Java Evasion Attempts: {', '.join(evasion_data['evasion_indicators'])}")
        
        # Show Java pattern summary
        pattern_summary = evasion_data.get('java_specific_patterns', {})
        if pattern_summary:
            print("Java Pattern Detections:")
            for pattern_type, count in pattern_summary.items():
                if count > 0:
                    print(f"  • {pattern_type}: {count} matches")
        
        print("Explanation:")
        for explanation in analysis['explanation']:
            print(f"  • {explanation}")
    
    # Java-specific comparison
    print("\n" + "=" * 55)
    print("JAVA DETECTION SUMMARY")
    print("=" * 55)
    
    for sample_name, result in results.items():
        confidence = result['copilot_confidence']
        evasion_detected = result['evasion_resistance']['evasion_detected']
        
        print(f"{sample_name.replace('_', ' ').title():<25}: {confidence:.1%} AI confidence", end="")
        if evasion_detected:
            print(" [EVASION DETECTED]")
        else:
            print()
    
    # Java-specific insights
    print("\n" + "=" * 55)
    print("JAVA FORMATTING RESILIENCE")
    print("=" * 55)
    
    original_conf = results['original_ai_java']['copilot_confidence']
    formatted_conf = results['formatted_ai_java']['copilot_confidence']
    human_conf = results['human_java']['copilot_confidence']
    
    java_resilience = (formatted_conf / original_conf) if original_conf > 0 else 0
    
    print(f"Java Detection Resilience: {java_resilience:.1%}")
    print(f"  Original AI Java: {original_conf:.1%}")
    print(f"  Formatted AI Java: {formatted_conf:.1%}")
    print(f"  Human Java: {human_conf:.1%}")
    
    if java_resilience > 0.70:
        print("✅ Excellent Java evasion resistance")
    elif java_resilience > 0.50:
        print("⚠️ Moderate Java evasion resistance")
    else:
        print("❌ Poor Java evasion resistance")
    
    print("\nJava-Specific Evasion Resistance Techniques:")
    print("• Semantic pattern analysis (exception handling, method patterns)")
    print("• Java structure analysis (class organization, annotations)")
    print("• Complexity analysis (method complexity, inheritance patterns)")
    print("• Java naming convention analysis (AI vs human naming)")
    print("• API usage pattern analysis (preferred Java APIs)")
    print("• Formatter signature detection (Google Java Format, Spotless)")
    
    print("\nJava Formatting Tools Handled:")
    print("• Google Java Format (code style normalization)")
    print("• Spotless (import organization, formatting)")
    print("• IntelliJ IDEA refactoring (method extraction, variable renaming)")
    print("• Eclipse formatter (brace style, indentation)")
    print("• Checkstyle compliance formatting")

if __name__ == "__main__":
    test_java_evasion_resistance()