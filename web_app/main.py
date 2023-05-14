import os
import openai
import re
openai.api_key = os.getenv("OPENAI_API_KEY")

# reference - (Ryan & Deci, 2000)
# model = "gpt-4"
model = "gpt-3.5-turbo"

# Report handles the student report written by the student
class Report:
  def __init__(self, path="", text=""):
    # Provide path to report
    self.path = path
    # Otherwise use raw text input
    self.text = text

    # Convert file path to text
    if path:
      with open(path) as f:
        self.text = f.read()

  # Getter for raw student original text
  def get_text(self):
    return self.text

  # Rewrite student report based on findings supplied
  # Findings - List of all relevant findings identified
  def rewrite(self, findings, citation, output_terminal=False):
    concat_findings = "I have conducted research recently and discovered the following cool ideas and findings from a research paper I read:\n\n"
    for num, finding in enumerate(findings):
      concat_findings = concat_findings + str(num+1) + ": " + finding

    rewrite_prompt = "Using these findings, rewrite my report below, integrating the ideas and findings discovered from the research above. Do so in an extremely professional, academic, superb quality, that would be accepted in professional academia. Focus only on integrating my findings in a natural manner into the body of text.\n"
    citation_prompt = "A reminder that when referring to the findings I have supplied, utilise the in-text reference of the paper: " + citation + "\nThis must be done to ensure the paper is cited appropriately using the supplied in-text reference.\n"
    report_prompt = "My report is below:\n\n"

    question = concat_findings + "\n" + rewrite_prompt + citation_prompt + report_prompt + self.text

    completion = openai.ChatCompletion.create(
      model=model,
      messages=[
        {"role": "user", "content": question}
      ]
    )
    new_text = completion.choices[0].message.content

    if output_terminal:
      print(new_text)
    with open('output.txt', 'w') as f:
      f.write(new_text)

    return new_text

class Research:
  def __init__(self, path="", text=""):
    self.path = path
    self.text = text
    self.analysis_list = []
    self.citation = ""
    self.student_report = ""

    if path:
      with open(path) as f:
        self.text = f.read()

  def set_student_report(self, student_report):
    self.student_report = student_report
  
  def read(self, dot_points=3):
    question = "Identify exactly " + str(dot_points) + "key takeaways from this research paper: " + self.text

    completion = openai.ChatCompletion.create(
      model=model,
      messages=[
        {"role": "user", "content": question}
      ]
    )

    analysis = completion.choices[0].message.content
    pattern = r'\d+\.\s'
    self.analysis_list = re.split(pattern, analysis.strip())[1:]
    
  def select(self, selected_items=[]):
    filtered_analysis = []

    if not selected_items:
      print("The following dot points have been extracted from the research provided. Answer Yes (Y) or No (N) to decide if the item should be included:")
      for number, analysis in enumerate(self.analysis_list):
        relevance = self.relevance_helper(analysis)
        selection = input(str(number + 1) + " (" + relevance + " Relevance): " + ''.join(analysis.split('\n')) + '\n')
        if (selection == "Y" or selection == "y"):
          filtered_analysis.append(analysis)
    else:
      for number, analysis in enumerate(self.analysis_list):
        for selected_item in selected_items:
          if number == selected_item:
            filtered_analysis.append(analysis)

    return filtered_analysis
  
  def get_analysis_list(self, include_relevancy=False):
    if include_relevancy:
      temp_analysis = []
      for item in self.analysis_list:
        relevance = self.relevance_helper(item)
        finding_result = {
          "finding": item,
          "relevance": relevance
        }
        temp_analysis.append(finding_result)
      return temp_analysis
    else:
      return self.analysis_list

  def relevance_helper(self, finding):
    question = "Here is something cool I recently found: " + finding + "\n Give a percentage value that indicates what percent this cool piece of knowledge relates to my report below:" + self.student_report + "\n Respond by only giving the raw percentage value, nothing else. RESPOND ONLY WITH A RAW PERCENTAGE VALUE!"
    completion = openai.ChatCompletion.create(
      model=model,
      messages=[
        {"role": "user", "content": question}
      ]
    )
    return completion.choices[0].message.content

  def set_citation(self, citation=""):
    if not citation:
      self.citation = str(input('Please provide the appropriate in-text reference for the research paper you supplied: '))
    else:
      self.citation = citation

  def get_citation(self):
    return self.citation

if __name__ == "__main__":
    research = Research('research.txt')
    takeaways = int(input('How many takeaways would you like from this paper? '))
    research.read(takeaways)
    report = Report('report.txt')

    research.set_student_report(report.get_text())

    inquiry = research.select()

    research.set_citation()

    report.rewrite(inquiry, research.get_citation())

    print(research.get_analysis_list(include_relevancy=True))