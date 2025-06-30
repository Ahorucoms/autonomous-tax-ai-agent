import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { ScrollArea } from './ui/scroll-area';
import { Avatar, AvatarFallback } from './ui/avatar';
import { 
  Send, 
  Bot, 
  User, 
  ThumbsUp, 
  ThumbsDown, 
  Copy, 
  RefreshCw,
  MessageSquare,
  Sparkles,
  Clock,
  CheckCircle
} from 'lucide-react';

export function ChatInterface({ user, jurisdiction, language, persona }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    initializeChat();
  }, [jurisdiction, language, persona]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = async () => {
    try {
      // Create new conversation
      const conversation = await createConversation();
      setConversationId(conversation.id);
      
      // Add welcome message
      const welcomeMessage = getWelcomeMessage();
      setMessages([welcomeMessage]);
      
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const createConversation = async () => {
    // Simulate API call - in production, this would call the backend
    const conversation = {
      id: `conv-${Date.now()}`,
      title: 'New Conversation',
      created_at: new Date().toISOString(),
      jurisdiction,
      language,
      persona_id: persona?.id
    };
    
    return conversation;
  };

  const getWelcomeMessage = () => {
    const welcomeTexts = {
      en: {
        MT: `Hello! I'm your AI tax advisor for Malta. I can help you with income tax calculations, VAT registration, corporate tax, and compliance questions. What would you like to know about Malta's tax system?`,
        FR: `Hello! I'm your AI tax advisor for France. I can help you with income tax, corporate tax, VAT, and French tax compliance. How can I assist you today?`,
        default: `Hello! I'm your AI tax advisor. I can help you with tax calculations, compliance questions, and regulatory guidance for ${jurisdiction}. What would you like to know?`
      },
      fr: {
        FR: `Bonjour ! Je suis votre conseiller fiscal IA pour la France. Je peux vous aider avec l'impôt sur le revenu, l'impôt sur les sociétés, la TVA et la conformité fiscale française. Comment puis-je vous aider aujourd'hui ?`,
        MT: `Bonjour ! Je suis votre conseiller fiscal IA pour Malte. Je peux vous aider avec les calculs d'impôt sur le revenu, l'enregistrement TVA, l'impôt des sociétés et les questions de conformité. Que souhaitez-vous savoir sur le système fiscal maltais ?`,
        default: `Bonjour ! Je suis votre conseiller fiscal IA. Je peux vous aider avec les calculs fiscaux, les questions de conformité et les conseils réglementaires pour ${jurisdiction}. Que souhaitez-vous savoir ?`
      }
    };

    const text = welcomeTexts[language]?.[jurisdiction] || welcomeTexts[language]?.default || welcomeTexts.en.default;

    return {
      id: `msg-welcome-${Date.now()}`,
      type: 'assistant',
      content: text,
      timestamp: new Date().toISOString(),
      metadata: {
        confidence_score: 1.0,
        intent: 'welcome',
        suggestions: getSuggestions()
      }
    };
  };

  const getSuggestions = () => {
    const suggestions = {
      en: {
        MT: [
          "How do I calculate income tax in Malta?",
          "What are the VAT rates in Malta?",
          "How do I register for VAT?",
          "What business expenses can I deduct?"
        ],
        FR: [
          "How do I calculate income tax in France?",
          "What are the French VAT rates?",
          "How do I file my tax return online?",
          "What tax deductions are available?"
        ]
      },
      fr: {
        FR: [
          "Comment calculer mon impôt sur le revenu en France ?",
          "Quels sont les taux de TVA français ?",
          "Comment déclarer mes revenus en ligne ?",
          "Quelles déductions fiscales sont disponibles ?"
        ],
        MT: [
          "Comment calculer l'impôt sur le revenu à Malte ?",
          "Quels sont les taux de TVA à Malte ?",
          "Comment s'enregistrer pour la TVA ?",
          "Quelles charges d'entreprise puis-je déduire ?"
        ]
      }
    };

    return suggestions[language]?.[jurisdiction] || suggestions.en.MT;
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: `msg-user-${Date.now()}`,
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Simulate AI response - in production, this would call the backend API
      const aiResponse = await getAIResponse(inputMessage.trim());
      
      const assistantMessage = {
        id: `msg-assistant-${Date.now()}`,
        type: 'assistant',
        content: aiResponse.content,
        timestamp: new Date().toISOString(),
        metadata: aiResponse.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Failed to get AI response:', error);
      
      const errorMessage = {
        id: `msg-error-${Date.now()}`,
        type: 'system',
        content: language === 'fr' 
          ? "Désolé, une erreur s'est produite. Veuillez réessayer."
          : "Sorry, an error occurred. Please try again.",
        timestamp: new Date().toISOString(),
        metadata: { error: true }
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getAIResponse = async (message) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    // Simple response logic based on message content
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('income tax') || lowerMessage.includes('impôt sur le revenu')) {
      return getIncomeTaxResponse();
    } else if (lowerMessage.includes('vat') || lowerMessage.includes('tva')) {
      return getVATResponse();
    } else if (lowerMessage.includes('business') || lowerMessage.includes('entreprise')) {
      return getBusinessResponse();
    } else if (lowerMessage.includes('deduction') || lowerMessage.includes('déduction')) {
      return getDeductionResponse();
    } else {
      return getGeneralResponse();
    }
  };

  const getIncomeTaxResponse = () => {
    if (jurisdiction === 'MT' && language === 'en') {
      return {
        content: `Malta operates a progressive income tax system for 2025:

**Tax Brackets:**
• €0 - €9,100: 0% (tax-free allowance)
• €9,101 - €14,500: 15%
• €14,501 - €19,500: 25%
• €19,501 - €60,000: 25%
• Above €60,000: 35%

**Example Calculation for €45,000 annual salary:**
1. First €9,100: €0 tax
2. €9,101 - €14,500: €5,400 × 15% = €810
3. €14,501 - €45,000: €30,500 × 25% = €7,625

**Total Income Tax: €8,435**

Additional considerations:
• Married couples get an extra €600 deduction
• Self-employed can deduct business expenses
• Social security contributions are separate

Would you like me to calculate tax for a specific income amount?`,
        metadata: {
          confidence_score: 0.95,
          intent: 'income_tax_calculation',
          calculations: {
            example_income: 45000,
            total_tax: 8435,
            effective_rate: 18.7
          },
          suggested_actions: [
            'Calculate tax for specific income',
            'Learn about deductions',
            'Understand social security'
          ]
        }
      };
    } else if (jurisdiction === 'FR' && language === 'fr') {
      return {
        content: `La France applique un barème progressif de l'impôt sur le revenu pour 2025 :

**Tranches d'imposition :**
• Jusqu'à €10,777 : 0%
• €10,778 - €27,478 : 11%
• €27,479 - €78,570 : 30%
• €78,571 - €168,994 : 41%
• Au-delà de €168,995 : 45%

**Exemple de calcul pour €50,000 de revenus annuels :**
1. Jusqu'à €10,777 : €0 d'impôt
2. €10,778 - €27,478 : €16,700 × 11% = €1,837
3. €27,479 - €50,000 : €22,521 × 30% = €6,756

**Impôt total : €8,593**

Considérations supplémentaires :
• Abattement de 10% sur les salaires
• Quotient familial selon le nombre de parts
• Déductions possibles (frais réels, dons, etc.)

Souhaitez-vous que je calcule l'impôt pour un montant spécifique ?`,
        metadata: {
          confidence_score: 0.95,
          intent: 'calcul_impot_revenu',
          calculations: {
            exemple_revenus: 50000,
            impot_total: 8593,
            taux_effectif: 17.2
          },
          suggested_actions: [
            'Calculer pour revenus spécifiques',
            'En savoir plus sur les déductions',
            'Comprendre le quotient familial'
          ]
        }
      };
    }

    return getGeneralResponse();
  };

  const getVATResponse = () => {
    if (jurisdiction === 'MT' && language === 'en') {
      return {
        content: `Malta VAT (Value Added Tax) system for 2025:

**VAT Rates:**
• Standard Rate: 18%
• Reduced Rate: 5% (accommodation, books, newspapers, certain food)
• Super Reduced Rate: 7% (medical equipment, cultural events)
• Zero Rate: 0% (exports, international transport)

**Registration Requirements:**
• Mandatory if annual turnover exceeds €35,000
• Must register within 10 days of exceeding threshold
• Voluntary registration available for lower turnovers

**VAT Returns:**
• Monthly: turnover > €700,000
• Quarterly: most businesses
• Annual: turnover < €56,000

**Registration Process:**
1. Apply online through IRD Malta portal
2. Provide business details and projections
3. Receive VAT number within 2-3 weeks

Need help with VAT registration or calculating VAT for your business?`,
        metadata: {
          confidence_score: 0.92,
          intent: 'vat_information',
          suggested_actions: [
            'Calculate VAT for specific amount',
            'Help with VAT registration',
            'Understand VAT return filing'
          ]
        }
      };
    }

    return getGeneralResponse();
  };

  const getBusinessResponse = () => {
    return {
      content: `Business tax considerations for ${jurisdiction}:

**Key Areas:**
• Corporate income tax rates and calculations
• Business expense deductions
• VAT registration and compliance
• Employment tax obligations
• Annual filing requirements

**Common Deductible Expenses:**
• Office rent and utilities
• Professional fees and services
• Business equipment and software
• Travel and transportation
• Marketing and advertising
• Professional development

**Important Deadlines:**
• VAT returns: Monthly/Quarterly
• Income tax returns: Annual
• Corporate tax: Annual

Would you like specific information about any of these areas?`,
      metadata: {
        confidence_score: 0.88,
        intent: 'business_tax_guidance',
        suggested_actions: [
          'Learn about corporate tax rates',
          'Understand deductible expenses',
          'Get VAT guidance'
        ]
      }
    };
  };

  const getDeductionResponse = () => {
    return {
      content: `Tax deductions available in ${jurisdiction}:

**Personal Deductions:**
• Standard personal allowance
• Married couple allowances
• Dependent allowances
• Charitable donations
• Professional development expenses

**Business Deductions:**
• Operating expenses
• Equipment depreciation
• Professional fees
• Business travel
• Home office expenses (if applicable)

**Documentation Required:**
• Keep all receipts and invoices
• Maintain detailed records
• Ensure expenses are business-related
• Follow local tax authority guidelines

Would you like specific guidance on claiming any of these deductions?`,
      metadata: {
        confidence_score: 0.85,
        intent: 'tax_deductions',
        suggested_actions: [
          'Learn about personal allowances',
          'Understand business deductions',
          'Get record-keeping guidance'
        ]
      }
    };
  };

  const getGeneralResponse = () => {
    return {
      content: `I'm here to help with your tax questions for ${jurisdiction}. I can assist with:

• **Tax Calculations**: Income tax, corporate tax, VAT calculations
• **Compliance**: Filing requirements, deadlines, registration
• **Deductions**: Personal and business expense deductions
• **Forms**: Help with tax forms and documentation
• **Planning**: Tax planning strategies and optimization

Please feel free to ask specific questions about:
- Tax rates and calculations
- Filing requirements and deadlines
- Deductible expenses
- Business tax obligations
- Personal tax planning

What specific tax topic would you like to explore?`,
      metadata: {
        confidence_score: 0.75,
        intent: 'general_assistance',
        suggested_actions: [
          'Ask about tax calculations',
          'Learn about filing requirements',
          'Understand deductions'
        ]
      }
    };
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
  };

  const handleFeedback = async (messageId, rating) => {
    try {
      // In production, this would call the feedback API
      console.log(`Feedback for message ${messageId}: ${rating}`);
      
      // Update message with feedback
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, feedback: rating }
          : msg
      ));
      
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Chat Header */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary/10 p-2 rounded-lg">
                <Bot className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">AI Tax Advisor</CardTitle>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Badge variant="secondary">{jurisdiction}</Badge>
                  <Badge variant="outline">{language.toUpperCase()}</Badge>
                  {persona && <Badge variant="default">{persona.name}</Badge>}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm" onClick={initializeChat}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Messages Area */}
      <Card className="flex-1 flex flex-col">
        <CardContent className="flex-1 p-0">
          <ScrollArea className="h-[500px] p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex space-x-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className={`rounded-lg p-3 ${
                      message.type === 'user' 
                        ? 'bg-primary text-primary-foreground' 
                        : message.type === 'system'
                        ? 'bg-destructive/10 text-destructive'
                        : 'bg-muted'
                    }`}>
                      <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                      
                      {/* Message metadata */}
                      {message.metadata && (
                        <div className="mt-2 pt-2 border-t border-border/20">
                          {message.metadata.confidence_score && (
                            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                              <CheckCircle className="h-3 w-3" />
                              <span>Confidence: {Math.round(message.metadata.confidence_score * 100)}%</span>
                            </div>
                          )}
                          
                          {message.metadata.suggested_actions && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {message.metadata.suggested_actions.map((action, index) => (
                                <Badge key={index} variant="secondary" className="text-xs cursor-pointer"
                                       onClick={() => handleSuggestionClick(action)}>
                                  {action}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Message actions */}
                      {message.type === 'assistant' && (
                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/20">
                          <div className="flex items-center space-x-1">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => handleFeedback(message.id, 'positive')}
                              className={`h-6 w-6 p-0 ${message.feedback === 'positive' ? 'text-green-600' : ''}`}
                            >
                              <ThumbsUp className="h-3 w-3" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => handleFeedback(message.id, 'negative')}
                              className={`h-6 w-6 p-0 ${message.feedback === 'negative' ? 'text-red-600' : ''}`}
                            >
                              <ThumbsDown className="h-3 w-3" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => copyMessage(message.content)}
                              className="h-6 w-6 p-0"
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex space-x-3 max-w-[80%]">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        <Bot className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="bg-muted rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin">
                          <Sparkles className="h-4 w-4" />
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {language === 'fr' ? 'Réflexion en cours...' : 'Thinking...'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>

        {/* Input Area */}
        <div className="p-4 border-t">
          {/* Quick suggestions */}
          {messages.length === 1 && messages[0].metadata?.suggestions && (
            <div className="mb-3">
              <div className="text-xs text-muted-foreground mb-2">
                {language === 'fr' ? 'Suggestions :' : 'Quick suggestions:'}
              </div>
              <div className="flex flex-wrap gap-2">
                {messages[0].metadata.suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="text-xs"
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}

          <div className="flex space-x-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={language === 'fr' 
                ? 'Posez votre question fiscale...' 
                : 'Ask your tax question...'
              }
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              onClick={sendMessage} 
              disabled={!inputMessage.trim() || isLoading}
              size="sm"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

