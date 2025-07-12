# Test Questions for Voice Conversational Agentic AI

## 🎯 Basic Functionality Tests

### Voice/Text Chat
1. **Simple greeting**: "Hello, how are you?"
2. **Basic conversation**: "What's the weather like today?"
3. **System capabilities**: "What can you help me with?"
4. **Real-time response**: "Can you respond quickly to my questions?"

### Real Estate Knowledge Base Tests

#### Property Information
5. **Property search**: "Tell me about properties in the database"
6. **Specific property**: "What properties are available in New York?"
7. **Price range**: "Show me properties under $500,000"
8. **Property details**: "What are the features of the luxury properties?"

#### Market Analysis
9. **Market trends**: "What are the current real estate market trends?"
10. **Price analysis**: "Which areas have the highest property prices?"
11. **Investment advice**: "What are good investment opportunities in the database?"
12. **Market comparison**: "Compare property prices across different cities"

#### Broker Information
13. **Broker details**: "Who are the top brokers in the database?"
14. **Broker contact**: "How can I contact the brokers listed?"
15. **Broker performance**: "Which brokers have the most properties?"

#### Data Analysis
16. **Statistics**: "What are the summary statistics of the property database?"
17. **Property types**: "What types of properties are available?"
18. **Geographic distribution**: "Where are most properties located?"
19. **Price distribution**: "What's the average property price?"

## 🔍 Advanced Feature Tests

### RAG (Retrieval-Augmented Generation)
20. **Specific query**: "Find properties with 3 bedrooms and 2 bathrooms"
21. **Complex search**: "Show me luxury properties with swimming pools"
22. **Location-based**: "What properties are available in downtown areas?"
23. **Price-performance**: "Which properties offer the best value for money?"

### Voice Interaction
24. **Voice quality**: "Can you speak clearly and naturally?"
25. **Response timing**: "How quickly do you respond to voice input?"
26. **Audio processing**: "Can you understand my voice clearly?"

### Conversation Memory
27. **Context retention**: "Remember what we discussed about properties?"
28. **Follow-up questions**: "Tell me more about the properties you mentioned"
29. **Conversation history**: "What was our previous conversation about?"

## 🧪 Edge Case Tests

### Error Handling
30. **Invalid queries**: "Find properties that don't exist"
31. **Empty requests**: Send empty message
32. **Malformed data**: "Search for properties with invalid criteria"

### Performance Tests
33. **Long queries**: "Give me a detailed analysis of all properties with comprehensive market insights and investment recommendations"
34. **Multiple requests**: Send several questions quickly
35. **Large data requests**: "Show me all properties with complete details"

## 🎨 Creative Tests

### Natural Language Understanding
36. **Casual language**: "Hey, what's up with the real estate market?"
37. **Complex questions**: "If I had $1 million to invest in real estate, what would you recommend based on the data?"
38. **Hypothetical scenarios**: "What if I wanted to buy a property for rental income?"

### Multi-modal Interaction
39. **Text + Voice**: Mix text and voice messages
40. **Conversation flow**: Have a natural back-and-forth conversation

## 📊 Data-Specific Tests

### CSV Dataset Queries
41. **Dataset overview**: "What's in the HackathonInternalKnowledgeBase.csv file?"
42. **Data structure**: "What columns are in the real estate dataset?"
43. **Sample data**: "Show me some examples from the property database"
44. **Data quality**: "How many properties are in the database?"

### Specific Property Queries
45. **By location**: "Find properties in California"
46. **By price**: "Show me properties between $200,000 and $400,000"
47. **By features**: "Find properties with specific amenities"
48. **By broker**: "Show me properties listed by specific brokers"

## 🚀 System Integration Tests

### API Endpoints
49. **Health check**: Test `/health` endpoint
50. **Chat API**: Test `/api/v1/chat` with different messages
51. **Document upload**: Test document upload functionality
52. **Conversation management**: Test conversation history

### WebSocket Functionality
53. **Connection stability**: Keep WebSocket open for extended period
54. **Message handling**: Send various message types
55. **Error recovery**: Test connection recovery after errors

## 🎯 Recommended Test Sequence

### Quick Test (5 minutes)
1. "Hello, how are you?"
2. "What properties are in the database?"
3. "Tell me about the real estate market"
4. "Who are the top brokers?"
5. "What's the average property price?"

### Comprehensive Test (15 minutes)
1. Start with basic greeting
2. Ask about dataset contents
3. Query specific property information
4. Test voice interaction
5. Ask follow-up questions
6. Test error handling
7. Verify conversation memory

### Advanced Test (30 minutes)
1. Test all major features
2. Try complex queries
3. Test voice quality and timing
4. Verify RAG functionality
5. Test conversation flow
6. Check data accuracy
7. Test system performance

## 📝 Testing Tips

1. **Use the web interface** at `http://localhost:8000` for visual testing
2. **Test both voice and text** input methods
3. **Check response quality** and relevance
4. **Verify audio output** is clear and natural
5. **Test conversation continuity** across multiple messages
6. **Monitor server logs** for any errors or issues
7. **Test with real estate data** to verify RAG functionality

## 🐛 Common Issues to Watch For

- WebSocket connection errors
- Speech-to-text accuracy
- Text-to-speech quality
- Response generation time
- Data retrieval accuracy
- Conversation memory issues
- Audio processing errors 