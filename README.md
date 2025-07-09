## AThis edition builds **Who is the "agent" here?** You're correct - it's the LLM acting as a human-like agent!!

### Understand Files

- **`main.py`**: The main file responsible for processing paragraphs from a given text, decontextualizing them, and executing the agentic chunking process.
- **`AgenticChunker.py`**: Contains the class and methods that implement the agentic chunking functionality.
- **`chunks.json`**: Output file containing the organized chunks with their titles, summaries, and constituent paragraphs. work of Ranjith, but uses full paragraphs rather than atomic propositions.

### How does a human go about chunking a text?

1. You take a pen and paper, and you start at the top of the text, treating the first part as the starting point for a new chunk.

2. As you move down the text, you evaluate if a new paragraph should be a part of the previous chunk (if similarity > 50%), if not, then create a new chunk.

3. You repeat this process, methodically working through the text chunk by chunk until you've covered the entire text.

4. Special attention is paid to section headers (often in uppercase) which typically indicate the beginning of a new topic and thus a new chunk.unker

Agentic Chunking involves taking a text and organizing its paragraphs into grouped "chunks." Each chunk is a collection of related paragraphs that are semantically interconnected, allowing for more efficient processing and retrieval within a RAG system.

This edition builds on the work of Ranjith.

### How does a human go about chunking a text?

1. You take a pen and paper, and you start at the top of the text, treating the first part as the starting point for a new chunk.

2. As you move down the text, you evaluate if a new sentence or piece should be a part of the previous chunk, if not, then create a new chunk.

3. You repeat this process, methodically working through the text chunk by chunk until you've covered the entire text.

**Who is the "agent" here?** You're correct - it's the human!!

### Understand Files

- **`main.py`**: The main file responsible for generating propositions from a given text and executing the agentic chunking process.
- **`AgenticChunker.py`**: Contains the class and methods that implement the agentic chunking functionality.

### Features

1. **Paragraph-Based Processing**: Works with complete paragraphs rather than breaking text into atomic propositions.

2. **Intelligent Chunking**: Uses AI to determine when paragraphs belong together or should form new chunks.

3. **Strict Similarity Threshold**: Only groups paragraphs when they have >50% similarity, creating more focused chunks.

4. **Section Header Detection**: Automatically identifies potential section headers (uppercase text) as likely new chunk boundaries.

5. **Introduction Handling**: Special handling for introductory paragraphs to avoid over-grouping content with general introductions.

6. **JSON Export**: Exports all chunks with their titles, summaries, and paragraphs to a JSON file for easy integration with other systems.

### Usage

1. Place your text file at `D:\agentic_chunker\sample_text_data.txt` (or modify the path in the code).

2. Run the main script:
   ```
   python main.py
   ```

3. The script will:
   - Process each paragraph by decontextualizing pronouns
   - Group related paragraphs into chunks
   - Generate appropriate titles and summaries for each chunk
   - Export results to `chunks.json`
   - Display chunks with their contents in the console

4. Examine the created chunks in `chunks.json` for use in your RAG system or other applications.
