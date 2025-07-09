import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from pprint import pprint
import json
import google.generativeai as genAI
import os
import re

genAI.configure(api_key = "AIzaSyBt7d5UiyLXRjyhSDcj1D88jb8sHJK6Z_A")
llm_model = genAI.GenerativeModel("gemini-2.0-flash")

# Process paragraphs
print("----- Processing Paragraphs -----")

prompt = """Decontextualize the provided paragraph by replacing pronouns (e.g., "it", "he", "she", "they", "this", "that") 
with the full name of the entities they refer to. Keep the original paragraph structure intact.
Do not split into propositions or change the original text beyond pronoun replacement.
Important: Return ONLY the processed paragraph text as a single string. Do NOT include any explanations, formatting, or metadata.
Format your output as a simple JSON string (not an array).

Example:

Input: Title: ¯Eostre. Section: Theories and interpretations, Connection to Easter Hares. Content:
The earliest evidence for the Easter Hare (Osterhase) was recorded in south-west Germany in
1678 by the professor of medicine Georg Franck von Franckenau, but it remained unknown in
other parts of Germany until the 18th century. Scholar Richard Sermon writes that "hares were
frequently seen in gardens in spring, and thus may have served as a convenient explanation for the
origin of the colored eggs hidden there for children. Alternatively, there is a European tradition
that hares laid eggs, since a hare’s scratch or form and a lapwing’s nest look very similar, and
both occur on grassland and are first seen in the spring. In the nineteenth century the influence
of Easter cards, toys, and books was to make the Easter Hare/Rabbit popular throughout Europe.
German immigrants then exported the custom to Britain and America where it evolved into the
Easter Bunny."
Output: [ "The earliest evidence for the Easter Hare was recorded in south-west Germany in
1678 by Georg Franck von Franckenau.", "Georg Franck von Franckenau was a professor of
medicine.", "The evidence for the Easter Hare remained unknown in other parts of Germany until
the 18th century.", "Richard Sermon was a scholar.", "Richard Sermon writes a hypothesis about
the possible explanation for the connection between hares and the tradition during Easter", "Hares
were frequently seen in gardens in spring.", "Hares may have served as a convenient explanation
for the origin of the colored eggs hidden in gardens for children.", "There is a European tradition
that hares laid eggs.", "A hare’s scratch or form and a lapwing’s nest look very similar.", "Both
hares and lapwing’s nests occur on grassland and are first seen in the spring.", "In the nineteenth
century the influence of Easter cards, toys, and books was to make the Easter Hare/Rabbit popular
throughout Europe.", "German immigrants exported the custom of the Easter Hare/Rabbit to
Britain and America.", "The custom of the Easter Hare/Rabbit evolved into the Easter Bunny in
Britain and America."]

Decompose the following:
{input}"""

def process_paragraph(text):
    # Skip empty paragraphs
    if not text.strip():
        return ""
    
    # Replace prompt with improved one
    improved_prompt = """Decontextualize the provided paragraph by replacing pronouns (e.g., "it", "he", "she", "they", "this", "that") 
with the full name of the entities they refer to. Keep the original paragraph structure intact.
Do not split into propositions or change the original text beyond pronoun replacement.
Important: Return ONLY the processed paragraph text as a single string. Do NOT include any explanations, formatting, or metadata.
Format your output as a simple JSON string (not an array).

Example:

Input: The earliest evidence for the Easter Hare (Osterhase) was recorded in south-west Germany in
1678 by the professor of medicine Georg Franck von Franckenau, but it remained unknown in
other parts of Germany until the 18th century.

Output: "The earliest evidence for the Easter Hare (Osterhase) was recorded in south-west Germany in
1678 by the professor of medicine Georg Franck von Franckenau, but the Easter Hare remained unknown in
other parts of Germany until the 18th century."

Process the following paragraph:
{input}"""
    
    response = llm_model.generate_content(improved_prompt.replace("{input}", text)).text
    # Print response to debug
    print(f"Raw response: {response[:100]}...") # Print first 100 chars for debugging
    
    # Try to parse the response as JSON
    try:
        # Try direct JSON parsing
        try:
            parsed_response = json.loads(response)
            # Ensure we always return a string
            if isinstance(parsed_response, str):
                return parsed_response
            elif isinstance(parsed_response, dict) and any(isinstance(v, str) for v in parsed_response.values()):
                # If it's a dict with string values, convert to string
                return str(next((v for v in parsed_response.values() if isinstance(v, str)), str(parsed_response)))
            elif isinstance(parsed_response, list) and len(parsed_response) > 0:
                # If it's a list, take the first string item or convert first item to string
                return str(next((item for item in parsed_response if isinstance(item, str)), str(parsed_response[0])))
            else:
                # For any other type, convert to string
                return str(parsed_response)
        except:
            # Look for a JSON string in the response
            import re
            # Look for content in quotes that might be JSON
            json_match = re.search(r'"(.*?)"', response, re.DOTALL)
            if json_match:
                # Try to extract the content inside quotes
                extracted = json_match.group(1).replace('\\"', '"')
                return extracted
            # If not found, try to remove code formatting if present
            code_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
            if code_match:
                content = code_match.group(1)
                # Try parsing again
                try:
                    parsed = json.loads(content)
                    # Ensure we always return a string
                    if isinstance(parsed, str):
                        return parsed
                    elif isinstance(parsed, dict) and any(isinstance(v, str) for v in parsed.values()):
                        # If it's a dict with string values, convert to string
                        return str(next((v for v in parsed.values() if isinstance(v, str)), str(parsed)))
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        # If it's a list, take the first string item or convert first item to string
                        return str(next((item for item in parsed if isinstance(item, str)), str(parsed[0])))
                    else:
                        # For any other type, convert to string
                        return str(parsed)
                except:
                    pass
            
        # If all parsing attempts fail, return original text with warning
        print("Warning: Could not parse LLM response as proper JSON, using original text")
        return text
    except Exception as e:
        print(f"Error: {e}")
        print(f"Problem response: {response}")
        # Return the original text as fallback
        return text

with open("D:\\agentic_chunker\\sample_text_data.txt", "r") as file:
    text = file.read()
    
# Split by double newline but filter out empty paragraphs
paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
print(f"Found {len(paragraphs)} paragraphs in the document")

processed_paragraphs = []
for i, para in enumerate(paragraphs):
    print(f"Processing paragraph {i+1}/{len(paragraphs)}...")
    processed_para = process_paragraph(para)
    if processed_para:  # Only add non-empty paragraphs
        processed_paragraphs.append(processed_para)
    print(f"Done with {i+1}-Paragraph")

print(f"Successfully processed {len(processed_paragraphs)} paragraphs\n")
if processed_paragraphs:
    print("Sample of processed paragraphs:")
    pprint(processed_paragraphs[0])
    if len(processed_paragraphs) > 1:
        pprint(processed_paragraphs[1])
print("\n")


print("----- Agentic Chunking ------")

from AgenticChunker import AgenticChunker
ac = AgenticChunker()
# Process all paragraphs, not just the first few
ac.add_paragraphs(processed_paragraphs)

# Export chunks to JSON file
with open("D:\\agentic_chunker\\chunks.json", "w") as json_file:
    json.dump(ac.get_chunks_for_export(), json_file, indent=4)
print("Chunks exported to chunks.json")

ac.pretty_print_chunks()
