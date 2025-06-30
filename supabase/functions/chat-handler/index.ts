import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { message, conversation_id, user_id, context } = await req.json()

    // Validate input
    if (!message || !user_id) {
      return new Response(
        JSON.stringify({ error: 'Message and user_id are required' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Store user message
    await supabaseClient
      .from('messages')
      .insert({
        conversation_id,
        user_id,
        type: 'user',
        content: message,
        metadata: context || {}
      })

    // Call OpenAI API
    const openaiApiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openaiApiKey) {
      throw new Error('OpenAI API key not configured')
    }

    // Build conversation history
    const { data: messageHistory } = await supabaseClient
      .from('messages')
      .select('*')
      .eq('conversation_id', conversation_id)
      .order('created_at', { ascending: true })
      .limit(20)

    const conversationHistory: ChatMessage[] = messageHistory?.map((msg: any) => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.content
    })) || []

    // Add system message
    const systemMessage: ChatMessage = {
      role: 'system',
      content: `You are an expert Malta tax advisor AI assistant. You help users with:
      - Malta income tax calculations
      - Corporate tax guidance
      - VAT calculations
      - Social security contributions
      - Stamp duty calculations
      - Tax compliance advice
      
      Always provide accurate, helpful information specific to Malta's tax system. 
      When performing calculations, be precise and show your work.
      
      User context: ${JSON.stringify(context || {})}`
    }

    const messages = [
      systemMessage,
      ...conversationHistory,
      { role: 'user' as const, content: message }
    ]

    // Call OpenAI
    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: messages,
        max_tokens: 1000,
        temperature: 0.1,
        stream: false
      })
    })

    if (!openaiResponse.ok) {
      throw new Error(`OpenAI API error: ${openaiResponse.status}`)
    }

    const openaiData = await openaiResponse.json()
    const assistantMessage = openaiData.choices[0]?.message?.content

    if (!assistantMessage) {
      throw new Error('No response from OpenAI')
    }

    // Store assistant response
    await supabaseClient
      .from('messages')
      .insert({
        conversation_id,
        user_id,
        type: 'assistant',
        content: assistantMessage,
        metadata: {
          model: 'gpt-4o',
          tokens_used: openaiData.usage?.total_tokens || 0
        }
      })

    // Update conversation
    await supabaseClient
      .from('conversations')
      .update({
        updated_at: new Date().toISOString(),
        message_count: (messageHistory?.length || 0) + 2
      })
      .eq('id', conversation_id)

    return new Response(
      JSON.stringify({
        message: assistantMessage,
        conversation_id,
        tokens_used: openaiData.usage?.total_tokens || 0,
        timestamp: new Date().toISOString()
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('Chat handler error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}) 