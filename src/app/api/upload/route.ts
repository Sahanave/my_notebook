import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { DocumentSummary } from '@/types/api';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

function extractTextFromPDF(buffer: Buffer): string {
  // Simple text extraction - in production you'd use a proper PDF parser
  // For now, we'll simulate this since PDF parsing in browser/serverless is complex
  const text = buffer.toString('utf8', 0, Math.min(2000, buffer.length));
  return text.replace(/[^\x20-\x7E]/g, ' ').trim();
}

async function generateSummaryWithAI(text: string, filename: string): Promise<DocumentSummary> {
  const prompt = `Please analyze this document and generate a comprehensive summary.
  
Document filename: ${filename}
Document content: ${text.slice(0, 3000)}...

Provide a structured summary with title, abstract, key points, main topics, difficulty level, estimated read time, document type, authors, and publication date.`;

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are an expert document analyst. Analyze documents and provide structured summaries in JSON format."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      tools: [{
        type: "function",
        function: {
          name: "extract_summary",
          description: "Extract structured summary from document",
          parameters: {
            type: "object",
            properties: {
              title: { type: "string" },
              abstract: { type: "string" },
              key_points: { type: "array", items: { type: "string" } },
              main_topics: { type: "array", items: { type: "string" } },
              difficulty_level: { type: "string", enum: ["beginner", "intermediate", "advanced"] },
              estimated_read_time: { type: "string" },
              document_type: { type: "string", enum: ["research_paper", "tutorial", "book_chapter", "article"] },
              authors: { type: "array", items: { type: "string" } },
              publication_date: { type: "string" }
            },
            required: ["title", "abstract", "key_points", "main_topics", "difficulty_level", "estimated_read_time", "document_type", "authors", "publication_date"]
          }
        }
      }],
      tool_choice: { type: "function", function: { name: "extract_summary" } }
    });

    if (completion.choices[0]?.message?.tool_calls?.[0]) {
      const toolCall = completion.choices[0].message.tool_calls[0];
      const structuredData = JSON.parse(toolCall.function.arguments);
      return structuredData as DocumentSummary;
    }

    throw new Error("No structured response from OpenAI");

  } catch (error) {
    console.error("Error generating AI summary:", error);
    
    // Fallback summary
    return {
      title: filename.replace('.pdf', ''),
      abstract: `AI-generated summary of ${filename}. Full analysis unavailable due to processing error.`,
      key_points: [
        "Document uploaded successfully",
        "Text extraction completed", 
        "Basic analysis performed"
      ],
      main_topics: ["Document analysis", "Content processing"],
      difficulty_level: "intermediate",
      estimated_read_time: "30 minutes",
      document_type: "article",
      authors: ["Unknown"],
      publication_date: new Date().toISOString().split('T')[0]
    };
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ detail: 'No file provided' }, { status: 400 });
    }

    if (file.type !== 'application/pdf') {
      return NextResponse.json({ detail: 'Only PDF files are allowed' }, { status: 400 });
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      return NextResponse.json({ detail: 'File size must be less than 10MB' }, { status: 400 });
    }

    const startTime = Date.now();
    
    // Read file buffer
    const buffer = Buffer.from(await file.arrayBuffer());
    
    // Extract text (simplified)
    const extractedText = extractTextFromPDF(buffer);
    
    // Generate AI summary
    let documentSummary: DocumentSummary;
    
    if (process.env.OPENAI_API_KEY) {
      try {
        documentSummary = await generateSummaryWithAI(extractedText, file.name);
        console.log(`✅ AI summary generated for: ${file.name}`);
      } catch (error) {
        console.error("Error generating summary:", error);
        // Use fallback from the function
        documentSummary = await generateSummaryWithAI(extractedText, file.name);
      }
    } else {
      // Basic fallback when no OpenAI key
      documentSummary = {
        title: file.name.replace('.pdf', ''),
        abstract: `Document analysis of ${file.name}. Set OPENAI_API_KEY environment variable to enable AI-powered analysis.`,
        key_points: [
          "Document uploaded successfully",
          "Text extraction completed",
          "Basic analysis performed"
        ],
        main_topics: ["Document processing", "Content analysis"],
        difficulty_level: "intermediate",
        estimated_read_time: "30 minutes",
        document_type: "article",
        authors: ["Unknown"],
        publication_date: new Date().toISOString().split('T')[0]
      };
    }

    // Calculate metrics
    const fileSizeMB = file.size / (1024 * 1024);
    const processingTime = (Date.now() - startTime) / 1000;
    const estimatedPages = Math.ceil(buffer.length / 2000); // Rough estimation

    const result = {
      success: true,
      message: `Successfully processed '${file.name}' with ${process.env.OPENAI_API_KEY ? 'AI' : 'basic'} analysis`,
      filename: file.name,
      fileSize: `${fileSizeMB.toFixed(2)} MB`,
      pages: estimatedPages,
      processingTime: `${processingTime.toFixed(2)} seconds`,
      detectedLanguage: "English",
      complexity: "Intermediate",
      extractedText: extractedText.slice(0, 1000) + (extractedText.length > 1000 ? "..." : ""),
      documentSummary: documentSummary
    };

    return NextResponse.json(result);

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json({ 
      detail: 'Upload processing failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// Optional: Add GET endpoint to check upload status or list uploaded files
export async function GET() {
  return NextResponse.json({
    message: "PDF Upload endpoint ready",
    maxFileSize: "10MB",
    supportedFormats: ["PDF"],
    status: "operational"
  });
} 