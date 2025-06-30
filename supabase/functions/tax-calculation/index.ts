import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { annual_income, marital_status = 'single', calculation_type = 'income_tax' } = await req.json()

    // Validate input
    if (!annual_income || annual_income <= 0) {
      return new Response(
        JSON.stringify({ error: 'Valid annual income is required' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Malta 2024 tax calculation logic
    let result: any = {}

    if (calculation_type === 'income_tax') {
      // Malta 2024 tax brackets
      const brackets = marital_status === 'single' 
        ? [
            { limit: 9100, rate: 0.0 },
            { limit: 14500, rate: 0.15 },
            { limit: 19500, rate: 0.25 },
            { limit: 60000, rate: 0.25 },
            { limit: Infinity, rate: 0.35 }
          ]
        : [
            { limit: 12700, rate: 0.0 },
            { limit: 21200, rate: 0.15 },
            { limit: 28700, rate: 0.25 },
            { limit: 60000, rate: 0.25 },
            { limit: Infinity, rate: 0.35 }
          ]

      let tax_due = 0
      let remaining_income = annual_income
      const breakdown = []

      for (let i = 0; i < brackets.length; i++) {
        if (remaining_income <= 0) break

        const bracket = brackets[i]
        const prev_limit = i === 0 ? 0 : brackets[i-1].limit
        const taxable_in_bracket = Math.min(remaining_income, bracket.limit - prev_limit)

        if (taxable_in_bracket > 0) {
          const tax_in_bracket = taxable_in_bracket * bracket.rate
          tax_due += tax_in_bracket

          breakdown.push({
            bracket: `€${prev_limit.toLocaleString()} - €${Math.min(bracket.limit, annual_income).toLocaleString()}`,
            rate: `${(bracket.rate * 100).toFixed(0)}%`,
            taxable_amount: taxable_in_bracket,
            tax_amount: tax_in_bracket
          })
        }

        remaining_income -= taxable_in_bracket
      }

      const effective_rate = (tax_due / annual_income) * 100

      result = {
        annual_income,
        marital_status,
        tax_due: Math.round(tax_due * 100) / 100,
        effective_rate: Math.round(effective_rate * 100) / 100,
        breakdown,
        calculation_date: new Date().toISOString()
      }
    }

    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Log calculation to database
    await supabaseClient
      .from('tax_calculations')
      .insert({
        calculation_type,
        input_data: { annual_income, marital_status },
        result_data: result,
        created_at: new Date().toISOString()
      })

    return new Response(
      JSON.stringify(result),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}) 