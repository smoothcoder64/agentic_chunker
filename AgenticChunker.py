import uuid
import google.generativeai as genAI
import time
import os

genAI.configure(api_key = "AIzaSyC1H9Sc76_UQdYzYhvfK0am1gX6-1fvRks")

class AgenticChunker:
    def __init__(self):
        self.chunks = {} # chunk information
        self.agent = genAI.GenerativeModel("gemini-2.0-flash") # LLM model
        self.chunk_id_length = 5 # For truncating the Chunk ID

    def add_paragraphs(self, paragraphs):
        for paragraph in paragraphs:
            self.add_paragraph(paragraph)
            time.sleep(1.5) # This pause is required for controlling the overhead through API calls
    
    def add_paragraph(self, paragraph): # Method to add a paragraph to a chunk
        # Convert paragraph to string if it's not already
        if not isinstance(paragraph, str):
            print(f"Warning: Converting non-string paragraph to string: {type(paragraph)}")
            paragraph = str(paragraph)
            
        print(f"Adding paragraph: {paragraph[:50]}...")

        if len(self.chunks) == 0: # When there is no chunk present
            print("No Chunks, Creating!!")
            self.create_new_chunk(paragraph)
            return
        
        relevant_chunk_id = self.find_relevant_chunk(paragraph) # To get a relevant chunk with respective to paragraph
        
        if relevant_chunk_id != None: # if a relevant chunk is found
            print(f"Chunk Found!! ({self.chunks[relevant_chunk_id]['chunk_id']}), adding to : {self.chunks[relevant_chunk_id]['title']}")
            self.add_paragraph_to_chunk(relevant_chunk_id, paragraph) # Add the paragraph to existing chunk, update title and summary
            return
        else:
            print("Chunk Not Found")
            self.create_new_chunk(paragraph) # Create a new chunk

    def add_paragraph_to_chunk(self, chunk_id, paragraph):
        # Ensure paragraph is a string
        if not isinstance(paragraph, str):
            paragraph = str(paragraph)
            
        self.chunks[chunk_id]["paragraphs"].append(paragraph)

        self.chunks[chunk_id]["summary"] = self.update_chunk_summary(self.chunks[chunk_id])
        self.chunks[chunk_id]["title"] = self.update_chunk_title(self.chunks[chunk_id])
    
    def update_chunk_summary(self, chunk): # Method to update with new paragraphs and assign summary to a chunk
        prompt = f"""
        You are the steward of a group of chunks which represent groups of paragraphs that talk about a similar topic
        A new paragraph was just added to one of your chunks, you should generate a very brief 1-sentence summary which will inform viewers what a chunk group is about.

        A good summary will say what the chunk is about, and give any clarifying instructions on what to add to the chunk.

        You will be given a group of paragraphs which are in the chunk and the chunks current summary.

        Your summaries should anticipate generalization. If you get a paragraph about apples, generalize it to food.
        Or month, generalize it to "date and times".

        Example:
        Input: Paragraph: Greg likes to eat pizza. He enjoys trying different toppings.
        Output: This chunk contains information about the types of food Greg likes to eat.

        Only respond with the chunk new summary, nothing else.

        Chunk's paragraphs:\n{chunk['paragraphs']}\n\nCurrent chunk summary:\n{chunk['summary']}
        """

        return self.agent.generate_content(prompt).text # returns updated summary

    def update_chunk_title(self, chunk): # Method to update with new paragraphs and assign title to a chunk
        prompt = f"""
        You are the steward of a group of chunks which represent groups of paragraphs that talk about a similar topic
        A new paragraph was just added to one of your chunks, you should generate a very brief updated chunk title which will inform viewers what a chunk group is about.

        A good title will say what the chunk is about.

        You will be given a group of paragraphs which are in the chunk, chunk summary and the chunk title.

        Your title should anticipate generalization. If you get a paragraph about apples, generalize it to food.
        Or month, generalize it to "date and times".

        Example:
        Input: Summary: This chunk is about dates and times that the author talks about
        Output: Date & Times

        Only respond with the new chunk title, nothing else.

        Chunk's paragraphs:\n{chunk['paragraphs']}\n\nChunk summary:\n{chunk['summary']}\n\nCurrent chunk title:\n{chunk['title']}
        """

        return self.agent.generate_content(prompt).text # returns updated title

    def get_new_chunk_summary(self, paragraph): # Method to create and assign summary to a chunk
        prompt = f"""
        You are the steward of a group of chunks which represent groups of paragraphs that talk about a similar topic
        You should generate a very brief 1-sentence summary which will inform viewers what a chunk group is about.

        A good summary will say what the chunk is about, and give any clarifying instructions on what to add to the chunk.

        You will be given a paragraph which will go into a new chunk. This new chunk needs a summary.

        Your summaries should anticipate generalization. If you get a paragraph about apples, generalize it to food.
        Or month, generalize it to "date and times".

        Example:
        Input: Paragraph: Greg likes to eat pizza. He enjoys trying different toppings.
        Output: This chunk contains information about the types of food Greg likes to eat.

        Only respond with the new chunk summary, nothing else.

        Determine the summary of the new chunk that this paragraph will go into:
        {paragraph}
        """
        return self.agent.generate_content(prompt).text # generates a title

    def get_new_chunk_title(self, summary): # Method to create and assign title to a chunk
        prompt = f"""
        You are the steward of a group of chunks which represent groups of paragraphs that talk about a similar topic.
        You should generate a very brief, precise and specific chunk title (2-5 words) which will inform viewers what this specific chunk group is about.

        A good chunk title is brief but specifically describes what the chunk is about.
        For technical or formal documents, preserve key terminology in your titles.
        For section headers that appear in uppercase in the text, maintain that terminology in your title.

        You will be given a summary of a chunk which needs a title.

        Titles should be specific rather than overly generic. If the content is about "Pipeline Safety Requirements," 
        don't just title it "Safety" - be specific: "Pipeline Safety Requirements".

        Example:
        Input Summary: This chunk contains information about the specific risk assessment procedures required for pipeline integrity management.
        Output: PIPELINE RISK ASSESSMENT

        Only respond with the new chunk title, nothing else.

        Determine the title of the chunk that this summary belongs to:
        {summary}
        """
        return self.agent.generate_content(prompt).text # generates a summary

    def create_new_chunk(self, paragraph): # Method to create a new chunk, add summary and title with respective to the paragraph
        # Ensure paragraph is a string
        if not isinstance(paragraph, str):
            paragraph = str(paragraph)
            
        new_chunk_id = str(uuid.uuid4())[:self.chunk_id_length] # chunk's unique id
        new_chunk_summary = self.get_new_chunk_summary(paragraph) # chunk's summary
        new_chunk_title = self.get_new_chunk_title(new_chunk_summary) # chunk's title

        self.chunks[new_chunk_id] = {
            'chunk_id' : new_chunk_id,
            'paragraphs': [paragraph],
            'title' : new_chunk_title,
            'summary': new_chunk_summary,
            'chunk_index' : len(self.chunks)
        }

        print(f"Created new chunk ({new_chunk_id}) : {new_chunk_title}")

    def get_chunk_outline(self): # Method that returns all the chunks' detail
        curr_chunk_outline = ""

        for chunk_id, chunk in self.chunks.items():
            chunk_outline = f"Chunk ID: {chunk_id}\nChunk Name: {chunk['title']}\nChunk Summary: {chunk['summary']}\n\n"
            curr_chunk_outline += chunk_outline
        
        return curr_chunk_outline
    
    def find_relevant_chunk(self, paragraph): # Method to search for a chunk present in the self.chunks that matches this paragraph
        curr_chunk_outline = self.get_chunk_outline()
        
        # Ensure paragraph is a string
        if not isinstance(paragraph, str):
            paragraph = str(paragraph)
            
        # Check for uppercase section headers which often indicate new topics
        uppercase_words = sum(1 for word in paragraph.split() if word.isupper())
        total_words = len(paragraph.split())
        uppercase_ratio = uppercase_words / total_words if total_words > 0 else 0
        
        # If paragraph has significant uppercase words (potential section header), create new chunk
        if uppercase_ratio > 0.3 and uppercase_words > 2:
            print("Detected potential section header with uppercase words - creating new chunk")
            return None
            
        # Special handling for first few paragraphs that might be introductions
        if len(self.chunks) <= 2 and len(self.chunks) > 0:
            # Get the index of the first chunk
            first_chunk_index = min(chunk['chunk_index'] for chunk in self.chunks.values())
            # If we're processing what might be an introduction followed by content
            if any(chunk['chunk_index'] == first_chunk_index for chunk in self.chunks.values()):
                print("Special handling for content after introduction")
                # Increase threshold for similarity to avoid everything going into introduction

        prompt = f"""
        Determine whether or not the "Paragraph" should belong to any of the existing chunks.

        A paragraph should ONLY belong to a chunk if their meaning, direction, or intention are VERY similar (>50% similarity).
        Be very strict in your evaluation - if there's any doubt, DO NOT add to an existing chunk.
        Create new chunks liberally rather than forcing content into existing ones.
        
        Pay special attention to:
        1. Paragraphs with uppercase words/sections as they often indicate new topics
        2. Early paragraphs that might be general introductions shouldn't absorb specific content 
           that follows
        
        Evaluate similarity based on:
        - Specific subject matter (not just general topics)
        - Document section/purpose
        - Level of detail/specificity
        
        If you think a paragraph should be joined with a chunk, return the chunk id.
        If you do not think an item should be joined with an existing chunk, just return "No chunks"

        Example:
        Input:
            - Paragraph: "Greg really likes hamburgers. He often eats them on weekends."
            - Current Chunks:
                - Chunk ID: 2n4l3d
                - Chunk Name: Places in San Francisco
                - Chunk Summary: Overview of the things to do with San Francisco Places

                - Chunk ID: 93833k
                - Chunk Name: Food Greg likes
                - Chunk Summary: Lists of the food and dishes that Greg likes
        Output: 93833k
        
        Current Chunks:\n--Start of current chunks--\n{curr_chunk_outline}\n--End of current chunks--
        Determine if the following paragraph should belong to one of the chunks outlined:
        {paragraph}
        """
        curr_chunk_id = self.agent.generate_content(prompt).text.strip()
        
        if len(curr_chunk_id) != self.chunk_id_length:
            return None
        return curr_chunk_id

    def pretty_print_chunks(self): # Method to display the chunks
        print("\n----- Chunks Created -----\n")
        for _, chunk in self.chunks.items():
            print(f"Chunk ID    : {chunk['chunk_id']}")
            print(f"Title       : {chunk['title'].strip() if isinstance(chunk['title'], str) else str(chunk['title'])}")
            print(f"Summary     : {chunk['summary'].strip() if isinstance(chunk['summary'], str) else str(chunk['summary'])}")
            print("Paragraphs:")
            for para in chunk['paragraphs']:
                para_str = str(para) if not isinstance(para, str) else para
                print(f"    -{para_str[:50]}...")  # Print first 50 chars of each paragraph
            print("\n\n")
            
    def get_chunks_for_export(self):
        """Export chunks in a format suitable for JSON file"""
        export_data = {}
        for chunk_id, chunk in self.chunks.items():
            export_data[chunk_id] = {
                'title': chunk['title'].strip(),
                'summary': chunk['summary'].strip(),
                'paragraphs': chunk['paragraphs']
            }
        return export_data
