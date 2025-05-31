package com.copilotanalyzer.intellij.events

import com.google.gson.Gson
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.BlockingQueue
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread

object EventPublisher {
    private val eventQueue: BlockingQueue<Map<String, Any>> = LinkedBlockingQueue()
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val gson = Gson()
    private var isPublishing = false
    private var publishingThread: Thread? = null
    
    // Configuration
    private var apiEndpoint: String = ""
    private var apiKey: String = ""
    private var batchSize: Int = 10
    private var maxRetries: Int = 3
    
    fun configure(endpoint: String, key: String, batch: Int = 10) {
        apiEndpoint = endpoint
        apiKey = key
        batchSize = batch
        startPublishing()
    }
    
    fun publishEvent(event: Map<String, Any>) {
        if (apiEndpoint.isNotEmpty()) {
            eventQueue.offer(event)
        }
    }
    
    private fun startPublishing() {
        if (!isPublishing) {
            isPublishing = true
            publishingThread = thread(start = true, name = "EventPublisher") {
                publishEvents()
            }
        }
    }
    
    fun stopPublishing() {
        isPublishing = false
        publishingThread?.interrupt()
    }
    
    private fun publishEvents() {
        val batch = mutableListOf<Map<String, Any>>()
        
        while (isPublishing) {
            try {
                // Collect events in batches
                val event = eventQueue.poll(5, TimeUnit.SECONDS)
                if (event != null) {
                    batch.add(event)
                    
                    // Collect more events until batch is full or timeout
                    while (batch.size < batchSize && eventQueue.isNotEmpty()) {
                        val nextEvent = eventQueue.poll(100, TimeUnit.MILLISECONDS)
                        if (nextEvent != null) {
                            batch.add(nextEvent)
                        } else {
                            break
                        }
                    }
                    
                    if (batch.isNotEmpty()) {
                        sendBatch(batch.toList())
                        batch.clear()
                    }
                }
            } catch (e: InterruptedException) {
                break
            } catch (e: Exception) {
                println("Error in event publishing: ${e.message}")
            }
        }
    }
    
    private fun sendBatch(events: List<Map<String, Any>>) {
        var attempt = 0
        while (attempt < maxRetries) {
            try {
                val payload = mapOf(
                    "events" to events,
                    "timestamp" to System.currentTimeMillis(),
                    "source" to "intellij-plugin",
                    "version" to "1.0.0"
                )
                
                val json = gson.toJson(payload)
                val mediaType = "application/json; charset=utf-8".toMediaType()
                val requestBody = json.toRequestBody(mediaType)
                
                val request = Request.Builder()
                    .url(apiEndpoint)
                    .addHeader("Authorization", "Bearer $apiKey")
                    .addHeader("Content-Type", "application/json")
                    .addHeader("User-Agent", "CopilotAnalyzer-IntelliJ/1.0.0")
                    .post(requestBody)
                    .build()
                
                client.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        println("Successfully published ${events.size} events")
                        return
                    } else {
                        println("Failed to publish events: ${response.code} ${response.message}")
                    }
                }
            } catch (e: IOException) {
                println("Network error publishing events: ${e.message}")
            }
            
            attempt++
            if (attempt < maxRetries) {
                Thread.sleep(1000 * attempt) // Exponential backoff
            }
        }
        
        println("Failed to publish events after $maxRetries attempts")
    }
    
    fun getQueueSize(): Int = eventQueue.size
    
    fun isConnected(): Boolean = apiEndpoint.isNotEmpty() && apiKey.isNotEmpty()
}