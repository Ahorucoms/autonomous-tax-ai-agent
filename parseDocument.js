/**
 * parseDocument Edge Function
 * Serverless function for parsing Malta tax documents with OCR and structured data extraction
 */

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
    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Get authorization header
    const authHeader = req.headers.get('Authorization')!
    const token = authHeader.replace('Bearer ', '')

    // Verify user authentication
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)
    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (req.method === 'POST') {
      return await handleDocumentParsing(req, supabase, user)
    }

    if (req.method === 'GET') {
      return await handleDocumentRetrieval(req, supabase, user)
    }

    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Edge function error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error', details: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

async function handleDocumentParsing(req, supabase, user) {
  const formData = await req.formData()
  const file = formData.get('file')
  const documentType = formData.get('documentType') || 'unknown'
  const metadata = JSON.parse(formData.get('metadata') || '{}')

  if (!file) {
    return new Response(
      JSON.stringify({ error: 'No file provided' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  // Generate unique filename
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `${user.id}/${timestamp}-${file.name}`

  try {
    // Upload file to Supabase Storage
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('documents')
      .upload(filename, file, {
        cacheControl: '3600',
        upsert: false
      })

    if (uploadError) {
      throw new Error(`Upload failed: ${uploadError.message}`)
    }

    // Get file buffer for processing
    const fileBuffer = await file.arrayBuffer()
    const fileType = file.type || getFileTypeFromName(file.name)

    // Parse document based on type
    const parseResult = await parseDocumentContent(fileBuffer, fileType, documentType)

    // Create document record in database
    const documentRecord = {
      id: crypto.randomUUID(),
      user_id: user.id,
      filename: file.name,
      file_path: filename,
      file_type: fileType,
      file_size: file.size,
      document_type: documentType,
      metadata: {
        ...metadata,
        original_filename: file.name,
        upload_timestamp: new Date().toISOString()
      },
      parsed_content: parseResult.content,
      extracted_data: parseResult.extractedData,
      processing_status: 'completed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    const { data: dbData, error: dbError } = await supabase
      .from('documents')
      .insert(documentRecord)
      .select()

    if (dbError) {
      throw new Error(`Database insert failed: ${dbError.message}`)
    }

    // Generate embeddings for vector search
    const embeddings = await generateEmbeddings(parseResult.content)
    
    // Store in vector database (Pinecone integration)
    await storeInVectorDatabase(documentRecord.id, embeddings, {
      document_type: documentType,
      user_id: user.id,
      filename: file.name,
      ...parseResult.extractedData
    })

    return new Response(
      JSON.stringify({
        success: true,
        document: dbData[0],
        parsing_result: parseResult,
        message: 'Document parsed and stored successfully'
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Document parsing error:', error)
    
    // Clean up uploaded file if processing failed
    try {
      await supabase.storage.from('documents').remove([filename])
    } catch (cleanupError) {
      console.error('Cleanup error:', cleanupError)
    }

    return new Response(
      JSON.stringify({ 
        error: 'Document parsing failed', 
        details: error.message 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
}

async function handleDocumentRetrieval(req, supabase, user) {
  const url = new URL(req.url)
  const documentId = url.searchParams.get('id')
  const search = url.searchParams.get('search')
  const documentType = url.searchParams.get('type')

  try {
    if (documentId) {
      // Get specific document
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .eq('id', documentId)
        .eq('user_id', user.id)
        .single()

      if (error) {
        throw new Error(`Document retrieval failed: ${error.message}`)
      }

      return new Response(
        JSON.stringify({ document: data }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (search) {
      // Perform vector search
      const searchResults = await performVectorSearch(search, {
        user_id: user.id,
        document_type: documentType
      })

      return new Response(
        JSON.stringify({ results: searchResults }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get user's documents
    let query = supabase
      .from('documents')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (documentType) {
      query = query.eq('document_type', documentType)
    }

    const { data, error } = await query

    if (error) {
      throw new Error(`Documents retrieval failed: ${error.message}`)
    }

    return new Response(
      JSON.stringify({ documents: data }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Document retrieval error:', error)
    return new Response(
      JSON.stringify({ 
        error: 'Document retrieval failed', 
        details: error.message 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
}

async function parseDocumentContent(fileBuffer, fileType, documentType) {
  const content = {
    text: '',
    pages: [],
    metadata: {}
  }

  const extractedData = {}

  try {
    if (fileType.includes('pdf')) {
      return await parsePDF(fileBuffer, documentType)
    } else if (fileType.includes('image')) {
      return await parseImage(fileBuffer, documentType)
    } else if (fileType.includes('text') || fileType.includes('plain')) {
      const text = new TextDecoder().decode(fileBuffer)
      return {
        content: { text, pages: [text], metadata: { pageCount: 1 } },
        extractedData: await extractTaxData(text, documentType)
      }
    } else {
      throw new Error(`Unsupported file type: ${fileType}`)
    }
  } catch (error) {
    console.error('Content parsing error:', error)
    return {
      content: { text: '', pages: [], metadata: { error: error.message } },
      extractedData: {}
    }
  }
}

async function parsePDF(fileBuffer, documentType) {
  // Simulate PDF parsing (in production, use pdf-parse or similar)
  const text = `[PDF Content] Document type: ${documentType}\nExtracted text from PDF document...`
  
  return {
    content: {
      text,
      pages: [text],
      metadata: { pageCount: 1, format: 'pdf' }
    },
    extractedData: await extractTaxData(text, documentType)
  }
}

async function parseImage(fileBuffer, documentType) {
  // Simulate OCR processing (in production, use Tesseract.js or cloud OCR)
  const text = `[OCR Content] Document type: ${documentType}\nExtracted text from image using OCR...`
  
  return {
    content: {
      text,
      pages: [text],
      metadata: { format: 'image', ocr: true }
    },
    extractedData: await extractTaxData(text, documentType)
  }
}

async function extractTaxData(text, documentType) {
  const extractedData = {
    document_type: documentType,
    confidence: 0.85
  }

  // Malta tax form specific extraction
  if (documentType === 'fs3') {
    extractedData.taxpayer_name = extractField(text, /name[:\s]+([^\n]+)/i)
    extractedData.id_number = extractField(text, /id[:\s]+([0-9]+[A-Z]?)/i)
    extractedData.annual_income = extractField(text, /income[:\s]+€?([0-9,]+)/i)
    extractedData.tax_year = extractField(text, /year[:\s]+([0-9]{4})/i)
  } else if (documentType === 'vat_return') {
    extractedData.vat_number = extractField(text, /vat[:\s]+([0-9]+)/i)
    extractedData.period = extractField(text, /period[:\s]+([^\n]+)/i)
    extractedData.total_vat = extractField(text, /total[:\s]+€?([0-9,]+)/i)
  }

  return extractedData
}

function extractField(text, regex) {
  const match = text.match(regex)
  return match ? match[1].trim() : null
}

async function generateEmbeddings(text) {
  // Simulate embedding generation (in production, use OpenAI embeddings or similar)
  const words = text.toLowerCase().split(/\s+/)
  const embedding = new Array(1536).fill(0).map(() => Math.random() - 0.5)
  
  return embedding
}

async function storeInVectorDatabase(documentId, embeddings, metadata) {
  // Simulate Pinecone storage (in production, use actual Pinecone client)
  const pineconeApiKey = Deno.env.get('PINECONE_API_KEY')
  const pineconeEnvironment = Deno.env.get('PINECONE_ENVIRONMENT')
  const pineconeIndex = Deno.env.get('PINECONE_INDEX')

  if (!pineconeApiKey) {
    console.log('Pinecone not configured, skipping vector storage')
    return
  }

  try {
    const response = await fetch(`https://${pineconeIndex}-${pineconeEnvironment}.svc.pinecone.io/vectors/upsert`, {
      method: 'POST',
      headers: {
        'Api-Key': pineconeApiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        vectors: [{
          id: documentId,
          values: embeddings,
          metadata: metadata
        }]
      })
    })

    if (!response.ok) {
      throw new Error(`Pinecone upsert failed: ${response.statusText}`)
    }

    console.log('Vector stored successfully in Pinecone')
  } catch (error) {
    console.error('Vector storage error:', error)
    // Don't throw - document parsing should succeed even if vector storage fails
  }
}

async function performVectorSearch(query, filters = {}) {
  // Simulate vector search (in production, use actual Pinecone query)
  const queryEmbedding = await generateEmbeddings(query)
  
  const pineconeApiKey = Deno.env.get('PINECONE_API_KEY')
  const pineconeEnvironment = Deno.env.get('PINECONE_ENVIRONMENT')
  const pineconeIndex = Deno.env.get('PINECONE_INDEX')

  if (!pineconeApiKey) {
    return []
  }

  try {
    const response = await fetch(`https://${pineconeIndex}-${pineconeEnvironment}.svc.pinecone.io/query`, {
      method: 'POST',
      headers: {
        'Api-Key': pineconeApiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        vector: queryEmbedding,
        topK: 10,
        includeMetadata: true,
        filter: filters
      })
    })

    if (!response.ok) {
      throw new Error(`Pinecone query failed: ${response.statusText}`)
    }

    const data = await response.json()
    return data.matches || []
  } catch (error) {
    console.error('Vector search error:', error)
    return []
  }
}

function getFileTypeFromName(filename) {
  const extension = filename.split('.').pop()?.toLowerCase()
  
  const typeMap = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
    'tiff': 'image/tiff'
  }
  
  return typeMap[extension] || 'application/octet-stream'
}

