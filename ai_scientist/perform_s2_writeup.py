import json
import os
from ai_scientist.tools.semantic_scholar import SemanticScholarSearchTool
import argparse
import google.generativeai as genai

# Initialize Gemini client
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

def search_papers(query, num_papers=3):
    """Searches Semantic Scholar for relevant papers."""
    s2 = SemanticScholarSearchTool()
    results = s2.search_for_papers(query)
    return results

def generate_paper(topic, search_results):
    """Generates a paper with the specified sections in LaTeX format."""
    paper = "\\documentclass{article}\n"
    paper += "\\usepackage{amsmath}\n"
    paper += "\\usepackage{graphicx}\n"
    paper += "\\title{" + topic['Title'] + "}\n"
    paper += "\\author{}\n"
    paper += "\\date{}\n"
    paper += "\\begin{document}\n"
    paper += "\\maketitle\n"

    paper += "\\section{Purpose}\n"
    paper += "[Add the purpose of the research here, based on the topic.]\n\n"

    paper += "\\section{Background}\n"
    paper += topic['Related Work'] + "\n\n"

    paper += "\\section{Experiments}\n"
    if 'Experiments' in topic:
        paper += "\\begin{enumerate}\n"
        for experiment in topic['Experiments']:
            paper += "\\item " + experiment + "\n"
        paper += "\\end{enumerate}\n"
    else:
        paper += "No experiments described.\\n\\n"

    # Generate Results section using Gemini
    results_prompt = f"Generate the expected results for the following research topic in Japanese: {topic['Title']}. The experiments are: {topic.get('Experiments', 'No experiments described.')}"
    results_response = model.generate_content(results_prompt)
    results_text = results_response.text

    paper += "\\section{Results}\n"
    paper += results_text + "\n\n"

    # Generate Discussion section using Gemini
    discussion_prompt = f"Generate a discussion based on the following results in Japanese: {results_text}. The research topic is: {topic['Title']}"
    discussion_response = model.generate_content(discussion_prompt)
    discussion_text = discussion_response.text

    paper += "\\section{Discussion}\n"
    paper += discussion_text + "\n\n"

    paper += "\\section{Conclusion}\n"
    paper += "[Add your conclusion here].\n\n"

    paper += "\\section{References}\n"
    paper += "No references available (API calls disabled).\n\n"

    paper += "\\end{document}\n"
    return paper

def main(json_file_path, output_dir="s2_papers"):
    """
    Reads research topics from a JSON file, searches for papers on Semantic Scholar,
    and generates a paper for each topic.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(json_file_path, 'r') as f:
        topics = json.load(f)

    for topic in topics:
        search_query = f"{topic['Title']} {topic['Abstract']}　抗曇";
        search_results = search_papers(search_query)
        paper = generate_paper(topic, search_results)

        output_file = os.path.join(output_dir, f"{topic['Name']}_s2_paper.tex")
        with open(output_file, 'w') as f:
            f.write(paper)

        print(f"Paper generated for {topic['Name']} and saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate papers from research topics using Semantic Scholar.")
    parser.add_argument("json_file_path", help="Path to the JSON file containing research topics.")
    parser.add_argument("--output_dir", help="Directory to save the generated papers (default: s2_papers).", default="s2_papers")

    args = parser.parse_args()

    main(args.json_file_path, args.output_dir)
